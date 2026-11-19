# Meme Coin Research Desk: paper results
_Generated 2026-11-19T21:30+00:00 UTC · 2.3 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 107 | 31 | 35 | 70 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.4% | 32.3% | 45.7% | 31.4% | – |
| Average win | $19.86 | $18.48 | $19.11 | $14.43 | – |
| Average loss | -$26.90 | -$29.54 | -$24.96 | -$22.68 | – |
| Net P&L after all costs | -$1,054.75 | -$435.53 | -$168.40 | -$771.09 | $0.00 |
| Average return per trade | -9.9% | -14.0% | -4.8% | -11.0% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.98 | -2.54 | -1.24 | -4.66 | – |
| Worst drawdown | -$1,054.75 | -$435.53 | -$291.27 | -$771.09 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 2.3 of 4 weeks of data; net P&L after costs is $-1,054.75 (not positive); t-stat -3.98 below 2.0
- **volume_breakout**: only 2.3 of 4 weeks of data; only 31 of 100 completed trades; net P&L after costs is $-435.53 (not positive); t-stat -2.54 below 2.0
- **pullback**: only 2.3 of 4 weeks of data; only 35 of 100 completed trades; net P&L after costs is $-168.40 (not positive); t-stat -1.24 below 2.0
- **founder_screen**: only 2.3 of 4 weeks of data; only 70 of 100 completed trades; net P&L after costs is $-771.09 (not positive); t-stat -4.66 below 2.0
- **copy_trader**: only 2.3 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 42,720 · watching now: 204 · snapshots: 103,302
- Safety checks: 3,679 · passed: 182

Most common safety failures:
- too young (< 1h): 2887
- liquidity < $50k (or unknown): 2407
- LP not burned/locked (or unknown): 2146
- top-10 holders >= 30%: 1762
- selling our size loses > 10%: 1092
- no sell route found: 722
- too few sells in last hour: 314
- mint authority NOT revoked: 15
- sell tax 100 bps: 9
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4509. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 71 trades so far.

## Signals by strategy
- momentum: {'pending': 1, 'filled': 107, 'rejected_safety': 2504}
- volume_breakout: {'filled': 31, 'rejected_safety': 1653}
- pullback: {'filled': 35, 'rejected_safety': 109}
- founder_screen: {'pending': 1, 'filled': 70, 'rejected_safety': 789}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
