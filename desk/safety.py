"""Safety filters. A token must pass EVERY check before any paper entry.

Rule: fail closed. If a fact is missing or a source could not be reached,
the check fails with a reason that says so. We never assume a token is safe.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import SAFETY, SafetyRules

BURN_ADDRESSES = {
    "1nc1nerator11111111111111111111111111111111",
    "11111111111111111111111111111111",
}
POOL_LIKE_TYPES = {"AMM", "LOCKER", "BURN", "PROGRAM", "AMM_POOL"}
BAD_EXTENSIONS = ("transferHook", "permanentDelegate", "nonTransferable")


@dataclass
class SafetyResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)   # why it failed (empty if passed)
    checks: dict[str, bool] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Turning raw source data into plain facts
# ---------------------------------------------------------------------------

def lp_locked_pct_from_rugcheck(report: dict | None, pool_address: str | None) -> float | None:
    if not report:
        return None
    markets = report.get("markets") or []
    if not markets:
        return None
    chosen = None
    for m in markets:
        if pool_address and m.get("pubkey") == pool_address:
            chosen = m
            break
    if chosen is None:  # fall back to the deepest market
        def depth(m):
            lp = m.get("lp") or {}
            return float(lp.get("baseUSD") or 0) + float(lp.get("quoteUSD") or 0)
        chosen = max(markets, key=depth)
    lp = chosen.get("lp") or {}
    pct = lp.get("lpLockedPct")
    return float(pct) if pct is not None else None


def _collect_strings(obj, out: set) -> None:
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_strings(v, out)


def top10_pct_from_rugcheck(report: dict | None) -> float | None:
    """Top-10 holder share in %, excluding liquidity pools, lockers and burn addresses."""
    if not report:
        return None
    holders = report.get("topHolders")
    if holders is None:
        return None
    excluded = set(BURN_ADDRESSES)
    for addr, meta in (report.get("knownAccounts") or {}).items():
        if str((meta or {}).get("type", "")).upper() in POOL_LIKE_TYPES:
            excluded.add(addr)
    for m in report.get("markets") or []:
        _collect_strings(m, excluded)
    real = [h for h in holders
            if h.get("address") not in excluded and h.get("owner") not in excluded]
    real.sort(key=lambda h: float(h.get("pct") or 0), reverse=True)
    return round(sum(float(h.get("pct") or 0) for h in real[:10]), 4)


def transfer_fee_bps(mint: dict | None) -> int | None:
    if not mint:
        return None
    cfg = (mint.get("extensions") or {}).get("transferFeeConfig")
    if not cfg:
        return 0
    fees = [((cfg.get(k) or {}).get("transferFeeBasisPoints")) for k in ("newerTransferFee", "olderTransferFee")]
    fees = [int(f) for f in fees if f is not None]
    return max(fees) if fees else None


def risky_extensions(mint: dict | None) -> list[str] | None:
    if not mint:
        return None
    ext = mint.get("extensions") or {}
    bad = []
    for name in BAD_EXTENSIONS:
        if name in ext:
            state = ext[name] or {}
            # A hook/delegate set to null is harmless; nonTransferable is always bad.
            if name == "nonTransferable" or any(v for v in state.values()):
                bad.append(name)
    return bad


def build_facts(*, snapshot: dict, age_hours: float | None, mint: dict | None,
                mint_error: str | None, rugcheck: dict | None, rugcheck_error: str | None,
                sell_quote: dict | None, sell_quote_error: str | None, position_usd: float) -> dict:
    sell_loss = None
    if sell_quote is not None and position_usd > 0:
        sell_loss = round(100.0 * (1 - sell_quote["out_usd"] / position_usd), 3)
    return {
        "mint_known": mint is not None,
        "mint_error": mint_error,
        "mint_authority": mint.get("mint_authority") if mint else None,
        "freeze_authority": mint.get("freeze_authority") if mint else None,
        "transfer_fee_bps": transfer_fee_bps(mint),
        "risky_extensions": risky_extensions(mint),
        "rugcheck_error": rugcheck_error,
        "lp_locked_pct": lp_locked_pct_from_rugcheck(rugcheck, snapshot.get("pool_address")),
        "top10_pct": top10_pct_from_rugcheck(rugcheck),
        "rugged_flag": bool((rugcheck or {}).get("rugged")),
        "liquidity_usd": snapshot.get("liquidity_usd"),
        "age_hours": age_hours,
        "sells_h1": snapshot.get("sells_h1"),
        "sellers_h1": snapshot.get("sellers_h1"),
        "sell_quote_error": sell_quote_error,
        "sell_quote_found": sell_quote is not None,
        "sell_loss_pct": sell_loss,
    }


# ---------------------------------------------------------------------------
# The filters themselves (pure functions, fully tested)
# ---------------------------------------------------------------------------

def evaluate(f: dict, rules: SafetyRules = SAFETY) -> SafetyResult:
    r = SafetyResult(passed=True)

    def check(name: str, ok: bool, why: str) -> None:
        r.checks[name] = ok
        if not ok:
            r.passed = False
            r.reasons.append(why)

    # 1-2. Authorities: the creator must not be able to print tokens or freeze wallets.
    if not f.get("mint_known"):
        msg = f"mint account unreadable ({f.get('mint_error') or 'not found'})"
        check("mint_authority_revoked", False, msg)
        check("freeze_authority_revoked", False, msg)
    else:
        check("mint_authority_revoked", f.get("mint_authority") is None, "mint authority NOT revoked")
        check("freeze_authority_revoked", f.get("freeze_authority") is None, "freeze authority NOT revoked")

    # 3. Liquidity burned or locked.
    lp = f.get("lp_locked_pct")
    if lp is None:
        check("lp_locked", False, f"LP lock unknown ({f.get('rugcheck_error') or 'no market data'})")
    else:
        check("lp_locked", lp >= rules.min_lp_locked_pct, f"LP only {lp:.1f}% burned/locked")

    # 4. Holder concentration.
    t10 = f.get("top10_pct")
    if t10 is None:
        check("top10_holders", False, f"holder data unknown ({f.get('rugcheck_error') or 'missing'})")
    else:
        check("top10_holders", t10 < rules.max_top10_pct, f"top-10 holders own {t10:.1f}%")

    # 5. Minimum liquidity.
    liq = f.get("liquidity_usd")
    check("min_liquidity", liq is not None and liq >= rules.min_liquidity_usd,
          f"liquidity ${liq:,.0f} below minimum" if liq is not None else "liquidity unknown")

    # 6. Minimum age.
    age = f.get("age_hours")
    check("min_age", age is not None and age >= rules.min_age_hours,
          f"only {age:.2f}h old" if age is not None else "age unknown")

    # 7. Honeypot / sell tax: Token-2022 fee or hostile extensions.
    fee = f.get("transfer_fee_bps")
    bad_ext = f.get("risky_extensions")
    if fee is None or bad_ext is None:
        check("no_sell_tax", False, "token program data unknown")
    else:
        check("no_sell_tax", fee <= rules.max_transfer_fee_bps and not bad_ext,
              f"sell tax {fee} bps" if fee > rules.max_transfer_fee_bps else f"risky token extensions: {bad_ext}")

    # 8. Real people are selling successfully.
    sells, sellers = f.get("sells_h1"), f.get("sellers_h1")
    check("sells_observed",
          sells is not None and sellers is not None
          and sells >= rules.min_sells_h1 and sellers >= rules.min_sellers_h1,
          f"too few sells in last hour ({sells} sells / {sellers} sellers)")

    # 9. A sell route exists at our size with acceptable loss.
    if f.get("sell_quote_error"):
        check("sell_route", False, f"sell quote unavailable ({f['sell_quote_error']})")
    elif not f.get("sell_quote_found"):
        check("sell_route", False, "no sell route found (possible honeypot)")
    else:
        loss = f.get("sell_loss_pct")
        check("sell_route", loss is not None and loss <= rules.max_sell_price_impact_pct,
              f"selling our size loses {loss:.1f}%")

    # 10. Not already flagged as rugged.
    check("not_rugged", not f.get("rugged_flag"), "flagged as rugged by RugCheck")
    return r
