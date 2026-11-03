"""Diagnostics: show raw answers from each data source. Read-only.

Run with: python -m desk.diag
"""
from __future__ import annotations

import json

import requests

from . import config
from .sources import geckoterminal as gt

BONK = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"


def show(label, r):
    body = r.text[:400].replace("\n", " ")
    print(f"--- {label}: HTTP {r.status_code}\n{body}\n")


def main():
    s = requests.Session()
    params = {"inputMint": BONK, "outputMint": config.USDC_MINT, "amount": 10_000_000_000, "slippageBps": 500}
    for url in (config.JUPITER_QUOTE, "https://api.jup.ag/swap/v1/quote", "https://quote-api.jup.ag/v6/quote"):
        try:
            show(f"jupiter {url}", s.get(url, params=params, timeout=20))
        except Exception as e:
            print(f"--- jupiter {url}: ERROR {e}\n")
    from .sources import onchain
    try:
        print("--- fixed sell quote BONK 10k tokens:", onchain.jupiter_sell_quote(BONK, 5, 1_000_000))
    except Exception as e:
        print(f"--- fixed sell quote: ERROR {e}")
    try:
        print("--- SOL price:", onchain.sol_usd_price())
    except Exception as e:
        print(f"--- SOL price: ERROR {e}")
    try:
        show("rugcheck BONK", s.get(f"{config.RUGCHECK_BASE}/tokens/{BONK}/report/summary", timeout=30))
    except Exception as e:
        print(f"--- rugcheck: ERROR {e}")
    try:
        r = s.post(config.SOLANA_RPC_URL, json={"jsonrpc": "2.0", "id": 1, "method": "getAccountInfo",
                                                "params": [BONK, {"encoding": "jsonParsed"}]}, timeout=20)
        show("solana rpc getAccountInfo BONK", r)
    except Exception as e:
        print(f"--- rpc: ERROR {e}")
    for mint in config.WATCH_TOKENS:
        pools = gt.token_pools(mint)
        print(f"--- geckoterminal pools for watch token {mint}: {len(pools)}")
        for p in pools[:3]:
            print(json.dumps({k: p.get(k) for k in ("pool_address", "dex", "liquidity_usd", "chg_h24", "pool_created_at")}))


if __name__ == "__main__":
    main()
