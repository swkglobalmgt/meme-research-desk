# Meme Coin Research Desk: paper results
_Generated 2026-11-24T23:00+00:00 UTC · 3.0 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 112 | 33 | 37 | 88 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 38.4% | 33.3% | 43.2% | 33.0% | – |
| Average win | $20.09 | $17.58 | $19.11 | $16.00 | – |
| Average loss | -$26.87 | -$28.82 | -$25.23 | -$22.67 | – |
| Net P&L after all costs | -$990.05 | -$440.54 | -$224.07 | -$873.43 | $0.00 |
| Average return per trade | -8.8% | -13.3% | -6.1% | -9.9% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.63 | -2.55 | -1.61 | -4.58 | – |
| Worst drawdown | -$1,054.75 | -$440.54 | -$291.27 | -$873.43 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 9 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 3.0 of 4 weeks of data; net P&L after costs is $-990.05 (not positive); t-stat -3.63 below 2.0
- **volume_breakout**: only 3.0 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-440.54 (not positive); t-stat -2.55 below 2.0
- **pullback**: only 3.0 of 4 weeks of data; only 37 of 100 completed trades; net P&L after costs is $-224.07 (not positive); t-stat -1.61 below 2.0
- **founder_screen**: only 3.0 of 4 weeks of data; only 88 of 100 completed trades; net P&L after costs is $-873.43 (not positive); t-stat -4.58 below 2.0
- **copy_trader**: only 3.0 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 46,072 · watching now: 229 · snapshots: 102,391
- Safety checks: 4,065 · passed: 207

Most common safety failures:
- too young (< 1h): 3185
- liquidity < $50k (or unknown): 2684
- LP not burned/locked (or unknown): 2410
- top-10 holders >= 30%: 1928
- selling our size loses > 10%: 1155
- no sell route found: 872
- too few sells in last hour: 322
- mint authority NOT revoked: 15
- sell tax 100 bps: 10
- freeze authority NOT revoked: 7
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 300 bps: 4

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4802. Median real cost of one sell: 0.5% vs our model 3.0%.
- Quote was worse than our model 44% of the time. When it was, that trade was charged the real (worse) cost: 78 trades so far.

## Signals by strategy
- momentum: {'pending': 1, 'filled': 112, 'rejected_safety': 2709}
- volume_breakout: {'filled': 33, 'rejected_safety': 1808}
- pullback: {'pending': 1, 'filled': 37, 'rejected_safety': 111}
- founder_screen: {'filled': 88, 'rejected_safety': 843}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
