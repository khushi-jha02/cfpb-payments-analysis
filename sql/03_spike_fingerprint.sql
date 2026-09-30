-- =====================================================================
-- 03_spike_fingerprint.sql
-- Goal: decide whether the Jan 2025 spike is "normal" customer friction
--       or an event-driven wave, by comparing its fingerprint month by
--       month against normal months.
-- Run:  duckdb cfpb.duckdb   then   .read sql/03_spike_fingerprint.sql
-- Needs: 02_scope_and_spike.sql has been run (creates "p2p")
-- =====================================================================

-- For each month we calculate 3 percentages:
--   pct_other_txn_problem : share filed under the vague issue
--                           "Other transaction problem"
--   pct_cashapp_or_zelle  : share filed against Block or Early Warning
--   pct_closed_explained  : share the company closed with only an
--                           explanation (no money back, no fix)
-- Pattern: 100.0 * (count of matching rows) / (all rows in that month)
-- We write 100.0 (not 100) so SQL does decimal math, not whole numbers.
-- ROUND(x, 1) keeps one decimal place.
SELECT
    strftime(date_received, '%Y-%m') AS month,
    COUNT(*)                         AS complaints,
    ROUND(100.0 * SUM(CASE WHEN issue = 'Other transaction problem'
                           THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_other_txn_problem,
    ROUND(100.0 * SUM(CASE WHEN company IN ('Block, Inc.', 'Early Warning Services, LLC')
                           THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_cashapp_or_zelle,
    ROUND(100.0 * SUM(CASE WHEN company_response = 'Closed with explanation'
                           THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_closed_explained
FROM p2p
WHERE date_received >= '2024-07-01'
GROUP BY month
ORDER BY month;
