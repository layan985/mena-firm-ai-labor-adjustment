# MENA firm AI adoption and labor adjustment

Annual reports often say a company is “using AI” long before they identify an operational deployment. The same reports can switch between group employees, domestic employees, contractors, full-time employees, and employee-benefit populations without making the change obvious. Those measurement problems have to be resolved before an event-study coefficient means anything.

This repository builds a 50-firm × 2018–2025 panel while keeping AI evidence, employment definitions, source documents, reporting perimeter, and corrections auditable.

## Current status

**v0.2.0a2 is the audited collection/provenance alpha.** The 50-firm frame, validation/freeze machinery, blinded coding workflow, OECD/GDELT extension, and incremental immutable source-binding workflow are integrated on `main`. The empirical panel is **not yet frozen for causal estimation** because collection and an independent second-human coding gate remain unfinished.

As of 13 August 2026, from `data/interim/pilot_50_coverage_summary.json` and the committed validation files:

| Item | Current state |
| --- | --- |
| Target frame | 50 firms × 2018–2025 = 400 firm-years |
| Numeric employment evidence | 176/400 firm-years |
| Firms with numeric employment | 38/50 |
| Exact numeric employment observations | 126 |
| Rounded numeric employment observations | 26 |
| Numeric observations carrying a scope/comparability warning | 24 |
| Employment observations with SHA-256 source bindings | 168/176 |
| Employment conflicts | 0 |
| AI evidence coverage | 66 firm-years across 35/50 firms |
| Unique labeled AI passages | 75 |
| Blinded second-coder sample | 16 passages (21.3%) drawn and frozen |
| Unresolved firm-years | 224 |
| Preferred causal estimates | Not inspected |
| Independent second-human coding | Pending |

The current collection contains primary-source series for firms including Almarai, Air Arabia, Qatar Islamic Bank, Dubai Financial Market, Tabreed, and Milaha. Where issuers publish rounded totals or change workforce terminology, those limitations stay explicit in the row metadata.

Eight numeric employment rows remain hash-pending. Issuer access failures and missing disclosures remain unresolved rather than being replaced with secondary estimates.

## Provenance behavior

The collection workflow now separates two operations that should not be conflated:

- **full source refresh**, used deliberately when a historical source must be re-fetched or audited;
- **incremental immutable binding**, used during normal collection to download only sources needed by new/unbound rows.

An existing research-row hash is never silently replaced by whatever bytes a dynamic issuer URL happens to serve later. If a pre-existing immutable hash must be registered in the manifest, the downloader must reproduce those exact bytes or fail. A dead or changed legacy URL therefore cannot rewrite historical evidence or block unrelated new sources from being bound.

## Large-data extension

The alpha also includes a separate scalable exposure/narrative pipeline:

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
- **Almarai:** the 2020 comparable series uses the retrospective GCC + USA + Argentina workforce definition; the broader 41,222 annual-report total is not spliced into that narrower series.
- **Banque Saudi Fransi:** lower Bank-entity figures are kept separate from the comparable Group series; the 2023 one-person retrospective restatement is preserved rather than silently overwritten.
- **QNB:** ESG workforce figures with a different reporting perimeter are stored separately from rounded global workforce disclosures.
- **Milaha:** 2018–2025 annual governance disclosures are retained as explicitly approximate; 2018–2020 carry a perimeter warning because those editions do not explicitly say “including crew and divers,” while 2021 onward do.
- **Tabreed:** 2021–2022 “Total Employees” observations are kept separate from the explicit 2023–2025 ESG S2.1 full-time definition and carry a comparability warning. Contractor/consultant populations are not added to either series.

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
- `data/pilot/source_archive_manifest.csv`: source-object bindings and SHA-256 provenance;
- `data/interim/pilot_50_coverage_summary.json`: machine-generated current coverage counts;
- `docs/PILOT_50_COLLECTION_PROTOCOL.md`: collection rules;
- `docs/AI_CODING_CODEBOOK_V0_2.md`: 0–3 AI substantiveness rubric;
- `scripts/build_pilot_coverage.py`: machine-audited coverage report;
- `scripts/archive_pilot_sources.py`: explicit full source archival/refresh;
- `scripts/archive_pending_sources.py`: incremental immutable binder for new evidence;
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

The repository CI covers Python tests/pipeline checks, the 50-firm coverage/source audits, R syntax validation and the LaTeX paper build. Employment-source collection additionally runs the incremental immutable binder before refreshing the committed coverage summary.

An outside researcher can use [`audits/README.md`](audits/README.md) as a clean-room handoff. The Lab does not use the label **independently reproduced** until a non-author publishes a completed report and discrepancy log.

## Freeze rule

The engineering/data alpha can be released while the empirical study remains gated. A preferred causal coefficient is not released until the 50 × 2018–2025 frame has an attempted headcount status for every firm-year, provenance failures are resolved or explicitly classified, the AI search is complete, and the blinded second-human coding exercise has been completed and scored.

Missing evidence is never replaced with zero, a guessed adoption date, a commercial headcount estimate, or an AI-generated second-coder label.

The fixed flagship release contract is in [`docs/FLAGSHIP_RELEASE_GATE.md`](docs/FLAGSHIP_RELEASE_GATE.md). No expansion beyond the 50-firm frame is in scope before that gate closes and a citable release is archived.
