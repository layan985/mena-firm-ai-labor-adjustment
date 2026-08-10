from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "data" / "pilot"
MANIFEST = PILOT_DIR / "source_archive_manifest.csv"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(
    manifest_path: Path,
    batch_paths: Iterable[Path],
    *,
    root: Path = ROOT,
    verify_files: bool = False,
) -> dict[str, int]:
    errors: list[str] = []
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))

    by_url: dict[str, dict[str, str]] = {}
    archived_urls = failed_urls = 0
    for line, row in enumerate(manifest_rows, start=2):
        url = str(row.get("source_url", "")).strip()
        if not url:
            errors.append(f"{manifest_path}: line {line}: empty source_url")
            continue
        if url in by_url:
            errors.append(f"{manifest_path}: line {line}: duplicate source_url {url}")
        by_url[url] = row
        status = str(row.get("status", "")).strip()
        digest = str(row.get("sha256", "")).strip().lower()
        if status == "archived":
            archived_urls += 1
            if not HASH_RE.fullmatch(digest):
                errors.append(f"{manifest_path}: line {line}: archived row has invalid SHA-256")
            if int(row.get("size_bytes") or 0) < 128:
                errors.append(f"{manifest_path}: line {line}: archived payload is too small")
            local_path = str(row.get("local_path", "")).strip()
            if not local_path:
                errors.append(f"{manifest_path}: line {line}: archived row has no local_path")
            elif verify_files:
                path = root / local_path
                if not path.is_file():
                    errors.append(f"{manifest_path}: line {line}: archive file is missing: {local_path}")
                elif HASH_RE.fullmatch(digest) and _sha256_file(path) != digest:
                    errors.append(f"{manifest_path}: line {line}: archive file hash mismatch: {local_path}")
        else:
            failed_urls += 1
            if digest:
                errors.append(f"{manifest_path}: line {line}: failed row unexpectedly carries a hash")

    bound_rows = 0
    pending_rows = 0
    for path in batch_paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for line, row in enumerate(csv.DictReader(handle), start=2):
                digest = str(row.get("source_sha256", "")).strip().lower()
                if not digest:
                    pending_rows += 1
                    continue
                bound_rows += 1
                url = str(row.get("source_url", "")).strip()
                manifest_row = by_url.get(url)
                if not HASH_RE.fullmatch(digest):
                    errors.append(f"{path}: line {line}: invalid source_sha256")
                elif manifest_row is None:
                    errors.append(f"{path}: line {line}: hash has no manifest URL")
                elif manifest_row.get("status") != "archived" or manifest_row.get("sha256") != digest:
                    errors.append(f"{path}: line {line}: batch hash does not match archived manifest bytes")

    if errors:
        raise ValueError("Source-manifest validation failed:\n- " + "\n- ".join(errors))
    return {
        "manifest_urls": len(by_url),
        "archived_urls": archived_urls,
        "failed_urls": failed_urls,
        "source_rows_bound_to_sha256": bound_rows,
        "source_rows_pending_sha256": pending_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate pilot source-manifest and batch hash bindings.")
    parser.add_argument("--verify-files", action="store_true", help="Re-hash every local archived file.")
    args = parser.parse_args()
    paths = sorted(PILOT_DIR.glob("research_batch_*_employment.csv")) + sorted(
        PILOT_DIR.glob("research_batch_*_ai_evidence.csv")
    )
    print(json.dumps(validate(MANIFEST, paths, verify_files=args.verify_files), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
