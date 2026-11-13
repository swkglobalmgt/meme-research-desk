# Meme Coin Research Desk: paper results
_Generated 2026-11-13T20:28+00:00 UTC · 1.4 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 97 | 29 | 33 | 51 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.1% | 34.5% | 42.4% | 31.4% | – |
| Average win | $20.04 | $18.48 | $19.30 | $12.77 | – |
| Average loss | -$27.04 | -$31.27 | -$24.96 | -$22.24 | – |
| Net P&L after all costs | -$975.19 | -$409.41 | -$203.96 | -$574.15 | $0.00 |
| Average return per trade | -10.1% | -14.1% | -6.2% | -11.3% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.82 | -2.38 | -1.55 | -4.14 | – |
| Worst drawdown | -$975.19 | -$411.11 | -$291.27 | -$596.37 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 8 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.4 of 4 weeks of data; only 97 of 100 completed trades; net P&L after costs is $-975.19 (not positive); t-stat -3.82 below 2.0
- **volume_breakout**: only 1.4 of 4 weeks of data; only 29 of 100 completed trades; net P&L after costs is $-409.41 (not positive); t-stat -2.38 below 2.0
- **pullback**: only 1.4 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-203.96 (not positive); t-stat -1.55 below 2.0
- **founder_screen**: only 1.4 of 4 weeks of data; only 51 of 100 completed trades; net P&L after costs is $-574.15 (not positive); t-stat -4.14 below 2.0
- **copy_trader**: only 1.4 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 38,689 · watching now: 253 · snapshots: 99,719
- Safety checks: 3,341 · passed: 153

Most common safety failures:
- too young (< 1h): 2663
- liquidity < $50k (or unknown): 2195
- LP not burned/locked (or unknown): 1961
- top-10 holders >= 30%: 1636
- selling our size loses > 10%: 1014
- no sell route found: 663
- too few sells in last hour: 295
- mint authority NOT revoked: 14
- sell tax 100 bps: 6
- freeze authority NOT revoked: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 500 bps: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4137. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 63 trades so far.

## Signals by strategy
- momentum: {'filled': 97, 'rejected_safety': 2314}
- volume_breakout: {'filled': 29, 'rejected_safety': 1526}
- pullback: {'filled': 33, 'rejected_safety': 96}
- founder_screen: {'filled': 51, 'rejected_safety': 723}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
