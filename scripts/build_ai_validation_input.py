from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "data" / "pilot"
OUT = ROOT / "data" / "interim" / "ai_evidence_labeled.csv"
REQUIRED = {"evidence_id", "firm_id", "year", "ai_score", "evidence_excerpt", "source_url"}
FINGERPRINT = ["firm_id", "year", "ai_score", "evidence_excerpt", "source_url"]


def build(paths: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(paths):
        frame = pd.read_csv(path, dtype="string")
        missing = REQUIRED.difference(frame.columns)
        if missing:
            raise ValueError(f"{path}: missing required columns {sorted(missing)}")
        frame = frame.copy()
        frame["source_batch"] = path.name
        frames.append(frame)
    if not frames:
        raise ValueError("No AI-evidence batches supplied")

    evidence = pd.concat(frames, ignore_index=True, sort=False)
    evidence["evidence_id"] = evidence["evidence_id"].str.strip()
    evidence["year"] = pd.to_numeric(evidence["year"], errors="raise").astype(int)
    evidence["ai_score"] = pd.to_numeric(evidence["ai_score"], errors="raise").astype(int)
    if evidence["evidence_id"].eq("").any() or evidence["evidence_id"].isna().any():
        raise ValueError("AI evidence_id must be nonempty")
    if not evidence["ai_score"].isin([0, 1, 2, 3]).all():
        raise ValueError("AI scores must be in {0,1,2,3}")

    collisions: list[str] = []
    for evidence_id, group in evidence.groupby("evidence_id", sort=False):
        if len(group[FINGERPRINT].drop_duplicates()) > 1:
            collisions.append(str(evidence_id))
    if collisions:
        raise ValueError(
            "Evidence IDs reused for substantively different passages: " + ", ".join(sorted(collisions))
        )

    valid_hash = evidence.get("source_sha256", pd.Series("", index=evidence.index)).fillna("").str.fullmatch(
        r"[0-9a-f]{64}"
    )
    evidence = evidence.assign(_valid_hash=valid_hash).sort_values(
        ["evidence_id", "_valid_hash", "source_batch"], ascending=[True, False, True]
    )
    provenance = evidence.groupby("evidence_id")["source_batch"].agg(
        duplicate_batch_count="size", source_batches=lambda values: "|".join(sorted(set(values)))
    )
    out = evidence.drop_duplicates("evidence_id", keep="first").drop(columns="_valid_hash")
    out = out.merge(provenance, left_on="evidence_id", right_index=True, how="left", validate="one_to_one")
    out = out.rename(
        columns={"evidence_id": "ai_evidence_id", "ai_label": "ai_label_text", "ai_score": "ai_label"}
    )
    if out["ai_evidence_id"].duplicated().any():
        raise AssertionError("Validation input must have unique evidence IDs")
    return out.sort_values(["firm_id", "year", "ai_evidence_id"]).reset_index(drop=True)


def main() -> None:
    paths = sorted(PILOT_DIR.glob("research_batch_*_ai_evidence.csv"))
    out = build(paths)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    duplicates = int((out["duplicate_batch_count"] > 1).sum())
    print(f"wrote {len(out)} unique passages ({duplicates} deduplicated IDs) -> {OUT}")


if __name__ == "__main__":
    main()
