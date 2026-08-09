from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "metadata" / "firms_50.csv"
OUT = ROOT / "data" / "interim" / "pilot_50_skeleton.csv"


def build() -> pd.DataFrame:
    firms = pd.read_csv(FRAME, dtype={"ticker": "string"})
    if len(firms) != 50 or firms["firm_id"].nunique() != 50:
        raise ValueError("Pilot frame must contain exactly 50 unique firms")
    years = pd.DataFrame({"year": list(range(2018, 2026))})
    panel = firms.assign(_k=1).merge(years.assign(_k=1), on="_k").drop(columns="_k")
    panel = panel[["firm_id", "firm_name", "country", "exchange", "ticker", "sector", "year"]]
    for col in [
        "employees", "employment_missing_reason", "employment_source_id", "employment_source_page",
        "employment_source_sha256", "reporting_scope", "ai_label", "ai_search_complete",
        "ai_missing_reason", "ai_source_id", "ai_source_page", "ai_source_sha256", "ai_evidence_id",
        "source_retrieval_date", "scope_break_flag", "scope_break_reason"
    ]:
        panel[col] = pd.NA
    if len(panel) != 400 or panel[["firm_id", "year"]].duplicated().any():
        raise AssertionError("Expected exactly 400 unique firm-years")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT, index=False)
    return panel


if __name__ == "__main__":
    x = build()
    print(f"wrote {len(x)} firm-years for {x.firm_id.nunique()} firms -> {OUT}")
