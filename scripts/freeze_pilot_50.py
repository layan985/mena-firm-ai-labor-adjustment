from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "processed" / "firm_year_panel_v0.1.csv"
EVIDENCE = ROOT / "data" / "processed" / "ai_evidence_v0.1.csv"
AGREEMENT = ROOT / "data" / "validation" / "agreement_results.json"
FREEZE_DIR = ROOT / "data" / "freeze" / "v0.1-50firm"
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_panel(df: pd.DataFrame) -> dict:
    if df["firm_id"].nunique() != 50:
        raise ValueError("Freeze requires exactly 50 unique firms")
    if len(df) != 400:
        raise ValueError("Freeze requires exactly 400 firm-years")
    if df[["firm_id", "year"]].duplicated().any():
        raise ValueError("Duplicate firm-year rows found")
    required = ["employees", "employment_source_id", "employment_source_page", "employment_source_sha256",
                "reporting_scope", "ai_label", "source_retrieval_date"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    populated_emp = df["employees"].notna()
    for c in ["employment_source_id", "employment_source_page", "employment_source_sha256", "reporting_scope"]:
        if df.loc[populated_emp, c].isna().any():
            raise ValueError(f"Employment observation lacks provenance: {c}")
    hashes = df.loc[populated_emp, "employment_source_sha256"].astype(str)
    if not hashes.map(lambda x: bool(HASH_RE.fullmatch(x))).all():
        raise ValueError("Malformed employment source SHA-256")
    labels = df["ai_label"].dropna().astype(int)
    if not labels.isin([0, 1, 2, 3]).all():
        raise ValueError("AI labels must be 0–3")
    return {
        "n_firms": int(df.firm_id.nunique()),
        "n_firm_years": int(len(df)),
        "employment_observations": int(populated_emp.sum()),
        "employment_missing": int((~populated_emp).sum()),
        "countries": sorted(df.country.dropna().astype(str).unique().tolist()),
        "sectors": sorted(df.sector.dropna().astype(str).unique().tolist()),
        "ai_label_counts": {str(k): int(v) for k, v in df.ai_label.value_counts(dropna=False).items()},
    }


def freeze() -> dict:
    for p in [PANEL, EVIDENCE, AGREEMENT]:
        if not p.exists():
            raise FileNotFoundError(f"Freeze blocked; missing {p.relative_to(ROOT)}")
    panel = pd.read_csv(PANEL)
    summary = validate_panel(panel)
    agreement = json.loads(AGREEMENT.read_text())
    if agreement.get("n_double_coded", 0) < 1:
        raise ValueError("Freeze blocked: no completed double-coded validation set")
    FREEZE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "freeze_id": "v0.1-50firm",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "agreement": agreement,
        "objects": {
            str(PANEL.relative_to(ROOT)): sha256(PANEL),
            str(EVIDENCE.relative_to(ROOT)): sha256(EVIDENCE),
            str(AGREEMENT.relative_to(ROOT)): sha256(AGREEMENT),
        },
    }
    (FREEZE_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == "__main__":
    print(json.dumps(freeze(), indent=2))
