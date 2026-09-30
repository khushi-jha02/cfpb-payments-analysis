-- =====================================================================
-- 05_company_compare.sql
-- Goal: Insight 3 (how do the big apps compare?)
--   - What kinds of problems does each app get?
--   - How often does the complaint end with the customer getting
--     money back (monetary relief) or some other fix?
-- Run:  duckdb cfpb.duckdb   then   .read sql/05_company_compare.sql
-- Needs: 04_top_issues.sql has been run (creates view "p2p_compare")
-- Notes:
--   * Venmo is owned by PayPal, so CFPB files both under
--     "Paypal Holdings, Inc". We cannot split them.
--   * Early Warning Services runs the Zelle network, but the customer's
--     BANK usually decides refunds. Zelle complaints filed against banks
--     are inside "Banks & others".
--   * Resolution % excludes complaints still "In progress" (not closed
--     yet), so recent months don't look artificially better or worse.
-- =====================================================================

SELECT
    period,
    CASE company
        WHEN 'Block, Inc.'                 THEN 'Cash App (Block)'
        WHEN 'Paypal Holdings, Inc'        THEN 'PayPal + Venmo'
        WHEN 'Early Warning Services, LLC' THEN 'Zelle network (EWS)'
        ELSE 'Banks & others'
    END                                                             AS app,
    COUNT(*)                                                        AS complaints,
    ROUND(COUNT(*) / MAX(months_in_period), 0)                      AS per_month,

    -- what kind of problems (share of this app's complaints)
    ROUND(100.0 * SUM(CASE WHEN issue IN ('Fraud or scam',
                               'Unauthorized transactions or other transaction problem')
                           THEN 1 ELSE 0 END) / COUNT(*), 1)        AS pct_fraud_unauth,
    ROUND(100.0 * SUM(CASE WHEN issue IN ('Trouble accessing funds in your mobile or digital wallet',
                               'Managing, opening, or closing your mobile wallet account')
                           THEN 1 ELSE 0 END) / COUNT(*), 1)        AS pct_access_account,

    -- how complaints ended (share of CLOSED complaints only)
    SUM(CASE WHEN company_response <> 'In progress' THEN 1 ELSE 0 END) AS closed,
    ROUND(100.0 * SUM(CASE WHEN company_response = 'Closed with monetary relief'
                           THEN 1 ELSE 0 END)
          / SUM(CASE WHEN company_response <> 'In progress' THEN 1 ELSE 0 END), 1) AS pct_money_back,
    ROUND(100.0 * SUM(CASE WHEN company_response IN ('Closed with monetary relief',
                                                     'Closed with non-monetary relief')
                           THEN 1 ELSE 0 END)
          / SUM(CASE WHEN company_response <> 'In progress' THEN 1 ELSE 0 END), 1) AS pct_any_relief
FROM p2p_compare
GROUP BY period, app
ORDER BY period DESC, complaints DESC;
