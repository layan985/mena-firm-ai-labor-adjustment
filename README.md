# MENA firm AI adoption and labor adjustment

Annual reports often say a company is “using AI” long before they identify an operational deployment. The same reports can switch between group employees, domestic employees, contractors, and employee-benefit populations without making the change obvious. Those measurement problems have to be resolved before an event-study coefficient means anything.

This repository is my attempt to build a firm-year panel that keeps the AI evidence, employment definition, source page, and reporting perimeter visible.

## Current status

As of 10 August 2026, this is a data-collection project, not a completed empirical paper.

| Item | Current state |
| --- | --- |
| Sampling frame | 20 named firms reviewed for the first collection batch |
| Employment seed | 9 firm-year observations across Aramco, stc, and Almarai |
| AI evidence seed | 7 manually reviewed excerpts |
| 50-firm panel | Not complete; collection templates are still empty |
| Causal estimates | None |
| Human intercoder validation | Not started |
| Frozen analysis plan | Not yet frozen |

The public seed exists to find coding problems before collection scales. It is too small and too selected for inference.

## Question

The main question is whether firms with greater pre-2022 exposure to generative AI changed employment differently after 30 November 2022. A secondary, more descriptive question is what happened around a firm's first documented operational AI deployment.

These are not the same design. Adoption timing is chosen by the firm and may respond to the same shocks that affect employment.

## Decisions from the first three firms

- **Aramco:** substantive AI language is already present in 2020. The adoption date is left-censored, so 2020 is not coded as the first adoption year.
- **stc:** reported group headcount falls from 22,751 in 2023 to 19,863 in 2024, while the 2023 report also announces workforce right-sizing. The change is flagged until the corporate perimeter and reporting definition are reconciled.
- **Almarai:** a “50,000+ workforce” headline is not treated as interchangeable with the 46,997 GCC employee population used in the employee-benefit disclosure. Its 2024 discussion of future AI deployment is coded as planning, not treatment.

The full record of these choices is in [docs/PILOT_AUDIT_LOG.md](docs/PILOT_AUDIT_LOG.md). Dated notes explain the reasoning in less formal language:

- [notes/2026-08-10-employment-conflict.md](notes/2026-08-10-employment-conflict.md)
- [notes/2026-08-10-first-ai-labeling-problem.md](notes/2026-08-10-first-ai-labeling-problem.md)
- [notes/2026-08-10-identification-question.md](notes/2026-08-10-identification-question.md)

## Identification choice

The stronger design uses exposure measured before the public release of ChatGPT:

\[
Y_{it}=\alpha_i+\lambda_{ct}+\sum_{k\ne -1}\beta_k
\left(Exposure_i\times 1[t-T_0=k]\right)+\varepsilon_{it}.
\]

Firm adoption will be shown in event time only after the disclosure is manually checked. I do not interpret that graph as causal merely because it uses a modern staggered-DiD estimator. [docs/IDENTIFICATION.md](docs/IDENTIFICATION.md) records the distinction and the main threats to validity.

## Data files

- [data/pilot/public_seed_firm_year.csv](data/pilot/public_seed_firm_year.csv): nine employment observations used to test definitions and flags.
- [data/pilot/ai_evidence_seed.csv](data/pilot/ai_evidence_seed.csv): seven manually reviewed excerpts scored from rhetoric to operational integration.
- [data/pilot/sampling_frame_batch01_20.csv](data/pilot/sampling_frame_batch01_20.csv): first 20 firms selected for document collection.
- [data/pilot/README.md](data/pilot/README.md): missingness rules and requirements for the 50-firm pilot.

Licensed or registration-gated source files are not committed.

## Run the checks

```bash
python -m pip install -e ".[dev]"
pytest
python scripts/validate_public_seed.py
```

The R scripts under [analysis/](analysis/) are placeholders for the eventual descriptive and event-study work. Their existence is not evidence that the corresponding estimates have been run on a completed panel.

## Results and next work

[RESULTS.md](RESULTS.md) distinguishes pilot findings from untested hypotheses.

The next work is narrow:

1. collect the remaining documents for the first 20 firms;
2. reconcile employment definitions before adding more years;
3. label a blinded AI excerpt sample with a second human coder before freezing treatment rules.

No preferred causal estimate will be selected before those steps are complete.
