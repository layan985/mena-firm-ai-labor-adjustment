# Results

Last updated: 13 August 2026.

## What exists now

The project has a real 50-firm collection frame and a substantially populated audit panel, but **no preferred causal estimate has been inspected**.

Current machine-audited collection:

- 400 target firm-years;
- 176 numeric employment firm-years across 38/50 firms;
- 126 exact numeric employment observations, 26 explicitly rounded observations, and 24 observations carrying scope-break warnings;
- 168/176 numeric employment observations bound to archived source bytes and SHA-256 hashes;
- 66 AI-evidence firm-years across 35/50 firms;
- 75 unique labeled AI passages;
- 16 passages drawn deterministically for independent blinded second coding;
- 224 unresolved firm-years.

## Empirical hypotheses

| Hypothesis | Status | Reason |
| --- | --- | --- |
| Pre-2022 AI exposure changes post-2022 employment growth | Not tested | The 400-row outcome frame is not complete/frozen. |
| Employment changes around first operational AI adoption | Not tested | Adoption coding is not yet independently validated. |
| Adjustment is concentrated in particular worker groups | Not tested | Comparable composition outcomes are not collected at scale. |

There are no causal coefficients, event-study figures, or p-values to report yet.

## Measurement findings already established

The collection has identified several reproducible data problems that directly affect later estimation:

- Aramco's AI adoption timing is left-censored because substantive AI activity is already visible in 2020.
- stc's 2023–2024 workforce change coincides with right-sizing language and requires reporting-perimeter review.
- Almarai's broad workforce headline and GCC employee-benefit population are not interchangeable series.
- Banque Saudi Fransi discloses distinct Bank-entity and Group workforce measures; the comparable Group series is preserved separately.
- QNB disclosures include workforce series with different perimeters; they are not spliced automatically.

These are measurement results, not evidence that AI raised or reduced employment.

## Remaining freeze gates

The preferred analysis remains blocked until the 224 unresolved firm-years are attempted/classified, the remaining archive-access failures are resolved or formally documented, the AI search is complete, and a non-author human finishes the frozen blinded coding sample so agreement statistics can be reported.

The current counts are machine-generated collection facts, not causal results. See `docs/FLAGSHIP_RELEASE_GATE.md` for the fixed pilot-release contract and `audits/README.md` for the external reproduction protocol.
