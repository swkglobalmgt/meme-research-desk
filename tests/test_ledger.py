from datetime import datetime, timedelta, timezone

import pytest

from desk import costs, ledger, report
from desk.db import DB, iso

T0 = 1_793_000_000 - (1_793_000_000 % 60)   # a minute boundary
NOW = datetime.fromtimestamp(T0 + 6 * 3600, tz=timezone.utc)


def c(ts, o, h, l, cl):
    return (ts, o, h, l, cl, 1000.0)


# --- entry fills -----------------------------------------------------------

def test_fill_waits_60s_and_takes_candle_high():
    candles = [c(T0, 1, 1.1, 0.9, 1), c(T0 + 60, 1, 1.5, 0.95, 1.2), c(T0 + 120, 1.2, 1.3, 1.1, 1.2)]
    # signal at T0+10 -> earliest fill T0+70 -> first candle starting >= that is T0+120
    assert ledger.find_fill(candles, T0 + 10) == (T0 + 120, 1.3)
    # signal exactly on a minute -> candle starting at +60 qualifies
    assert ledger.find_fill(candles, T0) == (T0 + 60, 1.5)


def test_fill_waits_when_no_candle_yet_and_cancels_when_dead():
    assert ledger.find_fill([c(T0, 1, 1, 1, 1)], T0) is None
    late = [c(T0 + 60 + 16 * 60, 1, 1, 1, 1)]
    assert ledger.find_fill(late, T0) == "cancel"


# --- exits ------------------------------------------------------------------

TP, SL, MAXH = 1.3, 0.8, T0 + 10_000


def test_stop_checked_before_take_profit_in_same_candle():
    assert ledger.scan_exit([c(T0 + 60, 1, 1.4, 0.7, 1)], T0, TP, SL, MAXH) == (T0 + 60, SL, "stop_loss")


def test_gap_through_stop_exits_at_worse_open():
    assert ledger.scan_exit([c(T0 + 60, 0.3, 0.35, 0.2, 0.25)], T0, TP, SL, MAXH) == (T0 + 60, 0.3, "stop_loss")


def test_take_profit_at_limit_price_even_on_gap_up():
    assert ledger.scan_exit([c(T0 + 60, 2.0, 2.5, 1.9, 2.2)], T0, TP, SL, MAXH) == (T0 + 60, TP, "take_profit")
    assert ledger.scan_exit([c(T0 + 60, 1.0, 1.35, 0.95, 1.2)], T0, TP, SL, MAXH) == (T0 + 60, TP, "take_profit")


def test_max_hold_and_skips_already_seen_candles():
    candles = [c(T0, 1, 5, 0.1, 1), c(T0 + 60, 1, 1.1, 0.9, 1), c(MAXH, 1.05, 1.1, 1, 1)]
    assert ledger.scan_exit(candles, T0, TP, SL, MAXH) == (MAXH, 1.05, "max_hold")
    assert ledger.scan_exit(candles[:2], T0, TP, SL, MAXH) is None


def test_is_rug():
    assert ledger.is_rug(100_000, 500)          # below sellable minimum
    assert ledger.is_rug(100_000, None)
    assert ledger.is_rug(100_000, 19_000)       # 81% drop
    assert not ledger.is_rug(100_000, 25_000)


def test_completed_drops_forming_candle():
    now = datetime.fromtimestamp(T0 + 90, tz=timezone.utc)
    assert [x[0] for x in ledger.completed([c(T0, 1, 1, 1, 1), c(T0 + 60, 1, 1, 1, 1)], now)] == [T0]


# --- full database flow -------------------------------------------------------

@pytest.fixture
def db():
    d = DB("sqlite:///:memory:")
    d.init()
    yield d
    d.close()


SNAP = {"pool_address": "POOL", "token_mint": "MINT", "symbol": "TEST", "price_usd": 1.0,
        "liquidity_usd": 100_000}


def _signal(db, strategy="momentum", when=None):
    return ledger.record_signal(db, strategy, SNAP, when or datetime.fromtimestamp(T0, tz=timezone.utc), "pending")


def test_signal_fill_and_stop_loss_flow(db):
    _signal(db)
    candles = [c(T0 + 60, 1.0, 1.0, 0.98, 1.0),       # fill at high = 1.0
               c(T0 + 120, 0.95, 0.96, 0.75, 0.8)]     # hits stop 0.8
    log = []
    ledger.fill_pending(db, NOW, lambda p: candles, log)
    pos = db.one("SELECT * FROM positions")
    assert pos["status"] == "open" and pos["entry_price"] == 1.0
    assert pos["stop_loss_price"] == pytest.approx(0.8)
    ledger.manage_open(db, NOW, lambda p: candles, lambda p: {"liquidity_usd": 100_000, "price_usd": 0.8}, log)
    pos = db.one("SELECT * FROM positions")
    assert pos["status"] == "closed" and pos["exit_reason"] == "stop_loss"
    b = costs.buy(100, 1.0, 100_000)
    s = costs.sell(b["tokens"], 0.8, 100_000)
    assert pos["net_pnl_usd"] == pytest.approx(s["proceeds_usd"] - 100.5)
    assert pos["net_return"] < -0.20   # a -20% stop costs more than 20% after costs


