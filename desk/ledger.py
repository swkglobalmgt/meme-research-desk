"""Paper ledger: turns signals into simulated fills and exits.

Realism rules:
  * We see a signal at time T. We cannot buy until T + 60s. We fill at the
    HIGH of the first 1-minute candle starting at or after T + 60s (worst
    price that minute), plus slippage and fees.
  * Exits are checked against every 1-minute candle after entry, as if a bot
    watched continuously. If a candle could have hit both the stop and the
    take-profit, we assume the stop hit first. If price gaps through the stop,
    we exit at the (worse) gap price.
  * If liquidity collapses the trade is marked as a rug. Below the minimum
    liquidity the tokens are treated as unsellable: value zero.
  * Every filled trade is counted forever, including rugs.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import costs
from .config import COSTS, STRATEGIES, Costs
from .db import DB, iso, parse_ts


# ---------------------------------------------------------------------------
# Pure helpers (tested)
# ---------------------------------------------------------------------------

def find_fill(candles: list[tuple], signal_epoch: int, c: Costs = COSTS):
    """Return (candle_ts, fill_price) or 'cancel' or None (wait for more data).

    candles: oldest-first (ts, open, high, low, close, vol).
    """
    earliest = signal_epoch + c.entry_delay_seconds
    deadline = earliest + c.fill_window_minutes * 60
    for ts, o, h, l, cl, v in candles:
        if ts >= earliest:
            if ts > deadline:
                return "cancel"
            return ts, h
    return None


def scan_exit(candles: list[tuple], after_ts: int, tp: float, sl: float, max_hold_epoch: int,
              leader_exit_epoch: int | None = None):
    """Walk candles after `after_ts`. Return (ts, price, reason) at first exit, or None.

    leader_exit_epoch: for copy trades, when we would follow the leader out. We
    sell at the LOW of that minute (worst case).
    """
    for ts, o, h, l, cl, v in candles:
        if ts <= after_ts:
            continue
        if ts >= max_hold_epoch:
            return ts, o, "max_hold"
        if leader_exit_epoch is not None and ts >= leader_exit_epoch:
            return ts, l, "leader_sold"
        if o <= sl:
            return ts, o, "stop_loss"          # gapped through the stop
        if l <= sl:
            return ts, sl, "stop_loss"         # stop checked before take-profit
        if o >= tp:
            return ts, tp, "take_profit"       # limit order fills at TP, no gap bonus
        if h >= tp:
            return ts, tp, "take_profit"
    return None


def completed(candles: list[tuple], now: datetime) -> list[tuple]:
    """Drop the still-forming current minute so we never read a candle twice."""
    cutoff = now.timestamp() - 60
    return [c for c in candles if c[0] <= cutoff]


def is_rug(entry_liq: float | None, now_liq: float | None, c: Costs = COSTS) -> bool:
    if now_liq is None or now_liq < c.rug_liquidity_usd:
        return True
    if entry_liq and entry_liq > 0:
        return (1 - now_liq / entry_liq) * 100 >= c.rug_liquidity_drop_pct
    return False


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------

def open_count(db: DB, strategy: str) -> int:
    row = db.one("SELECT COUNT(*) AS n FROM signals WHERE strategy = ? AND status = 'pending'", [strategy])
    row2 = db.one("SELECT COUNT(*) AS n FROM positions WHERE strategy = ? AND status = 'open'", [strategy])
    return int(row["n"]) + int(row2["n"])


def in_cooldown(db: DB, strategy: str, token: str, now: datetime) -> bool:
    hours = STRATEGIES[strategy].reentry_cooldown_hours
    since = iso(now - timedelta(hours=hours))
    row = db.one(
        "SELECT id FROM signals WHERE strategy = ? AND token_mint = ? AND ts >= ? "
        "AND status IN ('pending', 'filled')", [strategy, token, since])
    return row is not None


def record_signal(db: DB, strategy: str, snap: dict, now: datetime, status: str,
                  reason: str | None = None, details: dict | None = None) -> int:
    return db.insert("signals", {
        "strategy": strategy, "pool_address": snap["pool_address"], "token_mint": snap["token_mint"],
        "symbol": snap.get("symbol"), "ts": iso(now), "signal_price": snap.get("price_usd"),
        "liquidity_usd": snap.get("liquidity_usd"), "details": details or {},
        "status": status, "status_reason": reason,
    })


def _close(db: DB, pos: dict, exit_dt: datetime, price: float, reason: str,
           liq_now: float | None, rug: bool) -> None:
    s = costs.sell(pos["tokens"], price, liq_now, extra_slippage_pct=pos.get("cost_adj_pct") or 0.0)
    if not s["sellable"]:
        reason = "unsellable" if reason != "rug" else reason
    pnl = costs.trade_pnl(pos["size_usd"], s["proceeds_usd"])
    db.update("positions", "id", pos["id"], {
        "status": "closed", "exit_ts": iso(exit_dt), "exit_price": price, "exit_liquidity": liq_now,
        "exit_slippage_pct": s["slippage_pct"], "exit_reason": reason,
        "is_rug": 1 if (rug or not s["sellable"]) else 0,
        "proceeds_usd": s["proceeds_usd"], "fixed_costs_usd": pnl["fixed_costs_usd"],
        "net_pnl_usd": pnl["net_pnl_usd"], "net_return": pnl["net_return"],
    })


def fill_pending(db: DB, now: datetime, get_candles, log: list) -> None:
    """Turn pending signals into positions using real minute candles."""
    for sig in db.all("SELECT * FROM signals WHERE status = 'pending' ORDER BY id"):
        strat = STRATEGIES[sig["strategy"]]
        sig_epoch = int(parse_ts(sig["ts"]).timestamp())
        try:
            candles = completed(get_candles(sig["pool_address"]), now)
        except Exception as e:  # try again next run
            log.append(f"candles failed for signal {sig['id']}: {e}")
            continue
        res = find_fill(candles, sig_epoch)
        if res is None:
            if now.timestamp() > sig_epoch + COSTS.entry_delay_seconds + COSTS.fill_window_minutes * 60 + 600:
                db.update("signals", "id", sig["id"], {"status": "cancelled", "status_reason": "no trades after signal"})
            continue
        if res == "cancel":
            db.update("signals", "id", sig["id"], {"status": "cancelled", "status_reason": "no trades in fill window"})
            continue
        fill_ts, market_price = res
        d = sig.get("details")
        d = json.loads(d) if isinstance(d, str) else (d or {})
        extra = costs.quote_extra_pct(d.get("quoted_sell_cost_pct"), strat.position_usd, sig["liquidity_usd"])
        b = costs.buy(strat.position_usd, market_price, sig["liquidity_usd"], extra_slippage_pct=extra)
        entry_dt = datetime.fromtimestamp(fill_ts, tz=timezone.utc)
        db.insert("positions", {
            "strategy": strat.name, "signal_id": sig["id"], "pool_address": sig["pool_address"],
            "token_mint": sig["token_mint"], "symbol": sig["symbol"], "size_usd": strat.position_usd,
            "signal_ts": sig["ts"], "signal_price": sig["signal_price"], "entry_ts": iso(entry_dt),
            "entry_price": market_price, "entry_liquidity": sig["liquidity_usd"],
            "entry_slippage_pct": b["slippage_pct"], "tokens": b["tokens"], "status": "open",
            "take_profit_price": market_price * (1 + strat.take_profit_pct / 100),
            "stop_loss_price": market_price * (1 - strat.stop_loss_pct / 100),
            "max_hold_until": iso(entry_dt + timedelta(minutes=strat.max_hold_minutes)),
            "last_candle_ts": fill_ts, "leader": sig.get("leader"), "cost_adj_pct": extra,
        })
        db.update("signals", "id", sig["id"], {"status": "filled"})
        log.append(f"FILLED {strat.name} {sig['symbol']} @ {market_price:.10g}")


def manage_open(db: DB, now: datetime, get_candles, latest_snapshot, log: list,
                leader_exit=lambda pos: None) -> None:
    """Check every open position for rug, stop, take-profit or max hold."""
    for pos in db.all("SELECT * FROM positions WHERE status = 'open' ORDER BY id"):
        snap = latest_snapshot(pos["pool_address"])
        liq_now = snap.get("liquidity_usd") if snap else None
        pool = db.one("SELECT missing_count FROM pools WHERE pool_address = ?", [pos["pool_address"]])
        missing = (pool or {}).get("missing_count") or 0

        if is_rug(pos["entry_liquidity"], liq_now) or missing >= 2:
            price = (snap or {}).get("price_usd") or 0.0
            _close(db, pos, now, price, "rug", liq_now if missing < 2 else 0.0, rug=True)
            log.append(f"RUG {pos['strategy']} {pos['symbol']} liquidity {liq_now}")
            continue
        try:
            candles = completed(get_candles(pos["pool_address"]), now)
        except Exception as e:
            log.append(f"candles failed for position {pos['id']}: {e}")
            continue
        max_hold_epoch = int(parse_ts(pos["max_hold_until"]).timestamp())
        hit = scan_exit(candles, int(pos["last_candle_ts"] or 0), pos["take_profit_price"],
                        pos["stop_loss_price"], max_hold_epoch, leader_exit(pos))
        if hit:
            ts, price, reason = hit
            _close(db, pos, datetime.fromtimestamp(ts, tz=timezone.utc), price, reason, liq_now, rug=False)
            log.append(f"EXIT {reason} {pos['strategy']} {pos['symbol']}")
            continue
        if now.timestamp() >= max_hold_epoch:
            price = (snap or {}).get("price_usd") or (candles[-1][4] if candles else 0.0)
            _close(db, pos, now, price, "max_hold", liq_now, rug=False)
            log.append(f"EXIT max_hold (no candles) {pos['strategy']} {pos['symbol']}")
            continue
        if candles:
            db.update("positions", "id", pos["id"], {"last_candle_ts": candles[-1][0]})
