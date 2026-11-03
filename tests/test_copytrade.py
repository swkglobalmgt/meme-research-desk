from datetime import datetime, timedelta, timezone

import pytest

from desk import copytrade, ledger
from desk.config import USDC_MINT, CopyRules
from desk.db import DB, iso
from desk.sources import geckoterminal as gt
from desk.sources import onchain

W = "LeaderWallet1111111111111111111111111111111"
MEME = "MemeMint111111111111111111111111111111111pump"
NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def row(**kw):
    r = {"wallet": "w1", "closed_positions": 40, "realized_pnl_usd": 900, "total_cost_usd": 6000,
         "median_position_usd": 150, "win_rate": 0.48, "best_trade_share": 0.2, "pnl_7d": 120,
         "positive_weeks": 4, "active_weeks": 4}
    r.update(kw)
    return r


def test_screen_leaders_rules():
    rows = [row(wallet="good"),
            row(wallet="few", closed_positions=5),
            row(wallet="lucky", best_trade_share=0.8),
            row(wallet="streaky", positive_weeks=1),
            row(wallet="cold", pnl_7d=-10),
            row(wallet="whale", median_position_usd=90_000),
            row(wallet="dust", median_position_usd=3),
            row(wallet="loser", realized_pnl_usd=-5),
            row(wallet="coinflip", win_rate=0.2)]
    picked, rej = copytrade.screen_leaders(rows)
    assert [r["wallet"] for r in picked] == ["good"]
    assert rej["lucky"] == "profit mostly from one coin"
    assert rej["streaky"] == "not profitable in enough weeks"
    assert rej["whale"] == "position size not copyable"
    assert len(rej) == 8


def test_screen_ranks_by_return_not_size_and_caps():
    rules = CopyRules(max_leaders=2)
    rows = [row(wallet="big", realized_pnl_usd=5000, total_cost_usd=200_000),   # 2.5%
            row(wallet="eff", realized_pnl_usd=800, total_cost_usd=2_000),      # 40%
            row(wallet="mid", realized_pnl_usd=1000, total_cost_usd=10_000)]    # 10%
    picked, rej = copytrade.screen_leaders(rows, rules)
    assert [r["wallet"] for r in picked] == ["eff", "mid"]
    assert rej["big"] == "ranked below the cut"


def tx(pre, post, sol_pre=1_000_000_000, sol_post=1_000_000_000, err=None, t=1_793_000_000):
    def bal(entries):
        return [{"accountIndex": i, "mint": m, "owner": o, "uiTokenAmount": {"uiAmountString": str(a)}}
                for i, (m, o, a) in enumerate(entries)]
    return {"blockTime": t, "meta": {"err": err, "preTokenBalances": bal(pre), "postTokenBalances": bal(post),
                                     "preBalances": [sol_pre], "postBalances": [sol_post]},
            "transaction": {"message": {"accountKeys": [{"pubkey": W}]}}}


def test_parse_buy_and_sell():
    buy = copytrade.parse_swap(tx([(USDC_MINT, W, 500), (MEME, W, 0)], [(USDC_MINT, W, 400), (MEME, W, 1e6)]), W)
    assert buy["side"] == "buy" and buy["mint"] == MEME and buy["quote_delta"] == -100
    sell = copytrade.parse_swap(tx([(USDC_MINT, W, 400), (MEME, W, 1e6)], [(USDC_MINT, W, 530), (MEME, W, 0)]), W)
    assert sell["side"] == "sell" and sell["token_delta"] == -1e6


def test_parse_buy_with_sol():
    t = tx([(MEME, W, 0)], [(MEME, W, 5000)], sol_pre=2_000_000_000, sol_post=1_500_000_000)
    assert copytrade.parse_swap(t, W)["side"] == "buy"


