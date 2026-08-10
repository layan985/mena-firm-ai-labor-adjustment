from __future__ import annotations
from pathlib import Path
import hashlib
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "interim" / "ai_evidence_labeled.csv"
OUT = ROOT / "data" / "validation" / "blinded_ai_validation_sample.csv"
CODER1 = ROOT / "data" / "validation" / "coder_1.csv"


def deterministic_score(evidence_id: str, seed: str = "mena-ai-labor-v0.2") -> str:
    return hashlib.sha256(f"{seed}|{evidence_id}".encode()).hexdigest()


def select(df: pd.DataFrame, fraction: float = 0.20) -> pd.DataFrame:
    required = {"ai_evidence_id", "evidence_excerpt", "year", "ai_label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df["ai_evidence_id"].duplicated().any():
        raise ValueError("ai_evidence_id must be unique")
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")

    parts = []
    for label, g in df.groupby("ai_label", dropna=False):
        g = g.copy()
        g["_score"] = g["ai_evidence_id"].astype(str).map(deterministic_score)
        # Ceiling enforces the protocol's "at least 20%" requirement.
        n = max(1, math.ceil(len(g) * fraction))
        parts.append(g.sort_values("_score").head(n))

    sample = pd.concat(parts, ignore_index=True)
    sample["validation_id"] = sample["ai_evidence_id"].astype(str).map(
        lambda x: "VAL_" + hashlib.sha256(x.encode()).hexdigest()[:12].upper()
    )
    return sample.sample(frac=1, random_state=20260809).reset_index(drop=True)


def draw(df: pd.DataFrame, fraction: float = 0.20) -> pd.DataFrame:
    sample = select(df, fraction=fraction)
    blind = sample[["validation_id", "evidence_excerpt", "year"]].copy()
    blind["coder_label"] = pd.NA
    blind["coder_confidence"] = pd.NA
    blind["coder_notes"] = pd.NA
    return blind


if __name__ == "__main__":
    source = pd.read_csv(IN)
    selected = select(source)
    out = selected[["validation_id", "evidence_excerpt", "year"]].copy()
    out["coder_label"] = pd.NA
    out["coder_confidence"] = pd.NA
    out["coder_notes"] = pd.NA
    coder1 = selected[["validation_id", "ai_label"]].rename(columns={"ai_label": "coder_label"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    coder1.to_csv(CODER1, index=False)
    print(f"wrote {len(out)} blinded passages -> {OUT}; first-coder key -> {CODER1}")
