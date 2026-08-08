-- Example transformation after a WBES frame has been registered as `wbes_raw`.
CREATE OR REPLACE TABLE wbes_clean AS
SELECT
    CAST(firm_id AS VARCHAR) AS firm_id,
    country,
    CAST(year AS INTEGER) AS year,
    NULLIF(l1, -9) AS employment_now,
    NULLIF(l2, -9) AS employment_3y_ago,
    NULLIF(l6, -9) AS temporary_workers,
    CASE WHEN l10 = 1 THEN 1 WHEN l10 = 2 THEN 0 ELSE NULL END AS training_any,
    innovation_text
FROM wbes_raw
WHERE l1 IS NULL OR l1 >= 0;
