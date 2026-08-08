# Public-source audit seed

This directory contains a **small real-data audit seed**, not the final analysis dataset.

Purpose:

1. test provenance and comparability rules against actual corporate disclosures;
2. surface scope breaks before scaling collection;
3. test the AI substantiveness rubric on real language;
4. demonstrate that the pipeline can distinguish rhetoric, planned adoption, operational deployment, and core integration.

## Files

- `public_seed_firm_year.csv`: auditable workforce observations from public annual-report disclosures.
- `ai_evidence_seed.csv`: manually reviewed AI evidence with conservative 0–3 substantiveness scores.

## Non-negotiable cautions

- A disclosure in a later annual report may restate earlier years. Prefer the most recent comparable series when the reporting scope is explicit.
- Do not mix `stc Group`, `Saudi Arabian Oil Company`, `Almarai Group GCC employees`, and broader group-workforce headlines without a scope harmonization rule.
- The Aramco adoption date is **left-censored** because substantive AI language is already present in 2020; do not assign 2020 as the true first-adoption year until earlier reports are coded.
- stc's 2023–2024 headcount change is automatically flagged for structural-break review because the 2023 report announces a workforce right-sizing plan and the corporate perimeter changed around this period.
- These rows are for pipeline validation and qualitative audit. They are not a convenience sample for causal estimation.
