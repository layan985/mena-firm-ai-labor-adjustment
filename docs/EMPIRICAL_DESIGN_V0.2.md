# Empirical design — v0.2 large-data extension

## Primary estimand
The differential post-2022 change in labor outcomes for country-sector units with higher pre-period AI exposure.

## Treatment intensity
Construct sector exposure by mapping OECD O*NET-SOC exposure into ISCO-08 through an explicit crosswalk, then combining it with ILOSTAT `EMP_TEMP_ECO_OCU_NB` pre-period occupation shares within each country-sector. Freeze weights using only pre-shock data. Never use post-treatment occupational composition to define baseline exposure.

Crosswalk diagnostics are mandatory: weighted match coverage, one-to-many mappings, unmatched exposure mass, and sensitivity to equal-vs-employment-weighted crosswalk aggregation must be reported before estimation.

## Baseline event study
For country c, sector s, quarter t:

`y_cst = alpha_cs + gamma_ct + sum_{k != -1} beta_k Exposure_cs * 1[event_time=k] + epsilon_cst`

Suggested fixed effects:
- country × sector;
- country × quarter.

If the outcome or treatment construction makes this collinear, document the alternative rather than silently dropping fixed effects.

## Inference
Baseline: cluster by country-sector.
Required alternatives:
- cluster by country;
- two-way clustering when supported;
- wild-cluster bootstrap for small cluster counts;
- unweighted vs employment-weighted estimates.

## Diagnostics
- pre-trend joint test;
- event-study plot with confidence intervals;
- treatment-exposure balance in pre-period;
- leave-one-country-out coefficients;
- placebo shock dates;
- alternative exposure definitions;
- alternative event windows;
- alternative outcome transformations;
- missingness sensitivity.

## Firm analysis
Estimate descriptive/predictive relationships between AI adoption and:
- employment change;
- occupational change;
- training;
- productivity/sales where harmonized;
- digital technology baseline characteristics.

Do not call this causal without a valid design.

## Narrative analysis
Aggregate GDELT records to a consistent time-geography-sector grain. Pre-register dictionaries/classifiers used to label:
- AI adoption;
- automation;
- layoffs/job loss;
- hiring;
- productivity;
- regulation.

Use narratives as mechanisms or heterogeneity unless an independent identification strategy is justified.
