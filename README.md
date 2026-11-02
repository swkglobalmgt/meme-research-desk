# Meme Coin Research Desk (paper trading only)

**Question this project answers:** does any simple, rule-based meme-coin strategy on
Solana make money *after* fees, slippage, rug pulls and failed sells?

**No real money, no wallet, no keys.** The code has no ability to sign or send a
transaction, and it refuses to run if a private key is present in its environment.

## How it works (plain language)

Every 30 minutes GitHub runs one research cycle:

1. **Collect.** It pulls newly created and trending Solana pools from GeckoTerminal
   and keeps a watch list of young pools that have real liquidity.
2. **Look for entries.** It checks four strategies, each kept completely separate:
   | Strategy | Buys when… |
   |---|---|
   | `momentum` | up 20%+ over the last hour, still rising, more buyers than sellers |
   | `volume_breakout` | the last 5 minutes traded 3x the hour's normal pace and price jumped 3%+ |
   | `pullback` | ran up 50%+ over 6h, dipped 10-25% over the last hour, now bouncing |
   | `founder_screen` | top of the founder's DexScreener screen (24h gainers with liq ≥ $25k, 50+ txns, $10k+ volume) |
3. **Safety filters.** A coin must pass all of these first, otherwise there is no entry:
   mint authority revoked · freeze authority revoked · LP ≥ 90% burned/locked ·
   top-10 holders < 30% (pool/burn/locker excluded) · liquidity ≥ $50k · pool ≥ 1 hour old ·
   no sell tax or hostile token features · 20+ sells by 10+ different sellers in the last hour ·
   a real sell quote for our size that loses ≤ 10% · not flagged as rugged.
   **If any data is missing, the coin fails.**
4. **Paper trade.** Fixed rules: $100 per trade, take profit +30%, stop loss −20%,
   max hold 4 hours, max 10 open per strategy, no re-buying the same coin within 24h.
5. **Report.** Win rate, average win/loss, net P&L after all costs, worst drawdown,
   rugs hit, and a pass/fail decision gate, separately for each strategy.

## Realistic costs (deliberately pessimistic)

- We act **at least 60 seconds after** the price we saw, and pay the **highest price of that minute**.
- Every swap pays a 0.5% pool fee, **2% base slippage plus our own price impact** on the pool,
  and $0.25 in network/priority fees.
- If a stop and a take-profit could both have triggered in the same minute, we assume the **stop** hit.
- If price gaps through the stop, we get the **worse** price.
- If liquidity falls 80%+ or the pool disappears, the trade is a **rug**. Below $1k liquidity
  the tokens are worth **zero**.
- Every filled trade stays in the results, rugs included.

With no price movement at all, a round trip on a $50k pool costs about 6%.
A strategy has to beat that just to break even.

## Decision gate (checked per strategy, after 4+ weeks)

Real money is only discussed if **all** of these hold: 100+ completed trades, net
positive after costs, t-statistic ≥ 2, rugs included. Real trading also needs separate
written approval from the founder. If the gate fails, that is a useful answer.

## Where to look

- **Actions tab → research-cycle → latest run:** the summary table for that run.
- **`reports/REPORT.md`:** updated once a day.
- **`reports/dashboard.html`:** download it and open it in a browser.

## Setup (one time)

Add the `DATABASE_URL` repository secret (Neon Postgres connection string).
You can also add `SOLANA_RPC_URL` (e.g. a free Helius RPC URL) so mint checks are more reliable.

## For engineers

```
pip install -r requirements.txt
python -m pytest -q                  # safety filters, cost/P&L math, ledger, full-cycle test
python -m desk.run all               # one cycle (uses ./desk.sqlite3 if DATABASE_URL unset)
python -m desk.run report
```
All parameters live in `desk/config.py`. If you change a strategy's rules after it has
trades, give it a new name so the old and new results are never mixed.
