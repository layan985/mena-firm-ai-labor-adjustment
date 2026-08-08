# Data policy

This repository separates code from raw data.

## Do not commit

- registration-gated WBES microdata
- licensed firm databases
- downloaded annual reports if redistribution terms are unclear
- personally identifying data

## Local structure

Place source files under:

```text
data/raw/wbes/
data/raw/reports/<country>/<ticker>/<year>/
data/raw/exposure/
```

Every source file should be entered in `data/raw/source_manifest.csv` (created locally) with SHA-256, retrieval date, canonical URL, license/access note, and parser version.

CI uses only `data/synthetic/`.
