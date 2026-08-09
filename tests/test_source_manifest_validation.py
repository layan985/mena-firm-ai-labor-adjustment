import csv
from pathlib import Path

import pytest

from scripts.validate_source_manifest import validate


FIELDS = [
    "source_url",
    "final_url",
    "status",
    "sha256",
    "local_path",
    "mime_type",
    "size_bytes",
    "retrieved_utc",
    "etag",
    "last_modified",
    "error",
]


def _write_manifest(path: Path, digest: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(
            {
                "source_url": "https://example.org/report.pdf",
                "final_url": "https://example.org/report.pdf",
                "status": "archived",
                "sha256": digest,
                "local_path": "archive/report.pdf",
                "mime_type": "application/pdf",
                "size_bytes": 1024,
                "retrieved_utc": "2026-08-09T00:00:00+00:00",
            }
        )


def test_manifest_validation_accepts_exact_batch_binding(tmp_path: Path):
    digest = "a" * 64
    manifest = tmp_path / "manifest.csv"
    batch = tmp_path / "batch.csv"
    _write_manifest(manifest, digest)
    batch.write_text(
        f"source_url,source_sha256\nhttps://example.org/report.pdf,{digest}\n",
        encoding="utf-8",
    )
    summary = validate(manifest, [batch], root=tmp_path)
    assert summary["source_rows_bound_to_sha256"] == 1


def test_manifest_validation_rejects_hash_drift(tmp_path: Path):
    manifest = tmp_path / "manifest.csv"
    batch = tmp_path / "batch.csv"
    _write_manifest(manifest, "a" * 64)
    batch.write_text(
        f"source_url,source_sha256\nhttps://example.org/report.pdf,{'b' * 64}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not match"):
        validate(manifest, [batch], root=tmp_path)
