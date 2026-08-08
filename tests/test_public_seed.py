from pathlib import Path
import pandas as pd

from mena_ai_labor.provenance import detect_scope_breaks, flag_large_headcount_moves, validate_public_seed
from mena_ai_labor.panel import assign_first_adoption_year

ROOT = Path(__file__).resolve().parents[1]


def test_real_public_seed_validates():
    df = pd.read_csv(ROOT / "data" / "pilot" / "public_seed_firm_year.csv")
    validate_public_seed(df)
    assert len(df) == 9
    assert df["firm_id"].nunique() == 3


def test_seed_has_no_internal_scope_breaks_within_each_series():
    df = pd.read_csv(ROOT / "data" / "pilot" / "public_seed_firm_year.csv")
    assert detect_scope_breaks(df) == []


def test_stc_move_is_flagged_for_manual_review():
    df = pd.read_csv(ROOT / "data" / "pilot" / "public_seed_firm_year.csv")
    flagged = flag_large_headcount_moves(df, threshold=0.10)
    row = flagged[(flagged["firm_id"] == "SA_7010") & (flagged["year"] == 2024)].iloc[0]
    assert bool(row["large_headcount_move"])


def test_ai_evidence_scores_and_left_censoring():
    evidence = pd.read_csv(ROOT / "data" / "pilot" / "ai_evidence_seed.csv")
    assert set(evidence["ai_score"]).issubset({0, 1, 2, 3})
    almarai = assign_first_adoption_year(evidence[evidence["firm_id"] == "SA_2280"].copy())
    assert int(almarai["first_ai_year"].dropna().iloc[0]) == 2025
    aramco = evidence[evidence["firm_id"] == "SA_2222"]
    assert aramco["adoption_interpretation"].str.contains("left-censored", case=False).any()
