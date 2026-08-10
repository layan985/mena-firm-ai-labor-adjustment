# 50-firm pilot collection protocol

## Objective

Create the first auditable 2018–2025 listed-firm panel for the MENA AI × Labor project before any preferred outcome regressions are inspected.

The pilot target is **50 firms × 8 fiscal years = 400 firm-year rows**. The sample frame is defined before labor-outcome extraction and does not use AI language as an inclusion criterion.

## Locked pilot frame

The canonical sample frame is `metadata/firms_50.csv`.

- 20 Saudi Exchange firms
- 15 Dubai Financial Market firms
- 15 Qatar Stock Exchange firms
- 2018–2025 target window
- existing Aramco, stc and Almarai audit-seed firms retained

This is a documentation-validation pilot, not yet a claim to represent all listed MENA firms.

## Collection order

For every firm-year:

1. locate the annual report or exchange filing;
2. record source metadata before extracting outcomes;
3. store local filename and SHA-256 where redistribution is permitted;
4. extract employment using a like-for-like reporting scope;
5. record page/section locator;
6. extract candidate AI evidence independently of labor changes;
7. manually code the evidence using the frozen codebook;
8. flag mergers, divestitures, restatements or scope changes;
9. run QA;
10. only then admit the row to the frozen pilot.

## Minimum firm-year fields

Each target row must resolve, or be explicitly marked missing with a reason, for:

- `firm_id`
- `year`
- `employees`
- `employment_source_id`
- `employment_source_page`
- `employment_source_sha256`
- `reporting_scope`
- `ai_label`
- `ai_source_id`
- `ai_source_page`
- `ai_source_sha256`
- `ai_evidence_id`
- `source_retrieval_date`
- `scope_break_flag`
- `scope_break_reason`

Raw evidence and derived treatment variables must remain separate.

## AI validation

Before treatment freeze:

- manually review 100% of candidate positives;
- draw a deterministic stratified validation sample;
- double-code at least 20% of labeled passages;
- blind the second coder to firm identity, labor outcomes and first-coder labels;
- report raw agreement, Cohen's kappa and quadratic-weighted Cohen's kappa;
- resolve disagreements only after agreement statistics have been calculated on the pre-adjudication labels.

## Freeze gate

A freeze script must refuse to create a release if:

- the frame is not exactly 50 firms;
- the target skeleton is not exactly 400 firm-years;
- duplicate firm-years exist;
- required provenance fields are missing for non-missing observations;
- a source hash is malformed;
- AI labels fall outside the frozen codebook;
- treatment coding has not completed validation.

The freeze manifest should report counts, missingness, country/sector coverage, AI-label frequencies and SHA-256 hashes for all frozen research objects.

## Scientific rule

No preferred causal coefficient should be inspected before the pilot treatment coding and primary outcome extraction are frozen. Corrections after freeze must be versioned and logged rather than silently overwriting the frozen object.
