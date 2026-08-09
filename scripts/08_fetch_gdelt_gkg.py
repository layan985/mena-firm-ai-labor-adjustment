from __future__ import annotations

"""Stream selected GDELT 2.0 GKG files from the official master file list.

The downloader never loads a full day into pandas. It filters the master list,
downloads ZIPs sequentially, and leaves DuckDB to query compressed/expanded files.
"""

import argparse
import re
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
MASTER = 'https://data.gdeltproject.org/gdeltv2/masterfilelist.txt'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', required=True, help='YYYYMMDD')
    ap.add_argument('--end', required=True, help='YYYYMMDD')
    ap.add_argument('--max-files', type=int, default=0, help='0 means no cap')
    args = ap.parse_args()

    if not re.fullmatch(r'\d{8}', args.start) or not re.fullmatch(r'\d{8}', args.end):
        raise SystemExit('start/end must be YYYYMMDD')

    text = requests.get(MASTER, timeout=180).text
    urls = []
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        url = parts[-1]
        m = re.search(r'/(\d{14})\.gkg\.csv\.zip$', url)
        if not m:
            continue
        day = m.group(1)[:8]
        if args.start <= day <= args.end:
            urls.append(url)
    urls = sorted(urls)
    if args.max_files:
        urls = urls[:args.max_files]

    out_dir = ROOT / 'data' / 'raw' / 'gdelt_gkg_ai_jobs'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f'GDELT files selected: {len(urls)}')
    for i, url in enumerate(urls, 1):
        out = out_dir / url.rsplit('/', 1)[-1]
        if out.exists() and out.stat().st_size > 0:
            print(f'[{i}/{len(urls)}] exists {out.name}')
            continue
        with requests.get(url, timeout=180, stream=True) as r:
            r.raise_for_status()
            with out.open('wb') as f:
                for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                    if chunk:
                        f.write(chunk)
        print(f'[{i}/{len(urls)}] {out.name} {out.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
