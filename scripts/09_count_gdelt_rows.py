from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw' / 'gdelt_gkg_ai_jobs'
OUT = ROOT / 'outputs' / 'audits' / 'gdelt_row_counts.json'

rows = []
total = 0
for zpath in sorted(RAW.glob('*.zip')):
    with zipfile.ZipFile(zpath) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        count = 0
        for member in members:
            with zf.open(member) as f:
                for _ in f:
                    count += 1
        rows.append({'file': zpath.name, 'rows': count, 'bytes': zpath.stat().st_size})
        total += count
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({'files': rows, 'total_rows': total}, indent=2), encoding='utf-8')
print(json.dumps({'files': len(rows), 'total_rows': total}, indent=2))
