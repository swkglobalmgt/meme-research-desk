# Meme Coin Research Desk: paper results
_Generated 2026-11-09T14:24+00:00 UTC · 0.9 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 72 | 20 | 29 | 33 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 34.7% | 35.0% | 34.5% | 33.3% | – |
| Average win | $19.84 | $22.13 | $20.17 | $10.45 | – |
| Average loss | -$27.56 | -$36.01 | -$24.96 | -$20.99 | – |
| Net P&L after all costs | -$799.31 | -$313.19 | -$272.47 | -$346.87 | $0.00 |
| Average return per trade | -11.1% | -15.7% | -9.4% | -10.5% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.52 | -1.90 | -2.25 | -3.22 | – |
| Worst drawdown | -$848.11 | -$313.19 | -$291.27 | -$370.46 | $0.00 |
| Rugs / unsellable hit | 7 | 2 | 0 | 5 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.9 of 4 weeks of data; only 72 of 100 completed trades; net P&L after costs is $-799.31 (not positive); t-stat -3.52 below 2.0
- **volume_breakout**: only 0.9 of 4 weeks of data; only 20 of 100 completed trades; net P&L after costs is $-313.19 (not positive); t-stat -1.90 below 2.0
- **pullback**: only 0.9 of 4 weeks of data; only 29 of 100 completed trades; net P&L after costs is $-272.47 (not positive); t-stat -2.25 below 2.0
- **founder_screen**: only 0.9 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-346.87 (not positive); t-stat -3.22 below 2.0
- **copy_trader**: only 0.9 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 30,164 · watching now: 902 · snapshots: 84,706
- Safety checks: 2,648 · passed: 113

Most common safety failures:
- too young (< 1h): 2136
- liquidity < $50k (or unknown): 1741
- LP not burned/locked (or unknown): 1566
- top-10 holders >= 30%: 1327
- selling our size loses > 10%: 833
- no sell route found: 537
- too few sells in last hour: 251
- mint authority NOT revoked: 12
- sell tax 100 bps: 5
- freeze authority NOT revoked: 4
- risky token extensions: ['transferHook', 'permanentDelegate']: 3
- sell tax 500 bps: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 3272. Median real cost of one sell: 0.8% vs our model 3.0%.
- Quote was worse than our model 46% of the time. When it was, that trade was charged the real (worse) cost: 50 trades so far.

## Signals by strategy
- momentum: {'filled': 72, 'rejected_safety': 1853}
- volume_breakout: {'filled': 20, 'rejected_safety': 1241}
- pullback: {'filled': 29, 'rejected_safety': 73}
- founder_screen: {'pending': 1, 'filled': 33, 'rejected_safety': 550}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
