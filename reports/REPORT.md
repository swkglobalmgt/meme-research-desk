# Meme Coin Research Desk: paper results
_Generated 2026-11-10T14:20+00:00 UTC · 1.0 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 81 | 23 | 30 | 40 | 0 |
| Open positions | 0 | 2 | 0 | 0 | 0 |
| Win rate | 33.3% | 34.8% | 36.7% | 32.5% | – |
| Average win | $19.34 | $20.06 | $20.39 | $10.53 | – |
| Average loss | -$27.20 | -$34.48 | -$24.96 | -$21.58 | – |
| Net P&L after all costs | -$946.62 | -$356.69 | -$249.90 | -$445.66 | $0.00 |
| Average return per trade | -11.7% | -15.5% | -8.3% | -11.1% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -4.06 | -2.15 | -2.00 | -3.80 | – |
| Worst drawdown | -$946.62 | -$362.27 | -$291.27 | -$467.67 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 7 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.0 of 4 weeks of data; only 81 of 100 completed trades; net P&L after costs is $-946.62 (not positive); t-stat -4.06 below 2.0
- **volume_breakout**: only 1.0 of 4 weeks of data; only 23 of 100 completed trades; net P&L after costs is $-356.69 (not positive); t-stat -2.15 below 2.0
- **pullback**: only 1.0 of 4 weeks of data; only 30 of 100 completed trades; net P&L after costs is $-249.90 (not positive); t-stat -2.00 below 2.0
- **founder_screen**: only 1.0 of 4 weeks of data; only 40 of 100 completed trades; net P&L after costs is $-445.66 (not positive); t-stat -3.80 below 2.0
- **copy_trader**: only 1.0 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 34,048 · watching now: 350 · snapshots: 90,366
- Safety checks: 2,987 · passed: 127

Most common safety failures:
- too young (< 1h): 2425
- liquidity < $50k (or unknown): 1975
- LP not burned/locked (or unknown): 1781
- top-10 holders >= 30%: 1494
- selling our size loses > 10%: 910
- no sell route found: 603
- too few sells in last hour: 259
- mint authority NOT revoked: 12
- sell tax 100 bps: 5
- freeze authority NOT revoked: 4
- risky token extensions: ['transferHook', 'permanentDelegate']: 3
- sell tax 500 bps: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 3714. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 56 trades so far.

## Signals by strategy
- momentum: {'pending': 1, 'filled': 81, 'rejected_safety': 2089}
- volume_breakout: {'filled': 25, 'rejected_safety': 1398}
- pullback: {'filled': 30, 'rejected_safety': 78}
- founder_screen: {'filled': 40, 'rejected_safety': 644}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
