from __future__ import annotations

import re
from urllib.parse import urlparse

import pandas as pd

PILOT_YEARS = tuple(range(2018, 2026))
STATUS_DOMAIN = {"observed", "not_disclosed", "not_applicable", "not_collected"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

FIRM_YEAR_REQUIRED = {
    "firm_id",
    "firm_name_canonical",
    "country",
    "exchange",
    "ticker",
    "sector",
    "fiscal_year",
    "report_url",
    "report_sha256",
    "employee_count",
    "employee_count_status",
    "employee_count_page",
    "personnel_expense",
    "personnel_expense_status",
    "personnel_expense_page",
    "reporting_scope_flag",
    "merger_restructuring_flag",
    "notes",
}

AI_EVIDENCE_REQUIRED = {
    "firm_id",
    "firm_name_canonical",
    "fiscal_year",
    "ai_evidence_text",
    "ai_evidence_page",
    "ai_evidence_hash",
    "ai_substantiveness_score",
    "ai_functional_category",
    "manual_review",
    "first_substantive_adoption_year",
    "source_url",
}


def _require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} missing required columns: {sorted(missing)}")


def _valid_https(value: object) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme == "https" and bool(parsed.netloc)


def _validate_status_value_pairs(df: pd.DataFrame, value_col: str, status_col: str) -> None:
    if not df[status_col].isin(STATUS_DOMAIN).all():
        bad = sorted(set(df.loc[~df[status_col].isin(STATUS_DOMAIN), status_col].astype(str)))
        raise ValueError(f"{status_col} contains invalid statuses: {bad}")

    numeric = pd.to_numeric(df[value_col], errors="coerce")
    observed = df[status_col].eq("observed")
    if numeric[observed].isna().any():
        raise ValueError(f"{value_col} must be numeric when {status_col}='observed'")
    if (numeric[observed] < 0).any():
        raise ValueError(f"{value_col} cannot be negative")
    if df.loc[~observed, value_col].notna().any():
        raise ValueError(
            f"{value_col} must be blank unless {status_col}='observed'; "
            "use an explicit status instead of numeric sentinels"
        )


def validate_firm_year_pilot(
    df: pd.DataFrame,
    *,
    expected_firms: int = 50,
    require_release_complete: bool = False,
) -> None:
    """Validate the listed-firm pilot without pretending unfinished collection is complete.

    With ``require_release_complete=False`` this checks schema and internal integrity
    during data collection. The release mode additionally requires exactly 50 firms
    and one attempted row for every pilot year (2018-2025) for every firm.
    """
    _require_columns(df, FIRM_YEAR_REQUIRED, "firm-year pilot")
    if df.empty:
        return

    years = pd.to_numeric(df["fiscal_year"], errors="coerce")
    if years.isna().any() or not years.astype(int).isin(PILOT_YEARS).all():
        raise ValueError("fiscal_year must be an integer in 2018-2025")

    if df.duplicated(["firm_id", "fiscal_year"]).any():
        raise ValueError("Duplicate firm_id/fiscal_year rows in 50-firm pilot")

    _validate_status_value_pairs(df, "employee_count", "employee_count_status")
    _validate_status_value_pairs(df, "personnel_expense", "personnel_expense_status")

    source_needed = df["employee_count_status"].eq("observed") | df["personnel_expense_status"].eq("observed")
    for idx, row in df.loc[source_needed].iterrows():
        if not _valid_https(row["report_url"]):
            raise ValueError(f"Observed row {idx} requires a valid HTTPS report_url")
        if not SHA256_RE.fullmatch(str(row["report_sha256"])):
            raise ValueError(f"Observed row {idx} requires a 64-character report_sha256")
        if row["employee_count_status"] == "observed" and not str(row["employee_count_page"]).strip():
            raise ValueError(f"Observed employee_count row {idx} requires employee_count_page")
        if row["personnel_expense_status"] == "observed" and not str(row["personnel_expense_page"]).strip():
            raise ValueError(f"Observed personnel_expense row {idx} requires personnel_expense_page")

    if require_release_complete:
        firms = df["firm_id"].dropna().astype(str).unique()
        if len(firms) != expected_firms:
            raise ValueError(f"Release requires exactly {expected_firms} unique firms; found {len(firms)}")
        expected_years = set(PILOT_YEARS)
        for firm_id, g in df.groupby("firm_id"):
            got = set(pd.to_numeric(g["fiscal_year"], errors="raise").astype(int))
            if got != expected_years:
                missing = sorted(expected_years - got)
                extra = sorted(got - expected_years)
                raise ValueError(f"{firm_id} incomplete pilot-year coverage; missing={missing}, extra={extra}")
            if g["employee_count_status"].eq("not_collected").any():
                raise ValueError(f"{firm_id} still has employee_count_status='not_collected'")


def validate_ai_evidence_pilot(df: pd.DataFrame) -> None:
    _require_columns(df, AI_EVIDENCE_REQUIRED, "AI-evidence pilot")
    if df.empty:
        return

    years = pd.to_numeric(df["fiscal_year"], errors="coerce")
    if years.isna().any() or not years.astype(int).isin(PILOT_YEARS).all():
        raise ValueError("AI evidence fiscal_year must be in 2018-2025")

    score = pd.to_numeric(df["ai_substantiveness_score"], errors="coerce")
    if score.isna().any() or not score.astype(int).isin([0, 1, 2, 3]).all():
        raise ValueError("ai_substantiveness_score must be in {0,1,2,3}")

    substantive = score.ge(2)
    if not df.loc[substantive, "manual_review"].astype(str).str.lower().isin({"yes", "true", "1"}).all():
        raise ValueError("Every AI-evidence row scored >=2 must be manually reviewed")

    for idx, row in df.iterrows():
        if not _valid_https(row["source_url"]):
            raise ValueError(f"AI-evidence row {idx} requires a valid HTTPS source_url")
        if not str(row["ai_evidence_page"]).strip():
            raise ValueError(f"AI-evidence row {idx} requires ai_evidence_page")
        if not SHA256_RE.fullmatch(str(row["ai_evidence_hash"])):
            raise ValueError(f"AI-evidence row {idx} requires a 64-character ai_evidence_hash")


def pilot_manifest(firm_year: pd.DataFrame, ai_evidence: pd.DataFrame) -> dict[str, object]:
    """Return compact machine-readable progress metrics without claiming release status."""
    firms = int(firm_year["firm_id"].nunique()) if "firm_id" in firm_year else 0
    rows = int(len(firm_year))
    observed_headcount = (
        int(firm_year["employee_count_status"].eq("observed").sum())
        if "employee_count_status" in firm_year
        else 0
    )
    substantive_ai = (
        int(pd.to_numeric(ai_evidence["ai_substantiveness_score"], errors="coerce").ge(2).sum())
        if "ai_substantiveness_score" in ai_evidence
        else 0
    )
    return {
        "pilot_target_firms": 50,
        "pilot_years": list(PILOT_YEARS),
        "firms_entered": firms,
        "firm_year_rows": rows,
        "observed_headcount_rows": observed_headcount,
        "ai_evidence_rows": int(len(ai_evidence)),
        "substantive_ai_rows": substantive_ai,
        "release_complete": False,
    }
