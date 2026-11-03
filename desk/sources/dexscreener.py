"""DexScreener public API: lists of tokens people are paying attention to right now."""
from __future__ import annotations

from urllib.parse import urlparse

from .. import config
from . import http

http.set_rate(urlparse(config.DEXSCREENER_BASE).netloc, 1.1)  # 60/min limit on these endpoints

LISTS = {
    "dex_profiles": "/token-profiles/latest/v1",   # newest tokens that set up a profile
    "dex_boosts_latest": "/token-boosts/latest/v1",  # tokens that just paid for promotion
    "dex_boosts_top": "/token-boosts/top/v1",      # tokens with the most active promotion
}


def solana_tokens(path: str) -> list[str]:
    data = http.get_json(f"{config.DEXSCREENER_BASE}{path}")
    if isinstance(data, dict):  # some endpoints wrap the list
        data = data.get("data") or data.get("tokens") or []
    out = []
    for item in data or []:
        if isinstance(item, dict) and item.get("chainId") == config.CHAIN and item.get("tokenAddress"):
            out.append(item["tokenAddress"])
    return list(dict.fromkeys(out))
