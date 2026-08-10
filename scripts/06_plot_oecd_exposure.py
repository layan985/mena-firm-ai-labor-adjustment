from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/oecd_occupation_ai_exposure.csv"
OUT = ROOT / "outputs/figures/oecd_ai_exposure_top20.png"


def main() -> None:
    if not DATA.exists():
        raise SystemExit("Missing processed OECD exposure data. Run scripts/05_ingest_oecd_exposure.py first.")

    rows: list[tuple[str, float]] = []
    with DATA.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            title = (row.get("occupation_title") or row.get("occupation_code") or "unknown").strip()
            exposure = row.get("ai_exposure")
            if exposure in (None, ""):
                continue
            rows.append((title, float(exposure)))

    if not rows:
        raise SystemExit("Processed OECD exposure file contains no usable exposure values.")

    top = sorted(rows, key=lambda item: item[1], reverse=True)[:20]
    labels = [x[0] for x in top][::-1]
    values = [x[1] for x in top][::-1]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(labels, values)
    ax.set_xlabel("AI exposure")
    ax.set_title("Top 20 OECD occupations by AI exposure")
    fig.tight_layout()
    fig.savefig(OUT, dpi=180)
    plt.close(fig)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