def test_parse_ignores_transfers_failures_and_other_owners():
    airdrop = tx([(MEME, W, 0)], [(MEME, W, 1000)])           # tokens arrive, nothing paid
    assert copytrade.parse_swap(airdrop, W) is None
    failed = tx([(USDC_MINT, W, 500)], [(USDC_MINT, W, 400)], err={"x": 1})
    assert copytrade.parse_swap(failed, W) is None
    other = tx([(USDC_MINT, "X", 500), (MEME, "X", 0)], [(USDC_MINT, "X", 400), (MEME, "X", 10)])
    assert copytrade.parse_swap(other, W) is None
    assert copytrade.parse_swap(None, W) is None


def test_scan_exit_leader_sold_at_low():
    T = 1_793_000_040
    candles = [(T, 1.0, 1.1, 0.95, 1.0, 1), (T + 60, 1.05, 1.1, 0.9, 1.0, 1)]
    assert ledger.scan_exit(candles, T - 60, 2.0, 0.5, T + 99999, leader_exit_epoch=T + 30) == (T + 60, 0.9, "leader_sold")


@pytest.fixture
def db():
    d = DB("sqlite:///:memory:")
    d.init()
    yield d
    d.close()


def test_new_leader_starts_from_now_no_backfill(db, monkeypatch):
    monkeypatch.setattr(copytrade, "recent_signatures", lambda w, until, limit: [{"signature": "NEWEST"}])
    out = copytrade.refresh_leaders(db, NOW, [], run_query=lambda: [row(wallet=W)])
    assert out["selected"] == 1
    L = db.one("SELECT * FROM leaders")
    assert L["last_sig"] == "NEWEST" and L["active"] == 1
    # within a week: no re-screen
    assert copytrade.refresh_leaders(db, NOW + timedelta(days=2), [], run_query=lambda: [])["status"] == "fresh"
    # a week later the leader no longer qualifies -> unfollowed
    copytrade.refresh_leaders(db, NOW + timedelta(days=8), [], run_query=lambda: [row(wallet=W, pnl_7d=-1)])
    assert db.one("SELECT active FROM leaders")["active"] == 0


def test_screen_error_is_recorded_not_fatal(db):
    def boom():
        raise RuntimeError("dune down")
    out = copytrade.refresh_leaders(db, NOW, [], run_query=boom)
    assert out["status"].startswith("error")
    assert db.one("SELECT error FROM leader_screens")["error"] == "dune down"


def _leader(db, active=1):
    db.insert("leaders", {"wallet": W, "selected_at": iso(NOW - timedelta(days=1)), "active": active, "last_sig": "OLD"})


def test_poll_records_trades_and_returns_buys(db, monkeypatch):
    _leader(db)
    monkeypatch.setattr(copytrade, "recent_signatures",
                        lambda w, until, limit: [{"signature": "S2", "err": None}, {"signature": "S1", "err": None}])
    txs = {"S1": tx([(USDC_MINT, W, 500)], [(USDC_MINT, W, 400), (MEME, W, 10)], t=int(NOW.timestamp()) - 600),
           "S2": tx([(USDC_MINT, W, 400), (MEME, W, 10)], [(USDC_MINT, W, 450)], t=int(NOW.timestamp()) - 60)}
    monkeypatch.setattr(copytrade, "get_tx", lambda s: txs[s])
    buys = copytrade.poll_leaders(db, NOW, [])
    assert [b["mint"] for b in buys] == [MEME]
    assert db.one("SELECT COUNT(*) AS n FROM leader_trades")["n"] == 2
    assert db.one("SELECT last_sig FROM leaders")["last_sig"] == "S2"
    # second poll sees nothing new and does not duplicate
    monkeypatch.setattr(copytrade, "recent_signatures", lambda w, until, limit: [])
    assert copytrade.poll_leaders(db, NOW, []) == []


SAFE_REPORT = {"markets": [{"pubkey": "x", "lp": {"lpLockedPct": 100, "baseUSD": 1, "quoteUSD": 1}}],
               "topHolders": [{"address": f"h{i}", "owner": f"o{i}", "pct": 1.0} for i in range(12)]}


def _pool(liq):
    return {"pool_address": "POOLM", "token_mint": MEME, "symbol": "MEME", "name": "MEME / SOL",
            "pool_created_at": iso(NOW - timedelta(hours=6)), "price_usd": 0.001, "liquidity_usd": liq,
            "sells_h1": 100, "sellers_h1": 50}


