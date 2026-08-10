from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
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


def _source_state(paths: list[Path]) -> tuple[set[str], dict[str, set[str]]]:
    unbound_urls: set[str] = set()
    expected_hashes: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                url = str(row.get("source_url", "")).strip()
                if not url.startswith(("https://", "http://")):
                    continue
                digest = str(row.get("source_sha256", "")).strip().lower()
                if HASH_RE.fullmatch(digest):
                    expected_hashes[url].add(digest)
                elif not digest:
                    unbound_urls.add(url)
    return unbound_urls, dict(expected_hashes)


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
        description="Archive only sources needed by unbound rows or missing manifest registrations."
    )
    parser.add_argument("--scope", choices=("employment", "ai", "all"), default="employment")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--max-bytes", type=int, default=250 * 1024 * 1024)
    args = parser.parse_args()

    paths = _batch_paths(args.scope)
    unbound_urls, expected_hashes = _source_state(paths)
    results = _load_manifest(MANIFEST)

    # Existing valid manifest rows remain authoritative. Fetch only sources needed
    # to bind a blank row, plus already-hashed research rows whose exact source has
    # not yet been registered in the manifest. For the latter, downloaded bytes
    # must reproduce the pre-existing immutable research-row hash exactly.
    needed_urls = set(unbound_urls)
    for url, hashes in expected_hashes.items():
        result = results.get(url)
        if (
            result is None
            or result.status != "archived"
            or not HASH_RE.fullmatch(result.sha256)
            or result.sha256 not in hashes
        ):
            needed_urls.add(url)

    to_fetch = sorted(
        url
        for url in needed_urls
        if (
            url not in results
            or results[url].status != "archived"
            or not HASH_RE.fullmatch(results[url].sha256)
            or (url in expected_hashes and results[url].sha256 not in expected_hashes[url])
        )
    )

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(archive_url, url, ARCHIVE_DIR, args.timeout, args.max_bytes): url
            for url in to_fetch
        }
        for future in as_completed(futures):
            result = future.result()
            expected = expected_hashes.get(result.source_url, set())
            if result.status == "archived" and expected and result.sha256 not in expected:
                raise ValueError(
                    "Downloaded bytes do not reproduce immutable research-row hash for "
                    f"{result.source_url}: got {result.sha256}, expected one of {sorted(expected)}"
                )
            results[result.source_url] = result
            print(json.dumps({"url": result.source_url, "status": result.status, "error": result.error}))

    # A previously registered source must also agree with any immutable row hash.
    for url, hashes in expected_hashes.items():
        result = results.get(url)
        if result and result.status == "archived" and HASH_RE.fullmatch(result.sha256):
            if result.sha256 not in hashes:
                raise ValueError(
                    f"Manifest hash conflicts with immutable research-row hash for {url}: "
                    f"manifest={result.sha256}, rows={sorted(hashes)}"
                )

    write_manifest(MANIFEST, results)
    updated_rows, updated_files = _bind_pending(paths, results)
    remaining_unbound, _ = _source_state(paths)
    summary = {
        "scope": args.scope,
        "unbound_urls_before": len(unbound_urls),
        "missing_manifest_bound_urls": len(needed_urls - unbound_urls),
        "fetched_urls": len(to_fetch),
        "updated_rows": updated_rows,
        "updated_files": updated_files,
        "remaining_unbound_source_urls": len(remaining_unbound),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
