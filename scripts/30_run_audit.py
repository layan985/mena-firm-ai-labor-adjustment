from __future__ import annotations

import csv
import json
from pathlib import Path

from mena_ai_labor.io import discover_raw_files, sha256_file

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MANIFEST = ROOT / "config" / "source_manifest.csv"
OUT = ROOT / "outputs" / "audits" / "data_audit.json"

with MANIFEST.open(newline="", encoding="utf-8") as f:
    sources = list(csv.DictReader(f))

raw_files = []
for p in discover_raw_files(RAW):
    rel = p.relative_to(RAW)
    raw_files.append({
        "source_id": rel.parts[0],
        "path": str(p.relative_to(ROOT)),
        "bytes": p.stat().st_size,
        "sha256": sha256_file(p),
    })

present_ids = sorted({r["source_id"] for r in raw_files})
required_ids = sorted(s["source_id"] for s in sources if s["required"].lower() == "yes")
missing_required = sorted(set(required_ids) - set(present_ids))

processed_counts = {}
for p in PROCESSED.rglob("*.csv"):
    with p.open(newline="", encoding="utf-8") as f:
        processed_counts[str(p.relative_to(ROOT))] = max(sum(1 for _ in f) - 1, 0)

try:
    import duckdb
    con = duckdb.connect()
    for p in PROCESSED.rglob("*.parquet"):
        processed_counts[str(p.relative_to(ROOT))] = int(
            con.execute("SELECT count(*) FROM read_parquet(?)", [str(p)]).fetchone()[0]
        )
    con.close()
except ImportError:
    pass

report = {
    "manifest_sources": len(sources),
    "raw_source_ids_present": len(present_ids),
    "raw_files": len(raw_files),
    "raw_bytes": sum(r["bytes"] for r in raw_files),
    "missing_required_source_ids": missing_required,
    "processed_row_counts": processed_counts,
    "files": raw_files,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
