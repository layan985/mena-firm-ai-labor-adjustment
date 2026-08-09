import pandas as pd
import pytest

from scripts.draw_blinded_validation_sample import draw
from scripts.score_intercoder_agreement import score
from scripts.freeze_pilot_50 import validate_panel


def test_blinded_sample_has_no_identity_or_first_label():
    df = pd.DataFrame({
        "ai_evidence_id": [f"E{i}" for i in range(20)],
        "firm_id": ["SECRET"] * 20,
        "evidence_excerpt": [f"passage {i}" for i in range(20)],
        "year": [2024] * 20,
        "ai_label": [i % 4 for i in range(20)],
        "employees": [100] * 20,
    })
    out = draw(df, fraction=0.20)
    assert "firm_id" not in out.columns
    assert "employees" not in out.columns
    assert "ai_label" not in out.columns
    assert set(out.columns) == {"validation_id", "evidence_excerpt", "year", "coder_label", "coder_confidence", "coder_notes"}


def test_agreement_perfect_labels():
    c1 = pd.DataFrame({"validation_id": ["a", "b", "c", "d"], "coder_label": [0, 1, 2, 3]})
    c2 = c1.copy()
    result = score(c1, c2)
    assert result["raw_agreement"] == 1.0
    assert result["cohen_kappa"] == pytest.approx(1.0)
    assert result["quadratic_weighted_kappa"] == pytest.approx(1.0)


def complete_missing_panel() -> pd.DataFrame:
    return pd.DataFrame({
        "firm_id": [f"F{i:02d}" for i in range(50) for _ in range(8)],
        "year": list(range(2018, 2026)) * 50,
        "country": ["X"] * 400,
        "sector": ["S"] * 400,
        "employees": [pd.NA] * 400,
        "employment_missing_reason": ["official report reviewed; exact comparable headcount not disclosed"] * 400,
        "employment_source_id": [pd.NA] * 400,
        "employment_source_page": [pd.NA] * 400,
        "employment_source_sha256": [pd.NA] * 400,
        "reporting_scope": [pd.NA] * 400,
        "ai_label": [pd.NA] * 400,
        "ai_search_complete": [True] * 400,
        "ai_missing_reason": ["completed search found no qualifying evidence passage"] * 400,
        "source_retrieval_date": ["2026-08-09"] * 400,
    })


def test_freeze_accepts_documented_missingness_but_rejects_wrong_size():
    df = complete_missing_panel()
    summary = validate_panel(df)
    assert summary["n_firms"] == 50
    assert summary["n_firm_years"] == 400
    assert summary["employment_missing"] == 400
    assert summary["employment_missing_reasons_documented"] == 400
    assert summary["ai_search_complete"] == 400
    bad = df.iloc[:-1].copy()
    with pytest.raises(ValueError):
        validate_panel(bad)


def test_freeze_rejects_silent_employment_missingness():
    df = complete_missing_panel()
    df.loc[0, "employment_missing_reason"] = pd.NA
    with pytest.raises(ValueError, match="employment_missing_reason"):
        validate_panel(df)


def test_freeze_rejects_incomplete_ai_search():
    df = complete_missing_panel()
    df.loc[0, "ai_search_complete"] = False
    with pytest.raises(ValueError, match="AI search protocol is incomplete"):
        validate_panel(df)


def test_freeze_rejects_unexplained_missing_ai_label():
    df = complete_missing_panel()
    df.loc[0, "ai_missing_reason"] = pd.NA
    with pytest.raises(ValueError, match="ai_missing_reason"):
        validate_panel(df)
