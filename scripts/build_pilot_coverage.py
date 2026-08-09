from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "metadata" / "firms_50.csv"
PILOT_DIR = ROOT / "data" / "pilot"
OUT_CSV = ROOT / "data" / "interim" / "pilot_50_coverage.csv"
OUT_JSON = ROOT / "data" / "interim" / "pilot_50_coverage_summary.json"


def _truthy(value: object) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _load_employment_batches() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(PILOT_DIR.glob("research_batch_*_employment.csv")):
        df = pd.read_csv(path)
        if not {"firm_id", "year", "employees"}.issubset(df.columns):
            continue
        df = df.copy()
        df["source_batch"] = path.name
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        df["employees_numeric"] = pd.to_numeric(df["employees"], errors="coerce")
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=["firm_id", "year", "employees_numeric", "source_batch"])
    out = pd.concat(frames, ignore_index=True, sort=False)
    return out[out["year"].between(2018, 2025, inclusive="both")].copy()


def _load_ai_batches() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(PILOT_DIR.glob("research_batch_*_ai_evidence.csv")):
        df = pd.read_csv(path)
        if not {"firm_id", "year"}.issubset(df.columns):
            continue
        df = df.copy()
        df["source_batch"] = path.name
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=["firm_id", "year", "source_batch"])
    out = pd.concat(frames, ignore_index=True, sort=False)
    return out[out["year"].between(2018, 2025, inclusive="both")].copy()


def _classify_group(group: pd.DataFrame) -> pd.Series:
    numeric = group[group["employees_numeric"].notna()].copy()
    batches = sorted(group["source_batch"].astype(str).unique().tolist())
    if numeric.empty:
        return pd.Series({
            "employment_status": "unresolved",
            "employees": pd.NA,
            "employment_record_count": int(len(group)),
            "employment_source_batches": "|".join(batches),
            "scope_break": False,
            "hash_pending": True,
        })

    values = sorted(numeric["employees_numeric"].astype(float).unique().tolist())
    rounded = any(_truthy(x) for x in numeric.get("rounded_flag", pd.Series(False, index=numeric.index)))
    scope_break = any(_truthy(x) for x in numeric.get("scope_break_flag", pd.Series(False, index=numeric.index)))
    hashes = numeric.get("source_sha256", pd.Series(pd.NA, index=numeric.index))
    hash_pending = hashes.isna().any() or hashes.astype("string").str.len().fillna(0).lt(64).any()

    if len(values) > 1:
        status = "conflict"
        chosen = pd.NA
    elif rounded:
        status = "rounded"
        chosen = values[0]
    elif scope_break:
        status = "exact_scope_break"
        chosen = values[0]
    else:
        status = "exact"
        chosen = values[0]

    return pd.Series({
        "employment_status": status,
        "employees": chosen,
        "employment_record_count": int(len(group)),
        "employment_source_batches": "|".join(batches),
        "scope_break": bool(scope_break),
        "hash_pending": bool(hash_pending),
    })


def build() -> tuple[pd.DataFrame, dict]:
    firms = pd.read_csv(FRAME, dtype={"ticker": "string"})
    if len(firms) != 50 or firms["firm_id"].nunique() != 50:
        raise ValueError("Pilot frame must contain exactly 50 unique firms")

    years = pd.DataFrame({"year": range(2018, 2026)})
    grid = firms.assign(_k=1).merge(years.assign(_k=1), on="_k").drop(columns="_k")
    grid = grid[["firm_id", "firm_name", "country", "exchange", "sector", "year"]]
    if len(grid) != 400:
        raise AssertionError("Expected 400 target firm-years")

    emp = _load_employment_batches()
    if emp.empty:
        emp_cov = pd.DataFrame(columns=["firm_id", "year", "employment_status", "employees"])
    else:
        emp_cov = (
            emp.groupby(["firm_id", "year"], dropna=False, sort=False)
            .apply(_classify_group, include_groups=False)
            .reset_index()
        )

    ai = _load_ai_batches()
    if ai.empty:
        ai_cov = pd.DataFrame(columns=["firm_id", "year", "ai_evidence_count", "max_ai_score"])
    else:
        if "ai_score" in ai.columns:
            ai["ai_score"] = pd.to_numeric(ai["ai_score"], errors="coerce")
        else:
            ai["ai_score"] = pd.NA
        ai_cov = (
            ai.groupby(["firm_id", "year"], dropna=False)
            .agg(ai_evidence_count=("source_batch", "size"), max_ai_score=("ai_score", "max"))
            .reset_index()
        )

    coverage = grid.merge(emp_cov, on=["firm_id", "year"], how="left").merge(
        ai_cov, on=["firm_id", "year"], how="left"
    )
    coverage["employment_status"] = coverage["employment_status"].fillna("unresolved")
    coverage["employment_record_count"] = coverage["employment_record_count"].fillna(0).astype(int)
    coverage["ai_evidence_count"] = coverage["ai_evidence_count"].fillna(0).astype(int)
    coverage["scope_break"] = coverage["scope_break"].fillna(False).astype(bool)
    coverage["hash_pending"] = coverage["hash_pending"].fillna(True).astype(bool)

    status_counts = coverage["employment_status"].value_counts().to_dict()
    firms_with_any_employment = int(coverage.loc[coverage["employees"].notna(), "firm_id"].nunique())
    firms_with_ai_evidence = int(coverage.loc[coverage["ai_evidence_count"].gt(0), "firm_id"].nunique())
    summary = {
        "target_firms": 50,
        "target_firm_years": 400,
        "employment_status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "numeric_employment_firm_years": int(coverage["employees"].notna().sum()),
        "firms_with_any_numeric_employment": firms_with_any_employment,
        "firm_years_with_ai_evidence": int(coverage["ai_evidence_count"].gt(0).sum()),
        "firms_with_ai_evidence": firms_with_ai_evidence,
        "scope_break_firm_years": int(coverage["scope_break"].sum()),
        "employment_rows_with_hash_pending": int(
            coverage["employees"].notna().mul(coverage["hash_pending"]).sum()
        ),
        "unresolved_firm_years": int(coverage["employment_status"].eq("unresolved").sum()),
        "conflicting_firm_years": int(coverage["employment_status"].eq("conflict").sum()),
    }

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    coverage.sort_values(["firm_id", "year"]).to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return coverage, summary


if __name__ == "__main__":
    _, summary = build()
    print(json.dumps(summary, indent=2, sort_keys=True))
