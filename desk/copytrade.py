"""Paper copy-trading of fomo traders chosen for consistent REALIZED profit.

Honesty rules built in:
  * Leaders are picked from their PAST results, but only their trades AFTER the
    day we picked them count. No back-filling a winner's history.
  * We copy 60s+ after their buy, with the same costs and safety filters as
    every other strategy.
  * If a token passed the permanent safety checks but has already rugged by the
    time we notice the leader's buy, we still count the trade (and the rug).
    Otherwise copy-trading would look better than it is.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from . import collector, config, ledger
from .config import COPY, QUOTE_MINTS, USDC_MINT, CopyRules
from .db import DB, iso, parse_ts
from .sources import dune
from .sources import geckoterminal as gt
from .sources import http

STRATEGY = "copy_trader"
STATIC_CHECKS = ("mint_authority_revoked", "freeze_authority_revoked", "no_sell_tax")
STALE_HOURS = 12


# ---------------------------------------------------------------------------
# Pure logic (tested)
# ---------------------------------------------------------------------------

def _num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def screen_leaders(rows: list[dict], r: CopyRules = COPY) -> tuple[list[dict], dict[str, str]]:
    """Return (selected rows best-first, {wallet: reason rejected})."""
    picked, rejected = [], {}
    for row in rows:
        w = row.get("wallet")
        if not w:
            continue
        why = None
        if _num(row.get("closed_positions")) < r.min_closed_positions:
            why = "too few closed positions"
        elif _num(row.get("realized_pnl_usd")) <= 0:
            why = "not profitable (realized)"
        elif _num(row.get("positive_weeks")) < r.min_positive_weeks:
            why = "not profitable in enough weeks"
        elif _num(row.get("best_trade_share"), 1.0) > r.max_best_trade_share:
            why = "profit mostly from one coin"
        elif _num(row.get("win_rate")) < r.min_win_rate:
            why = "win rate too low"
        elif r.require_positive_7d and _num(row.get("pnl_7d")) <= 0:
            why = "losing over the last 7 days"
        elif not (r.min_median_position_usd <= _num(row.get("median_position_usd")) <= r.max_median_position_usd):
            why = "position size not copyable"
        if why:
            rejected[w] = why
        else:
            picked.append(row)
    # Rank by profit per dollar risked, not raw profit, so whales don't dominate.
    picked.sort(key=lambda x: _num(x.get("realized_pnl_usd")) / max(_num(x.get("total_cost_usd")), 1.0),
                reverse=True)
    for row in picked[r.max_leaders:]:
        rejected[row["wallet"]] = "ranked below the cut"
    return picked[: r.max_leaders], rejected


def parse_swap(tx: dict | None, wallet: str) -> dict | None:
    """Turn a jsonParsed Solana transaction into {side, mint, token_delta, quote_delta, block_time}.

    A swap = the wallet's balance of one non-quote token goes up (buy) or down
    (sell) while its USDC/SOL moves the opposite way. Anything else is ignored.
    """
    if not tx or not tx.get("meta") or tx["meta"].get("err") is not None:
        return None
    meta = tx["meta"]
    deltas: dict[str, float] = {}
    for key, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(key) or []:
            if b.get("owner") != wallet:
                continue
            ui = b.get("uiTokenAmount") or {}
            amt = _num(ui.get("uiAmountString", ui.get("uiAmount")))
            deltas[b["mint"]] = deltas.get(b["mint"], 0.0) + sign * amt
    tokens = {m: d for m, d in deltas.items() if m not in QUOTE_MINTS and abs(d) > 0}
    if not tokens:
        return None
    mint, tdelta = max(tokens.items(), key=lambda kv: abs(kv[1]))
    quote = deltas.get(USDC_MINT, 0.0)
    # Native SOL change for the wallet (fees are tiny; require a real move).
    keys = ((tx.get("transaction") or {}).get("message") or {}).get("accountKeys") or []
    sol = 0.0
    for i, k in enumerate(keys):
        pk = k.get("pubkey") if isinstance(k, dict) else k
        if pk == wallet and i < len(meta.get("preBalances") or []):
            sol = (meta["postBalances"][i] - meta["preBalances"][i]) / 1e9
    paid = quote < 0 or sol < -0.001 or deltas.get("So11111111111111111111111111111111111111112", 0) < 0
    got = quote > 0 or sol > 0.001 or deltas.get("So11111111111111111111111111111111111111112", 0) > 0
    if tdelta > 0 and paid:
        side = "buy"
    elif tdelta < 0 and got:
        side = "sell"
    else:
        return None
    bt = tx.get("blockTime")
    return {"side": side, "mint": mint, "token_delta": tdelta, "quote_delta": quote,
            "block_time": datetime.fromtimestamp(bt, tz=timezone.utc) if bt else None}


def leader_exit_epoch(db: DB, pos: dict) -> int | None:
    """Time the leader sold this token after our entry (we copy 60s later)."""
    if not pos.get("leader"):
        return None
    row = db.one("SELECT MIN(block_time) AS t FROM leader_trades WHERE wallet = ? AND mint = ? "
                 "AND side = 'sell' AND block_time > ?", [pos["leader"], pos["token_mint"], pos["signal_ts"]])
    if not row or not row["t"]:
        return None
    return int(parse_ts(row["t"]).timestamp()) + config.COSTS.entry_delay_seconds


# ---------------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------------

def _rpc(method: str, params: list):
    resp = http.post_json(config.SOLANA_RPC_URL, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if resp and resp.get("error"):
        raise http.FetchError(str(resp["error"])[:200])
    return (resp or {}).get("result")


def recent_signatures(wallet: str, until: str | None, limit: int) -> list[dict]:
    opts = {"limit": limit}
    if until:
        opts["until"] = until
    return _rpc("getSignaturesForAddress", [wallet, opts]) or []


def get_tx(sig: str) -> dict | None:
    return _rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])


# ---------------------------------------------------------------------------
# Steps run each cycle
# ---------------------------------------------------------------------------

def refresh_leaders(db: DB, now: datetime, log: list, run_query=None) -> dict:
    """Weekly: re-screen fomo traders on Dune and update who we follow."""
    if run_query is None:
        if not os.environ.get("DUNE_API_KEY"):
            return {"status": "skipped: no DUNE_API_KEY"}
        run_query = lambda: dune.run_sql(dune.render(
            "fomo_leaders.sql", days=COPY.lookback_days, min_closed=COPY.min_closed_positions))
    last = db.one("SELECT MAX(ts) AS t FROM leader_screens WHERE error IS NULL")
    if last and last["t"] and parse_ts(last["t"]) > now - timedelta(days=COPY.refresh_days):
        return {"status": "fresh"}
    try:
        rows = run_query()
    except Exception as e:
        db.insert("leader_screens", {"ts": iso(now), "error": str(e)[:500]})
        log.append(f"leader screen failed: {e}")
        return {"status": f"error: {e}"}
    picked, rejected = screen_leaders(rows)
    keep = {r["wallet"] for r in picked}
    for row in picked:
        w = row["wallet"]
        if db.one("SELECT wallet FROM leaders WHERE wallet = ?", [w]):
            db.update("leaders", "wallet", w, {"active": 1, "stats": row, "deactivated_at": None})
        else:
            # Start following from NOW: remember their newest transaction, copy nothing older.
            try:
                sigs = recent_signatures(w, None, 1)
            except Exception as e:
                log.append(f"could not anchor leader {w[:6]}: {e}")
                continue
            db.insert("leaders", {"wallet": w, "source": "dune_fomo", "selected_at": iso(now), "active": 1,
                                  "stats": row, "last_sig": sigs[0]["signature"] if sigs else None})
    for r in db.all("SELECT wallet FROM leaders WHERE active = 1"):
        if r["wallet"] not in keep:
            db.update("leaders", "wallet", r["wallet"], {"active": 0, "deactivated_at": iso(now)})
    db.insert("leader_screens", {"ts": iso(now), "candidates": len(rows), "selected": len(picked),
                                 "rows": {"top": rows[:50], "rejected_counts": _count(rejected.values())}})
    log.append(f"leader screen: {len(rows)} profitable fomo wallets, {len(picked)} passed")
    return {"status": "refreshed", "candidates": len(rows), "selected": len(picked)}


def _count(values) -> dict:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


def poll_leaders(db: DB, now: datetime, log: list) -> list[dict]:
    """Record new trades by every leader (active ones, and inactive ones we still hold)."""
    held = {r["leader"] for r in db.all("SELECT DISTINCT leader FROM positions WHERE status = 'open' "
                                        "AND leader IS NOT NULL")}
    leaders = [r for r in db.all("SELECT * FROM leaders") if r["active"] or r["wallet"] in held]
    new_buys = []
    for L in leaders:
        try:
            sigs = recent_signatures(L["wallet"], L["last_sig"], COPY.max_new_txs_per_leader)
        except Exception as e:
            log.append(f"leader {L['wallet'][:6]} poll failed: {e}")
            continue
        if not sigs:
            db.update("leaders", "wallet", L["wallet"], {"last_checked": iso(now)})
            continue
        for s in reversed(sigs):  # oldest first
            if s.get("err") is not None:
                continue
            if db.one("SELECT sig FROM leader_trades WHERE sig = ?", [s["signature"]]):
                continue
            try:
                sw = parse_swap(get_tx(s["signature"]), L["wallet"])
            except Exception as e:
                log.append(f"tx fetch failed {s['signature'][:8]}: {e}")
                continue
            if not sw or not sw["block_time"]:
                continue
            db.insert("leader_trades", {"sig": s["signature"], "wallet": L["wallet"], "block_time": iso(sw["block_time"]),
                                        "mint": sw["mint"], "side": sw["side"], "quote_delta": sw["quote_delta"],
                                        "token_delta": sw["token_delta"], "seen_at": iso(now)})
            if sw["side"] == "buy" and L["active"]:
                new_buys.append({"wallet": L["wallet"], "mint": sw["mint"], "time": sw["block_time"],
                                 "sig": s["signature"]})
        db.update("leaders", "wallet", L["wallet"], {"last_sig": sigs[0]["signature"], "last_checked": iso(now)})
    return new_buys


def make_signals(db: DB, now: datetime, buys: list[dict], log: list) -> dict:
    strat = config.STRATEGIES[STRATEGY]
    counts = {"leader_buys": len(buys), "pending": 0, "rejected_safety": 0, "counted_rug": 0,
              "skipped": 0, "no_data": 0, "stale": 0}
    for b in buys:
        if now - b["time"] > timedelta(hours=STALE_HOURS):
            counts["stale"] += 1
            continue
        if ledger.in_cooldown(db, STRATEGY, b["mint"], now) or \
           ledger.open_count(db, STRATEGY) >= strat.max_open_positions or \
           _leader_open(db, b["wallet"]) >= COPY.max_open_per_leader:
            counts["skipped"] += 1
            continue
        try:
            pools = gt.token_pools(b["mint"])
        except Exception as e:
            log.append(f"pool lookup failed {b['mint'][:6]}: {e}")
            pools = []
        if not pools:
            counts["no_data"] += 1
            db.insert("signals", {"strategy": STRATEGY, "pool_address": "", "token_mint": b["mint"],
                                  "ts": iso(b["time"]), "status": "no_data", "leader": b["wallet"],
                                  "status_reason": "no pool data found", "details": {"sig": b["sig"]}})
            continue
        best = max(pools, key=lambda p: p.get("liquidity_usd") or 0)
        collector._store(db, best, now, "copy", {"new_pools": 0, "snapshots": 0})
        snap = {**best, "pool_created_at": best.get("pool_created_at")}
        res = collector.check_safety(db, snap, now, strat.position_usd, as_of=b["time"])
        status, reason = "pending", None
        if not res.passed:
            static_ok = all(res.checks.get(c) for c in STATIC_CHECKS)
            rugged_now = ledger.is_rug(None, best.get("liquidity_usd"))
            if static_ok and rugged_now:
                reason = "liquidity already gone when noticed; counted as a trade"
                counts["counted_rug"] += 1
            else:
                status, reason = "rejected_safety", "; ".join(res.reasons)[:500]
                counts["rejected_safety"] += 1
        if status == "pending" and reason is None:
            counts["pending"] += 1
        db.insert("signals", {"strategy": STRATEGY, "pool_address": best["pool_address"], "token_mint": b["mint"],
                              "symbol": best.get("symbol"), "ts": iso(b["time"]),
                              "signal_price": best.get("price_usd"), "liquidity_usd": best.get("liquidity_usd"),
                              "details": {"sig": b["sig"]}, "status": status, "status_reason": reason,
                              "leader": b["wallet"]})
        if status == "pending":
            log.append(f"COPY SIGNAL {best.get('symbol')} after leader {b['wallet'][:6]}")
    return counts


def _leader_open(db: DB, wallet: str) -> int:
    a = db.one("SELECT COUNT(*) AS n FROM positions WHERE leader = ? AND status = 'open'", [wallet])["n"]
    b = db.one("SELECT COUNT(*) AS n FROM signals WHERE leader = ? AND status = 'pending'", [wallet])["n"]
    return int(a) + int(b)


def cycle(db: DB, now: datetime, log: list) -> dict:
    out = {"screen": refresh_leaders(db, now, log)}
    db.commit()
    if not db.one("SELECT wallet FROM leaders LIMIT 1"):
        out["status"] = "no leaders yet"
        return out
    buys = poll_leaders(db, now, log)
    db.commit()
    out["signals"] = make_signals(db, now, buys, log)
    out["following"] = db.one("SELECT COUNT(*) AS n FROM leaders WHERE active = 1")["n"]
    return out
