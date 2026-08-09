# 50-Firm Pilot Release Gate

## Objective

Move the project from a small real-data audit seed to a reproducible 50-firm pilot suitable for external methodological review before scaling to the full panel.

## Pilot contract

Target: **50 listed MENA firms × fiscal years 2018–2025**.

The pilot uses two linked tables rather than forcing evidence and outcomes into one row type.

### Firm-year collection table

For every firm-year, preserve or explicitly mark missing:

- `firm_id`
- `firm_name_canonical`
- `country`
- `exchange`
- `ticker`
- `sector`
- `fiscal_year`
- `report_url`
- `report_sha256`
- `employee_count`
- `employee_count_status`
- `employee_count_page`
- `personnel_expense`
- `personnel_expense_status`
- `personnel_expense_page`
- `reporting_scope_flag`
- `merger_restructuring_flag`
- `notes`

Allowed status values are:

- `observed`
- `not_disclosed`
- `not_applicable`
- `not_collected`

A numeric value is permitted only when its status is `observed`. This makes a genuine numeric zero distinguishable from missing, unavailable, or uncollected data.

### AI-evidence table

Each coded evidence record preserves:

- `firm_id`
- `firm_name_canonical`
- `fiscal_year`
- `ai_evidence_text`
- `ai_evidence_page`
- `ai_evidence_hash`
- `ai_substantiveness_score`
- `ai_functional_category`
- `manual_review`
- `first_substantive_adoption_year`
- `source_url`

## Release gates

The 50-firm pilot is not complete until all of the following hold:

- [ ] 50 unique firms are represented.
- [ ] 2018–2025 coverage is attempted for every firm.
- [ ] No release row remains `not_collected` for the primary headcount outcome.
- [ ] Every observed employment value has a report URL, SHA-256 hash, and page pointer.
- [ ] Every AI evidence record has a source URL, source page, and evidence hash.
- [ ] Annual-report files used for extraction have SHA-256 provenance recorded.
- [ ] Missing values are distinguished from true zeroes through explicit status fields.
- [ ] Reporting-scope changes and known mergers/restructurings are flagged.
- [ ] AI evidence scored >=2 is manually reviewed.
- [ ] A blinded validation sample is frozen for second-coder review.
- [ ] Validation scripts pass in CI.
- [ ] A machine-readable pilot manifest is generated.
- [ ] A short pilot memo reports coverage, missingness, treatment prevalence, and known limitations.

## Code-enforced checks

`src/mena_ai_labor/pilot50.py` implements two modes:

1. **Collection mode** validates schema and internal integrity while the pilot is incomplete.
2. **Release mode** additionally requires exactly 50 firms, one attempted row for every year 2018–2025 for every firm, and no unattempted headcount collection.

The validator deliberately does not convert blanks to zero and does not allow numeric sentinel values for missing observations.

## Second-coder validation

Before the primary treatment definition is frozen:

1. Randomly select at least 20% of candidate AI-evidence records, stratified by country/sector where feasible.
2. Remove the founder label from the validation packet.
3. Have a second human independently assign the 0–3 substantiveness score and functional category.
4. Report raw agreement and an appropriate chance-adjusted agreement statistic.
5. Resolve disagreements using a predeclared adjudication rule.
6. Preserve the original labels, second-coder labels, adjudicated labels, and timestamps.

## Output artifacts

The pilot release should produce:

- `data/processed/firm_year_panel_50.csv` (or a redistribution-safe derived equivalent)
- `data/processed/ai_evidence_50.csv`
- `data/processed/provenance_manifest_50.csv`
- `docs/PILOT_50_REPORT.md`
- `docs/INTERCODER_VALIDATION.md`
- an updated data dictionary
- reproducible validation command(s)

Working collection begins from:

- `data/pilot/firm_year_template_50.csv`
- `data/pilot/ai_evidence_template_50.csv`

## Stop rule

Do **not** scale to 150 firms merely because 50 names have been entered. Scale only after provenance, treatment coding, reporting-scope consistency, and the second-coder procedure have survived review on the 50-firm pilot.
