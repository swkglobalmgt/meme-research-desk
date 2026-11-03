-- Consistently profitable fomo traders, from public Solana data (DuneSQL / Trino).
--
-- How a fomo trade is recognised (same method DeFiLlama uses to count fomo volume):
--   * fomo pays the network fee for its users from a sponsor wallet (tx_signer), and
--   * every native fomo swap sends a USDC fee to fomo's fee wallet.
-- The wallet that pays that USDC fee is the fomo user.
--
-- Only REALIZED results count: a position is included only once the trader has
-- sold at least 90% of the tokens they bought inside the window. Paper gains on
-- coins still held are ignored on purpose.

WITH fee AS (
    SELECT DISTINCT tx_id, from_owner AS wallet
    FROM tokens_solana.transfers
    WHERE block_time >= now() - interval '{days}' day
      AND token_mint_address = 'EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr'
      AND to_owner = 'R4rNJHaffSUotNmqSKNEfDcJE8A7zJUkaoM5Jkd7cYX'
      AND tx_signer = 'AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51'
),
legs AS (
    SELECT t.tx_id, f.wallet, t.block_time, t.token_mint_address AS mint,
           CASE WHEN t.to_owner = f.wallet THEN CAST(t.amount AS DOUBLE)
                ELSE -CAST(t.amount AS DOUBLE) END AS amt
    FROM tokens_solana.transfers t
    JOIN fee f ON t.tx_id = f.tx_id
    WHERE t.block_time >= now() - interval '{days}' day
      AND (t.from_owner = f.wallet OR t.to_owner = f.wallet)
      AND NOT (t.from_owner = f.wallet AND t.to_owner = f.wallet)
),
per_tx AS (
    SELECT tx_id, wallet, MIN(block_time) AS block_time,
           SUM(CASE WHEN mint = 'EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr' THEN amt ELSE 0 END) / 1e6 AS usdc_delta,
           MAX(CASE WHEN mint NOT IN ('EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr',
                                      'So11111111111111111111111111111111111111112',
                                      'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB') THEN mint END) AS mint,
           SUM(CASE WHEN mint NOT IN ('EPjFWdd5AufqSSqeM2qFJmw5ZqeYuwPSURkdHnXDcqAr',
                                      'So11111111111111111111111111111111111111112',
                                      'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB') THEN amt ELSE 0 END) AS token_delta
    FROM legs
    GROUP BY tx_id, wallet
),
pos AS (
    SELECT wallet, mint,
           SUM(CASE WHEN token_delta > 0 THEN token_delta ELSE 0 END) AS bought,
           SUM(CASE WHEN token_delta < 0 THEN -token_delta ELSE 0 END) AS sold,
           SUM(CASE WHEN token_delta > 0 THEN -usdc_delta ELSE 0 END) AS cost_usd,
           SUM(usdc_delta) AS pnl_usd,
           MAX(block_time) AS closed_at
    FROM per_tx
    WHERE mint IS NOT NULL
    GROUP BY wallet, mint
),
closed AS (
    SELECT * FROM pos
    WHERE bought > 0 AND sold >= 0.9 * bought AND cost_usd > 0
),
weekly AS (
    SELECT wallet, date_trunc('week', closed_at) AS wk, SUM(pnl_usd) AS wk_pnl
    FROM closed GROUP BY 1, 2
),
weeks AS (
    SELECT wallet, COUNT_IF(wk_pnl > 0) AS positive_weeks, COUNT(*) AS active_weeks
    FROM weekly GROUP BY wallet
)
SELECT
    c.wallet,
    COUNT(*)                                                        AS closed_positions,
    SUM(c.pnl_usd)                                                  AS realized_pnl_usd,
    SUM(c.cost_usd)                                                 AS total_cost_usd,
    approx_percentile(c.cost_usd, 0.5)                              AS median_position_usd,
    AVG(CASE WHEN c.pnl_usd > 0 THEN 1.0 ELSE 0.0 END)              AS win_rate,
    MAX(c.pnl_usd) / NULLIF(SUM(CASE WHEN c.pnl_usd > 0 THEN c.pnl_usd END), 0) AS best_trade_share,
    SUM(CASE WHEN c.closed_at >= now() - interval '7' day THEN c.pnl_usd ELSE 0 END) AS pnl_7d,
    COUNT_IF(c.closed_at >= now() - interval '7' day)              AS closed_7d,
    MAX(w.positive_weeks)                                           AS positive_weeks,
    MAX(w.active_weeks)                                             AS active_weeks
FROM closed c
JOIN weeks w ON w.wallet = c.wallet
GROUP BY c.wallet
HAVING COUNT(*) >= {min_closed} AND SUM(c.pnl_usd) > 0
ORDER BY realized_pnl_usd DESC
LIMIT 500
