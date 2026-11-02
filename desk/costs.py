"""Cost model and P&L math for one paper trade. Pure functions, fully tested.

How a $100 paper buy works:
  1. The pool's swap fee is taken from the $100.
  2. We pay a worse price than we saw: base slippage + the price impact our own
     order has on a small pool (constant-product AMM formula).
  3. Selling repeats both costs on the way out, using liquidity at exit time.
  4. A fixed network/priority fee is paid on every swap, win or lose.
"""
from __future__ import annotations

from .config import COSTS, Costs


def amm_impact_pct(trade_usd: float, liquidity_usd: float | None) -> float:
    """Price impact of a trade on a constant-product pool, in %.

    A pool with $L total liquidity holds about L/2 on each side. Buying $s moves
    the price by roughly s / (L/2 + s). Unknown or zero liquidity = 100% impact.
    """
    if not liquidity_usd or liquidity_usd <= 0:
        return 100.0
    side = liquidity_usd / 2.0
    return 100.0 * trade_usd / (side + trade_usd)


def slippage_pct(trade_usd: float, liquidity_usd: float | None, c: Costs = COSTS) -> float:
    return min(100.0, c.base_slippage_pct + amm_impact_pct(trade_usd, liquidity_usd))


def buy(size_usd: float, price: float, liquidity_usd: float | None, c: Costs = COSTS) -> dict:
    """Simulate a market buy. Returns tokens received and the effective price paid."""
    if price <= 0:
        raise ValueError("price must be positive")
    slip = slippage_pct(size_usd, liquidity_usd, c)
    after_fee = size_usd * (1 - c.swap_fee_pct / 100.0)
    fill_price = price * (1 + slip / 100.0)
    return {"tokens": after_fee / fill_price, "fill_price": fill_price, "slippage_pct": slip}


def sell(tokens: float, price: float, liquidity_usd: float | None, c: Costs = COSTS) -> dict:
    """Simulate a market sell. If liquidity is gone, proceeds are zero (unsellable)."""
    if liquidity_usd is None or liquidity_usd < c.rug_liquidity_usd or price <= 0:
        return {"proceeds_usd": 0.0, "fill_price": 0.0, "slippage_pct": 100.0, "sellable": False}
    gross = tokens * price
    slip = slippage_pct(gross, liquidity_usd, c)
    fill_price = price * (1 - slip / 100.0)
    proceeds = tokens * fill_price * (1 - c.swap_fee_pct / 100.0)
    return {"proceeds_usd": proceeds, "fill_price": fill_price, "slippage_pct": slip, "sellable": True}


def trade_pnl(size_usd: float, proceeds_usd: float, c: Costs = COSTS) -> dict:
    """Net result after everything. Fixed fees are charged on both swaps even if
    the sell fails (a failed transaction still costs fees)."""
    fixed = 2 * c.fixed_cost_per_swap_usd
    net = proceeds_usd - size_usd - fixed
    return {"fixed_costs_usd": fixed, "net_pnl_usd": net, "net_return": net / size_usd}


def round_trip_cost_pct(size_usd: float, liquidity_usd: float, c: Costs = COSTS) -> float:
    """What % you lose if price does not move at all. Useful to explain costs."""
    b = buy(size_usd, 1.0, liquidity_usd, c)
    s = sell(b["tokens"], 1.0, liquidity_usd, c)
    return -100.0 * trade_pnl(size_usd, s["proceeds_usd"], c)["net_return"]
