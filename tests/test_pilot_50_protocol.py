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


def test_freeze_rejects_incomplete_panel():
    df = pd.DataFrame({
        "firm_id": [f"F{i:02d}" for i in range(50) for _ in range(8)],
        "year": list(range(2018, 2026)) * 50,
        "country": ["X"] * 400,
        "sector": ["S"] * 400,
        "employees": [pd.NA] * 400,
        "employment_source_id": [pd.NA] * 400,
        "employment_source_page": [pd.NA] * 400,
        "employment_source_sha256": [pd.NA] * 400,
        "reporting_scope": [pd.NA] * 400,
        "ai_label": [pd.NA] * 400,
        "source_retrieval_date": [pd.NA] * 400,
    })
    summary = validate_panel(df)
    assert summary["n_firms"] == 50
    assert summary["n_firm_years"] == 400
    bad = df.iloc[:-1].copy()
    with pytest.raises(ValueError):
        validate_panel(bad)
