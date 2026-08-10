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


def _nonempty(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype("string").str.strip().ne("")


def validate_panel(df: pd.DataFrame) -> dict:
    if df["firm_id"].nunique() != 50:
        raise ValueError("Freeze requires exactly 50 unique firms")
    if len(df) != 400:
        raise ValueError("Freeze requires exactly 400 firm-years")
    if df[["firm_id", "year"]].duplicated().any():
        raise ValueError("Duplicate firm-year rows found")

    required = [
        "employees", "employment_missing_reason", "employment_source_id", "employment_source_page",
        "employment_source_sha256", "reporting_scope", "ai_label", "ai_search_complete",
        "ai_missing_reason", "source_retrieval_date"
    ]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    populated_emp = df["employees"].notna()
    missing_emp = ~populated_emp
    for c in ["employment_source_id", "employment_source_page", "employment_source_sha256", "reporting_scope"]:
        if df.loc[populated_emp, c].isna().any():
            raise ValueError(f"Employment observation lacks provenance: {c}")
    if missing_emp.any() and not _nonempty(df.loc[missing_emp, "employment_missing_reason"]).all():
        raise ValueError("Every missing employment observation requires employment_missing_reason")

    hashes = df.loc[populated_emp, "employment_source_sha256"].astype(str)
    if not hashes.map(lambda x: bool(HASH_RE.fullmatch(x))).all():
        raise ValueError("Malformed employment source SHA-256")

    search_complete = df["ai_search_complete"].astype("string").str.strip().str.lower()
    if not search_complete.isin(["true", "false", "1", "0", "yes", "no"]).all():
        raise ValueError("ai_search_complete must be explicitly true/false for every firm-year")
    ai_done = search_complete.isin(["true", "1", "yes"])
    if not ai_done.all():
        raise ValueError("Freeze blocked: AI search protocol is incomplete for one or more firm-years")

    labels = pd.to_numeric(df["ai_label"], errors="coerce")
    if labels.notna().any() and not labels.dropna().isin([0, 1, 2, 3]).all():
        raise ValueError("AI labels must be 0–3")
    no_label = labels.isna()
    if no_label.any() and not _nonempty(df.loc[no_label, "ai_missing_reason"]).all():
        raise ValueError("Every completed AI search without a label requires ai_missing_reason")

    return {
        "n_firms": int(df.firm_id.nunique()),
        "n_firm_years": int(len(df)),
        "employment_observations": int(populated_emp.sum()),
        "employment_missing": int(missing_emp.sum()),
        "employment_missing_reasons_documented": int(_nonempty(df.loc[missing_emp, "employment_missing_reason"]).sum()),
        "ai_search_complete": int(ai_done.sum()),
        "ai_labels_populated": int(labels.notna().sum()),
        "countries": sorted(df.country.dropna().astype(str).unique().tolist()),
        "sectors": sorted(df.sector.dropna().astype(str).unique().tolist()),
        "ai_label_counts": {str(k): int(v) for k, v in labels.value_counts(dropna=False).items()},
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
