from __future__ import annotations
from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "interim" / "ai_evidence_labeled.csv"
OUT = ROOT / "data" / "validation" / "blinded_ai_validation_sample.csv"


def deterministic_score(evidence_id: str, seed: str = "mena-ai-labor-v0.2") -> str:
    return hashlib.sha256(f"{seed}|{evidence_id}".encode()).hexdigest()


def draw(df: pd.DataFrame, fraction: float = 0.20) -> pd.DataFrame:
    required = {"ai_evidence_id", "evidence_excerpt", "year", "ai_label"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df["ai_evidence_id"].duplicated().any():
        raise ValueError("ai_evidence_id must be unique")

    parts = []
    for label, g in df.groupby("ai_label", dropna=False):
        g = g.copy()
        g["_score"] = g["ai_evidence_id"].astype(str).map(deterministic_score)
        n = max(1, int(round(len(g) * fraction)))
        parts.append(g.sort_values("_score").head(n))

    sample = pd.concat(parts, ignore_index=True)
    sample["validation_id"] = sample["ai_evidence_id"].astype(str).map(
        lambda x: "VAL_" + hashlib.sha256(x.encode()).hexdigest()[:12].upper()
    )
    blind = sample[["validation_id", "evidence_excerpt", "year"]].copy()
    blind["coder_label"] = pd.NA
    blind["coder_confidence"] = pd.NA
    blind["coder_notes"] = pd.NA
    return blind.sample(frac=1, random_state=20260809).reset_index(drop=True)


if __name__ == "__main__":
    source = pd.read_csv(IN)
    out = draw(source)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"wrote {len(out)} blinded passages -> {OUT}")
