from __future__ import annotations

import argparse
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from archive_pilot_sources import (
    ARCHIVE_DIR,
    HASH_RE,
    MANIFEST,
    ArchiveResult,
    _batch_paths,
    _load_manifest,
    archive_url,
    write_manifest,
)


def _pending_urls(paths: list[Path]) -> set[str]:
    urls: set[str] = set()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                digest = str(row.get("source_sha256", "")).strip().lower()
                url = str(row.get("source_url", "")).strip()
                if not digest and url.startswith(("https://", "http://")):
                    urls.add(url)
    return urls


def _bind_pending(paths: list[Path], results: dict[str, ArchiveResult]) -> tuple[int, int]:
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
            current = str(row.get("source_sha256", "")).strip().lower()
            if current:
                # Existing bindings are immutable. This incremental command never refreshes them.
                continue
            url = str(row.get("source_url", "")).strip()
            result = results.get(url)
            if result is None or result.status != "archived" or not HASH_RE.fullmatch(result.sha256):
                continue
            row["source_sha256"] = result.sha256
            if "source_hash_status" in fieldnames:
                row["source_hash_status"] = "archived_sha256_verified"
            if (
                "verification_status" in fieldnames
                and row.get("verification_status") == "source_verified_hash_pending"
            ):
                row["verification_status"] = "source_verified_hash_verified"
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
    parser = argparse.ArgumentParser(
        description="Archive only source URLs needed by currently unbound research rows."
    )
    parser.add_argument("--scope", choices=("employment", "ai", "all"), default="employment")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--max-bytes", type=int, default=250 * 1024 * 1024)
    args = parser.parse_args()

    paths = _batch_paths(args.scope)
    urls = sorted(_pending_urls(paths))
    results = _load_manifest(MANIFEST)

    # A valid prior manifest binding is authoritative for incremental work even if
    # raw bytes are intentionally git-ignored. Full re-downloads belong to the
    # explicit refresh command, not the pending-row binder.
    to_fetch = [
        url
        for url in urls
        if url not in results
        or results[url].status != "archived"
        or not HASH_RE.fullmatch(results[url].sha256)
    ]

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(archive_url, url, ARCHIVE_DIR, args.timeout, args.max_bytes): url
            for url in to_fetch
        }
        for future in as_completed(futures):
            result = future.result()
            results[result.source_url] = result
            print(json.dumps({"url": result.source_url, "status": result.status, "error": result.error}))

    write_manifest(MANIFEST, results)
    updated_rows, updated_files = _bind_pending(paths, results)
    remaining = len(_pending_urls(paths))
    summary = {
        "scope": args.scope,
        "pending_urls_before": len(urls),
        "fetched_urls": len(to_fetch),
        "updated_rows": updated_rows,
        "updated_files": updated_files,
        "remaining_unbound_source_urls": remaining,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
