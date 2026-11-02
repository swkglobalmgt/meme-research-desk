import math

import pytest

from desk import report
from desk.config import Gate


def test_t_stat():
    assert report.t_stat([0.1]) is None
    r = [0.1, -0.05, 0.2, 0.0]
    mean = sum(r) / 4
    sd = math.sqrt(sum((x - mean) ** 2 for x in r) / 3)
    assert report.t_stat(r) == pytest.approx(mean / (sd / 2))
    assert report.t_stat([0.1, 0.1]) == math.inf


def test_max_drawdown():
    assert report.max_drawdown([]) == 0
    assert report.max_drawdown([10, -5, -10, 20, -30]) == pytest.approx(30)
    assert report.max_drawdown([-10, -10]) == pytest.approx(20)  # from the starting point


def T(pnl, rug=0, reason="stop_loss"):
    return {"net_pnl_usd": pnl, "net_return": pnl / 100, "is_rug": rug, "exit_reason": reason}


def test_summarize_counts_rugs_and_losses():
    s = report.summarize([T(24), T(-22), T(-100.5, rug=1, reason="rug"), T(10, reason="take_profit")])
    assert s["trades"] == 4 and s["rugs"] == 1 and s["big_losses"] == 1
    assert s["win_rate"] == 0.5
    assert s["net_pnl_usd"] == pytest.approx(-88.5)
    assert s["avg_loss_usd"] == pytest.approx((-22 - 100.5) / 2)


def test_gate():
    g = Gate(min_weeks=4, min_trades=100, min_t_stat=2.0)
    good = {"trades": 120, "net_pnl_usd": 500.0, "t_stat": 2.3}
    assert report.gate_verdict(good, 4.5, g) == (True, [])
    ok, fails = report.gate_verdict({**good, "t_stat": 1.9}, 4.5, g)
    assert not ok and "t-stat" in fails[0]
    ok, fails = report.gate_verdict({"trades": 10, "net_pnl_usd": -5, "t_stat": None}, 1, g)
    assert not ok and len(fails) == 4
