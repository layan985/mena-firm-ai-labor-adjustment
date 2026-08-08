# Identification strategy

## Principle

The repository must never collapse three distinct objects into one:

1. **AI exposure** — how strongly a firm's pre-existing tasks/business model are exposed to an external AI shock.
2. **AI adoption** — observed evidence that a firm actually deployed AI.
3. **Labor adjustment** — changes in employment levels or composition.

Voluntary adoption is selected. A clean event-study graph around adoption is not, by itself, proof that adoption caused the outcome.

## Design 1: exposure × post event study

Use a pre-2022 firm/sector exposure score and interact it with event time around 30 November 2022. The preferred model includes firm fixed effects and country-by-year fixed effects. Sector trends are added to absorb differential secular trajectories without mechanically absorbing a sector-level exposure-by-year treatment.

Pre-trend coefficients are part of the result, not decoration.

## Design 2: staggered adoption event study

Define first adoption as the first annual report with substantiveness score >= 2, after manual validation. Never-treated and not-yet-treated firms form controls where supported.

Use estimators robust to heterogeneous treatment effects. Report group-time ATT and an aggregated dynamic event study. Never use vanilla staggered TWFE as the sole specification.

## Design 3: WBES three-year employment change

WBES records current permanent full-time employment and employment three fiscal years earlier. Construct:

`employment_growth_log = log(1 + l1) - log(1 + l2)`

Compare AI-adoption candidates with carefully chosen controls, conditioning only on variables that are credibly pre-treatment or slow-moving. This design is vulnerable to endogenous adoption and imprecise treatment timing; it is supportive evidence.

## Inference

- cluster according to treatment variation, not convenience
- report sensitivity to alternative clusters
- use wild-cluster methods or randomization-style checks when cluster counts are small
- report simultaneous confidence bands for event-study paths when feasible

## Threats to validity

- selection into AI adoption
- strategic AI rhetoric in annual reports
- disclosure changes after adoption
- mergers and restructurings
- COVID-era labor dynamics
- oil-price / conflict / macro shocks
- differential reporting quality across exchanges
- post-treatment controls
- treatment anticipation
- staggered timing with heterogeneous effects

Every paper draft must include a table mapping each threat to a diagnostic or robustness test.
