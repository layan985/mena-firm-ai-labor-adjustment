# Public-source audit seed and 50-firm collection workspace

This directory contains a **small real-data audit seed plus empty collection templates**, not the final analysis dataset.

## Existing real-data seed

The seed exists to:

1. test provenance and comparability rules against actual corporate disclosures;
2. surface scope breaks before scaling collection;
3. test the AI substantiveness rubric on real language;
4. demonstrate that the pipeline can distinguish rhetoric, planned adoption, operational deployment, and core integration.

Files:

- `public_seed_firm_year.csv`: nine auditable workforce observations from public annual-report disclosures.
- `ai_evidence_seed.csv`: seven manually reviewed AI-evidence records with conservative 0–3 substantiveness scores.

These rows remain explicitly non-inferential.

## 50-firm pilot workspace

The 50-firm target is documented in `docs/50_FIRM_PILOT_GATE.md`.

Collection starts from:

- `firm_year_template_50.csv`
- `ai_evidence_template_50.csv`

The templates are intentionally empty. A row is added only when the firm/source has actually been reviewed; the repository does not pre-populate invented observations to make the pilot look larger than it is.

### Missingness rule

For headcount and personnel expense, use an explicit status:

- `observed`
- `not_disclosed`
- `not_applicable`
- `not_collected`

A numeric value is allowed only with `observed`. Never use 0, -99, or another numeric sentinel for missing information.

### Validation

`src/mena_ai_labor/pilot50.py` validates the working files during collection and applies stricter release gates when the pilot is ready for review.

Release mode requires:

- exactly 50 unique firms;
- one attempted row for each year 2018–2025 for every firm;
- no remaining `not_collected` headcount rows;
- source URL/page/hash provenance for observed outcomes;
- source/page/hash provenance for every AI evidence record;
- manual review for AI evidence scored 2 or 3.

Tests are in `tests/test_pilot50.py` and run under the repository CI test job.

## Non-negotiable cautions from the seed

- A disclosure in a later annual report may restate earlier years. Prefer the most recent comparable series when the reporting scope is explicit.
- Do not mix `stc Group`, `Saudi Arabian Oil Company`, `Almarai Group GCC employees`, and broader group-workforce headlines without a scope harmonization rule.
- The Aramco adoption date is **left-censored** because substantive AI language is already present in 2020; do not assign 2020 as the true first-adoption year until earlier reports are coded.
- stc's 2023–2024 headcount change is automatically flagged for structural-break review because the 2023 report announces a workforce right-sizing plan and the corporate perimeter changed around this period.
- Seed rows are for pipeline validation and qualitative audit. They are not a convenience sample for causal estimation.
