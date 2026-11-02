import pytest

from desk import costs
from desk.config import Costs

C = Costs(swap_fee_pct=0.5, base_slippage_pct=2.0, fixed_cost_per_swap_usd=0.25, rug_liquidity_usd=1000)


def test_amm_impact():
    # $100 into a $50k pool ($25k a side): 100 / 25100
    assert costs.amm_impact_pct(100, 50_000) == pytest.approx(100 * 100 / 25_100)
    assert costs.amm_impact_pct(100, 0) == 100.0
    assert costs.amm_impact_pct(100, None) == 100.0


def test_buy_math():
    b = costs.buy(100, 2.0, 50_000, C)
    slip = 2.0 + 100 * 100 / 25_100
    assert b["slippage_pct"] == pytest.approx(slip)
    assert b["fill_price"] == pytest.approx(2.0 * (1 + slip / 100))
    assert b["tokens"] == pytest.approx(99.5 / b["fill_price"])


def test_sell_unsellable_when_liquidity_gone():
    s = costs.sell(1000, 1.0, 500, C)
    assert s["proceeds_usd"] == 0 and not s["sellable"]
    assert not costs.sell(1000, 1.0, None, C)["sellable"]
    assert not costs.sell(1000, 0.0, 50_000, C)["sellable"]


def test_flat_price_round_trip_loses_money():
    # Price does not move: we must still lose fees + slippage, about 5-6% on a $50k pool.
    lost = costs.round_trip_cost_pct(100, 50_000, C)
    assert 5.0 < lost < 7.0


def test_full_trade_exact():
    b = costs.buy(100, 1.0, 1_000_000, C)
    s = costs.sell(b["tokens"], 1.3, 1_000_000, C)
    pnl = costs.trade_pnl(100, s["proceeds_usd"], C)
    # hand calculation
    slip_in = 2.0 + 100 * 100 / (500_000 + 100)
    tokens = 99.5 / (1.0 * (1 + slip_in / 100))
    gross = tokens * 1.3
    slip_out = 2.0 + 100 * gross / (500_000 + gross)
    proceeds = tokens * 1.3 * (1 - slip_out / 100) * 0.995
    assert s["proceeds_usd"] == pytest.approx(proceeds)
    assert pnl["net_pnl_usd"] == pytest.approx(proceeds - 100 - 0.5)
    assert pnl["net_return"] == pytest.approx((proceeds - 100.5) / 100)
    # +30% price move turns into roughly +24% after costs
    assert 0.22 < pnl["net_return"] < 0.26


def test_rug_loses_everything_plus_fees():
    pnl = costs.trade_pnl(100, 0.0, C)
    assert pnl["net_pnl_usd"] == pytest.approx(-100.5)
    assert pnl["net_return"] == pytest.approx(-1.005)


def test_buy_rejects_bad_price():
    with pytest.raises(ValueError):
        costs.buy(100, 0, 50_000, C)
