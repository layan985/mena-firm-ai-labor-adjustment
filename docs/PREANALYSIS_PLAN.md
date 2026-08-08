# Pre-analysis plan

**Status:** draft to be frozen before inspecting preferred treatment-effect estimates.

The purpose of this document is to prevent the analysis from drifting toward whichever specification produces the most dramatic coefficient. Version-control the frozen plan and record any later deviations in a dated amendment.

## 1. Units and sample

Primary unit: listed firm × fiscal year, 2018–2025.

A firm enters the primary panel if it has at least two usable pre-shock fiscal years, a stable identifier, a defensible sector code, and auditable employment outcomes. The preferred balanced/unbalanced rule must be frozen after the 50-firm pilot and before estimation at scale.

WBES is a separate firm-survey layer and is not pooled mechanically with listed-firm observations.

## 2. Treatment objects

### Exposure

`pre_ai_exposure` is constructed only from information available before 30 November 2022. It must not use post-shock annual-report language or observed later adoption.

### Adoption

`first_ai_year` is the first fiscal year with manually validated substantiveness score >= 2. A score of 1 is rhetoric/aspiration and is not treated as operational adoption.

The exposure design is the primary quasi-experimental design. The adoption event study is secondary because voluntary adoption timing is selected.

## 3. Primary outcomes

1. `log_employment = log(1 + employees)`
2. personnel/staff expense, transformed consistently within currency-deflated country-year data
3. non-production/administrative employment share, where disclosed
4. skilled employment share, where disclosed

Secondary outcomes include female employment share, temporary employment, and training measures. Missing disclosure is not coded as zero.

## 4. Primary estimating equation

For outcome `Y_it`, estimate event-time interactions between predetermined firm exposure and event year around the 30 November 2022 generative-AI shock:

`Y_it = alpha_i + lambda_ct + sector-specific trends + sum_k beta_k Exposure_i * 1[event_time=k] + error_it`

Reference event year: -1. Report all available pre-period coefficients and a joint pre-trend test.

## 5. Inference

The default clustering level must follow treatment variation. Report robustness to plausible alternative clustering and use few-cluster procedures if the effective number of clusters is small. Never select the clustering scheme by p-value.

## 6. Adoption-event estimators

Use estimators robust to staggered treatment and heterogeneous effects (Sun–Abraham and Callaway–Sant'Anna). Never make vanilla staggered TWFE the sole or preferred adoption estimate.

## 7. Prespecified heterogeneity

- sector
- pre-period labor intensity
- firm size
- country income group / digital readiness
- pre-period female employment share where available

Heterogeneity results are secondary and multiplicity should be made visible rather than hidden.

## 8. Prespecified robustness

- placebo shock dates
- alternative AI thresholds and dictionaries
- manual-label-only treatment
- balanced-panel restriction
- leave-one-country-out
- leave-one-sector-out
- exclude M&A/restructuring/IPO discontinuities
- alternative outcome transforms
- anticipation windows
- negative-control outcomes
- disclosure/attrition diagnostics
- alternative clustering and few-cluster inference

## 9. Researcher degrees of freedom log

Any change made after preferred estimates are viewed must be entered in `docs/DEVIATIONS.md` with date, rationale, and whether it changes a primary result.
