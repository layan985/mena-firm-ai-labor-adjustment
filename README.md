# MENA firm AI adoption and labor adjustment

Annual reports often say a company is “using AI” long before they identify an operational deployment. The same reports can switch between group employees, domestic employees, contractors, and employee-benefit populations without making the change obvious. Those measurement problems have to be resolved before an event-study coefficient means anything.

This repository builds a 50-firm × 2018–2025 panel while keeping AI evidence, employment definitions, source documents, reporting perimeter, and corrections auditable.

## Current status

**v0.2.0a1 is the completed engineering and data-collection alpha.** The 50-firm frame, source archive, validation/freeze machinery, blinded coding workflow, and large-data OECD/GDELT extension are integrated on `main` and CI-tested. The empirical panel is **not yet frozen for causal estimation** because real collection and an independent second-human coding gate remain unfinished.

As of 10 August 2026:

| Item | Current state |
| --- | --- |
| Target frame | 50 firms × 2018–2025 = 400 firm-years |
| Numeric employment evidence | 124/400 firm-years |
| Firms with numeric employment | 27/50 |
| Employment observations with archived SHA-256 source bindings | 113/124 |
| AI evidence coverage | 62 firm-years across 31/50 firms |
| Unique labeled AI passages | 71 |
| Blinded second-coder sample | 15 passages (21.1%) drawn and frozen |
| Archived source objects | 103 unique objects |
| Research rows bound to exact source bytes | 182 |
| Unresolved firm-years | 276 |
| Preferred causal estimates | Not inspected |
| Independent second-human coding | Pending |

Eleven numeric employment observations remain behind issuer access failures and are explicitly documented rather than treated as archive-complete observations.

## Large-data extension

The alpha also includes a separate scalable exposure/narrative pipeline rather than leaving it on an experimental branch:

- a versioned source manifest covering WBES, ILOSTAT, OECD AI exposure, GDELT and the ESCO/O*NET occupational crosswalk;
- an OECD occupation-level AI exposure downloader with retrieval metadata and SHA-256 hashing;
- machine-readable OECD workbook ingestion to CSV/Parquet plus an exposure audit and figure;
- bounded streaming of GDELT 2.x GKG files instead of loading an unbounded corpus into memory;
- reproducible audit scripts and a manually triggered bulk-data benchmark workflow;
- an empirical-design note that freezes pre-shock exposure weights and requires crosswalk diagnostics, pre-trend tests, placebo dates, clustering sensitivity and leave-one-country-out checks.

`docs/BULK_RUN.md` separates implemented ingestion capacity from data actually processed: no record count becomes a result or CV claim until the corresponding audit exists.

## Research question

The stronger design asks whether firms with greater **pre-2022 exposure** to generative-AI-susceptible tasks changed employment differently after 30 November 2022. A separate adoption event study describes what happens around a firm's first documented operational AI deployment.

These are not the same estimand. Adoption timing is chosen by the firm and may respond to demand, restructuring, management quality, labor costs, or other shocks.

## Measurement decisions already resolved

- **Aramco:** substantive AI language is visible by 2020, so the adoption date is left-censored rather than mechanically assigned to 2020.
- **stc:** the 2023–2024 headcount decline is flagged because a workforce right-sizing plan and possible reporting-perimeter changes overlap the change.
- **Almarai:** a broad “50,000+ workforce” headline is not spliced into the narrower GCC employee-benefit population; 2024 forward-looking AI language is planning, not treatment.
- **Banque Saudi Fransi:** lower Bank-entity figures are kept separate from the comparable Group series; the 2023 one-person retrospective restatement is preserved rather than silently overwritten.
- **QNB:** ESG workforce figures with a different reporting perimeter are stored separately from rounded global workforce disclosures.

The detailed record is in the audit logs, measurement files, and dated notes under `docs/`, `data/pilot/`, and `notes/`.

## Identification

The main exposure design is:

\[
Y_{it}=\alpha_i+\lambda_{ct}+\sum_{k\ne -1}\beta_k
\left(Exposure_i\times 1[t-T_0=k]\right)+\varepsilon_{it}.
\]

Firm adoption will be shown in event time only after disclosure coding is frozen. Modern staggered-DiD estimators address treatment-effect heterogeneity; they do not make voluntary adoption timing exogenous.

## Data and validation artifacts

The repository includes:

- `metadata/firms_50.csv`: the canonical pre-outcome 50-firm frame;
- `data/pilot/research_batch_*`: auditable employment, AI-evidence, labor-cost, and measurement-audit batches;
- `data/pilot/source_archive_manifest.csv`: exact source-object bindings and SHA-256 provenance;
- `docs/PILOT_50_COLLECTION_PROTOCOL.md`: collection rules;
- `docs/AI_CODING_CODEBOOK_V0_2.md`: 0–3 AI substantiveness rubric;
- `scripts/build_pilot_coverage.py`: machine-audited coverage report;
- `scripts/archive_pilot_sources.py`: content-addressed source archival;
- `scripts/build_ai_validation_input.py` and `scripts/draw_blinded_validation_sample.py`: blinded validation workflow;
- `scripts/score_intercoder_agreement.py`: prespecified agreement calculation;
- `scripts/freeze_pilot_50.py`: fail-closed empirical freeze gate;
- `src/mena_ai_labor/pilot50.py`: collection/release schema validation;
- `config/source_manifest_v0.2.csv`, `docs/BULK_RUN.md`, and `docs/EMPIRICAL_DESIGN_V0.2.md`: large-data extension contract.

Licensed or registration-gated source files are not redistributed when terms do not permit it.

## Run the checks

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/build_pilot_coverage.py
python scripts/validate_source_manifest.py
python scripts/report_pilot_conflicts.py
```

The integrated alpha passes the repository CI, including Python tests/pipeline checks, 50-firm coverage/source audits, R syntax validation and the LaTeX paper build.

## Freeze rule

The engineering alpha can be released while the empirical study remains gated. A preferred causal coefficient is not released until the 50 × 2018–2025 frame has an attempted headcount status for every firm-year, provenance failures are resolved or explicitly classified, the AI search is complete, and the blinded second-human coding exercise has been completed and scored.

Missing evidence is never replaced with zero, a guessed adoption date, or an AI-generated second-coder label.
