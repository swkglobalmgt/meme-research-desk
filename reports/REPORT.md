# Meme Coin Research Desk: paper results
_Generated 2026-11-26T22:20+00:00 UTC · 3.3 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 115 | 33 | 40 | 94 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.4% | 33.3% | 42.5% | 31.9% | – |
| Average win | $20.09 | $17.58 | $18.37 | $15.82 | – |
| Average loss | -$26.77 | -$28.82 | -$25.20 | -$23.04 | – |
| Net P&L after all costs | -$1,063.87 | -$440.54 | -$267.17 | -$1,000.03 | $0.00 |
| Average return per trade | -9.3% | -13.3% | -6.7% | -10.6% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.88 | -2.55 | -1.87 | -5.11 | – |
| Worst drawdown | -$1,063.87 | -$440.54 | -$291.27 | -$1,010.58 | $0.00 |
| Rugs / unsellable hit | 9 | 2 | 0 | 11 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 3.3 of 4 weeks of data; net P&L after costs is $-1,063.87 (not positive); t-stat -3.88 below 2.0
- **volume_breakout**: only 3.3 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-440.54 (not positive); t-stat -2.55 below 2.0
- **pullback**: only 3.3 of 4 weeks of data; only 40 of 100 completed trades; net P&L after costs is $-267.17 (not positive); t-stat -1.87 below 2.0
- **founder_screen**: only 3.3 of 4 weeks of data; only 94 of 100 completed trades; net P&L after costs is $-1,000.03 (not positive); t-stat -5.11 below 2.0
- **copy_trader**: only 3.3 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 47,209 · watching now: 264 · snapshots: 89,829
- Safety checks: 4,144 · passed: 216

Most common safety failures:
- too young (< 1h): 3241
- liquidity < $50k (or unknown): 2739
- LP not burned/locked (or unknown): 2462
- top-10 holders >= 30%: 1957
- selling our size loses > 10%: 1165
- no sell route found: 895
- too few sells in last hour: 324
- mint authority NOT revoked: 15
- sell tax 100 bps: 10
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4872. Median real cost of one sell: 0.4% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 79 trades so far.

## Signals by strategy
- momentum: {'filled': 115, 'rejected_safety': 2747}
- volume_breakout: {'filled': 33, 'rejected_safety': 1837}
- pullback: {'filled': 40, 'rejected_safety': 112}
- founder_screen: {'pending': 1, 'filled': 94, 'rejected_safety': 857}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
