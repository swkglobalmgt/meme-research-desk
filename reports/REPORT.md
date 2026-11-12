# Meme Coin Research Desk: paper results
_Generated 2026-11-12T20:49+00:00 UTC · 1.3 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 94 | 28 | 33 | 48 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 36.2% | 32.1% | 42.4% | 31.2% | – |
| Average win | $19.98 | $20.34 | $19.30 | $12.14 | – |
| Average loss | -$27.06 | -$31.27 | -$24.96 | -$22.09 | – |
| Net P&L after all costs | -$944.67 | -$411.11 | -$203.96 | -$546.82 | $0.00 |
| Average return per trade | -10.0% | -14.7% | -6.2% | -11.4% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -3.75 | -2.40 | -1.55 | -4.11 | – |
| Worst drawdown | -$971.43 | -$411.11 | -$291.27 | -$546.82 | $0.00 |
| Rugs / unsellable hit | 8 | 2 | 0 | 8 | 0 |
| Losses worse than -50% | 2 | 2 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 1.3 of 4 weeks of data; only 94 of 100 completed trades; net P&L after costs is $-944.67 (not positive); t-stat -3.75 below 2.0
- **volume_breakout**: only 1.3 of 4 weeks of data; only 28 of 100 completed trades; net P&L after costs is $-411.11 (not positive); t-stat -2.40 below 2.0
- **pullback**: only 1.3 of 4 weeks of data; only 33 of 100 completed trades; net P&L after costs is $-203.96 (not positive); t-stat -1.55 below 2.0
- **founder_screen**: only 1.3 of 4 weeks of data; only 48 of 100 completed trades; net P&L after costs is $-546.82 (not positive); t-stat -4.11 below 2.0
- **copy_trader**: only 1.3 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 37,925 · watching now: 457 · snapshots: 98,455
- Safety checks: 3,278 · passed: 148

Most common safety failures:
- too young (< 1h): 2619
- liquidity < $50k (or unknown): 2158
- LP not burned/locked (or unknown): 1928
- top-10 holders >= 30%: 1616
- selling our size loses > 10%: 994
- no sell route found: 658
- too few sells in last hour: 291
- mint authority NOT revoked: 14
- sell tax 100 bps: 6
- freeze authority NOT revoked: 6
- risky token extensions: ['transferHook', 'permanentDelegate']: 5
- sell tax 500 bps: 2

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 4057. Median real cost of one sell: 0.6% vs our model 3.0%.
- Quote was worse than our model 45% of the time. When it was, that trade was charged the real (worse) cost: 62 trades so far.

## Signals by strategy
- momentum: {'pending': 1, 'filled': 94, 'rejected_safety': 2273}
- volume_breakout: {'filled': 28, 'rejected_safety': 1501}
- pullback: {'filled': 33, 'rejected_safety': 96}
- founder_screen: {'filled': 48, 'rejected_safety': 710}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
