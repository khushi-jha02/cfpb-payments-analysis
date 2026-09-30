-- =====================================================================
-- 06_export_results.sql
-- Goal: save the numbers behind each insight as CSV files in results/
--       so the charts (and anyone on GitHub) use exactly these numbers.
-- Run:  duckdb cfpb.duckdb   then   .read sql/06_export_results.sql
-- Needs: 02_scope_and_spike.sql and 04_top_issues.sql have been run.
-- COPY (query) TO 'file.csv' (HEADER) writes a query's result to a CSV.
-- =====================================================================

-- Chart 1: monthly complaints, Jan 2022 to Sep 2026 (shows the 2025 wave)
COPY (
    SELECT strftime(date_received, '%Y-%m') AS month,
           COUNT(*)                         AS complaints
    FROM p2p
    GROUP BY month
    ORDER BY month
) TO 'results/monthly_complaints.csv' (HEADER);

-- Chart 2: issues per month, 2024 vs 2026 YTD (Insights 1 and 2)
COPY (
    SELECT issue,
           ROUND(SUM(CASE WHEN period = '2024'     THEN 1 ELSE 0 END) / 12.0, 0) AS per_month_2024,
           ROUND(SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END) /  9.0, 0) AS per_month_2026,
           ROUND(100.0 * SUM(CASE WHEN period = '2026 YTD' THEN 1 ELSE 0 END)
                 / (SELECT COUNT(*) FROM p2p_compare WHERE period = '2026 YTD'), 1) AS share_2026
    FROM p2p_compare
    GROUP BY issue
    ORDER BY per_month_2026 DESC
) TO 'results/issues_2024_vs_2026.csv' (HEADER);

-- Chart 3: outcomes by app, 2026 YTD, closed complaints only (Insight 3)
COPY (
    SELECT
        CASE company
            WHEN 'Block, Inc.'                 THEN 'Cash App (Block)'
            WHEN 'Paypal Holdings, Inc'        THEN 'PayPal + Venmo'
            WHEN 'Early Warning Services, LLC' THEN 'Zelle network (EWS)'
            ELSE 'Banks & others'
        END                                                          AS app,
        COUNT(*)                                                     AS closed_complaints,
        SUM(CASE WHEN company_response = 'Closed with monetary relief'     THEN 1 ELSE 0 END) AS money_back,
        SUM(CASE WHEN company_response = 'Closed with non-monetary relief' THEN 1 ELSE 0 END) AS other_relief,
        ROUND(100.0 * SUM(CASE WHEN company_response = 'Closed with monetary relief'
                               THEN 1 ELSE 0 END) / COUNT(*), 1)      AS pct_money_back,
        ROUND(100.0 * SUM(CASE WHEN company_response IN ('Closed with monetary relief',
                                                         'Closed with non-monetary relief')
                               THEN 1 ELSE 0 END) / COUNT(*), 1)      AS pct_any_relief
    FROM p2p_compare
    WHERE period = '2026 YTD'
      AND company_response <> 'In progress'
    GROUP BY app
    ORDER BY closed_complaints DESC
) TO 'results/outcomes_by_app_2026.csv' (HEADER);

-- Show the Insight 3 table on screen too
SELECT * FROM read_csv('results/outcomes_by_app_2026.csv');
