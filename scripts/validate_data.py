from pathlib import Path
import pandas as pd
from mena_ai_labor.qa import sha256_file

root = Path("data/raw")
paths = [p for p in root.rglob("*") if p.is_file() and p.name != ".gitkeep"]
if not paths:
    raise SystemExit("No raw data found. Place permitted source files under data/raw/ first.")
records = [{"path": str(p), "bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in paths]
out = Path("data/interim/raw_hashes.csv")
out.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(records).to_csv(out, index=False)
print(f"validated {len(records)} raw files -> {out}")
