# Meme Coin Research Desk: paper results
_Generated 2026-11-07T13:55+00:00 UTC · 0.6 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 47 | 12 | 19 | 21 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.2% | 33.3% | 31.6% | 38.1% | – |
| Average win | $19.13 | $21.71 | $21.28 | $8.53 | – |
| Average loss | -$26.83 | -$33.27 | -$24.29 | -$21.82 | – |
| Net P&L after all costs | -$479.51 | -$179.32 | -$188.08 | -$215.36 | $0.00 |
| Average return per trade | -10.2% | -14.9% | -9.9% | -10.3% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -2.70 | -1.46 | -1.91 | -2.56 | – |
| Worst drawdown | -$506.86 | -$179.32 | -$189.57 | -$230.09 | $0.00 |
| Rugs / unsellable hit | 6 | 1 | 0 | 3 | 0 |
| Losses worse than -50% | 1 | 1 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.6 of 4 weeks of data; only 47 of 100 completed trades; net P&L after costs is $-479.51 (not positive); t-stat -2.70 below 2.0
- **volume_breakout**: only 0.6 of 4 weeks of data; only 12 of 100 completed trades; net P&L after costs is $-179.32 (not positive); t-stat -1.46 below 2.0
- **pullback**: only 0.6 of 4 weeks of data; only 19 of 100 completed trades; net P&L after costs is $-188.08 (not positive); t-stat -1.91 below 2.0
- **founder_screen**: only 0.6 of 4 weeks of data; only 21 of 100 completed trades; net P&L after costs is $-215.36 (not positive); t-stat -2.56 below 2.0
- **copy_trader**: only 0.6 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 20,455 · watching now: 711 · snapshots: 43,950
- Safety checks: 1,796 · passed: 75

Most common safety failures:
- too young (< 1h): 1417
- liquidity < $50k (or unknown): 1178
- LP not burned/locked (or unknown): 1050
- top-10 holders >= 30%: 899
- selling our size loses > 10%: 569
- no sell route found: 380
- too few sells in last hour: 216
- mint authority NOT revoked: 9
- sell tax 100 bps: 5
- sell tax 500 bps: 2
- freeze authority NOT revoked: 2
- sell tax 300 bps: 1

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 2202. Median real cost of one sell: 2.3% vs our model 3.1%.
- Quote was worse than our model 48% of the time. When it was, that trade was charged the real (worse) cost: 31 trades so far.

## Signals by strategy
- momentum: {'filled': 47, 'rejected_safety': 1226}
- volume_breakout: {'filled': 12, 'rejected_safety': 824}
- pullback: {'filled': 19, 'rejected_safety': 50}
- founder_screen: {'filled': 21, 'rejected_safety': 434}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
