"""Read-only safety data: Solana RPC (mint account), RugCheck report, Jupiter sell quote.

Nothing here signs or sends anything. All calls are public reads.
"""
from __future__ import annotations

from .. import config
from . import http

TOKEN_2022 = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"


def mint_info(mint: str) -> dict | None:
    """Return {program, mint_authority, freeze_authority, decimals, supply, extensions:{...}} or None."""
    resp = http.post_json(config.SOLANA_RPC_URL, {
        "jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
        "params": [mint, {"encoding": "jsonParsed", "commitment": "confirmed"}],
    })
    value = ((resp or {}).get("result") or {}).get("value")
    if not value:
        return None
    parsed = ((value.get("data") or {}) if isinstance(value.get("data"), dict) else {}).get("parsed") or {}
    info = parsed.get("info") or {}
    if parsed.get("type") != "mint":
        return None
    ext = {}
    for e in info.get("extensions") or []:
        ext[e.get("extension")] = e.get("state") or {}
    return {
        "program": value.get("owner"),
        "mint_authority": info.get("mintAuthority"),
        "freeze_authority": info.get("freezeAuthority"),
        "decimals": info.get("decimals"),
        "supply": info.get("supply"),
        "extensions": ext,
    }


def rugcheck_report(mint: str) -> dict | None:
    return http.get_json(f"{config.RUGCHECK_BASE}/tokens/{mint}/report", timeout=30)


WSOL = "So11111111111111111111111111111111111111112"
_sol_price: dict = {}


class NoRoute(Exception):
    pass


def sol_usd_price() -> float:
    """SOL price in USD from GeckoTerminal (cached per run)."""
    if "p" not in _sol_price:
        data = http.get_json(f"{config.GECKO_BASE}/simple/networks/solana/token_price/{WSOL}")
        prices = (((data or {}).get("data") or {}).get("attributes") or {}).get("token_prices") or {}
        p = float(prices.get(WSOL) or 0)
        if p <= 0:
            raise http.FetchError("no SOL price")
        _sol_price["p"] = p
    return _sol_price["p"]


def jupiter_sell_quote(mint: str, decimals: int, token_amount: float) -> dict | None:
    """Quote selling `token_amount` tokens for SOL, valued in USD.

    Returns {'out_usd': float} or None if Jupiter says no route exists.
    Raises on any other failure, so an outage is never mistaken for a honeypot.
    (Jupiter stopped quoting into USDC in late 2026, hence SOL.)
    """
    raw = int(token_amount * (10 ** decimals))
    if raw <= 0:
        return None
    try:
        q = http.get_json(config.JUPITER_QUOTE, params={
            "inputMint": mint, "outputMint": WSOL, "amount": raw, "slippageBps": 500,
        })
    except http.FetchError as e:
        msg = str(e)
        if "400" in msg and ("NO_ROUTE" in msg.upper() or "COULD_NOT_FIND" in msg.upper()
                             or (mint in msg and "not tradable" in msg)):
            return None
        raise
    if not q or "outAmount" not in q:
        return None
    out_sol = int(q["outAmount"]) / 1e9
    return {"out_usd": out_sol * sol_usd_price(), "route_count": len(q.get("routePlan") or [])}
