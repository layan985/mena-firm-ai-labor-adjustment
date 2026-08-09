# Bulk-data execution runbook

This repository distinguishes **implemented ingestion code** from **data actually processed**. Never report a row count until `outputs/audits/data_audit.json` or the GDELT row audit contains it.

## 1. OECD occupation exposure

```bash
python scripts/04_fetch_oecd_exposure.py
python scripts/05_ingest_oecd_exposure.py
python scripts/06_plot_oecd_exposure.py
```

The parser reads the workbook's machine-readable `Data` sheet and uses `AI Capability Gap Index_Rev. norm.` as the 0–1 exposure measure. Higher values mean greater AI exposure, following the workbook codebook.

## 2. ILOSTAT labor outcomes

The production route is the official ILOSTAT bulk facility. Download annual/quarterly indicator files and preserve code dictionaries. The initial indicators are:

- `EMP_TEMP_SEX_ECO_NB` — employment by sex and economic activity;
- `EMP_TEMP_SEX_OCU_NB` — employment by sex and occupation;
- `SDG_0831_SEX_ECO_RT` — informal employment share by sex and economic activity.

Use `scripts/07_fetch_ilostat.py` where REST access is available, or download the corresponding `.csv.gz` files from the bulk facility and place them in the matching raw folders. Do not join on human-readable labels when coded classification fields are available.

## 3. GDELT high-volume stress run

`08_fetch_gdelt_gkg.py` reads the official GDELT 2.x master file list and streams selected GKG ZIP files to disk. A bounded initial stress window around the public ChatGPT shock is:

```bash
python scripts/08_fetch_gdelt_gkg.py --start 20221115 --end 20230115
python scripts/09_count_gdelt_rows.py
```

Do not set an artificial record target. Record whatever the source actually returns. For a larger engineering benchmark, extend the window only after the bounded run passes storage and memory checks.

## 4. Production environment

Install the project so DuckDB and PyArrow are available:

```bash
pip install -e .[dev]
```

Then build Parquet intermediates and run SQL transformations. The portable CSV fallback exists only so audits can still run in constrained environments.

## 5. Evidence required before CV claims

A CV number is permitted only when all five exist:

1. raw file fingerprint(s);
2. source manifest entry;
3. raw/processed row audit;
4. reproducible transformation script;
5. passing key/duplicate tests.

The intended final bullet is generated from audited values, not an aspirational number.
