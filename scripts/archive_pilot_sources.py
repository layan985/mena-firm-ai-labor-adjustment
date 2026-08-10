from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "data" / "pilot"
ARCHIVE_DIR = ROOT / "data" / "raw" / "source_archive"
MANIFEST = PILOT_DIR / "source_archive_manifest.csv"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)
MANIFEST_FIELDS = [
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


@dataclass(frozen=True)
class ArchiveResult:
    source_url: str
    final_url: str = ""
    status: str = "error"
    sha256: str = ""
    local_path: str = ""
    mime_type: str = ""
    size_bytes: int = 0
    retrieved_utc: str = ""
    etag: str = ""
    last_modified: str = ""
    error: str = ""


def _batch_paths(scope: str) -> list[Path]:
    patterns = {
        "employment": ("research_batch_*_employment.csv",),
        "ai": ("research_batch_*_ai_evidence.csv",),
        "all": ("research_batch_*_employment.csv", "research_batch_*_ai_evidence.csv"),
    }[scope]
    return sorted({path for pattern in patterns for path in PILOT_DIR.glob(pattern)})


def collect_source_urls(paths: Iterable[Path]) -> list[str]:
    urls: set[str] = set()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                url = str(row.get("source_url", "")).strip()
                if url.startswith(("https://", "http://")):
                    urls.add(url)
    return sorted(urls)


def _extension(data_prefix: bytes, mime_type: str, url: str) -> str:
    if data_prefix.startswith(b"%PDF"):
        return ".pdf"
    if data_prefix.startswith(b"PK\x03\x04"):
        return ".zip"
    if data_prefix.startswith(b"\x89PNG"):
        return ".png"
    if data_prefix.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    mime = mime_type.lower()
    if "html" in mime:
        return ".html"
    suffix = Path(urlsplit(url).path).suffix.lower()
    return suffix if suffix in {".pdf", ".html", ".htm", ".json", ".xml", ".txt"} else ".bin"


def _validate_payload(prefix: bytes, size_bytes: int, mime_type: str) -> None:
    if size_bytes < 128:
        raise ValueError(f"response too small to be a research source ({size_bytes} bytes)")
    lower = prefix.lower()
    if any(marker in lower for marker in (b"access denied", b"request rejected", b"captcha")):
        raise ValueError("access-block page returned instead of source document")
    if "pdf" in mime_type.lower() and not prefix.startswith(b"%PDF"):
        raise ValueError("server declared PDF but payload has no PDF signature")


def _archive_name(url: str, extension: str, content_sha256: str = "") -> str:
    url_key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]
    version = f"-{content_sha256[:16]}" if HASH_RE.fullmatch(content_sha256) else ""
    return f"{url_key}{version}{extension}"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def archive_url(url: str, archive_dir: Path, timeout: float, max_bytes: int) -> ArchiveResult:
    retrieved = datetime.now(timezone.utc).isoformat()
    archive_dir.mkdir(parents=True, exist_ok=True)
    parts = urlsplit(url)
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
            "Referer": f"{parts.scheme}://{parts.netloc}/",
        },
    )
    temp_path: Path | None = None
    try:
        with urlopen(request, timeout=timeout) as response:
            mime_type = response.headers.get_content_type() or "application/octet-stream"
            digest = hashlib.sha256()
            prefix = bytearray()
            size = 0
            with tempfile.NamedTemporaryFile(dir=archive_dir, delete=False) as handle:
                temp_path = Path(handle.name)
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    if size > max_bytes:
                        raise ValueError(f"response exceeds max size of {max_bytes} bytes")
                    if len(prefix) < 8192:
                        prefix.extend(block[: 8192 - len(prefix)])
                    digest.update(block)
                    handle.write(block)
            _validate_payload(bytes(prefix), size, mime_type)
            sha256 = digest.hexdigest()
            extension = _extension(bytes(prefix), mime_type, response.geturl())
            destination = archive_dir / _archive_name(url, extension, sha256)
            os.replace(temp_path, destination)
            temp_path = None
            return ArchiveResult(
                source_url=url,
                final_url=response.geturl(),
                status="archived",
                sha256=sha256,
                local_path=str(destination.relative_to(ROOT)),
                mime_type=mime_type,
                size_bytes=size,
                retrieved_utc=retrieved,
                etag=response.headers.get("ETag", ""),
                last_modified=response.headers.get("Last-Modified", ""),
            )
    except (HTTPError, URLError, TimeoutError, IncompleteRead, ValueError, OSError) as exc:
        return ArchiveResult(source_url=url, retrieved_utc=retrieved, error=f"{type(exc).__name__}: {exc}")
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _load_manifest(path: Path) -> dict[str, ArchiveResult]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        out = {}
        for row in csv.DictReader(handle):
            row["size_bytes"] = int(row.get("size_bytes") or 0)
            out[row["source_url"]] = ArchiveResult(**{field: row.get(field, "") for field in MANIFEST_FIELDS})
        return out


def _cached_result(result: ArchiveResult) -> bool:
    if result.status != "archived" or not HASH_RE.fullmatch(result.sha256):
        return False
    path = ROOT / result.local_path
    if not path.is_file():
        return False
    digest = _sha256_file(path)
    return digest == result.sha256


def _version_cached_result(result: ArchiveResult, root: Path = ROOT) -> ArchiveResult:
    """Migrate legacy URL-only archive names without changing the bytes."""
    if result.status != "archived" or not HASH_RE.fullmatch(result.sha256):
        return result
    path = root / result.local_path
    if not path.is_file() or _sha256_file(path) != result.sha256:
        return result
    destination = path.parent / _archive_name(result.source_url, path.suffix, result.sha256)
    if destination != path:
        if destination.exists():
            if _sha256_file(destination) != result.sha256:
                raise ValueError(f"Content-addressed archive collision: {destination}")
        else:
            os.replace(path, destination)
    return replace(result, local_path=str(destination.relative_to(root)))


def write_manifest(path: Path, results: dict[str, ArchiveResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        for url in sorted(results):
            writer.writerow(asdict(results[url]))


def apply_hashes(paths: Iterable[Path], results: dict[str, ArchiveResult]) -> tuple[int, int]:
    updated_rows = 0
    updated_files = 0
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
        if "source_sha256" not in fieldnames:
            continue
        changed = False
        for row in rows:
            result = results.get(str(row.get("source_url", "")).strip())
            if result is None or result.status != "archived" or not HASH_RE.fullmatch(result.sha256):
                continue
            current = str(row.get("source_sha256", "")).strip().lower()
            if HASH_RE.fullmatch(current) and current != result.sha256:
                raise ValueError(f"Refusing to overwrite conflicting hash in {path.relative_to(ROOT)}")
            row_changed = False
            if current != result.sha256:
                row["source_sha256"] = result.sha256
                row_changed = True
            if "source_hash_status" in fieldnames and row.get("source_hash_status") != "archived_sha256_verified":
                row["source_hash_status"] = "archived_sha256_verified"
                row_changed = True
            if (
                "verification_status" in fieldnames
                and row.get("verification_status") == "source_verified_hash_pending"
            ):
                row["verification_status"] = "source_verified_hash_verified"
                row_changed = True
            if row_changed:
                updated_rows += 1
                changed = True
        if changed:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            updated_files += 1
    return updated_rows, updated_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive public pilot sources and bind research rows to exact bytes.")
    parser.add_argument("--scope", choices=("employment", "ai", "all"), default="all")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument("--max-bytes", type=int, default=250 * 1024 * 1024)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Write verified hashes back into research batch CSVs.")
    args = parser.parse_args()

    paths = _batch_paths(args.scope)
    urls = collect_source_urls(paths)
    results = _load_manifest(MANIFEST)
    results = {url: _version_cached_result(result) for url, result in results.items()}
    pending = [url for url in urls if args.refresh or url not in results or not _cached_result(results[url])]

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(archive_url, url, ARCHIVE_DIR, args.timeout, args.max_bytes): url for url in pending}
        for future in as_completed(futures):
            result = future.result()
            results[result.source_url] = result
            print(json.dumps({"url": result.source_url, "status": result.status, "error": result.error}))

    write_manifest(MANIFEST, results)
    updated_rows = updated_files = 0
    if args.apply:
        updated_rows, updated_files = apply_hashes(paths, results)

    archived = sum(results.get(url, ArchiveResult(url)).status == "archived" for url in urls)
    summary = {
        "scope": args.scope,
        "source_urls": len(urls),
        "archived_urls": archived,
        "failed_urls": len(urls) - archived,
        "updated_rows": updated_rows,
        "updated_files": updated_files,
        "manifest": str(MANIFEST.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
