# Meme Coin Research Desk: paper results
_Generated 2026-11-08T13:55+00:00 UTC · 0.7 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 65 | 19 | 24 | 26 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 32.3% | 36.8% | 33.3% | 34.6% | – |
| Average win | $19.44 | $22.13 | $20.03 | $10.15 | – |
| Average loss | -$27.70 | -$36.95 | -$25.00 | -$21.91 | – |
| Net P&L after all costs | -$810.57 | -$288.41 | -$239.82 | -$281.21 | $0.00 |
| Average return per trade | -12.5% | -15.2% | -10.0% | -10.8% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.76 | -1.75 | -2.18 | -2.89 | – |
| Worst drawdown | -$848.11 | -$288.41 | -$239.82 | -$281.21 | $0.00 |
| Rugs / unsellable hit | 7 | 2 | 0 | 4 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.7 of 4 weeks of data; only 65 of 100 completed trades; net P&L after costs is $-810.57 (not positive); t-stat -3.76 below 2.0
- **volume_breakout**: only 0.7 of 4 weeks of data; only 19 of 100 completed trades; net P&L after costs is $-288.41 (not positive); t-stat -1.75 below 2.0
- **pullback**: only 0.7 of 4 weeks of data; only 24 of 100 completed trades; net P&L after costs is $-239.82 (not positive); t-stat -2.18 below 2.0
- **founder_screen**: only 0.7 of 4 weeks of data; only 26 of 100 completed trades; net P&L after costs is $-281.21 (not positive); t-stat -2.89 below 2.0
- **copy_trader**: only 0.7 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 25,430 · watching now: 865 · snapshots: 62,644
- Safety checks: 2,261 · passed: 99

Most common safety failures:
- too young (< 1h): 1812
- liquidity < $50k (or unknown): 1470
- LP not burned/locked (or unknown): 1331
- top-10 holders >= 30%: 1101
- selling our size loses > 10%: 708
- no sell route found: 451
- too few sells in last hour: 237
- mint authority NOT revoked: 11
- sell tax 100 bps: 5
- freeze authority NOT revoked: 3
- sell tax 500 bps: 2
- risky token extensions: ['transferHook', 'permanentDelegate']: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 2808. Median real cost of one sell: 0.8% vs our model 3.0%.
- Quote was worse than our model 46% of the time. When it was, that trade was charged the real (worse) cost: 43 trades so far.

## Signals by strategy
- momentum: {'filled': 65, 'rejected_safety': 1573}
- volume_breakout: {'filled': 19, 'rejected_safety': 1051}
- pullback: {'filled': 24, 'rejected_safety': 57}
- founder_screen: {'filled': 26, 'rejected_safety': 503}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
