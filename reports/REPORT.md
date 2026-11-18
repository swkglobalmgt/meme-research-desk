# Meme Coin Research Desk: paper results
_Generated 2026-11-18T21:26+00:00 UTC · 2.1 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 104 | 31 | 35 | 67 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.5% | 32.3% | 45.7% | 31.3% | – |
| Average win | $19.86 | $18.48 | $19.11 | $14.02 | – |
| Average loss | -$26.87 | -$29.54 | -$24.96 | -$22.48 | – |
| Net P&L after all costs | -$972.21 | -$435.53 | -$168.40 | -$739.78 | $0.00 |
| Average return per trade | -9.3% | -14.0% | -4.8% | -11.0% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.70 | -2.54 | -1.24 | -4.62 | – |
| Worst drawdown | -$979.66 | -$435.53 | -$291.27 | -$739.78 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 2.1 of 4 weeks of data; net P&L after costs is $-972.21 (not positive); t-stat -3.70 below 2.0
- **volume_breakout**: only 2.1 of 4 weeks of data; only 31 of 100 completed trades; net P&L after costs is $-435.53 (not positive); t-stat -2.54 below 2.0
- **pullback**: only 2.1 of 4 weeks of data; only 35 of 100 completed trades; net P&L after costs is $-168.40 (not positive); t-stat -1.24 below 2.0
- **founder_screen**: only 2.1 of 4 weeks of data; only 67 of 100 completed trades; net P&L after costs is $-739.78 (not positive); t-stat -4.62 below 2.0
- **copy_trader**: only 2.1 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 42,230 · watching now: 192 · snapshots: 102,852
- Safety checks: 3,644 · passed: 178

Most common safety failures:
- too young (< 1h): 2865
- liquidity < $50k (or unknown): 2394
- LP not burned/locked (or unknown): 2129
- top-10 holders >= 30%: 1749
- selling our size loses > 10%: 1085
- no sell route found: 718
- too few sells in last hour: 312
- mint authority NOT revoked: 15
- freeze authority NOT revoked: 7
- sell tax 100 bps: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4469. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 69 trades so far.

## Signals by strategy
- momentum: {'pending': 1, 'filled': 104, 'rejected_safety': 2484}
- volume_breakout: {'filled': 31, 'rejected_safety': 1644}
- pullback: {'filled': 35, 'rejected_safety': 109}
- founder_screen: {'pending': 2, 'filled': 67, 'rejected_safety': 779}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
