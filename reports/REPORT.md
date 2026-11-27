# Meme Coin Research Desk: paper results
_Generated 2026-11-27T21:57+00:00 UTC · 3.4 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 115 | 33 | 41 | 98 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.4% | 33.3% | 41.5% | 32.7% | – |
| Average win | $20.09 | $17.58 | $18.37 | $15.07 | – |
| Average loss | -$26.77 | -$28.82 | -$25.18 | -$22.92 | – |
| Net P&L after all costs | -$1,063.87 | -$440.54 | -$292.03 | -$1,030.48 | $0.00 |
| Average return per trade | -9.3% | -13.3% | -7.1% | -10.5% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.88 | -2.55 | -2.03 | -5.22 | – |
| Worst drawdown | -$1,063.87 | -$440.54 | -$292.03 | -$1,030.48 | $0.00 |
| Rugs / unsellable hit | 9 | 2 | 0 | 12 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 3.4 of 4 weeks of data; net P&L after costs is $-1,063.87 (not positive); t-stat -3.88 below 2.0
- **volume_breakout**: only 3.4 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-440.54 (not positive); t-stat -2.55 below 2.0
- **pullback**: only 3.4 of 4 weeks of data; only 41 of 100 completed trades; net P&L after costs is $-292.03 (not positive); t-stat -2.03 below 2.0
- **founder_screen**: only 3.4 of 4 weeks of data; only 98 of 100 completed trades; net P&L after costs is $-1,030.48 (not positive); t-stat -5.22 below 2.0
- **copy_trader**: only 3.4 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 47,810 · watching now: 277 · snapshots: 79,382
- Safety checks: 4,206 · passed: 219

Most common safety failures:
- too young (< 1h): 3287
- liquidity < $50k (or unknown): 2781
- LP not burned/locked (or unknown): 2506
- top-10 holders >= 30%: 1991
- selling our size loses > 10%: 1173
- no sell route found: 925
- too few sells in last hour: 326
- mint authority NOT revoked: 15
- sell tax 100 bps: 10
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4910. Median real cost of one sell: 0.4% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 79 trades so far.

## Signals by strategy
- momentum: {'filled': 115, 'rejected_safety': 2779}
- volume_breakout: {'filled': 33, 'rejected_safety': 1861}
- pullback: {'filled': 41, 'rejected_safety': 113}
- founder_screen: {'filled': 98, 'rejected_safety': 864}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
