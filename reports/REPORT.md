# Meme Coin Research Desk: paper results
_Generated 2026-11-17T21:45+00:00 UTC · 2.0 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 102 | 30 | 35 | 64 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 37.3% | 33.3% | 45.7% | 32.8% | – |
| Average win | $19.79 | $18.48 | $19.11 | $14.02 | – |
| Average loss | -$27.01 | -$30.29 | -$24.96 | -$22.48 | – |
| Net P&L after all costs | -$976.90 | -$421.06 | -$168.40 | -$672.38 | $0.00 |
| Average return per trade | -9.6% | -14.0% | -4.8% | -10.5% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.75 | -2.45 | -1.24 | -4.23 | – |
| Worst drawdown | -$979.66 | -$421.06 | -$291.27 | -$680.26 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 2.0 of 4 weeks of data; net P&L after costs is $-976.90 (not positive); t-stat -3.75 below 2.0
- **volume_breakout**: only 2.0 of 4 weeks of data; only 30 of 100 completed trades; net P&L after costs is $-421.06 (not positive); t-stat -2.45 below 2.0
- **pullback**: only 2.0 of 4 weeks of data; only 35 of 100 completed trades; net P&L after costs is $-168.40 (not positive); t-stat -1.24 below 2.0
- **founder_screen**: only 2.0 of 4 weeks of data; only 64 of 100 completed trades; net P&L after costs is $-672.38 (not positive); t-stat -4.23 below 2.0
- **copy_trader**: only 2.0 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 41,698 · watching now: 255 · snapshots: 102,369
- Safety checks: 3,595 · passed: 170

Most common safety failures:
- too young (< 1h): 2834
- liquidity < $50k (or unknown): 2367
- LP not burned/locked (or unknown): 2101
- top-10 holders >= 30%: 1730
- selling our size loses > 10%: 1070
- no sell route found: 714
- too few sells in last hour: 310
- mint authority NOT revoked: 15
- freeze authority NOT revoked: 7
- sell tax 100 bps: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4400. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 69 trades so far.

## Signals by strategy
- momentum: {'filled': 102, 'rejected_safety': 2454}
- volume_breakout: {'filled': 30, 'rejected_safety': 1619}
- pullback: {'filled': 35, 'rejected_safety': 107}
- founder_screen: {'filled': 64, 'rejected_safety': 772}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