def test_rug_is_counted_and_loses_everything(db):
    _signal(db)
    candles = [c(T0 + 60, 1.0, 1.0, 1.0, 1.0)]
    ledger.fill_pending(db, NOW, lambda p: candles, [])
    ledger.manage_open(db, NOW, lambda p: candles, lambda p: {"liquidity_usd": 300, "price_usd": 0.0001}, [])
    pos = db.one("SELECT * FROM positions")
    assert pos["is_rug"] == 1 and pos["exit_reason"] == "rug"
    assert pos["proceeds_usd"] == 0 and pos["net_pnl_usd"] == pytest.approx(-100.5)
    s = report.summarize(db.all("SELECT * FROM positions WHERE status = 'closed'"))
    assert s["trades"] == 1 and s["rugs"] == 1


def test_pool_vanished_counts_as_rug(db):
    _signal(db)
    ledger.fill_pending(db, NOW, lambda p: [c(T0 + 60, 1, 1, 1, 1)], [])
    db.insert("pools", {"pool_address": "POOL", "token_mint": "MINT", "first_seen_at": iso(NOW), "missing_count": 2})
    ledger.manage_open(db, NOW, lambda p: [], lambda p: {"liquidity_usd": 90_000, "price_usd": 1.0}, [])
    pos = db.one("SELECT * FROM positions")
    assert pos["is_rug"] == 1 and pos["net_pnl_usd"] == pytest.approx(-100.5)


def test_cancelled_when_no_trades(db):
    _signal(db)
    ledger.fill_pending(db, NOW, lambda p: [], [])
    assert db.one("SELECT status FROM signals")["status"] == "cancelled"
    assert db.one("SELECT COUNT(*) AS n FROM positions")["n"] == 0


def test_cooldown_and_open_count(db):
    when = NOW - timedelta(hours=1)
    _signal(db, when=when)
    assert ledger.in_cooldown(db, "momentum", "MINT", NOW)
    assert not ledger.in_cooldown(db, "pullback", "MINT", NOW)        # strategies are independent
    assert not ledger.in_cooldown(db, "momentum", "MINT", NOW + timedelta(hours=25))
    assert ledger.open_count(db, "momentum") == 1


def test_real_quote_worse_than_model_is_charged(db):
    ledger.record_signal(db, "momentum", SNAP, datetime.fromtimestamp(T0, tz=timezone.utc), "pending",
                         details={"quoted_sell_cost_pct": 12.0, "model_sell_cost_pct": 2.7})
    candles = [c(T0 + 60, 1.0, 1.0, 1.0, 1.0)]
    ledger.fill_pending(db, NOW, lambda p: candles, [])
    pos = db.one("SELECT * FROM positions")
    model = costs.one_way_cost_pct(100, 100_000)
    assert pos["cost_adj_pct"] == pytest.approx(12.0 - model)
    assert pos["tokens"] < costs.buy(100, 1.0, 100_000)["tokens"]


def test_migration_adds_column_to_old_database(tmp_path):
    import sqlite3
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE positions (id INTEGER PRIMARY KEY, strategy TEXT NOT NULL, pool_address TEXT NOT NULL, "
                "token_mint TEXT NOT NULL, size_usd REAL NOT NULL, status TEXT NOT NULL)")
    con.commit(); con.close()
    d = DB(f"sqlite:///{path}")
    d.init()
    cols = [r[1] for r in d.conn.execute("PRAGMA table_info(positions)").fetchall()]
    assert "cost_adj_pct" in cols
    d.close()


def test_rug_still_gets_stop_loss_chance_but_counts_as_rug(db):
    _signal(db)
    candles = [c(T0 + 60, 1.0, 1.0, 1.0, 1.0),
               c(T0 + 120, 0.9, 0.9, 0.7, 0.75),     # stop 0.8 hit on the way down
               c(T0 + 180, 0.1, 0.1, 0.02, 0.03)]    # the rug
    ledger.fill_pending(db, NOW, lambda p: candles, [])
    ledger.manage_open(db, NOW, lambda p: candles, lambda p: {"liquidity_usd": 50_000, "price_usd": 0.03}, [])
    pos = db.one("SELECT * FROM positions")
    assert pos["exit_reason"] == "stop_loss" and pos["exit_price"] == pytest.approx(0.8)
    assert pos["is_rug"] == 1


def test_rug_that_gaps_straight_down_exits_at_gap(db):
    _signal(db)
    candles = [c(T0 + 60, 1.0, 1.0, 1.0, 1.0), c(T0 + 120, 0.05, 0.05, 0.01, 0.02)]
    ledger.fill_pending(db, NOW, lambda p: candles, [])
    ledger.manage_open(db, NOW, lambda p: candles, lambda p: {"liquidity_usd": 50_000, "price_usd": 0.02}, [])
    pos = db.one("SELECT * FROM positions")
    assert pos["exit_price"] == pytest.approx(0.05) and pos["is_rug"] == 1