def _mock_safety(monkeypatch, mint_auth=None):
    monkeypatch.setattr(onchain, "mint_info", lambda m: {"mint_authority": mint_auth, "freeze_authority": None,
                                                         "decimals": 6, "extensions": {}})
    monkeypatch.setattr(onchain, "rugcheck_report", lambda m: SAFE_REPORT)
    monkeypatch.setattr(onchain, "jupiter_sell_quote", lambda m, d, a: {"out_usd": 96.0})


def test_copy_signal_pending_when_safe(db, monkeypatch):
    _leader(db)
    _mock_safety(monkeypatch)
    monkeypatch.setattr(gt, "token_pools", lambda m: [_pool(90_000)])
    c = copytrade.make_signals(db, NOW, [{"wallet": W, "mint": MEME, "time": NOW - timedelta(minutes=10), "sig": "S1"}], [])
    assert c["pending"] == 1
    s = db.one("SELECT * FROM signals")
    assert s["status"] == "pending" and s["leader"] == W and s["ts"] == iso(NOW - timedelta(minutes=10))


def test_already_rugged_token_is_still_counted(db, monkeypatch):
    """No survivorship bias: a rug that happened before we noticed still counts."""
    _leader(db)
    _mock_safety(monkeypatch)
    monkeypatch.setattr(gt, "token_pools", lambda m: [_pool(300)])
    c = copytrade.make_signals(db, NOW, [{"wallet": W, "mint": MEME, "time": NOW - timedelta(minutes=10), "sig": "S1"}], [])
    assert c["counted_rug"] == 1
    assert db.one("SELECT status FROM signals")["status"] == "pending"


def test_unsafe_token_rejected_even_if_rugged(db, monkeypatch):
    _leader(db)
    _mock_safety(monkeypatch, mint_auth="DEV")   # we would never have bought this
    monkeypatch.setattr(gt, "token_pools", lambda m: [_pool(300)])
    c = copytrade.make_signals(db, NOW, [{"wallet": W, "mint": MEME, "time": NOW - timedelta(minutes=10), "sig": "S1"}], [])
    assert c["rejected_safety"] == 1


def test_stale_buys_skipped(db):
    c = copytrade.make_signals(db, NOW, [{"wallet": W, "mint": MEME, "time": NOW - timedelta(hours=13), "sig": "S"}], [])
    assert c["stale"] == 1


def test_full_copy_trade_exits_when_leader_sells(db):
    T = int((NOW - timedelta(hours=2)).timestamp()) // 60 * 60
    sig_dt = datetime.fromtimestamp(T, tz=timezone.utc)
    db.insert("signals", {"strategy": "copy_trader", "pool_address": "POOLM", "token_mint": MEME, "symbol": "MEME",
                          "ts": iso(sig_dt), "signal_price": 1.0, "liquidity_usd": 100_000, "status": "pending",
                          "leader": W})
    db.insert("leader_trades", {"sig": "SELL", "wallet": W, "block_time": iso(sig_dt + timedelta(minutes=5)),
                                "mint": MEME, "side": "sell", "seen_at": iso(NOW)})
    candles = [(T + 60 * i, 1.0, 1.05, 0.97, 1.0, 1) for i in range(1, 12)]
    ledger.fill_pending(db, NOW, lambda p: candles, [])
    pos = db.one("SELECT * FROM positions")
    assert pos["leader"] == W
    ledger.manage_open(db, NOW, lambda p: candles, lambda p: {"liquidity_usd": 100_000, "price_usd": 1.0}, [],
                       leader_exit=lambda p: copytrade.leader_exit_epoch(db, p))
    pos = db.one("SELECT * FROM positions")
    assert pos["exit_reason"] == "leader_sold" and pos["exit_price"] == 0.97
    # leader sold at T+300 -> we follow 60s later -> first candle at/after T+360
    assert pos["exit_ts"] == iso(datetime.fromtimestamp(T + 360, tz=timezone.utc))
