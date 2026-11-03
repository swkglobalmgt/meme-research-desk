"""Collects new Solana pools, keeps a watch list fresh, and runs safety checks."""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from . import config, safety
from .db import DB, iso, parse_ts
from .sources import dexscreener as dex
from .sources import geckoterminal as gt
from .sources import onchain
from .sources.http import FetchError

SNAP_COLS = ["price_usd", "liquidity_usd", "fdv_usd", "vol_m5", "vol_h1", "vol_h6", "vol_h24",
             "chg_m5", "chg_h1", "chg_h6", "chg_h24", "buys_h1", "sells_h1", "buyers_h1",
             "sellers_h1", "txns_h24"]


def age_hours(pool_created_at: str | None, now: datetime) -> float | None:
    dt = parse_ts(pool_created_at)
    return None if dt is None else (now - dt).total_seconds() / 3600.0


def _store(db: DB, p: dict, now: datetime, source: str, stats: dict) -> None:
    """Store one pool (used outside the main batch, e.g. copy-trading lookups)."""
    _store_many(db, [(p, source)], now, stats)


def _store_many(db: DB, items: list[tuple[dict, str]], now: datetime, stats: dict) -> None:
    """Store many pools in a few batched queries (Neon round-trips are slow)."""
    if not items:
        return
    t = iso(now)
    addrs = [p["pool_address"] for p, _ in items]
    existing = set()
    for i in range(0, len(addrs), 500):
        chunk = addrs[i:i + 500]
        qs = ",".join("?" for _ in chunk)
        existing |= {r["pool_address"] for r in db.all(
            f"SELECT pool_address FROM pools WHERE pool_address IN ({qs})", chunk)}
    new_rows, upd_rows, snap_rows = [], [], []
    for p, source in items:
        a = p["pool_address"]
        if a not in existing:
            existing.add(a)
            new_rows.append((a, p["token_mint"], p.get("name"), p.get("symbol"), p.get("dex"),
                             p.get("pool_created_at"), t, t, source))
        else:
            upd_rows.append((t, a))
        # Keep storage small: only snapshot pools with real liquidity (or ones we hold).
        if (p.get("liquidity_usd") or 0) >= config.WATCH_MIN_LIQ_USD or source == "held":
            snap_rows.append((a, t, *[p.get(k) for k in SNAP_COLS]))
    db.executemany("INSERT INTO pools (pool_address, token_mint, name, symbol, dex, pool_created_at, "
                   "first_seen_at, last_snapshot_at, source) VALUES (?,?,?,?,?,?,?,?,?)", new_rows)
    db.executemany("UPDATE pools SET last_snapshot_at = ?, missing_count = 0 WHERE pool_address = ?", upd_rows)
    db.executemany(f"INSERT INTO snapshots (pool_address, ts, {', '.join(SNAP_COLS)}) "
                   f"VALUES ({','.join('?' for _ in range(2 + len(SNAP_COLS)))})", snap_rows)
    stats["new_pools"] = stats.get("new_pools", 0) + len(new_rows)
    stats["snapshots"] = stats.get("snapshots", 0) + len(snap_rows)


def collect(db: DB, now: datetime, log: list) -> dict:
    stats = {"new_pools": 0, "snapshots": 0, "api_errors": 0}
    seen: dict[str, dict] = {}

    def grab(fn, *args, label=""):
        try:
            return fn(*args)
        except FetchError as e:
            stats["api_errors"] += 1
            log.append(f"{label} failed: {e}")
            return []

    for page in range(1, config.NEW_POOL_PAGES + 1):
        for p in grab(gt.new_pools, page, label=f"new_pools p{page}"):
            seen[p["pool_address"]] = (p, "new_pools")
    for page in range(1, config.TRENDING_PAGES + 1):
        for p in grab(gt.trending_pools, page, label=f"trending p{page}"):
            seen.setdefault(p["pool_address"], (p, "trending"))
    for page in range(1, config.TRENDING_5M_PAGES + 1):
        for p in grab(gt.trending_pools_5m, page, label=f"trending5m p{page}"):
            seen.setdefault(p["pool_address"], (p, "trending_5m"))

    # DexScreener lists: tokens getting attention (profiles, paid promotion).
    dex_mints: dict[str, str] = {}
    for src, path in dex.LISTS.items():
        for m in grab(dex.solana_tokens, path, label=src):
            dex_mints.setdefault(m, src)
    known = {p["token_mint"] for p, _ in seen.values()}
    todo = [m for m in dex_mints if m not in known][: config.DEX_LIST_MAX_TOKENS]
    stats["dex_tokens"] = len(dex_mints)
    if todo:
        top = grab(gt.top_pool_addresses, todo, label="top pools for dex tokens") or {}
        addr_src = {a: dex_mints[m] for m, a in top.items()}
        for p in grab(gt.pools_multi, list(addr_src), label="pools for dex tokens"):
            seen.setdefault(p["pool_address"], (p, addr_src.get(p["pool_address"], "dexscreener")))

    for mint in config.WATCH_TOKENS:
        pools = grab(gt.token_pools, mint, label=f"watch token {mint[:6]}")
        if pools:  # the deepest pool for a hand-picked token
            best = max(pools, key=lambda x: x.get("liquidity_usd") or 0)
            seen[best["pool_address"]] = (best, "watch_token")

    _store_many(db, list(seen.values()), now, stats)

    # Refresh the watch list: young pools with liquidity, plus anything we hold.
    held = {r["pool_address"] for r in db.all(
        "SELECT pool_address FROM positions WHERE status = 'open' "
        "UNION SELECT pool_address FROM signals WHERE status = 'pending'")}
    watch = [r["pool_address"] for r in db.all("SELECT pool_address FROM pools WHERE active = 1")
             if r["pool_address"] not in seen]
    watch = list(dict.fromkeys(watch + [h for h in held if h not in seen]))
    refreshed = {p["pool_address"]: p for p in grab(gt.pools_multi, watch, label="pools_multi")}
    _store_many(db, [(refreshed[a], "held" if a in held else "watch") for a in watch if a in refreshed], now, stats)
    if refreshed:  # only count as missing if the call itself worked
        db.executemany("UPDATE pools SET missing_count = missing_count + 1 WHERE pool_address = ?",
                       [(a,) for a in watch if a not in refreshed])

    # Retire pools that are too old or too thin (never ones we hold, never hand-picked).
    retired = 0
    to_retire = []
    for r in db.all("SELECT pool_address, pool_created_at, source FROM pools WHERE active = 1"):
        if r["pool_address"] in held or r["source"] == "watch_token":
            continue
        age = age_hours(r["pool_created_at"], now)
        latest = (seen.get(r["pool_address"]) or (refreshed.get(r["pool_address"]), None))[0]
        liq = (latest or {}).get("liquidity_usd")
        if (age is not None and age > config.WATCH_MAX_AGE_HOURS) or \
           (age is not None and age >= 1 and (liq or 0) < config.WATCH_MIN_LIQ_USD):
            to_retire.append((r["pool_address"],))
            retired += 1
    db.executemany("UPDATE pools SET active = 0 WHERE pool_address = ?", to_retire)
    stats["retired"] = retired
    stats["watching"] = db.one("SELECT COUNT(*) AS n FROM pools WHERE active = 1")["n"]

    # Keep the free database small: drop old snapshots of pools we never traded.
    db.execute("DELETE FROM snapshots WHERE ts < ? AND pool_address NOT IN "
               "(SELECT pool_address FROM positions)", [iso(now - timedelta(days=21))])
    return stats


