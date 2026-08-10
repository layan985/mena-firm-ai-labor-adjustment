# 50-firm collection workspace

This directory contains the real public-source pilot collection, audit records, templates, and validation inputs for the 50-firm × 2018–2025 study.

## Current machine-audited collection

As of 10 August 2026:

- 400 target firm-years;
- 124 firm-years with numeric employment evidence across 27 firms;
- 276 unresolved firm-years;
- 62 AI-evidence firm-years across 31 firms;
- 71 unique labeled AI passages;
- a deterministic blinded second-coder sample of 15 passages;
- 103 unique source URLs archived and 182 research rows bound to exact source bytes;
- 113/124 numeric employment observations with archive/hash-complete source bindings.

These are collection metrics, not causal results.

## Files

- `public_seed_firm_year.csv` and `ai_evidence_seed.csv`: original small audit seed.
- `research_batch_*_employment.csv`: real employment collection batches.
- `research_batch_*_ai_evidence.csv`: real AI-evidence batches.
- `research_batch_*_measurement_audit.csv`: scope/comparability decisions.
- `research_batch_*_labor_cost.csv`: labor-cost evidence where collected.
- `source_archive_manifest.csv`: exact source-object provenance and hashes.
- `firm_year_template_50.csv` and `ai_evidence_template_50.csv`: schema templates for additional collection.
- `sampling_frame_batch01_20.csv`: the earlier 20-firm first-batch planning file; `metadata/firms_50.csv` is the canonical 50-firm frame.

## Missingness rule

For headcount and personnel expense, missingness must be explicit (`observed`, `not_disclosed`, `not_applicable`, or `not_collected`). A numeric value is permitted only with `observed`; numeric sentinel values are prohibited.

## Release gate

Collection-mode checks can pass while the panel remains unfinished. Freeze/release mode additionally requires the full 50-firm × eight-year grid to be attempted, provenance requirements to pass, unresolved conflicts to be classified, and the prespecified second-human AI coding exercise to be completed.

The source archive and validation workflow fail closed: block pages, false PDFs, conflicting hashes, and ambiguous reporting perimeters are preserved as problems rather than silently converted into usable observations.
