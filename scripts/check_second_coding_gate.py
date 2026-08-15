#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data/validation/blinded_ai_validation_sample.csv"
CODER2 = ROOT / "data/validation/coder_2.csv"
RECORD = ROOT / "audits/SECOND_CODER_RECORD.md"
AGREEMENT = ROOT / "data/validation/agreement_results.json"
ADJUDICATION = ROOT / "data/validation/adjudication.csv"
VALID_LABELS = {"0", "1", "2", "3"}
VALID_CONFIDENCE = {"low", "medium", "high"}


def rows(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    failures: list[str] = []
    sample = rows(SAMPLE)
    coder = rows(CODER2)

    sample_ids = [r.get("validation_id", "").strip() for r in sample]
    coder_ids = [r.get("validation_id", "").strip() for r in coder]

    if len(sample_ids) != 16:
        failures.append(f"frozen sample has {len(sample_ids)} rows; expected 16")
    if len(set(sample_ids)) != len(sample_ids):
        failures.append("frozen sample contains duplicate validation IDs")
    if coder_ids != sample_ids:
        failures.append("coder-2 worksheet IDs/order differ from frozen sample")

    for r in coder:
        vid = r.get("validation_id", "<missing>")
        label = r.get("coder_label", "").strip()
        confidence = r.get("coder_confidence", "").strip().lower()
        if label not in VALID_LABELS:
            failures.append(f"{vid}: coder_label incomplete or invalid")
        if confidence not in VALID_CONFIDENCE:
            failures.append(f"{vid}: coder_confidence incomplete or invalid")

    text = RECORD.read_text(encoding="utf-8")
    if "Status: **not completed**" in text:
        failures.append("second-coder completion record is not completed")
    required_confirmations = [
        r"Non-author:\s*`yes`",
        r"Founder labels hidden until coder-2 file frozen:\s*`yes`",
        r"Agreement output inspected before coding:\s*`no`",
        r"I completed the coder-2 labels before seeing founder labels for the sampled passages:\s*`yes`",
        r"Independence requirement satisfied:\s*`yes`",
    ]
    for pattern in required_confirmations:
        if not re.search(pattern, text, re.I):
            failures.append(f"completion record missing confirmation matching: {pattern}")

    if not AGREEMENT.exists():
        failures.append("agreement_results.json not generated")
    else:
        try:
            stats = json.loads(AGREEMENT.read_text(encoding="utf-8"))
            if stats.get("n_double_coded") != 16:
                failures.append("agreement output does not contain 16 paired labels")
            for key in ("raw_agreement", "cohen_kappa", "quadratic_weighted_kappa", "confusion_matrix"):
                if key not in stats:
                    failures.append(f"agreement output missing {key}")
        except Exception as exc:
            failures.append(f"agreement output invalid: {exc}")

    if ADJUDICATION.exists():
        adjudication = rows(ADJUDICATION)
        for r in adjudication:
            if r.get("validation_id", "").strip() not in set(sample_ids):
                failures.append(f"adjudication contains unknown validation ID {r.get('validation_id')}")
            if r.get("founder_label", "").strip() == r.get("coder_2_label", "").strip():
                failures.append(f"adjudication row {r.get('validation_id')} is not a disagreement")

    if failures:
        print("SECOND-CODING GATE: OPEN")
        for item in failures:
            print(f"- {item}")
        return 1

    print("SECOND-CODING GATE: CLOSED")
    print("All 16 frozen passages have independent coder-2 labels, completion evidence and agreement output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
