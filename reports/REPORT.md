# Meme Coin Research Desk: paper results
_Generated 2026-11-15T19:22+00:00 UTC · 1.7 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 98 | 30 | 34 | 56 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.7% | 33.3% | 44.1% | 33.9% | – |
| Average win | $20.11 | $18.48 | $18.89 | $13.75 | – |
| Average loss | -$27.04 | -$30.29 | -$24.96 | -$22.38 | – |
| Net P&L after all costs | -$952.77 | -$421.06 | -$190.90 | -$566.77 | $0.00 |
| Average return per trade | -9.7% | -14.0% | -5.6% | -10.1% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.70 | -2.45 | -1.44 | -3.79 | – |
| Worst drawdown | -$975.19 | -$421.06 | -$291.27 | -$598.73 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 8 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.7 of 4 weeks of data; only 98 of 100 completed trades; net P&L after costs is $-952.77 (not positive); t-stat -3.70 below 2.0
- **volume_breakout**: only 1.7 of 4 weeks of data; only 30 of 100 completed trades; net P&L after costs is $-421.06 (not positive); t-stat -2.45 below 2.0
- **pullback**: only 1.7 of 4 weeks of data; only 34 of 100 completed trades; net P&L after costs is $-190.90 (not positive); t-stat -1.44 below 2.0
- **founder_screen**: only 1.7 of 4 weeks of data; only 56 of 100 completed trades; net P&L after costs is $-566.77 (not positive); t-stat -3.79 below 2.0
- **copy_trader**: only 1.7 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 40,306 · watching now: 246 · snapshots: 101,131
- Safety checks: 3,472 · passed: 159

Most common safety failures:
- too young (< 1h): 2752
- liquidity < $50k (or unknown): 2278
- LP not burned/locked (or unknown): 2038
- top-10 holders >= 30%: 1693
- selling our size loses > 10%: 1047
- no sell route found: 687
- too few sells in last hour: 301
- mint authority NOT revoked: 15
- freeze authority NOT revoked: 7
- sell tax 100 bps: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 3

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4276. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 65 trades so far.

## Signals by strategy
- momentum: {'filled': 98, 'rejected_safety': 2386}
- volume_breakout: {'filled': 30, 'rejected_safety': 1572}
- pullback: {'filled': 34, 'rejected_safety': 105}
- founder_screen: {'filled': 56, 'rejected_safety': 751}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
