CREATE OR REPLACE VIEW analysis_panel AS
SELECT
    *,
    year - first_ai_year AS event_time,
    CASE WHEN first_ai_year IS NOT NULL AND year >= first_ai_year THEN 1 ELSE 0 END AS adopted,
    CASE WHEN year >= 2023 THEN 1 ELSE 0 END AS post_chatgpt,
    LN(1 + employee_count) AS log_employment,
    LN(1 + personnel_expense) AS log_personnel_expense
FROM firm_year;
