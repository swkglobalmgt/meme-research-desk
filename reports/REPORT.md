# Meme Coin Research Desk: paper results
_Generated 2026-11-20T21:04+00:00 UTC · 2.4 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 108 | 31 | 35 | 75 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.0% | 32.3% | 45.7% | 33.3% | – |
| Average win | $19.91 | $18.48 | $19.11 | $15.38 | – |
| Average loss | -$26.90 | -$29.54 | -$24.96 | -$22.77 | – |
| Net P&L after all costs | -$1,032.58 | -$435.53 | -$168.40 | -$753.78 | $0.00 |
| Average return per trade | -9.6% | -14.0% | -4.8% | -10.1% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.87 | -2.54 | -1.24 | -4.28 | – |
| Worst drawdown | -$1,054.75 | -$435.53 | -$291.27 | -$771.09 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 2.4 of 4 weeks of data; net P&L after costs is $-1,032.58 (not positive); t-stat -3.87 below 2.0
- **volume_breakout**: only 2.4 of 4 weeks of data; only 31 of 100 completed trades; net P&L after costs is $-435.53 (not positive); t-stat -2.54 below 2.0
- **pullback**: only 2.4 of 4 weeks of data; only 35 of 100 completed trades; net P&L after costs is $-168.40 (not positive); t-stat -1.24 below 2.0
- **founder_screen**: only 2.4 of 4 weeks of data; only 75 of 100 completed trades; net P&L after costs is $-753.78 (not positive); t-stat -4.28 below 2.0
- **copy_trader**: only 2.4 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 43,564 · watching now: 202 · snapshots: 103,911
- Safety checks: 3,761 · passed: 186

Most common safety failures:
- too young (< 1h): 2951
- liquidity < $50k (or unknown): 2470
- LP not burned/locked (or unknown): 2201
- top-10 holders >= 30%: 1800
- selling our size loses > 10%: 1109
- no sell route found: 748
- too few sells in last hour: 317
- mint authority NOT revoked: 15
- sell tax 100 bps: 9
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4580. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 71 trades so far.

## Signals by strategy
- momentum: {'filled': 108, 'rejected_safety': 2551}
- volume_breakout: {'filled': 31, 'rejected_safety': 1687}
- pullback: {'filled': 35, 'rejected_safety': 109}
- founder_screen: {'filled': 75, 'rejected_safety': 801}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
