-- =====================================================================
-- 01_load_and_check.sql
-- Goal: load the 3 CFPB CSV files into one DuckDB table and check that
--       the data is complete and clean before analyzing anything.
-- Data: CFPB Consumer Complaint Database, product =
--       "Money transfer, virtual currency, or money service",
--       2022-01-01 to 2026-09-30 (downloaded 2026-09-30)
-- Run:  duckdb cfpb.duckdb   then   .read sql/01_load_and_check.sql
-- =====================================================================

-- STEP 1: Create one table from all three CSV files.
-- read_csv('data/*.csv') reads every CSV in the data folder as one table.
-- nullstr = 'None' tells DuckDB that CFPB writes missing values as "None".
-- We rename columns to short snake_case names so they're easy to type.
-- CFPB timestamps are in UTC, so we convert to a date *in UTC*, which
-- keeps our yearly counts identical to the CFPB website's counts.
CREATE OR REPLACE TABLE complaints AS
SELECT
    "Complaint ID"                                  AS complaint_id,
    CAST(timezone('UTC', "Date received") AS DATE)  AS date_received,
    "Product"                                       AS product,
    "Sub-product"                                   AS sub_product,
    "Issue"                                         AS issue,
    "Company"                                       AS company,
    "State"                                         AS state,
    "Submitted via"                                 AS submitted_via,
    "Company response to consumer"                  AS company_response,
    "Timely response?"                              AS timely_response
FROM read_csv('data/*.csv', header = true, nullstr = 'None');

-- CHECK 1: How many rows, and is every complaint ID unique?
-- If unique_ids < total_rows, we downloaded some complaints twice.
SELECT
    COUNT(*)                     AS total_rows,
    COUNT(DISTINCT complaint_id) AS unique_ids
FROM complaints;

-- CHECK 2: Does the date range match what we asked for?
SELECT
    MIN(date_received) AS first_date,
    MAX(date_received) AS last_date
FROM complaints;

-- CHECK 3: How many complaints per year?
SELECT
    YEAR(date_received) AS year,
    COUNT(*)            AS complaints
FROM complaints
GROUP BY year
ORDER BY year;

-- CHECK 4: What sub-products are inside this product category?
-- (This tells us what to keep for our P2P & wallet scope in Query 02.)
SELECT
    sub_product,
    COUNT(*) AS complaints
FROM complaints
GROUP BY sub_product
ORDER BY complaints DESC;
