"""Entry rules for each paper strategy. Each strategy is judged on its own.

Input: the latest snapshot of every candidate pool (already safety-checked
separately). Output: the pools this strategy wants to buy right now.
"""
from __future__ import annotations

from .config import STRATEGIES, Strategy


def _n(x, default=0.0):
    return default if x is None else x


def momentum(s: dict, p: dict) -> bool:
    buys, sells = _n(s.get("buys_h1")), _n(s.get("sells_h1"))
    ratio = buys / sells if sells else (float("inf") if buys else 0)
    return (_n(s.get("chg_h1"), -999) >= p["min_chg_h1"]
            and _n(s.get("chg_m5"), -999) > p["min_chg_m5"]
            and _n(s.get("vol_h1")) >= p["min_vol_h1"]
            and ratio >= p["min_buy_sell_ratio"])


def volume_breakout(s: dict, p: dict) -> bool:
    vol_h1 = _n(s.get("vol_h1"))
    pace_5m = vol_h1 / 12.0
    return (vol_h1 >= p["min_vol_h1"]
            and pace_5m > 0
            and _n(s.get("vol_m5")) >= p["vol_mult"] * pace_5m
            and _n(s.get("chg_m5"), -999) >= p["min_chg_m5"])


def pullback(s: dict, p: dict) -> bool:
    h1 = s.get("chg_h1")
    return (_n(s.get("chg_h6"), -999) >= p["min_chg_h6"]
            and h1 is not None and p["min_pullback_h1"] <= h1 <= p["max_pullback_h1"]
            and _n(s.get("chg_m5"), -999) >= p["min_chg_m5"])


def founder_screen(snaps: list[dict], p: dict) -> list[dict]:
    """Mirror of the founder's DexScreener screen, ranked by 24h price change."""
    ok = [s for s in snaps
          if _n(s.get("liquidity_usd")) >= p["min_liq"]
          and _n(s.get("txns_h24")) >= p["min_txns_h24"]
          and _n(s.get("vol_h24")) >= p["min_vol_h24"]
          and _n(s.get("chg_h24"), -999) > p["min_chg_h24"]]
    ok.sort(key=lambda s: _n(s.get("chg_h24"), -999), reverse=True)
    return ok[: p["top_n"]]


_PER_POOL = {"momentum": momentum, "volume_breakout": volume_breakout, "pullback": pullback}


def select(strategy: Strategy, snaps: list[dict]) -> list[dict]:
    if strategy.name == "founder_screen":
        return founder_screen(snaps, strategy.params)
    fn = _PER_POOL[strategy.name]
    return [s for s in snaps if fn(s, strategy.params)]


def all_strategies() -> list[Strategy]:
    return list(STRATEGIES.values())
