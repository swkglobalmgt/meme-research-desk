"""GeckoTerminal public API: pool discovery, snapshots and 1-minute candles."""
from __future__ import annotations

from urllib.parse import urlparse

from .. import config
from . import http

http.set_rate(urlparse(config.GECKO_BASE).netloc, config.GECKO_MIN_INTERVAL_S)
NET = config.CHAIN


def _f(x):
    try:
        return float(x) if x is not None and x != "" else None
    except (TypeError, ValueError):
        return None


def _i(x):
    try:
        return int(x) if x is not None else None
    except (TypeError, ValueError):
        return None


def parse_pool(obj: dict) -> dict | None:
    """Turn one GeckoTerminal pool object into our flat record."""
    try:
        a = obj["attributes"]
        rel = obj.get("relationships", {})
        base_id = rel["base_token"]["data"]["id"]
    except (KeyError, TypeError):
        return None
    mint = base_id.split("_", 1)[1] if "_" in base_id else base_id
    vol = a.get("volume_usd") or {}
    chg = a.get("price_change_percentage") or {}
    tx = a.get("transactions") or {}
    h1 = tx.get("h1") or {}
    h24 = tx.get("h24") or {}
    name = a.get("name") or ""
    return {
        "pool_address": a.get("address"),
        "token_mint": mint,
        "name": name,
        "symbol": name.split(" / ")[0].strip() if name else None,
        "dex": ((rel.get("dex") or {}).get("data") or {}).get("id"),
        "pool_created_at": a.get("pool_created_at"),
        "price_usd": _f(a.get("base_token_price_usd")),
        "liquidity_usd": _f(a.get("reserve_in_usd")),
        "fdv_usd": _f(a.get("fdv_usd")),
        "vol_m5": _f(vol.get("m5")), "vol_h1": _f(vol.get("h1")),
        "vol_h6": _f(vol.get("h6")), "vol_h24": _f(vol.get("h24")),
        "chg_m5": _f(chg.get("m5")), "chg_h1": _f(chg.get("h1")),
        "chg_h6": _f(chg.get("h6")), "chg_h24": _f(chg.get("h24")),
        "buys_h1": _i(h1.get("buys")), "sells_h1": _i(h1.get("sells")),
        "buyers_h1": _i(h1.get("buyers")), "sellers_h1": _i(h1.get("sellers")),
        "txns_h24": (_i(h24.get("buys")) or 0) + (_i(h24.get("sells")) or 0) if h24 else None,
    }


def _pools(path: str, params: dict | None = None) -> list[dict]:
    data = http.get_json(f"{config.GECKO_BASE}{path}", params=params)
    if not data:
        return []
    out = []
    for obj in data.get("data") or []:
        p = parse_pool(obj)
        if p and p["pool_address"]:
            out.append(p)
    return out


def new_pools(page: int) -> list[dict]:
    return _pools(f"/networks/{NET}/new_pools", {"page": page})


def trending_pools(page: int) -> list[dict]:
    return _pools(f"/networks/{NET}/trending_pools", {"page": page, "duration": "1h"})


def pools_multi(addresses: list[str]) -> list[dict]:
    out = []
    for i in range(0, len(addresses), 30):
        chunk = addresses[i:i + 30]
        out += _pools(f"/networks/{NET}/pools/multi/{','.join(chunk)}")
    return out


def top_pool_addresses(mints: list[str]) -> dict[str, str]:
    """{mint: its top pool address} for up to 30 mints per call."""
    out = {}
    for i in range(0, len(mints), 30):
        chunk = mints[i:i + 30]
        data = http.get_json(f"{config.GECKO_BASE}/networks/{NET}/tokens/multi/{','.join(chunk)}",
                             params={"include": "top_pools"})
        for tok in (data or {}).get("data") or []:
            mint = ((tok.get("attributes") or {}).get("address"))
            pools = (((tok.get("relationships") or {}).get("top_pools") or {}).get("data")) or []
            if mint and pools:
                pid = pools[0].get("id", "")
                out[mint] = pid.split("_", 1)[1] if "_" in pid else pid
    return out


def trending_pools_5m(page: int) -> list[dict]:
    return _pools(f"/networks/{NET}/trending_pools", {"page": page, "duration": "5m"})


def token_pools(mint: str) -> list[dict]:
    return _pools(f"/networks/{NET}/tokens/{mint}/pools", {"page": 1})


def minute_candles(pool: str, limit: int = 1000) -> list[tuple]:
    """Return 1-minute candles oldest-first as (ts, open, high, low, close, volume_usd)."""
    data = http.get_json(
        f"{config.GECKO_BASE}/networks/{NET}/pools/{pool}/ohlcv/minute",
        params={"aggregate": 1, "limit": limit, "currency": "usd", "token": "base"},
    )
    if not data:
        return []
    rows = ((data.get("data") or {}).get("attributes") or {}).get("ohlcv_list") or []
    out = [(int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])) for r in rows]
    out.sort(key=lambda r: r[0])
    return out
