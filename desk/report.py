"""Results, decision gate, and the dashboard (Markdown + HTML)."""
from __future__ import annotations

import html
import json
import math
from collections import Counter
from datetime import datetime

from .config import GATE, STRATEGIES, Gate
from .db import DB, parse_ts


# ---------------------------------------------------------------------------
# Pure statistics (tested)
# ---------------------------------------------------------------------------

def t_stat(returns: list[float]) -> float | None:
    """One-sample t statistic of the mean trade return vs zero."""
    n = len(returns)
    if n < 2:
        return None
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / (n - 1)
    if var == 0:
        return math.inf if mean > 0 else (-math.inf if mean < 0 else 0.0)
    return mean / math.sqrt(var / n)


def max_drawdown(pnls: list[float]) -> float:
    """Largest peak-to-trough fall of cumulative $ P&L (returned as a positive number)."""
    peak = cum = worst = 0.0
    for p in pnls:
        cum += p
        peak = max(peak, cum)
        worst = max(worst, peak - cum)
    return worst


def summarize(trades: list[dict]) -> dict:
    """trades: closed positions ordered by exit time."""
    pnls = [t["net_pnl_usd"] for t in trades]
    rets = [t["net_return"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    n = len(trades)
    return {
        "trades": n,
        "win_rate": len(wins) / n if n else None,
        "avg_win_usd": sum(wins) / len(wins) if wins else None,
        "avg_loss_usd": sum(losses) / len(losses) if losses else None,
        "net_pnl_usd": sum(pnls),
        "mean_return": sum(rets) / n if n else None,
        "t_stat": t_stat(rets),
        "max_drawdown_usd": max_drawdown(pnls),
        "rugs": sum(1 for t in trades if t.get("is_rug")),
        "big_losses": sum(1 for r in rets if r <= -0.5),
        "exit_reasons": dict(Counter(t.get("exit_reason") for t in trades)),
    }


def gate_verdict(s: dict, weeks: float, g: Gate = GATE) -> tuple[bool, list[str]]:
    fails = []
    if weeks < g.min_weeks:
        fails.append(f"only {weeks:.1f} of {g.min_weeks} weeks of data")
    if s["trades"] < g.min_trades:
        fails.append(f"only {s['trades']} of {g.min_trades} completed trades")
    if s["net_pnl_usd"] <= 0:
        fails.append(f"net P&L after costs is ${s['net_pnl_usd']:,.2f} (not positive)")
    t = s["t_stat"]
    if t is None or t < g.min_t_stat:
        fails.append(f"t-stat {'n/a' if t is None else f'{t:.2f}'} below {g.min_t_stat}")
    return (not fails), fails


# ---------------------------------------------------------------------------
# Gather from the database
# ---------------------------------------------------------------------------

def build(db: DB, now: datetime) -> dict:
    out = {"generated_at": now.isoformat(timespec="minutes"), "strategies": {}}
    first = db.one("SELECT MIN(entry_ts) AS t FROM positions")
    first_dt = parse_ts(first["t"]) if first and first["t"] else None
    weeks = (now - first_dt).days / 7.0 if first_dt else 0.0
    out["weeks_of_data"] = weeks
    for name in STRATEGIES:
        closed = db.all("SELECT * FROM positions WHERE strategy = ? AND status = 'closed' "
                        "ORDER BY exit_ts, id", [name])
        s = summarize(closed)
        s["open"] = db.one("SELECT COUNT(*) AS n FROM positions WHERE strategy = ? AND status = 'open'",
                           [name])["n"]
        sig = db.all("SELECT status, COUNT(*) AS n FROM signals WHERE strategy = ? GROUP BY status", [name])
        s["signals"] = {r["status"]: r["n"] for r in sig}
        s["gate_pass"], s["gate_fails"] = gate_verdict(s, weeks)
        s["description"] = STRATEGIES[name].description
        out["strategies"][name] = s

    out["funnel"] = {
        "pools_seen": db.one("SELECT COUNT(*) AS n FROM pools")["n"],
        "pools_watching": db.one("SELECT COUNT(*) AS n FROM pools WHERE active = 1")["n"],
        "snapshots": db.one("SELECT COUNT(*) AS n FROM snapshots")["n"],
        "safety_checks": db.one("SELECT COUNT(*) AS n FROM safety_checks")["n"],
        "safety_passed": db.one("SELECT COUNT(*) AS n FROM safety_checks WHERE passed = 1")["n"],
    }
    reasons = Counter()
    for r in db.all("SELECT reasons FROM safety_checks WHERE passed = 0"):
        rs = json.loads(r["reasons"]) if isinstance(r["reasons"], str) else (r["reasons"] or [])
        for x in rs:
            reasons[_bucket(x)] += 1
    out["safety_fail_reasons"] = reasons.most_common(12)
    return out


def _bucket(reason: str) -> str:
    """Group reasons like 'only 0.42h old' into 'only …h old' style buckets."""
    for key in ("mint authority", "freeze authority", "LP", "top-10", "liquidity", "old", "sell tax",
                "extensions", "few sells", "sell quote", "sell route", "selling our size", "rugged",
                "mint account", "holder data", "age", "token program"):
        if key in reason:
            return {"old": "too young (< 1h)", "LP": "LP not burned/locked (or unknown)",
                    "top-10": "top-10 holders >= 30%", "liquidity": "liquidity < $50k (or unknown)",
                    "few sells": "too few sells in last hour", "selling our size": "selling our size loses > 10%",
                    }.get(key, reason.split("(")[0].strip())
    return reason


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _money(x):
    return "–" if x is None else (f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}")


def _pct(x):
    return "–" if x is None else f"{100 * x:.1f}%"


def _t(x):
    return "–" if x is None else ("∞" if x == math.inf else f"{x:.2f}")


ROWS = [("Completed trades", lambda s: str(s["trades"])), ("Open positions", lambda s: str(s["open"])),
        ("Win rate", lambda s: _pct(s["win_rate"])), ("Average win", lambda s: _money(s["avg_win_usd"])),
        ("Average loss", lambda s: _money(s["avg_loss_usd"])),
        ("Net P&L after all costs", lambda s: _money(s["net_pnl_usd"])),
        ("Average return per trade", lambda s: _pct(s["mean_return"])),
        ("t-stat (need ≥ 2)", lambda s: _t(s["t_stat"])),
        ("Worst drawdown", lambda s: _money(-s["max_drawdown_usd"]) if s["max_drawdown_usd"] else "$0.00"),
        ("Rugs / unsellable hit", lambda s: str(s["rugs"])),
        ("Losses worse than -50%", lambda s: str(s["big_losses"])),
        ("Decision gate", lambda s: "PASS" if s["gate_pass"] else "NOT YET / FAIL")]


def markdown(r: dict) -> str:
    names = list(r["strategies"])
    lines = [f"# Meme Coin Research Desk: paper results",
             f"_Generated {r['generated_at']} UTC · {r['weeks_of_data']:.1f} weeks of trade data · PAPER ONLY_", "",
             "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for label, fn in ROWS:
        lines.append(f"| {label} | " + " | ".join(fn(r["strategies"][n]) for n in names) + " |")
    lines += ["", "## Why the gate is not passed yet"]
    for n in names:
        s = r["strategies"][n]
        lines.append(f"- **{n}**: " + ("all conditions met" if s["gate_pass"] else "; ".join(s["gate_fails"])))
    f = r["funnel"]
    lines += ["", "## Data funnel",
              f"- Pools seen: {f['pools_seen']:,} · watching now: {f['pools_watching']:,} · snapshots: {f['snapshots']:,}",
              f"- Safety checks: {f['safety_checks']:,} · passed: {f['safety_passed']:,}", "",
              "Most common safety failures:"]
    lines += [f"- {k}: {v}" for k, v in r["safety_fail_reasons"]] or ["- none yet"]
    lines += ["", "## Signals by strategy"]
    for n in names:
        lines.append(f"- {n}: {r['strategies'][n]['signals'] or 'none yet'}")
    lines += ["", "_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. "
              "Treat a pass below t ≈ 2.5 with extra suspicion._"]
    return "\n".join(lines) + "\n"


def dashboard_html(r: dict, trades: list[dict]) -> str:
    names = list(r["strategies"])
    head = "".join(f"<th>{html.escape(n)}</th>" for n in names)
    body = "".join(
        f"<tr><td>{label}</td>" + "".join(f"<td>{html.escape(fn(r['strategies'][n]))}</td>" for n in names) + "</tr>"
        for label, fn in ROWS)
    trade_rows = "".join(
        f"<tr><td>{html.escape(t['strategy'])}</td><td>{html.escape(str(t.get('symbol') or ''))}</td>"
        f"<td>{html.escape(str(t.get('entry_ts') or ''))}</td><td>{html.escape(str(t.get('exit_ts') or 'open'))}</td>"
        f"<td>{html.escape(str(t.get('exit_reason') or ''))}</td>"
        f"<td class='{'neg' if (t.get('net_pnl_usd') or 0) < 0 else 'pos'}'>{_money(t.get('net_pnl_usd'))}</td></tr>"
        for t in trades[:200])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Meme Research Desk</title>
<style>body{{font:14px system-ui,sans-serif;max-width:1000px;margin:24px auto;padding:0 16px;color:#222}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}td,th{{border-bottom:1px solid #ddd;padding:6px 8px;text-align:right}}
td:first-child,th:first-child{{text-align:left}}.neg{{color:#b00020}}.pos{{color:#0a7a3a}}
.banner{{background:#fff4d6;padding:8px 12px;border-radius:6px}}</style></head><body>
<h1>Meme Coin Research Desk</h1><p class="banner">PAPER TRADING ONLY. No real money. Generated {html.escape(r['generated_at'])} UTC,
{r['weeks_of_data']:.1f} weeks of data.</p>
<table><tr><th></th>{head}</tr>{body}</table>
<h2>Latest trades</h2><table><tr><th>Strategy</th><th>Token</th><th>Entry</th><th>Exit</th><th>Reason</th><th>Net P&amp;L</th></tr>{trade_rows}</table>
</body></html>"""
