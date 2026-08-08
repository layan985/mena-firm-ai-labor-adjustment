# MENA Firm-Level AI Adoption and Labor-Market Adjustment

> A research-grade, end-to-end empirical repository for measuring substantive AI adoption at the firm level and estimating labor-market adjustment in the Middle East and North Africa.

**Status:** research scaffold / data-acquisition stage. The repository is designed so raw licensed or registration-gated files are never committed. Synthetic fixtures are included for CI and pipeline testing.

**Real-data audit seed:** the repo now includes nine verified public firm-year workforce rows across Aramco, stc, and Almarai plus seven manually reviewed AI-evidence records. These are explicitly non-inferential and exist to test provenance, treatment timing, reporting-scope consistency, and structural-break flags before the 50-firm pilot is scaled.

## Why this project exists

A January 2026 World Bank paper, *AI Adoption in MENAAP: Evidence from Enterprise Surveys*, showed that open-ended World Bank Enterprise Survey (WBES) innovation responses can be mined to identify AI adoption. It covers 7,016 firms across 11 MENAAP economies and explicitly identifies linking adoption to employment dynamics as a next research step. Its MENAAP sample contains very few high-confidence AI adopters, however, so this repository does **not** treat a MENA-only WBES regression as a credible causal backbone.

Instead, the project has two linked empirical layers:

1. **Measurement / external-validity layer — WBES.** Reproduce and extend transparent AI-adoption classification on firm survey text; measure employment, skill composition, temporary work and training outcomes; validate coding choices.
2. **Main panel layer — listed MENA firms.** Build a 2018–2025 firm-year panel from annual reports and exchange filings, identify the first year of *substantive* AI deployment, extract employment outcomes, and estimate dynamic adjustment with modern DiD/event-study methods.

This makes the project simultaneously an economics paper, a data-engineering project, an NLP measurement project, and a reproducible research object.

## Research questions

1. When MENA firms move from generic AI discussion to substantive operational deployment, what happens to total headcount?
2. Is adjustment concentrated in non-production/administrative labor, temporary labor, skilled labor, training, or personnel expense?
3. Are effects heterogeneous by firm size, sector, digital readiness, country income, female employment share, and pre-period labor intensity?
4. Does greater pre-2022 exposure to generative-AI-susceptible tasks predict stronger post-ChatGPT adoption and labor adjustment?
5. Do observed changes look like labor displacement, labor augmentation, or organizational re-composition?

## Identification hierarchy

The repo deliberately separates **causal**, **quasi-causal**, and **descriptive** evidence.

### A. Main exposure DiD

Estimate differential post-30-Nov-2022 changes for firms with higher **pre-determined AI/task exposure** measured using information available before the shock.

\[
Y_{it}=\alpha_i+\lambda_{ct}+\theta_s t+\sum_{k\neq -1}\beta_k\left(Exposure_i\times 1[t-T_0=k]\right)+\varepsilon_{it}
\]

- firm fixed effects: `firm_id`
- country × year fixed effects: `country^year`
- sector-specific trends or richer pre-trend controls
- event-time coefficients around the public release of ChatGPT
- standard errors clustered at the level implied by treatment variation, with few-cluster robustness where needed

This design estimates the effect of **differential exposure to the generative-AI shock**, not automatically the causal effect of voluntary firm adoption.

### B. Adoption event study

For firms with a defensible first substantive AI-adoption year, estimate a staggered event study using Sun–Abraham / Callaway–Sant'Anna style estimators. This is a powerful dynamic design, but adoption timing is endogenous; it is therefore presented as an adoption-linked event-time design unless identification diagnostics justify stronger language.

### C. WBES three-year-change design

WBES includes current employment (`l1`) and employment three fiscal years earlier (`l2`), plus skill, temporary-work and training variables. For firms reporting an AI-relevant product/process innovation during the same three-year window, estimate matched/doubly robust changes. This is supportive evidence, not the principal causal claim.

## Repository map

```text
.
├── .github/workflows/ci.yml
├── config/
│   ├── project.yml
│   └── data_sources.yml
├── data/
│   ├── README.md
│   ├── raw/.gitkeep
│   ├── interim/.gitkeep
│   ├── processed/.gitkeep
│   └── synthetic/wbes_fixture.csv
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── IDENTIFICATION.md
│   ├── NLP_LABELING_PROTOCOL.md
│   ├── PROVENANCE.md
│   ├── PREANALYSIS_PLAN.md
│   ├── DEVIATIONS.md
│   ├── REPRODUCIBILITY.md
│   └── ROADMAP.md
├── sql/
│   ├── 00_schema.sql
│   ├── 10_wbes_clean.sql
│   └── 20_firm_panel.sql
├── src/mena_ai_labor/
│   ├── __init__.py
│   ├── ai_classifier.py
│   ├── estimators.py
│   ├── ingest_wbes.py
│   ├── labor_outcomes.py
│   ├── panel.py
│   └── qa.py
├── scripts/
│   ├── build_synthetic.py
│   ├── run_python_pipeline.py
│   └── validate_data.py
├── analysis/
│   ├── 01_descriptives.R
│   ├── 02_exposure_event_study.R
│   ├── 03_adoption_event_study.R
│   ├── 04_wbes_change_models.R
│   └── 05_robustness.R
├── paper/
│   ├── main.tex
│   ├── references.bib
│   └── sections/*.tex
├── tests/
│   ├── test_ai_classifier.py
│   ├── test_estimators.py
│   └── test_labor_outcomes.py
├── .zenodo.json
├── CITATION.cff
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── Makefile
├── pyproject.toml
├── requirements.lock
└── renv.lock
```

