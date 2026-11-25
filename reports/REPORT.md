# Meme Coin Research Desk: paper results
_Generated 2026-11-25T22:30+00:00 UTC · 3.1 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 113 | 33 | 39 | 88 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 38.1% | 33.3% | 43.6% | 33.0% | – |
| Average win | $20.09 | $17.58 | $18.37 | $16.00 | – |
| Average loss | -$26.84 | -$28.82 | -$25.21 | -$22.67 | – |
| Net P&L after all costs | -$1,014.69 | -$440.54 | -$242.17 | -$873.43 | $0.00 |
| Average return per trade | -9.0% | -13.3% | -6.2% | -9.9% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.71 | -2.55 | -1.71 | -4.58 | – |
| Worst drawdown | -$1,054.75 | -$440.54 | -$291.27 | -$873.43 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 3.1 of 4 weeks of data; net P&L after costs is $-1,014.69 (not positive); t-stat -3.71 below 2.0
- **volume_breakout**: only 3.1 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-440.54 (not positive); t-stat -2.55 below 2.0
- **pullback**: only 3.1 of 4 weeks of data; only 39 of 100 completed trades; net P&L after costs is $-242.17 (not positive); t-stat -1.71 below 2.0
- **founder_screen**: only 3.1 of 4 weeks of data; only 88 of 100 completed trades; net P&L after costs is $-873.43 (not positive); t-stat -4.58 below 2.0
- **copy_trader**: only 3.1 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 46,502 · watching now: 242 · snapshots: 98,336
- Safety checks: 4,104 · passed: 210

Most common safety failures:
- too young (< 1h): 3213
- liquidity < $50k (or unknown): 2713
- LP not burned/locked (or unknown): 2436
- top-10 holders >= 30%: 1941
- selling our size loses > 10%: 1161
- no sell route found: 885
- too few sells in last hour: 324
- mint authority NOT revoked: 15
- sell tax 100 bps: 10
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4831. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 79 trades so far.

## Signals by strategy
- momentum: {'filled': 113, 'rejected_safety': 2725}
- volume_breakout: {'filled': 33, 'rejected_safety': 1822}
- pullback: {'filled': 39, 'rejected_safety': 112}
- founder_screen: {'pending': 2, 'filled': 88, 'rejected_safety': 851}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
