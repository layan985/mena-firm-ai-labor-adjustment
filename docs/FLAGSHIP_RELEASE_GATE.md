# Flagship Release Gate — 50-Firm AI × Labor Panel

## Status

**In development — v0.2.0a2 collection/provenance alpha.**  
**Target:** a citable 50-firm pilot release; no preferred causal estimate is released before the empirical freeze gate closes.

This document freezes the flagship scope. The project will not add a 51st firm, a new headline estimand, or a second public observatory before the 50-firm research object is complete enough for external review.

## Fixed scope

- 50 listed MENA firms selected before outcome analysis
- fiscal years 2018–2025
- 400 firm-year collection obligations
- primary outcome: disclosed employment/headcount with explicit measurement scope
- treatment evidence: source-bound 0–3 AI substantiveness coding
- supporting artifacts: source manifest, immutable hashes, codebook, data dictionary, validation scripts, limitations, release manifest, and external reproduction report

## Machine-audited baseline — 13 August 2026

| Gate input | Current state |
| --- | ---: |
| Target firm-years | 400 |
| Numeric employment firm-years | 176 |
| Firms with any numeric employment | 38/50 |
| Exact / rounded / scope-warning observations | 126 / 26 / 24 |
| Numeric rows with SHA-256 source binding | 168/176 |
| Unresolved firm-years | 224 |
| AI-evidence firm-years | 66 across 35 firms |
| Unique labeled passages | 75 |
| Frozen blinded second-coder sample | 16 |
| Employment conflicts | 0 |
| Independent second-human coding | Pending |
| Preferred causal estimates | Not inspected |

The baseline must be regenerated from code. It is not a manually maintained marketing count.

## Release gates

### Coverage and measurement

- [ ] All 400 firm-years have an attempted and valid headcount status.
- [ ] No primary-outcome row remains `not_collected`.
- [ ] Numeric values preserve unit, reporting perimeter, page pointer, and comparability warnings.
- [ ] Missing disclosure remains missing; it is never imputed as zero.
- [ ] Known restructuring, merger, and scope breaks are documented.

### Provenance and rights

- [ ] Every redistributed numeric observation has a permitted source binding and SHA-256 hash.
- [ ] Every non-redistributed input has a deterministic acquisition record or rights-based omission note.
- [ ] All eight currently hash-pending numeric rows are bound or explicitly classified.
- [ ] The release manifest records file paths, byte sizes, and SHA-256 hashes.

### Treatment validation

- [x] Founder labels are removed from a deterministic blinded validation sample.
- [ ] A non-author human codes all 16 frozen passages without access to founder labels.
- [ ] Raw agreement, unweighted Cohen's kappa, and quadratic-weighted kappa are published.
- [ ] Original labels, coder-2 labels, discrepancies, and adjudication remain separately preserved.
- [ ] The AI-evidence search is complete or every gap is classified.

### Reproducibility and review

- [ ] Tests and pipeline checks pass from a clean environment.
- [ ] A non-author researcher completes `audits/INDEPENDENT_REPRODUCTION_REPORT.md`.
- [ ] All discrepancies are logged; none are silently deleted after repair.
- [ ] The final methodology, data dictionary, provenance note, and limitations match the released files.
- [ ] The public package reproduces all released tables and figures from one documented entry point.

### Versioning and citation

- [ ] `CHANGELOG.md` records the delta from v0.2.0a2.
- [ ] `CITATION.cff` matches the release title, authors, version, date, and repository URL.
- [ ] A signed or annotated GitHub release freezes the exact commit.
- [ ] The release is archived in a DOI-issuing repository such as Zenodo.
- [ ] The DOI resolves to the exact release, not the moving `main` branch.

## Permitted status labels

Before every box above closes, public descriptions may say:

- **v0.2.0a2 collection/provenance alpha**
- **50-firm pilot in development**
- **independent reproduction pending**
- **preferred causal estimates not inspected**

The labels **complete**, **independently reproduced**, **causal result**, and **citable flagship release** are not permitted yet.

## Stop rule

Two things take precedence over expansion: closing the 400-row attempt ledger and completing the non-author validation/audit. New firm frames, dashboards, or estimands remain frozen until this gate is satisfied or a documented scope decision replaces it.
