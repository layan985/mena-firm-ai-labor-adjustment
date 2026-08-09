import pandas as pd
import pytest

from mena_ai_labor.pilot50 import (
    PILOT_YEARS,
    pilot_manifest,
    validate_ai_evidence_pilot,
    validate_firm_year_pilot,
)

HEX = "a" * 64


def firm_year_row(**overrides):
    row = {
        "firm_id": "SA_TEST",
        "firm_name_canonical": "Test Firm",
        "country": "Saudi Arabia",
        "exchange": "Saudi Exchange",
        "ticker": "0000",
        "sector": "Industrials",
        "fiscal_year": 2024,
        "report_url": "https://example.com/report.pdf",
        "report_sha256": HEX,
        "employee_count": 100,
        "employee_count_status": "observed",
        "employee_count_page": "p. 10",
        "personnel_expense": None,
        "personnel_expense_status": "not_disclosed",
        "personnel_expense_page": "",
        "reporting_scope_flag": "stable",
        "merger_restructuring_flag": "none_known",
        "notes": "",
    }
    row.update(overrides)
    return row


def ai_row(**overrides):
    row = {
        "firm_id": "SA_TEST",
        "firm_name_canonical": "Test Firm",
        "fiscal_year": 2024,
        "ai_evidence_text": "deployed an AI system in operations",
        "ai_evidence_page": "p. 20",
        "ai_evidence_hash": HEX,
        "ai_substantiveness_score": 2,
        "ai_functional_category": "operations",
        "manual_review": "yes",
        "first_substantive_adoption_year": 2024,
        "source_url": "https://example.com/report.pdf",
    }
    row.update(overrides)
    return row


def test_working_firm_year_schema_accepts_observed_and_explicit_missingness():
    df = pd.DataFrame([firm_year_row()])
    validate_firm_year_pilot(df)


def test_numeric_sentinel_is_rejected_when_status_is_missing():
    df = pd.DataFrame([firm_year_row(employee_count=0, employee_count_status="not_disclosed")])
    with pytest.raises(ValueError, match="must be blank"):
        validate_firm_year_pilot(df)


def test_observed_zero_is_distinct_and_allowed():
    df = pd.DataFrame([firm_year_row(employee_count=0, employee_count_status="observed")])
    validate_firm_year_pilot(df)


def test_observed_value_requires_hash_and_page():
    df = pd.DataFrame([firm_year_row(report_sha256="", employee_count_page="")])
    with pytest.raises(ValueError):
        validate_firm_year_pilot(df)


def test_substantive_ai_requires_manual_review():
    df = pd.DataFrame([ai_row(manual_review="no")])
    with pytest.raises(ValueError, match="manually reviewed"):
        validate_ai_evidence_pilot(df)


def test_release_mode_requires_50_firms_and_all_eight_years():
    rows = []
    for i in range(50):
        for year in PILOT_YEARS:
            rows.append(
                firm_year_row(
                    firm_id=f"F{i:02d}",
                    fiscal_year=year,
                    employee_count=None,
                    employee_count_status="not_disclosed",
                    employee_count_page="",
                    report_url="",
                    report_sha256="",
                )
            )
    df = pd.DataFrame(rows)
    validate_firm_year_pilot(df, require_release_complete=True)


def test_release_mode_rejects_unattempted_collection():
    rows = []
    for i in range(50):
        for year in PILOT_YEARS:
            status = "not_collected" if (i == 0 and year == 2018) else "not_disclosed"
            rows.append(
                firm_year_row(
                    firm_id=f"F{i:02d}",
                    fiscal_year=year,
                    employee_count=None,
                    employee_count_status=status,
                    employee_count_page="",
                    report_url="",
                    report_sha256="",
                )
            )
    with pytest.raises(ValueError, match="not_collected"):
        validate_firm_year_pilot(pd.DataFrame(rows), require_release_complete=True)


def test_manifest_is_progress_not_a_fake_release_claim():
    fy = pd.DataFrame([firm_year_row()])
    ai = pd.DataFrame([ai_row()])
    manifest = pilot_manifest(fy, ai)
    assert manifest["pilot_target_firms"] == 50
    assert manifest["firms_entered"] == 1
    assert manifest["release_complete"] is False
