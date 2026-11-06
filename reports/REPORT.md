# Meme Coin Research Desk: paper results
_Generated 2026-11-06T14:23+00:00 UTC · 0.4 weeks of trade data · PAPER ONLY_

| | momentum | volume_breakout | pullback | founder_screen | copy_trader |
|---|---|---|---|---|---|
| Completed trades | 39 | 11 | 14 | 13 | 0 |
| Open positions | 0 | 0 | 0 | 0 | 0 |
| Win rate | 33.3% | 36.4% | 35.7% | 30.8% | – |
| Average win | $19.38 | $21.71 | $21.89 | $12.87 | – |
| Average loss | -$26.67 | -$33.67 | -$26.30 | -$19.72 | – |
| Net P&L after all costs | -$441.44 | -$148.86 | -$127.25 | -$125.95 | $0.00 |
| Average return per trade | -11.3% | -13.5% | -9.1% | -9.7% | – |
| t-stat (need ≥ 2; shown from 10 trades) | -2.70 | -1.22 | -1.41 | -1.77 | – |
| Worst drawdown | -$463.93 | -$148.86 | -$189.57 | -$129.23 | $0.00 |
| Rugs / unsellable hit | 5 | 1 | 0 | 2 | 0 |
| Losses worse than -50% | 1 | 1 | 0 | 0 | 0 |
| Decision gate | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL | NOT YET / FAIL |

## Why the gate is not passed yet
- **momentum**: only 0.4 of 4 weeks of data; only 39 of 100 completed trades; net P&L after costs is $-441.44 (not positive); t-stat -2.70 below 2.0
- **volume_breakout**: only 0.4 of 4 weeks of data; only 11 of 100 completed trades; net P&L after costs is $-148.86 (not positive); t-stat -1.22 below 2.0
- **pullback**: only 0.4 of 4 weeks of data; only 14 of 100 completed trades; net P&L after costs is $-127.25 (not positive); t-stat -1.41 below 2.0
- **founder_screen**: only 0.4 of 4 weeks of data; only 13 of 100 completed trades; net P&L after costs is $-125.95 (not positive); t-stat -1.77 below 2.0
- **copy_trader**: only 0.4 of 4 weeks of data; only 0 of 100 completed trades; net P&L after costs is $0.00 (not positive); too few trades for a meaningful t-stat

## Data funnel
- Pools seen: 15,703 · watching now: 527 · snapshots: 29,865
- Safety checks: 1,355 · passed: 59

Most common safety failures:
- too young (< 1h): 1021
- liquidity < $50k (or unknown): 894
- LP not burned/locked (or unknown): 778
- top-10 holders >= 30%: 689
- selling our size loses > 10%: 432
- no sell route found: 303
- too few sells in last hour: 180
- mint authority NOT revoked: 7
- sell tax 100 bps: 4
- sell tax 500 bps: 2
- sell tax 300 bps: 1
- freeze authority NOT revoked: 1

## Cost check (are our cost assumptions honest?)
- Real Jupiter sell quotes collected: 1656. Median real cost of one sell: 2.9% vs our model 3.1%.
- Quote was worse than our model 50% of the time. When it was, that trade was charged the real (worse) cost: 21 trades so far.

## Signals by strategy
- momentum: {'filled': 39, 'rejected_safety': 928}
- volume_breakout: {'filled': 11, 'rejected_safety': 615}
- pullback: {'filled': 14, 'rejected_safety': 39}
- founder_screen: {'filled': 13, 'rejected_safety': 344}
- copy_trader: none yet

## Copy-trading fomo traders
- Not screened yet (needs the DUNE_API_KEY secret).

_Note: with several strategies tested at once, one can pass t ≥ 2 by luck. Treat a pass below t ≈ 2.5 with extra suspicion._
