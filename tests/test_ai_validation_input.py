from pathlib import Path

import pandas as pd
import pytest

from scripts.build_ai_validation_input import build


def _batch(path: Path, rows: list[dict]) -> Path:
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_validation_input_deduplicates_same_passage_across_batches(tmp_path: Path):
    row = {
        "evidence_id": "E1",
        "firm_id": "F1",
        "year": 2024,
        "ai_score": 2,
        "ai_label": "2_deployed",
        "evidence_excerpt": "deployed AI system",
        "source_url": "https://example.org/source",
        "source_sha256": "a" * 64,
    }
    out = build([_batch(tmp_path / "a.csv", [row]), _batch(tmp_path / "b.csv", [row])])
    assert len(out) == 1
    assert out.loc[0, "duplicate_batch_count"] == 2
    assert out.loc[0, "ai_label"] == 2


def test_validation_input_rejects_id_reuse_for_different_passages(tmp_path: Path):
    rows = [
        {
            "evidence_id": "E1",
            "firm_id": "F1",
            "year": 2024,
            "ai_score": 2,
            "evidence_excerpt": excerpt,
            "source_url": "https://example.org/source",
        }
        for excerpt in ("passage one", "passage two")
    ]
    with pytest.raises(ValueError, match="substantively different"):
        build([_batch(tmp_path / "batch.csv", rows)])
