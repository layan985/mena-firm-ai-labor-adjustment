# Independent Reproduction Report — Template

## Record

- Auditor name:
- Affiliation, if any:
- ORCID or public profile, if any:
- Contact:
- Audit start/end dates:
- Repository URL:
- Commit SHA:
- Release/tag, if any:
- Modules audited: pipeline / blinded coding / both
- Compensation or relationship disclosure:

## Environment

- Operating system:
- Architecture:
- Python version:
- Installation command:
- Dependency manifest or environment file:
- Fresh clone and environment used: yes / no

## Procedure

Describe exactly what was run, any deviations from `audits/README.md`, and whether the founder provided help after the audit began.

## Pipeline results

| Check | Expected at audited commit | Observed | Pass / discrepancy / not run |
| --- | --- | --- | --- |
| Test suite | all tests pass |  |  |
| Target firm-years | 400 |  |  |
| Numeric employment firm-years | derive from committed summary |  |  |
| Firms with numeric employment | derive from committed summary |  |  |
| Numeric source hashes complete | derive from committed summary |  |  |
| Unresolved firm-years | derive from committed summary |  |  |
| Employment conflicts | 0 |  |  |
| Source-manifest validation | pass |  |  |

## Blinded coding results

- Founder labels hidden until return of coder file: yes / no / not applicable
- Frozen rows received:
- Rows completed:
- Raw agreement:
- Cohen's kappa:
- Quadratic-weighted kappa:
- Disagreements requiring adjudication:

## Discrepancies

Summarize every discrepancy and refer to its `record_id` in `discrepancies.csv`. A repaired discrepancy remains part of the report.

## Scope boundary

State what this audit does **not** establish. At minimum, distinguish computational reproduction from source accuracy, measurement validity, identification, causal interpretation, and external validity.

## Conclusion

Select one and explain:

- [ ] Reproduced exactly
- [ ] Reproduced with documented discrepancies
- [ ] Not reproduced
- [ ] Incomplete audit; no reproduction conclusion

## Auditor attestation

I confirm that this report identifies the exact code version and procedure I used, discloses relevant relationships, and preserves discrepancies rather than silently treating repaired output as the original result.

- Name:
- Date:
- Signature or verifiable public post, if used:
