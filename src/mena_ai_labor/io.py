from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def discover_raw_files(raw_dir: Path) -> list[Path]:
    return sorted(p for p in raw_dir.rglob("*") if p.is_file() and p.name != ".gitkeep")
