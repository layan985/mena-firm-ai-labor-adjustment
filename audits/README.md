# Independent Reproduction Handoff

## Current status

**Ready for an outside researcher; no independent reproduction has been claimed.**

This folder lets a non-author audit two different objects without relying on verbal instructions from the founder:

1. the public collection/provenance pipeline; and
2. the frozen 16-passage blinded AI coding sample.

An auditor may reproduce either module or both. Reproducing the pipeline does not validate the causal design, and coding the sample does not certify the employment panel.

## Auditor independence

The report must identify whether the auditor:

- contributed code, data, or labels to this release;
- has a financial, supervisory, or close personal relationship with the founder;
- received compensation for the audit; or
- saw founder labels before returning the blinded coding file.

An audit with a disclosed relationship can still be useful, but it must not be described as independent if independence is not credible.

## Module A — clean-room pipeline reproduction

Record the exact commit SHA before starting, then use a fresh clone and environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
python scripts/build_pilot_coverage.py
python scripts/validate_source_manifest.py
python scripts/report_pilot_conflicts.py
```

Compare the generated coverage summary with `data/interim/pilot_50_coverage_summary.json`. At the 13 August 2026 handoff baseline, the expected headline facts are 176/400 numeric employment firm-years, 38/50 firms with numeric employment, 168/176 numeric rows hash-bound, 224 unresolved firm-years, 66 AI-evidence firm-years across 35 firms, and zero employment conflicts.

Do not repair the repository before documenting a failure. Record it first in `discrepancies.csv`, then link any proposed fix.

## Module B — blinded second coding

1. Confirm that `data/validation/blinded_ai_validation_sample.csv` contains 16 rows and no founder label column.
2. Work offline from the founder's labels and assign a 0–3 `coder_label` to every row using `docs/AI_CODING_CODEBOOK_V0_2.md`.
3. Record confidence and notes. Preserve the `validation_id` values.
4. Save the completed file as `data/validation/coder_2.csv` only after coding is final.
5. Return the completed file before requesting or viewing the founder key.
6. Run:

```bash
python scripts/score_intercoder_agreement.py
```

The resulting `data/validation/agreement_results.json` should report the paired sample size, raw agreement, Cohen's kappa, quadratic-weighted kappa, and confusion matrix. Disagreements must remain visible through adjudication.

## Publishable audit artifacts

Return or publish:

- a completed `INDEPENDENT_REPRODUCTION_REPORT.md`;
- the completed `discrepancies.csv`;
- terminal logs or an environment manifest;
- `coder_2.csv` and `agreement_results.json` if Module B was performed; and
- any repair pull request, clearly separated from the initial audit result.

The Lab may use **independently reproduced** only after a non-author report identifies the exact commit, procedure, result, and discrepancies and is publicly accessible.
