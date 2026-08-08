from __future__ import annotations

import hashlib
from pathlib import Path
import pandas as pd


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_unique_firm_year(df: pd.DataFrame) -> None:
    dupes = df.duplicated(["firm_id", "year"], keep=False)
    if dupes.any():
        raise ValueError(f"Duplicate firm-year rows: {int(dupes.sum())}")


def assert_ai_score_domain(df: pd.DataFrame) -> None:
    bad = ~df["ai_score"].isin([0, 1, 2, 3])
    if bad.any():
        raise ValueError("ai_score must be in {0,1,2,3}")
