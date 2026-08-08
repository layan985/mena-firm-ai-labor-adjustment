# Contributing

This is a research repository. Contributions must preserve auditability.

- Never commit restricted or registration-gated raw microdata.
- Never add an AI adoption label without a source pointer and coding rationale.
- Never overwrite a manual correction silently; record it as a new auditable decision.
- Add or update tests when transformation logic changes.
- Keep causal claims aligned with the identification strategy in `docs/IDENTIFICATION.md`.
- Before opening a pull request, run `make test` and the synthetic fixture pipeline.

For empirical changes, the pull request should state whether the change alters the sample, treatment, outcome construction, estimator, inference, or a prespecified robustness check.
