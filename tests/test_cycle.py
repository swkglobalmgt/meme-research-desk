"""End-to-end run with every outside service faked. Proves the pipeline wires up."""
from datetime import datetime, timedelta, timezone

from desk import collector, run
from desk.db import DB
from desk.sources import geckoterminal as gt
from desk.sources import onchain


def pool(addr, mint, **kw):
    p = {"pool_address": addr, "token_mint": mint, "name": f"{mint} / SOL", "symbol": mint, "dex": "pumpswap",
         "pool_created_at": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
         "price_usd": 0.01, "liquidity_usd": 120_000, "fdv_usd": 1e6, "vol_m5": 3000, "vol_h1": 80_000,
         "vol_h6": 300_000, "vol_h24": 900_000, "chg_m5": 2.0, "chg_h1": 35.0, "chg_h6": 60.0,
         "chg_h24": 150.0, "buys_h1": 400, "sells_h1": 250, "buyers_h1": 200, "sellers_h1": 120,
         "txns_h24": 5000}
    p.update(kw)
    return p


def test_full_cycle(monkeypatch, tmp_path):
    safe = pool("P_SAFE", "SAFE")
    scam = pool("P_SCAM", "SCAM")
    young = pool("P_YOUNG", "YOUNG", pool_created_at=datetime.now(timezone.utc).isoformat())
    monkeypatch.setattr(gt, "new_pools", lambda page: [safe, scam, young] if page == 1 else [])
    monkeypatch.setattr(gt, "trending_pools", lambda page: [])
    monkeypatch.setattr(gt, "trending_pools_5m", lambda page: [])
    from desk.sources import dexscreener
    monkeypatch.setattr(dexscreener, "solana_tokens", lambda path: [])
    monkeypatch.setattr(gt, "token_pools", lambda mint: [])
    monkeypatch.setattr(gt, "pools_multi", lambda addrs: [])
    monkeypatch.setattr(gt, "minute_candles", lambda p: [])

    def mint_info(m):
        return {"program": "Tokenkeg", "mint_authority": "EVIL" if m == "SCAM" else None,
                "freeze_authority": None, "decimals": 6, "supply": "1", "extensions": {}}

    report = {"markets": [{"pubkey": "x", "lp": {"lpLockedPct": 100, "baseUSD": 1, "quoteUSD": 1}}],
              "topHolders": [{"address": f"h{i}", "owner": f"o{i}", "pct": 1.5} for i in range(15)]}
    monkeypatch.setattr(onchain, "mint_info", mint_info)
    monkeypatch.setattr(onchain, "rugcheck_report", lambda m: report)
    monkeypatch.setattr(onchain, "jupiter_sell_quote", lambda m, d, a: {"out_usd": 95.0})

    db = DB(f"sqlite:///{tmp_path}/t.db")
    db.init()
    log = []
    stats = run.cycle(db, log)
    db.commit()

    assert stats["collect"]["new_pools"] == 3
    pend = {r["token_mint"] for r in db.all("SELECT token_mint FROM signals WHERE status = 'pending'")}
    rej = {r["token_mint"] for r in db.all("SELECT token_mint FROM signals WHERE status = 'rejected_safety'")}
    assert pend == {"SAFE"}
    assert {"SCAM", "YOUNG"} <= rej
    # One safety lookup per token, reused across strategies.
    assert db.one("SELECT COUNT(*) AS n FROM safety_checks")["n"] == 3

    md = run.write_reports(db, tmp_path / "out")
    assert "momentum" in md and (tmp_path / "out" / "dashboard.html").exists()
    db.close()
