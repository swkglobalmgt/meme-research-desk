# Meme Coin Research Desk: paper results
_Generated 2026-11-11T14:24+00:00 UTC · 1.1 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 91 | 27 | 33 | 45 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.3% | 33.3% | 42.4% | 31.1% | – |
| Average win | $19.91 | $20.34 | $19.30 | $11.42 | – |
| Average loss | -$27.28 | -$31.65 | -$24.96 | -$21.63 | – |
| Net P&L after all costs | -$925.03 | -$386.65 | -$203.96 | -$510.65 | $0.00 |
| Average return per trade | -10.2% | -14.3% | -6.2% | -11.3% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.71 | -2.26 | -1.55 | -4.05 | – |
| Worst drawdown | -$971.43 | -$386.65 | -$291.27 | -$510.65 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 7 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.1 of 4 weeks of data; only 91 of 100 completed trades; net P&L after costs is $-925.03 (not positive); t-stat -3.71 below 2.0
- **volume_breakout**: only 1.1 of 4 weeks of data; only 27 of 100 completed trades; net P&L after costs is $-386.65 (not positive); t-stat -2.26 below 2.0
- **pullback**: only 1.1 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-203.96 (not positive); t-stat -1.55 below 2.0
- **founder_screen**: only 1.1 of 4 weeks of data; only 45 of 100 completed trades; net P&L after costs is $-510.65 (not positive); t-stat -4.05 below 2.0
- **copy_trader**: only 1.1 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 37,120 · watching now: 455 · snapshots: 96,869
- Safety checks: 3,211 · passed: 141

Most common safety failures:
- too young (< 1h): 2571
- liquidity < $50k (or unknown): 2113
- LP not burned/locked (or unknown): 1891
- top-10 holders >= 30%: 1597
- selling our size loses > 10%: 976
- no sell route found: 649
- too few sells in last hour: 290
- mint authority NOT revoked: 14
- sell tax 100 bps: 6
- freeze authority NOT revoked: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 500 bps: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 3989. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 61 trades so far.

## Signals by strategy
- momentum: {'filled': 91, 'rejected_safety': 2239}
- volume_breakout: {'filled': 27, 'rejected_safety': 1478}
- pullback: {'filled': 33, 'rejected_safety': 94}
- founder_screen: {'pending': 1, 'filled': 45, 'rejected_safety': 699}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
