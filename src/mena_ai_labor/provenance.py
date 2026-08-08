from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import pandas as pd


@dataclass(frozen=True)
class ScopeBreak:
    firm_id: str
    years: tuple[int, int]
    prior_scope: str
    current_scope: str


def validate_public_seed(df: pd.DataFrame) -> None:
    required = {"firm_id", "year", "employees", "source_url", "source_locator", "reporting_scope", "source_status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.duplicated(["firm_id", "year"]).any():
        raise ValueError("Duplicate firm-year rows in public seed")
    if (pd.to_numeric(df["employees"], errors="coerce") <= 0).any():
        raise ValueError("Employee counts must be positive")
    if not df["source_status"].eq("verified_public").all():
        raise ValueError("Public seed must contain only verified_public rows")
    for url in df["source_url"]:
        parsed = urlparse(str(url))
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"Invalid source URL: {url}")


def detect_scope_breaks(df: pd.DataFrame) -> list[ScopeBreak]:
    breaks: list[ScopeBreak] = []
    ordered = df.sort_values(["firm_id", "year"])
    for firm_id, g in ordered.groupby("firm_id"):
        rows = g[["year", "reporting_scope"]].itertuples(index=False, name=None)
        previous = None
        for year, scope in rows:
            if previous is not None:
                prev_year, prev_scope = previous
                if scope != prev_scope:
                    breaks.append(ScopeBreak(str(firm_id), (int(prev_year), int(year)), str(prev_scope), str(scope)))
            previous = (year, scope)
    return breaks


def flag_large_headcount_moves(df: pd.DataFrame, threshold: float = 0.10) -> pd.DataFrame:
    out = df.sort_values(["firm_id", "year"]).copy()
    out["employee_growth"] = out.groupby("firm_id")["employees"].pct_change()
    out["large_headcount_move"] = out["employee_growth"].abs().ge(threshold).fillna(False)
    return out
