from __future__ import annotations

import pandas as pd


def assign_first_adoption_year(df: pd.DataFrame, threshold: int = 2) -> pd.DataFrame:
    out = df.copy()
    treated = out.loc[out["ai_score"] >= threshold, ["firm_id", "year"]]
    first = treated.groupby("firm_id", as_index=False)["year"].min().rename(columns={"year": "first_ai_year"})
    out = out.drop(columns=["first_ai_year"], errors="ignore").merge(first, on="firm_id", how="left")
    out["event_time"] = out["year"] - out["first_ai_year"]
    out["adopted"] = ((out["first_ai_year"].notna()) & (out["year"] >= out["first_ai_year"])).astype(int)
    return out
