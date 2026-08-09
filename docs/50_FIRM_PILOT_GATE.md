# 50-Firm Pilot Release Gate

## Objective

Move the project from a small real-data audit seed to a reproducible 50-firm pilot suitable for external methodological review before scaling to the full panel.

## Pilot contract

Target: **50 listed MENA firms × fiscal years 2018–2025**.

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
- `employee_count_page`
- `personnel_expense`
- `personnel_expense_page`
- `ai_evidence_text`
- `ai_evidence_page`
- `ai_evidence_hash`
- `ai_substantiveness_score`
- `ai_functional_category`
- `first_substantive_adoption_year`
- `reporting_scope_flag`
- `merger_restructuring_flag`
- `notes`

## Release gates

The 50-firm pilot is not complete until all of the following hold:

- [ ] 50 unique firms are represented.
- [ ] 2018–2025 coverage is attempted for every firm.
- [ ] Every non-missing employment observation has a report URL and page pointer.
- [ ] Every AI treatment record has a source page and evidence hash.
- [ ] Annual-report files used for extraction have SHA-256 provenance recorded.
- [ ] Missing values are distinguished from true zeroes.
- [ ] Reporting-scope changes and known mergers/restructurings are flagged.
- [ ] AI evidence scored >=2 is manually reviewed.
- [ ] A blinded validation sample is frozen for second-coder review.
- [ ] Validation scripts pass in CI.
- [ ] A machine-readable pilot manifest is generated.
- [ ] A short pilot memo reports coverage, missingness, treatment prevalence, and known limitations.

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

## Stop rule

Do **not** scale to 150 firms merely because 50 names have been entered. Scale only after provenance, treatment coding, reporting-scope consistency, and the second-coder procedure have survived review on the 50-firm pilot.
