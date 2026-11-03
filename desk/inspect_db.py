"""Read-only: print positions and the snapshots around them. python -m desk.inspect_db"""
from .db import DB


def main():
    db = DB()
    for p in db.all("SELECT id, strategy, symbol, pool_address, entry_ts, entry_price, entry_liquidity, status, "
                    "exit_ts, exit_price, exit_liquidity, exit_reason, is_rug, net_pnl_usd, cost_adj_pct "
                    "FROM positions ORDER BY id"):
        print("POSITION", p)
        for s in db.all("SELECT ts, price_usd, liquidity_usd, vol_h1 FROM snapshots WHERE pool_address = ? "
                        "ORDER BY ts", [p["pool_address"]]):
            print("   snap", s)
        print("   signal", db.one("SELECT ts, signal_price, liquidity_usd FROM signals WHERE pool_address = ? "
                                  "AND status = 'filled' ORDER BY ts LIMIT 1", [p["pool_address"]]))
    db.close()


if __name__ == "__main__":
    main()
