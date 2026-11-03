"""Entry point. `python -m desk.run all` does one full research cycle."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import timedelta
from pathlib import Path

from . import collector, config, copytrade, costs, ledger, report, strategies
from .db import connect, iso, utcnow
from .sources import geckoterminal as gt


def _assert_paper() -> None:
    if not config.PAPER_ONLY:
        sys.exit("Refusing to run: PAPER_ONLY is off. Real trading needs written founder approval.")
    if os.environ.get("GITHUB_ACTIONS") and not os.environ.get("DATABASE_URL"):
        sys.exit("DATABASE_URL secret is missing. Add it in GitHub: Settings > Secrets and variables > Actions.")
    for var in ("PRIVATE_KEY", "WALLET_PRIVATE_KEY", "SEED_PHRASE", "SOLANA_PRIVATE_KEY"):
        if os.environ.get(var):
            sys.exit(f"Refusing to run: {var} is set. This project never uses keys.")


def cycle(db, log: list) -> dict:
    now = utcnow()
    stats = {"collect": collector.collect(db, now, log)}
    db.commit()

    candle_cache: dict[str, list] = {}

    def candles(pool):
        if pool not in candle_cache:
            candle_cache[pool] = gt.minute_candles(pool)
        return candle_cache[pool]

    ledger.fill_pending(db, now, candles, log)
    ledger.manage_open(db, now, candles, lambda p: collector.latest_snapshot(db, p), log,
                       leader_exit=lambda pos: copytrade.leader_exit_epoch(db, pos))
    db.commit()

    # Copy-trading: re-screen fomo traders weekly, then look for their new trades.
    try:
        stats["copy_trader"] = copytrade.cycle(db, now, log)
    except Exception as e:  # never let one source break the whole run
        db.rollback()
        stats["copy_trader"] = {"status": f"error: {e}"}
        log.append(f"copy_trader error: {e}")
    db.commit()

    # New signals from this run's snapshots.
    snaps = collector.latest_snapshots(db, now - timedelta(minutes=5))
    sig_stats = {}
    for strat in strategies.all_strategies():
        picked = strategies.select(strat, snaps)
        counts = {"picked": len(picked), "pending": 0, "rejected_safety": 0, "skipped": 0}
        for s in picked:
            if ledger.in_cooldown(db, strat.name, s["token_mint"], now):
                counts["skipped"] += 1
                continue
            if ledger.open_count(db, strat.name) >= strat.max_open_positions:
                counts["skipped"] += 1
                continue
            res = collector.check_safety(db, s, now, strat.position_usd)
            cost_check = {"quoted_sell_cost_pct": res.facts.get("sell_loss_pct"),
                          "model_sell_cost_pct": round(costs.one_way_cost_pct(
                              strat.position_usd, s.get("liquidity_usd")), 3)}
            if res.passed:
                ledger.record_signal(db, strat.name, s, now, "pending", details=cost_check)
                counts["pending"] += 1
                log.append(f"SIGNAL {strat.name} {s.get('symbol')} price {s.get('price_usd')}")
            else:
                ledger.record_signal(db, strat.name, s, now, "rejected_safety", "; ".join(res.reasons)[:500],
                                     details=cost_check)
                counts["rejected_safety"] += 1
        sig_stats[strat.name] = counts
        db.commit()
    stats["signals"] = sig_stats

    # Hand-picked tokens: always run the safety check so the founder sees the verdict.
    watch = {}
    for mint in config.WATCH_TOKENS:
        snap = next((s for s in snaps if s["token_mint"] == mint), None)
        if snap is None:
            watch[mint] = {"status": "no fresh pool data"}
            continue
        res = collector.check_safety(db, snap, now, 100.0)
        watch[mint] = {"symbol": snap.get("symbol"), "passed": res.passed, "reasons": res.reasons,
                       "liquidity_usd": snap.get("liquidity_usd"), "chg_h24": snap.get("chg_h24")}
    stats["watch_tokens"] = watch
    db.commit()
    return stats


def write_reports(db, out_dir: Path) -> str:
    now = utcnow()
    r = report.build(db, now)
    md = report.markdown(r)
    trades = db.all("SELECT * FROM positions ORDER BY COALESCE(exit_ts, entry_ts) DESC, id DESC")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "REPORT.md").write_text(md)
    (out_dir / "dashboard.html").write_text(report.dashboard_html(r, trades))
    (out_dir / "summary.json").write_text(json.dumps(r, indent=2, default=str))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(md)
    return md


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["all", "report", "init"])
    ap.add_argument("--out", default="reports")
    args = ap.parse_args(argv)
    _assert_paper()
    log: list[str] = []
    with connect() as db:
        if args.command == "init":
            print("database ready")
            return 0
        run_id = db.insert("runs", {"started_at": iso(utcnow()), "kind": args.command})
        db.commit()
        stats, err = {}, None
        try:
            if args.command == "all":
                stats = cycle(db, log)
        except Exception:
            err = traceback.format_exc()
            db.rollback()
        db.update("runs", "id", run_id, {"finished_at": iso(utcnow()), "stats": stats,
                                         "errors": (err or "") + "\n".join(log[-50:])})
        db.commit()
        md = write_reports(db, Path(args.out))
        print(json.dumps(stats, indent=2, default=str))
        print("\n".join(log[-40:]))
        print(md)
        if err:
            print(err, file=sys.stderr)
            return 1
        c = stats.get("collect") or {}
        if c.get("api_errors") and not c.get("snapshots"):
            print("No market data could be collected this run (all sources failed).", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
