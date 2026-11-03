# Meme Coin Research Desk: paper results
_Generated 2026-11-03T14:22+00:00 UTC · 0.0 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 9 | 1 | 3 | 7 | 0 |
| Open positions | 1 | 1 | 0 | 0 | 0 |
| Win rate | 44.4% | 0.0% | 0.0% | 28.6% | – |
| Average win | $18.06 | – | – | $23.13 | – |
| Average loss | -$37.85 | -$30.62 | -$27.37 | -$27.30 | – |
| Net P&L after all costs | -$117.00 | -$30.62 | -$82.12 | -$90.22 | $0.00 |
| Average return per trade | -13.0% | -30.6% | -27.4% | -12.9% | – |
| t-stat (need ≥ 2) | -1.01 | – | -20.69 | -1.38 | – |
| Worst drawdown | -$146.37 | -$30.62 | -$82.12 | -$90.22 | $0.00 |
| Rugs / unsellable hit | 2 | 0 | 0 | 2 | 0 |
| Losses worse than -50% | 1 | 0 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.0 of 4 weeks of data; only 9 of 100 completed trades; net P&L after costs is $-117.00 (not positive); t-stat -1.01 below 2.0
- **volume_breakout**: only 0.0 of 4 weeks of data; only 1 of 100 completed trades; net P&L after costs is $-30.62 (not positive); t-stat n/a below 2.0
- **pullback**: only 0.0 of 4 weeks of data; only 3 of 100 completed trades; net P&L after costs is $-82.12 (not positive); t-stat -20.69 below 2.0
- **founder_screen**: only 0.0 of 4 weeks of data; only 7 of 100 completed trades; net P&L after costs is $-90.22 (not positive); t-stat -1.38 below 2.0
- **copy_trader**: only 0.0 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); t-stat n/a below 2.0

## Data funnel
- Pools seen: 3,027 · watching now: 239 · snapshots: 2,456
- Safety checks: 276 · passed: 18

Most common safety failures:
- too young (< 1h): 247
- LP not burned/locked (or unknown): 188
- liquidity < $50k (or unknown): 188
- top-10 holders >= 30%: 108
- no sell route found: 69
- selling our size loses > 10%: 65
- too few sells in last hour: 13
- mint authority NOT revoked: 1

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 306. Median real cost of one sell: -0.3% vs our model 3.0%.
- Quote was worse than our model 40% of the time. When it was, that trade was charged the real (worse) cost: 5 trades so far.

## Signals by strategy
- momentum: {'filled': 10, 'rejected_safety': 208}
- volume_breakout: {'filled': 2, 'rejected_safety': 123}
- pullback: {'filled': 3, 'rejected_safety': 2}
- founder_screen: {'filled': 7, 'rejected_safety': 59}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
