from pathlib import Path
import pandas as pd

from mena_ai_labor.provenance import detect_scope_breaks, flag_large_headcount_moves, validate_public_seed

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "pilot" / "public_seed_firm_year.csv"
df = pd.read_csv(path)
validate_public_seed(df)
flagged = flag_large_headcount_moves(df)

print(f"validated_rows={len(df)}")
print(f"firms={df['firm_id'].nunique()}")
print(f"scope_breaks={len(detect_scope_breaks(df))}")
print("large_headcount_moves:")
cols = ["firm_id", "year", "employees", "employee_growth", "large_headcount_move"]
print(flagged.loc[flagged["large_headcount_move"], cols].to_string(index=False))