## Data architecture

### World Bank Enterprise Surveys

Use WBES as a transparent benchmark and labor-outcome layer. Relevant variables include:

- `l1`: permanent full-time employees at end of last fiscal year
- `l2`: permanent full-time employees three fiscal years ago
- `l3a`, `l3b`: production / non-production workers
- `l4a1`, `l4a2`, `l4b`: skilled / semi-skilled / low-skilled production workers where available
- `l5`, `l5a`, `l5b`: female employment measures
- `l6`: temporary full-time workers
- `l10`–`l12a`: formal training measures
- open-ended product/process innovation descriptions: AI-adoption measurement candidates

Do not commit WBES microdata if its terms do not allow redistribution. Store local source files under `data/raw/wbes/`; the pipeline creates derived tables and a provenance manifest.

### Listed-firm panel

Target 2018–2025 annual reports / exchange filings for listed firms in selected MENA markets. Extract:

- firm identifier, country, exchange, ticker, sector, fiscal year
- annual report URL and SHA-256
- employee count
- personnel/staff expense
- production vs non-production headcount where disclosed
- female employment / nationalization metrics where disclosed
- training expenditure/hours where disclosed
- AI evidence sentence(s)
- AI substantiveness score
- AI functional category
- first substantive adoption year

Every extracted field must retain a source pointer (`report_url`, page, sentence/snippet hash) so a reviewer can audit it.

## AI measurement

The classifier is deliberately conservative.

- **0 — no AI evidence:** no relevant use.
- **1 — rhetoric / aspiration:** strategy language, generic “AI transformation,” no operational use.
- **2 — substantive deployment:** named AI/ML system used in a business function.
- **3 — core integration:** AI embedded in production/service delivery, risk systems, products, or material workflow redesign.

Primary treatment for adoption-event analyses: first year with score `>= 2`, subject to persistence and manual review.

The Python classifier in this starter repo is a high-precision rules engine intended for candidate generation. A research release should add a blinded human-labelled validation set and report precision/recall/F1 by language and market.

## Econometrics

Production estimates live in R. Core packages:

- `fixest` for high-dimensional FE and Sun–Abraham event studies
- `did` for Callaway–Sant'Anna group-time ATT
- `modelsummary` for publication tables
- `data.table` / `arrow` for large panel data
- `ggplot2` for figures

Never report a two-way-fixed-effects staggered-adoption coefficient as the main estimate without checking treatment-effect heterogeneity.

## Robustness battery

The planned robustness suite includes:

- pre-trend / lead diagnostics
- alternative AI dictionaries and substantiveness thresholds
- manual-label-only sample
- placebo treatment dates (2020/2021)
- leave-one-country-out and leave-one-sector-out estimates
- winsorized vs inverse-hyperbolic-sine vs log outcomes
- balanced-panel restrictions
- excluding firms with mergers, major restructurings, IPO year or known reporting discontinuities
- alternative clustering schemes and wild-cluster bootstrap when clusters are few
- negative-control outcomes unlikely to respond quickly to AI adoption
- attrition / disclosure-selection diagnostics
- sensitivity to anticipation windows
- matched / entropy-balanced comparisons for adoption-linked designs

## One-command workflow

```bash
make setup-python
make test
make synthetic
make pipeline
# after licensed/registration-gated data are placed locally:
make validate-data
make r-analysis
make paper
```

`make all` is intentionally not the default until raw-data access is configured; the project refuses to fake a completed empirical analysis when the underlying data are not present.

## Reproducibility standard

A release is not “done” until all of the following are true:

- raw-data provenance is recorded
- every transformation is scripted
- processed data are deterministic from permitted inputs
- tests pass locally and in GitHub Actions
- R scripts pass syntax parsing in CI and the paper compiles in CI
- tables/figures are regenerated from code
- paper compiles from LaTeX
- package versions are pinned
- a tagged GitHub release exists
- Zenodo archives the release and provides a DOI
- `CITATION.cff` and `.zenodo.json` match the release metadata

## Immediate build order

1. Obtain WBES access and place country files locally.
2. Reproduce high-precision AI candidate detection and manually label all MENA positives plus a stratified negative sample.
3. Expand the verified three-firm public audit seed into the first 50-firm annual-report panel end-to-end before scaling collection.
4. Freeze the schema after the pilot.
5. Scale across exchanges/years.
6. Estimate descriptive patterns first; do not look at preferred causal coefficients until treatment coding and outcome extraction are frozen.
7. Run the full event-study / robustness battery.
8. Draft paper, release v1.0.0, archive to Zenodo.

## Ethical / scientific rules

- No fabricated observations.
- No silently imputed adoption dates.
- No causal language from selection-on-observables alone.
- No committing restricted raw microdata.
- No LLM label is accepted as ground truth without human validation.
- Every manual correction is logged.

## Suggested citation

See `CITATION.cff`. Replace placeholder author identifiers before the first public release.
