from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_wbes(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".dta":
        return pd.read_stata(path, convert_categoricals=False)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported WBES input format: {suffix}")


def standardize_fixture(df: pd.DataFrame) -> pd.DataFrame:
    rename = {
        "idstd": "firm_id",
        "l1": "l1",
        "l2": "l2",
    }
    out = df.rename(columns={k: v for k, v in rename.items() if k in df.columns}).copy()
    required = ["firm_id", "country", "year", "innovation_text", "l1", "l2"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return out
