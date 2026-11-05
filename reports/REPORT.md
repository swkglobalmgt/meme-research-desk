# Meme Coin Research Desk: paper results
_Generated 2026-11-05T14:25+00:00 UTC · 0.3 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 29 | 10 | 13 | 11 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 34.5% | 40.0% | 30.8% | 27.3% | – |
| Average win | $20.68 | $21.71 | $21.69 | $17.02 | – |
| Average loss | -$26.33 | -$34.73 | -$26.30 | -$21.94 | – |
| Net P&L after all costs | -$293.50 | -$121.53 | -$149.94 | -$124.43 | $0.00 |
| Average return per trade | -10.1% | -12.2% | -11.5% | -11.3% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -1.98 | -1.00 | -1.80 | -1.77 | – |
| Worst drawdown | -$293.50 | -$128.23 | -$189.57 | -$129.23 | $0.00 |
| Rugs / unsellable hit | 3 | 1 | 0 | 2 | 0 |
| Losses worse than -50% | 1 | 1 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.3 of 4 weeks of data; only 29 of 100 completed trades; net P&L after costs is $-293.50 (not positive); t-stat -1.98 below 2.0
- **volume_breakout**: only 0.3 of 4 weeks of data; only 10 of 100 completed trades; net P&L after costs is $-121.53 (not positive); t-stat -1.00 below 2.0
- **pullback**: only 0.3 of 4 weeks of data; only 13 of 100 completed trades; net P&L after costs is $-149.94 (not positive); t-stat -1.80 below 2.0
- **founder_screen**: only 0.3 of 4 weeks of data; only 11 of 100 completed trades; net P&L after costs is $-124.43 (not positive); t-stat -1.77 below 2.0
- **copy_trader**: only 0.3 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 11,724 · watching now: 524 · snapshots: 18,597
- Safety checks: 1,024 · passed: 50

Most common safety failures:
- too young (< 1h): 759
- liquidity < $50k (or unknown): 651
- LP not burned/locked (or unknown): 579
- top-10 holders >= 30%: 510
- selling our size loses > 10%: 313
- no sell route found: 245
- too few sells in last hour: 138
- mint authority NOT revoked: 6
- sell tax 100 bps: 4
- sell tax 500 bps: 2
- sell tax 300 bps: 1
- freeze authority NOT revoked: 1

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 1216. Median real cost of one sell: 2.7% vs our model 3.1%.
- Quote was worse than our model 50% of the time. When it was, that trade was charged the real (worse) cost: 17 trades so far.

## Signals by strategy
- momentum: {'filled': 29, 'rejected_safety': 705}
- volume_breakout: {'filled': 10, 'rejected_safety': 451}
- pullback: {'filled': 13, 'rejected_safety': 33}
- founder_screen: {'filled': 11, 'rejected_safety': 251}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
