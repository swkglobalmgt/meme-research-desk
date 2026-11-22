# Meme Coin Research Desk: paper results
_Generated 2026-11-22T20:20+00:00 UTC · 2.7 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 109 | 31 | 35 | 81 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.6% | 32.3% | 45.7% | 33.3% | – |
| Average win | $19.98 | $18.48 | $19.11 | $15.53 | – |
| Average loss | -$26.90 | -$29.54 | -$24.96 | -$22.60 | – |
| Net P&L after all costs | -$1,009.85 | -$435.53 | -$168.40 | -$800.96 | $0.00 |
| Average return per trade | -9.3% | -14.0% | -4.8% | -9.9% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.76 | -2.54 | -1.24 | -4.38 | – |
| Worst drawdown | -$1,054.75 | -$435.53 | -$291.27 | -$800.96 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 2.7 of 4 weeks of data; net P&L after costs is $-1,009.85 (not positive); t-stat -3.76 below 2.0
- **volume_breakout**: only 2.7 of 4 weeks of data; only 31 of 100 completed trades; net P&L after costs is $-435.53 (not positive); t-stat -2.54 below 2.0
- **pullback**: only 2.7 of 4 weeks of data; only 35 of 100 completed trades; net P&L after costs is $-168.40 (not positive); t-stat -1.24 below 2.0
- **founder_screen**: only 2.7 of 4 weeks of data; only 81 of 100 completed trades; net P&L after costs is $-800.96 (not positive); t-stat -4.38 below 2.0
- **copy_trader**: only 2.7 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 44,971 · watching now: 262 · snapshots: 105,013
- Safety checks: 3,922 · passed: 194

Most common safety failures:
- too young (< 1h): 3076
- liquidity < $50k (or unknown): 2580
- LP not burned/locked (or unknown): 2312
- top-10 holders >= 30%: 1862
- selling our size loses > 10%: 1129
- no sell route found: 812
- too few sells in last hour: 320
- mint authority NOT revoked: 15
- sell tax 100 bps: 10
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4697. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 75 trades so far.

## Signals by strategy
- momentum: {'filled': 109, 'rejected_safety': 2639}
- volume_breakout: {'pending': 1, 'filled': 31, 'rejected_safety': 1747}
- pullback: {'filled': 35, 'rejected_safety': 109}
- founder_screen: {'filled': 81, 'rejected_safety': 826}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
