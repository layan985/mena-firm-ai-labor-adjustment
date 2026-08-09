# Portfolio case study — MENA Firm-Level AI Adoption and Labor Adjustment

> Building the missing firm-year dataset before claiming an employment effect.

[Portfolio](https://layan-research-portfolio.r8ms5bfzb6.chatgpt.site) · [Repository overview](../README.md)

## The empirical problem

Generic AI discussion is not the same as operational adoption, and treatment timing inferred from corporate language is potentially endogenous. The project therefore separates measurement, descriptive adoption timing and higher-bar causal designs.

The target is a provenance-traced 2018–2025 panel linking workforce outcomes to page-level evidence of substantive AI deployment in listed MENA firms.

## Current public evidence

- a real-data audit seed across Aramco, stc and Almarai;
- manually reviewed AI-evidence records;
- a verified first 20-firm acquisition sampling frame;
- reporting-scope and structural-break checks;
- machine-auditable source fields, missingness rules and release gates;
- synthetic fixtures for pipeline and CI testing.

These observations are explicitly **non-inferential**.

## Identification hierarchy

1. Predetermined exposure around the post-30-Nov-2022 shock for the primary causal design.
2. Adoption-timing event studies labeled as potentially endogenous.
3. Descriptive diffusion, heterogeneity and measurement analysis.

No preferred causal estimate is selected before the data and validation gates are frozen.

## Evidence ladder

| Gate | Status |
| --- | --- |
| Audited real-data seed | Completed |
| 20-firm acquisition frame | Completed |
| 50-firm pilot | In progress |
| Blinded treatment-label sample | Required |
| Second human coder | Required—AI cannot substitute |
| Intercoder agreement | Not yet calculated |
| Frozen analysis plan | After measurement validation |
| Estimation | After freeze |

## Next validation gate

Complete the 50-firm pilot with employment, AI evidence, exact source page and source hash; recruit a second human coder; calculate agreement; then freeze the analysis plan before estimation.
