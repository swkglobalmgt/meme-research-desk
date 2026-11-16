# Meme Coin Research Desk: paper results
_Generated 2026-11-16T22:52+00:00 UTC · 1.9 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 101 | 30 | 34 | 60 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.6% | 33.3% | 44.1% | 31.7% | – |
| Average win | $19.79 | $18.48 | $18.89 | $13.75 | – |
| Average loss | -$27.04 | -$30.29 | -$24.96 | -$22.36 | – |
| Net P&L after all costs | -$951.60 | -$421.06 | -$190.90 | -$655.42 | $0.00 |
| Average return per trade | -9.4% | -14.0% | -5.6% | -10.9% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.65 | -2.45 | -1.44 | -4.30 | – |
| Worst drawdown | -$979.66 | -$421.06 | -$291.27 | -$655.42 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.9 of 4 weeks of data; net P&L after costs is $-951.60 (not positive); t-stat -3.65 below 2.0
- **volume_breakout**: only 1.9 of 4 weeks of data; only 30 of 100 completed trades; net P&L after costs is $-421.06 (not positive); t-stat -2.45 below 2.0
- **pullback**: only 1.9 of 4 weeks of data; only 34 of 100 completed trades; net P&L after costs is $-190.90 (not positive); t-stat -1.44 below 2.0
- **founder_screen**: only 1.9 of 4 weeks of data; only 60 of 100 completed trades; net P&L after costs is $-655.42 (not positive); t-stat -4.30 below 2.0
- **copy_trader**: only 1.9 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 41,050 · watching now: 275 · snapshots: 101,841
- Safety checks: 3,547 · passed: 167

Most common safety failures:
- too young (< 1h): 2800
- liquidity < $50k (or unknown): 2328
- LP not burned/locked (or unknown): 2074
- top-10 holders >= 30%: 1714
- selling our size loses > 10%: 1059
- no sell route found: 703
- too few sells in last hour: 306
- mint authority NOT revoked: 15
- freeze authority NOT revoked: 7
- sell tax 100 bps: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 3

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4349. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 69 trades so far.

## Signals by strategy
- momentum: {'filled': 101, 'rejected_safety': 2425}
- volume_breakout: {'filled': 30, 'rejected_safety': 1599}
- pullback: {'filled': 34, 'rejected_safety': 107}
- founder_screen: {'pending': 2, 'filled': 60, 'rejected_safety': 763}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
