-- =====================================================================
-- 04_top_issues.sql
-- Goal: Insight 1 (what breaks most?) and Insight 2 (what's growing?)
-- Method: compare two "clean" periods, 2024 vs Jan-Sep 2026. 2025 is
--         left out because of the event-driven complaint waves found in
--         03_spike_fingerprint.sql.
-- Run:  duckdb cfpb.duckdb   then   .read sql/04_top_issues.sql
-- Needs: 02_scope_and_spike.sql has been run (creates "p2p")
-- =====================================================================

-- STEP 1: A VIEW is a saved query that behaves like a table.
-- It stores no data, so it always reflects the current p2p table.
-- We label each complaint with its period and the number of months in
-- that period (2024 = 12 months, 2026 YTD = Jan-Sep = 9 months).
CREATE OR REPLACE VIEW p2p_compare AS
SELECT
    *,
    CASE WHEN YEAR(date_received) = 2024 THEN '2024'
         ELSE '2026 YTD' END                               AS period,
    CASE WHEN YEAR(date_received) = 2024 THEN 12 ELSE 9 END AS months_in_period
FROM p2p
WHERE YEAR(date_received) IN (2024, 2026);

-- RESULT A: Overall volume. Per-month makes 12 vs 9 months comparable.
SELECT
    period,
    COUNT(*)                                          AS complaints,
    MAX(months_in_period)                             AS months,
    ROUND(COUNT(*) / MAX(months_in_period), 0)        AS complaints_per_month
FROM p2p_compare
GROUP BY period
ORDER BY period;

-- RESULT B: Every issue, side by side for both periods.
-- share_*      = % of that period's complaints (uses a subquery in
--                parentheses to get the period's total)
-- per_month_*  = monthly average
-- growth_x     = 2026 per-month / 2024 per-month (2.0 = doubled)
SELECT
    issue,
    SUM(CASE WHEN period = '2024'     THEN 1 ELSE 0 END) AS n_2024,
    SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END) AS n_2026,
    ROUND(100.0 * SUM(CASE WHEN period = '2024' THEN 1 ELSE 0 END)
          / (SELECT COUNT(*) FROM p2p_compare WHERE period = '2024'), 1)     AS share_2024,
    ROUND(100.0 * SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END)
          / (SELECT COUNT(*) FROM p2p_compare WHERE period = '2026 YTD'), 1) AS share_2026,
    ROUND(SUM(CASE WHEN period = '2024'     THEN 1 ELSE 0 END) / 12.0, 0)    AS per_month_2024,
    ROUND(SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END) /  9.0, 0)    AS per_month_2026,
    ROUND( (SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END) / 9.0)
         / (SUM(CASE WHEN period = '2024'     THEN 1 ELSE 0 END) / 12.0), 1) AS growth_x
FROM p2p_compare
GROUP BY issue
ORDER BY n_2026 DESC;

-- RESULT C: Headline number. What share of complaints are about money
-- leaving an account without the customer's real consent?
-- (fraud/scams + unauthorized transactions combined)
SELECT
    period,
    COUNT(*) AS complaints,
    SUM(CASE WHEN issue IN ('Fraud or scam',
                            'Unauthorized transactions or other transaction problem')
             THEN 1 ELSE 0 END)                                              AS fraud_or_unauthorized,
    ROUND(100.0 * SUM(CASE WHEN issue IN ('Fraud or scam',
                            'Unauthorized transactions or other transaction problem')
             THEN 1 ELSE 0 END) / COUNT(*), 1)                               AS pct_fraud_or_unauthorized
FROM p2p_compare
GROUP BY period
ORDER BY period;
