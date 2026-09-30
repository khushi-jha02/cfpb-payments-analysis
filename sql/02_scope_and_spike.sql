-- =====================================================================
-- 02_scope_and_spike.sql
-- Goal: (a) keep only the complaints in our P2P & wallet scope
--       (b) investigate the 2025 spike before trusting any trend
-- Run:  duckdb cfpb.duckdb   then   .read sql/02_scope_and_spike.sql
-- Needs: 01_load_and_check.sql has been run (creates "complaints")
-- =====================================================================

-- STEP 1: Build our scoped table.
-- WHERE ... IN (...) keeps rows whose sub_product matches either value.
-- We drop crypto, international transfers, money orders, etc.
CREATE OR REPLACE TABLE p2p AS
SELECT *
FROM complaints
WHERE sub_product IN ('Domestic (US) money transfer',
                      'Mobile or digital wallet');

-- CHECK: how many complaints are in scope, per year?
SELECT
    YEAR(date_received) AS year,
    COUNT(*)            AS complaints
FROM p2p
GROUP BY year
ORDER BY year;

-- STEP 2: Zoom in on the spike month by month (Oct 2024 to Jun 2025).
-- strftime(date, '%Y-%m') turns a date like 2025-01-17 into '2025-01'.
SELECT
    strftime(date_received, '%Y-%m') AS month,
    COUNT(*)                         AS complaints
FROM p2p
WHERE date_received BETWEEN '2024-10-01' AND '2025-06-30'
GROUP BY month
ORDER BY month;

-- STEP 3: Which days were the biggest, and which companies drove them?
-- SUM(CASE WHEN ... THEN 1 ELSE 0 END) counts only the rows that match
-- the condition. It's the standard SQL way to count "sub-groups".
-- LIMIT 10 keeps only the top 10 rows after sorting.
SELECT
    date_received                                                     AS day,
    COUNT(*)                                                          AS complaints,
    SUM(CASE WHEN company = 'Block, Inc.'                 THEN 1 ELSE 0 END) AS cash_app_block,
    SUM(CASE WHEN company = 'Early Warning Services, LLC' THEN 1 ELSE 0 END) AS zelle_ews,
    SUM(CASE WHEN company = 'Paypal Holdings, Inc'        THEN 1 ELSE 0 END) AS paypal_venmo
FROM p2p
GROUP BY day
ORDER BY complaints DESC
LIMIT 10;
