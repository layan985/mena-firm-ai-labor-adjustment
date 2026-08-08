import pandas as pd
from mena_ai_labor.panel import assign_first_adoption_year


def test_assign_first_adoption_year_and_event_time():
    df = pd.DataFrame({
        "firm_id": ["a", "a", "a", "b", "b"],
        "year": [2021, 2022, 2023, 2022, 2023],
        "ai_score": [0, 1, 2, 0, 0],
    })
    out = assign_first_adoption_year(df, threshold=2)
    a = out[out.firm_id == "a"].sort_values("year")
    assert a["first_ai_year"].tolist() == [2023, 2023, 2023]
    assert a["adopted"].tolist() == [0, 0, 1]
    assert a["event_time"].tolist() == [-2, -1, 0]
    assert out.loc[out.firm_id == "b", "first_ai_year"].isna().all()
