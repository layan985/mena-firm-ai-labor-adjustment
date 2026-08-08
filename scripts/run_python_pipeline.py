from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from mena_ai_labor.ai_classifier import classify_ai_text
from mena_ai_labor.ingest_wbes import read_wbes, standardize_fixture
from mena_ai_labor.labor_outcomes import log_change, share
from mena_ai_labor.qa import assert_ai_score_domain, assert_unique_firm_year


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    df = standardize_fixture(read_wbes(args.input))
    cls = df["innovation_text"].map(classify_ai_text)
    df["ai_score"] = cls.map(lambda x: x.score)
    df["ai_category"] = cls.map(lambda x: x.category)
    df["ai_terms"] = cls.map(lambda x: "|".join(x.matched_terms))
    df["employment_log_change_3y"] = [log_change(a,b) for a,b in zip(df["l1"], df["l2"])]
    if "l5" in df:
        df["female_share"] = [share(a,b) for a,b in zip(df["l5"], df["l1"])]

    assert_unique_firm_year(df)
    assert_ai_score_domain(df)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"wrote {len(df)} rows -> {out}")

if __name__ == "__main__":
    main()
