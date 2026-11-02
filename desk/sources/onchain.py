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


def jupiter_sell_quote(mint: str, decimals: int, token_amount: float) -> dict | None:
    """Quote selling `token_amount` tokens for USDC. Returns {'out_usd': float} or None if no route."""
    raw = int(token_amount * (10 ** decimals))
    if raw <= 0:
        return None
    try:
        q = http.get_json(config.JUPITER_QUOTE, params={
            "inputMint": mint, "outputMint": config.USDC_MINT, "amount": raw, "slippageBps": 500,
        })
    except http.FetchError as e:
        if "400" in str(e):  # Jupiter answers 400 when no route exists
            return None
        raise
    if not q or "outAmount" not in q:
        return None
    return {"out_usd": int(q["outAmount"]) / 1e6, "route_count": len(q.get("routePlan") or [])}
