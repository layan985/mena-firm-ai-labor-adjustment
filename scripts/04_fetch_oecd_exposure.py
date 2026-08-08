from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "oecd_ai_exposure" / "oecd_ai_exposure_2026.xlsx"
PROV = ROOT / "outputs" / "audits" / "oecd_download_provenance.json"
URL = "https://www.oecd.org/content/dam/oecd/en/about/projects/edu/aifs-%28ai-and-future-skills%29/OECD%20AI%20Capability%20Gap%20Index_public%20data.xlsx/_jcr_content/renditions/original.media_file.download_attachment.file/OECD%20AI%20Capability%20Gap%20Index_public%20data.xlsx"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    PROV.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and not args.force:
        print(f"Using existing {OUT.relative_to(ROOT)}")
    else:
        with requests.get(URL, timeout=120, stream=True) as r:
            r.raise_for_status()
            with OUT.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
    record = {
        "source_id": "oecd_ai_exposure",
        "url": URL,
        "retrieved_on": date.today().isoformat(),
        "path": str(OUT.relative_to(ROOT)),
        "bytes": OUT.stat().st_size,
        "sha256": sha256(OUT),
    }
    PROV.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
