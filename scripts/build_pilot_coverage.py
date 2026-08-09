from __future__ import annotations

from pathlib import Path
import csv
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


def _research_batch_paths() -> list[Path]:
    patterns = ("research_batch_*_employment.csv", "research_batch_*_ai_evidence.csv")
    return sorted({path for pattern in patterns for path in PILOT_DIR.glob(pattern)})


def _validate_csv_shapes() -> None:
    errors: list[str] = []
    for path in _research_batch_paths():
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = csv.reader(handle)
            try:
                header = next(rows)
            except StopIteration:
                errors.append(f"{path.relative_to(ROOT)}: empty CSV")
                continue
            expected = len(header)
            for line_no, row in enumerate(rows, start=2):
                if len(row) != expected:
                    errors.append(
                        f"{path.relative_to(ROOT)} line {line_no}: expected {expected} fields, found {len(row)}"
                    )
    if errors:
        raise ValueError("Malformed research batch CSVs:\n- " + "\n- ".join(errors))


def _read_batch(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _load_employment_batches() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(PILOT_DIR.glob("research_batch_*_employment.csv")):
        df = _read_batch(path)
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
        df = _read_batch(path)
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
        employee_value = pd.NA
    elif rounded:
        status = "rounded"
        employee_value = values[0]
    elif scope_break:
        status = "exact_scope_break"
        employee_value = values[0]
    else:
        status = "exact"
        employee_value = values[0]

    return pd.Series({
        "employment_status": status,
        "employees": employee_value,
        "employment_record_count": int(len(group)),
        "employment_source_batches": "|".join(batches),
        "scope_break": scope_break,
        "hash_pending": bool(hash_pending),
    })


def build() -> tuple[pd.DataFrame, dict]:
    _validate_csv_shapes()
    frame = pd.read_csv(FRAME)
    years = pd.DataFrame({"year": range(2018, 2026)})
    grid = frame.assign(_key=1).merge(years.assign(_key=1), on="_key").drop(columns="_key")

    if len(frame) != 50 or frame["firm_id"].nunique() != 50:
        raise ValueError("Pilot frame must contain exactly 50 unique firms")
    if len(grid) != 400:
        raise ValueError("Pilot grid must contain exactly 400 firm-years")

    employment = _load_employment_batches()
    if employment.empty:
        emp_summary = pd.DataFrame(columns=["firm_id", "year", "employment_status", "employees"])
    else:
        emp_summary = (
            employment.groupby(["firm_id", "year"], dropna=False)
            .apply(_classify_group, include_groups=False)
            .reset_index()
        )

    ai = _load_ai_batches()
    ai_summary = (
        ai.groupby(["firm_id", "year"], dropna=False)
        .agg(
            ai_evidence_records=("source_batch", "size"),
            ai_source_batches=("source_batch", lambda x: "|".join(sorted(set(map(str, x))))),
        )
        .reset_index()
        if not ai.empty
        else pd.DataFrame(columns=["firm_id", "year", "ai_evidence_records", "ai_source_batches"])
    )

    coverage = grid.merge(emp_summary, on=["firm_id", "year"], how="left").merge(
        ai_summary, on=["firm_id", "year"], how="left"
    )
    coverage["employment_status"] = coverage["employment_status"].fillna("unresolved")
    coverage["ai_evidence_records"] = coverage["ai_evidence_records"].fillna(0).astype(int)
    coverage["hash_pending"] = coverage["hash_pending"].astype("boolean").fillna(True).astype(bool)
    coverage["scope_break"] = coverage["scope_break"].astype("boolean").fillna(False).astype(bool)

    numeric_statuses = {"exact", "rounded", "exact_scope_break"}
    numeric_mask = coverage["employment_status"].isin(numeric_statuses)
    per_firm = (
        coverage.assign(has_numeric=numeric_mask.astype(int))
        .groupby(["firm_id", "firm_name"], as_index=False)
        .agg(numeric_years=("has_numeric", "sum"), unresolved_years=("employment_status", lambda s: int((s == "unresolved").sum())))
    )
    zero_numeric_firms = per_firm.loc[per_firm["numeric_years"].eq(0), "firm_id"].tolist()
    partial_firms = per_firm.loc[per_firm["numeric_years"].between(1, 7), ["firm_id", "numeric_years"]]

    summary = {
        "target_firms": 50,
        "target_firm_years": 400,
        "employment_firm_years_with_numeric_value": int(numeric_mask.sum()),
        "firms_with_any_numeric_employment": int(coverage.loc[numeric_mask, "firm_id"].nunique()),
        "employment_exact_firm_years": int((coverage["employment_status"] == "exact").sum()),
        "employment_rounded_firm_years": int((coverage["employment_status"] == "rounded").sum()),
        "employment_scope_break_firm_years": int((coverage["employment_status"] == "exact_scope_break").sum()),
        "employment_conflict_firm_years": int((coverage["employment_status"] == "conflict").sum()),
        "employment_unresolved_firm_years": int((coverage["employment_status"] == "unresolved").sum()),
        "ai_evidence_firm_years": int((coverage["ai_evidence_records"] > 0).sum()),
        "firms_with_ai_evidence": int(coverage.loc[coverage["ai_evidence_records"] > 0, "firm_id"].nunique()),
        "numeric_employment_rows_with_hash_pending": int((numeric_mask & coverage["hash_pending"]).sum()),
        "numeric_employment_rows_hash_complete": int((numeric_mask & ~coverage["hash_pending"]).sum()),
        "firms_with_zero_numeric_employment": zero_numeric_firms,
        "partial_firm_coverage": {row.firm_id: int(row.numeric_years) for row in partial_firms.itertuples(index=False)},
    }

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return coverage, summary


if __name__ == "__main__":
    _, summary = build()
    print(json.dumps(summary, indent=2, sort_keys=True))
