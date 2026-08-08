# Reproducibility

## Python

Python dependencies are pinned in `requirements.lock`; `pyproject.toml` defines the package. Before a tagged public release, regenerate a fully resolved lock in an internet-connected environment and commit it.

## R

`renv.lock` pins the principal analysis packages. Run `renv::restore()` and then `renv::snapshot()` in the target environment before the first tagged release so transitive dependency records are captured.

## Data

Restricted inputs remain local. Public releases should include either permitted derived data or a deterministic acquisition manifest and exact reproduction instructions.

## Determinism

- set seeds for all stochastic steps
- store classifier version
- hash input files
- do not overwrite manually adjudicated labels
- generate every table/figure from scripts
