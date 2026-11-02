"""Every tunable number lives here, so the rules are fixed and visible.

Changing a number here changes the experiment. If you change a strategy's
rules after trades exist, give it a new name (e.g. "momentum_v2") so old and
new results are never mixed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# HARD SAFETY SWITCH. This project is paper-only. There is no code path that
# signs or sends a transaction, and no wallet or key is ever loaded.
# --------------------------------------------------------------------------
PAPER_ONLY = True

CHAIN = "solana"

# ---- Data sources (all public / free) ------------------------------------
GECKO_BASE = "https://api.geckoterminal.com/api/v2"
DEXSCREENER_BASE = "https://api.dexscreener.com"
RUGCHECK_BASE = "https://api.rugcheck.xyz/v1"
JUPITER_QUOTE = "https://lite-api.jup.ag/swap/v1/quote"
SOLANA_RPC_URL = os.environ.get("SOLANA_RPC_URL") or "https://api.mainnet-beta.solana.com"
USDC_MINT = "EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr"

GECKO_MIN_INTERVAL_S = 2.2      # free tier is ~30 calls/minute
NEW_POOL_PAGES = 10             # 20 pools per page
TRENDING_PAGES = 3
WATCH_MAX_AGE_HOURS = 72        # stop tracking pools older than this
WATCH_MIN_LIQ_USD = 10_000      # stop tracking pools that fall below this (after 1h)
SAFETY_RECHECK_MINUTES = 120    # cache a safety verdict this long


@dataclass(frozen=True)
class SafetyRules:
    min_liquidity_usd: float = 50_000
    min_age_hours: float = 1.0
    max_top10_pct: float = 30.0           # excluding pool vaults / burn / lockers
    min_lp_locked_pct: float = 90.0       # burned or locked
    min_sells_h1: int = 20                # proof that people can actually sell
    min_sellers_h1: int = 10
    max_sell_price_impact_pct: float = 10.0
    max_transfer_fee_bps: int = 0         # any sell tax fails


SAFETY = SafetyRules()


@dataclass(frozen=True)
class Costs:
    """Conservative cost assumptions applied to every paper trade."""
    swap_fee_pct: float = 0.5             # DEX/LP fee per swap (pools range 0.25-1%)
    base_slippage_pct: float = 2.0        # minimum slippage per swap, on top of pool impact
    fixed_cost_per_swap_usd: float = 0.25 # network + priority fee + tip, per swap
    entry_delay_seconds: int = 60         # we are slower than sniper bots
    fill_window_minutes: int = 15         # no trade activity in this window -> order cancelled
    rug_liquidity_usd: float = 1_000      # below this a sell is treated as impossible (value 0)
    rug_liquidity_drop_pct: float = 80.0  # liquidity down this much from entry = rug


COSTS = Costs()


@dataclass(frozen=True)
class Strategy:
    name: str
    description: str
    position_usd: float = 100.0
    take_profit_pct: float = 30.0
    stop_loss_pct: float = 20.0
    max_hold_minutes: int = 240
    max_open_positions: int = 10
    reentry_cooldown_hours: int = 24
    params: dict = field(default_factory=dict)


STRATEGIES = {
    s.name: s
    for s in [
        Strategy(
            name="momentum",
            description="Safe token already rising: +20% or more over 1h, still up over 5m, more buys than sells.",
            params={"min_chg_h1": 20.0, "min_chg_m5": 0.0, "min_vol_h1": 50_000, "min_buy_sell_ratio": 1.1},
        ),
        Strategy(
            name="volume_breakout",
            description="Last 5 minutes traded 3x+ the hour's average pace and price is up 3%+ in those 5 minutes.",
            params={"vol_mult": 3.0, "min_chg_m5": 3.0, "min_vol_h1": 25_000},
        ),
        Strategy(
            name="pullback",
            description="Up 50%+ over 6h, then pulled back 10-25% over the last hour, now bouncing over 5m.",
            params={"min_chg_h6": 50.0, "min_pullback_h1": -25.0, "max_pullback_h1": -10.0, "min_chg_m5": 0.5},
        ),
        Strategy(
            name="founder_screen",
            description=("Founder's DexScreener screen: top 24h gainers with liq >= $25k, 24h txns >= 50, "
                         "24h volume >= $10k (safety filters still require $50k liq). Buys the top-ranked names."),
            params={"min_liq": 25_000, "min_txns_h24": 50, "min_vol_h24": 10_000, "top_n": 5, "min_chg_h24": 0.0},
        ),
    ]
}

# Tokens the founder asked to watch by hand (still must pass every safety filter).
WATCH_TOKENS = [
    "EDM8ynBGuaxXex6Lx78Q4WYDNtH6F6ANPvmi72Mspump",  # from founder's GMGN link, 2026-11-02
]


@dataclass(frozen=True)
class Gate:
    min_weeks: int = 4
    min_trades: int = 100
    min_t_stat: float = 2.0


GATE = Gate()
