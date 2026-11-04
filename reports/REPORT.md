# Meme Coin Research Desk: paper results
_Generated 2026-11-04T14:25+00:00 UTC · 0.1 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 17 | 3 | 9 | 8 | 0 |
| Open positions | 0 | 0 | 0 | 1 | 0 |
| Win rate | 35.3% | 33.3% | 11.1% | 25.0% | – |
| Average win | $19.57 | $23.00 | $22.49 | $23.13 | – |
| Average loss | -$29.38 | -$23.86 | -$26.51 | -$27.98 | – |
| Net P&L after all costs | -$205.80 | -$24.71 | -$189.57 | -$121.64 | $0.00 |
| Average return per trade | -12.1% | -8.2% | -21.1% | -15.2% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -1.61 | – | – | – | – |
| Worst drawdown | -$205.80 | -$30.62 | -$189.57 | -$121.64 | $0.00 |
| Rugs / unsellable hit | 3 | 0 | 0 | 2 | 0 |
| Losses worse than -50% | 1 | 0 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.1 of 4 weeks of data; only 17 of 100 completed trades; net P&L after costs is $-205.80 (not positive); t-stat -1.61 below 2.0
- **volume_breakout**: only 0.1 of 4 weeks of data; only 3 of 100 completed trades; net P&L after costs is $-24.71 (not positive); too few trades for a meaningful t-stat
- **pullback**: only 0.1 of 4 weeks of data; only 9 of 100 completed trades; net P&L after costs is $-189.57 (not positive); too few trades for a meaningful t-stat
- **founder_screen**: only 0.1 of 4 weeks of data; only 8 of 100 completed trades; net P&L after costs is $-121.64 (not positive); too few trades for a meaningful t-stat
- **copy_trader**: only 0.1 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 7,481 · watching now: 409 · snapshots: 9,208
- Safety checks: 642 · passed: 30

Most common safety failures:
- too young (< 1h): 497
- liquidity < $50k (or unknown): 404
- LP not burned/locked (or unknown): 377
- top-10 holders >= 30%: 301
- selling our size loses > 10%: 176
- no sell route found: 171
- too few sells in last hour: 86
- mint authority NOT revoked: 3
- sell tax 100 bps: 3
- sell tax 500 bps: 1
- sell tax 300 bps: 1

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 729. Median real cost of one sell: 1.3% vs our model 3.1%.
- Quote was worse than our model 46% of the time. When it was, that trade was charged the real (worse) cost: 10 trades so far.

## Signals by strategy
- momentum: {'filled': 17, 'rejected_safety': 450}
- volume_breakout: {'filled': 3, 'rejected_safety': 278}
- pullback: {'filled': 9, 'rejected_safety': 14}
- founder_screen: {'filled': 9, 'rejected_safety': 159}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