def latest_snapshots(db: DB, since: datetime) -> list[dict]:
    """The newest snapshot per pool taken at/after `since`, joined with pool info."""
    rows = db.all(
        "SELECT s.*, p.token_mint, p.symbol, p.pool_created_at, p.source FROM snapshots s "
        "JOIN pools p ON p.pool_address = s.pool_address WHERE s.ts >= ? ORDER BY s.ts", [iso(since)])
    out: dict[str, dict] = {}
    for r in rows:
        out[r["pool_address"]] = r
    return list(out.values())


def latest_snapshot(db: DB, pool: str) -> dict | None:
    return db.one("SELECT * FROM snapshots WHERE pool_address = ? ORDER BY ts DESC LIMIT 1", [pool])


# ---------------------------------------------------------------------------
# Safety checks (expensive source data cached for SAFETY_RECHECK_MINUTES)
# ---------------------------------------------------------------------------

def check_safety(db: DB, snap: dict, now: datetime, position_usd: float,
                 as_of: datetime | None = None) -> safety.SafetyResult:
    mint = snap["token_mint"]
    since = iso(now - timedelta(minutes=config.SAFETY_RECHECK_MINUTES))
    cached = db.one("SELECT details FROM safety_checks WHERE token_mint = ? AND ts >= ? "
                    "ORDER BY ts DESC LIMIT 1", [mint, since])
    age = age_hours(snap.get("pool_created_at"), as_of or now)
    facts = None
    if cached:
        facts = json.loads(cached["details"]) if isinstance(cached["details"], str) else cached["details"]
        if facts.get("mint_error") or facts.get("rugcheck_error") or facts.get("sell_quote_error") \
                or not facts.get("sell_quote_found"):
            facts = None  # never cache a source outage; try again
    if facts:
        facts.update({"liquidity_usd": snap.get("liquidity_usd"), "age_hours": age,
                      "sells_h1": snap.get("sells_h1"), "sellers_h1": snap.get("sellers_h1")})
        return safety.evaluate(facts)

    m = m_err = rc = rc_err = q = q_err = None
    try:
        m = onchain.mint_info(mint)
    except Exception as e:
        m_err = str(e)[:120]
    try:
        rc = onchain.rugcheck_report(mint)
    except Exception as e:
        rc_err = str(e)[:120]
    price = snap.get("price_usd")
    if m and price:
        try:
            q = onchain.jupiter_sell_quote(mint, int(m["decimals"]), position_usd / price)
        except Exception as e:
            q_err = str(e)[:120]
    elif not price:
        q_err = "no price"
    else:
        q_err = "mint unreadable"

    facts = safety.build_facts(snapshot=snap, age_hours=age, mint=m, mint_error=m_err, rugcheck=rc,
                               rugcheck_error=rc_err, sell_quote=q, sell_quote_error=q_err,
                               position_usd=position_usd)
    result = safety.evaluate(facts)
    db.insert("safety_checks", {"token_mint": mint, "pool_address": snap["pool_address"], "ts": iso(now),
                                "passed": 1 if result.passed else 0, "reasons": result.reasons,
                                "details": facts})
    return result
