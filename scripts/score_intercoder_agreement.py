from __future__ import annotations
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "data" / "interim" / "ai_evidence_labeled.csv"
CODER2 = ROOT / "data" / "validation" / "coder_2.csv"
OUT = ROOT / "data" / "validation" / "agreement_results.json"


def validation_id(evidence_id: str) -> str:
    return "VAL_" + hashlib.sha256(str(evidence_id).encode()).hexdigest()[:12].upper()


def founder_key(labeled: pd.DataFrame) -> pd.DataFrame:
    required = {"ai_evidence_id", "ai_label"}
    missing = required.difference(labeled.columns)
    if missing:
        raise ValueError(f"Missing founder-label columns: {sorted(missing)}")
    out = labeled[["ai_evidence_id", "ai_label"]].copy()
    out["validation_id"] = out["ai_evidence_id"].map(validation_id)
    return out[["validation_id", "ai_label"]].rename(columns={"ai_label": "coder_label"})


def cohen_kappa(a, b, weights: str | None = None) -> float:
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    labels = np.array([0, 1, 2, 3])
    n = len(a)
    if n == 0:
        raise ValueError("No paired labels")
    cm = np.zeros((4, 4), dtype=float)
    for x, y in zip(a, b):
        cm[x, y] += 1
    observed = cm / n
    pa = cm.sum(axis=1) / n
    pb = cm.sum(axis=0) / n
    expected = np.outer(pa, pb)
    if weights is None:
        w = np.ones((4, 4)) - np.eye(4)
    elif weights == "quadratic":
        i, j = np.meshgrid(labels, labels, indexing="ij")
        w = ((i - j) / 3.0) ** 2
    else:
        raise ValueError("weights must be None or 'quadratic'")
    num = (w * observed).sum()
    den = (w * expected).sum()
    return float(1 - num / den) if den else 1.0


def score(c1: pd.DataFrame, c2: pd.DataFrame) -> dict:
    m = c1[["validation_id", "coder_label"]].merge(
        c2[["validation_id", "coder_label"]], on="validation_id", suffixes=("_1", "_2")
    ).dropna()
    if m.empty:
        raise ValueError("No complete paired labels")
    a = m["coder_label_1"].astype(int)
    b = m["coder_label_2"].astype(int)
    if not a.isin(range(4)).all() or not b.isin(range(4)).all():
        raise ValueError("Labels must be integers 0–3")
    return {
        "n_double_coded": int(len(m)),
        "raw_agreement": float((a == b).mean()),
        "cohen_kappa": cohen_kappa(a, b),
        "quadratic_weighted_kappa": cohen_kappa(a, b, weights="quadratic"),
        "confusion_matrix": pd.crosstab(a, b, dropna=False).to_dict(),
    }


if __name__ == "__main__":
    c1 = founder_key(pd.read_csv(LABELED))
    c2 = pd.read_csv(CODER2)
    result = score(c1, c2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))
