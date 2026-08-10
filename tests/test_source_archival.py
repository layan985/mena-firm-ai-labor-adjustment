from pathlib import Path

import pytest

from scripts.archive_pilot_sources import (
    ArchiveResult,
    _archive_name,
    _extension,
    _load_manifest,
    _version_cached_result,
    _validate_payload,
    apply_hashes,
    collect_source_urls,
    write_manifest,
)


def test_archive_name_is_deterministic_and_does_not_leak_url():
    url = "https://example.org/report.pdf?token=secret"
    assert _archive_name(url, ".pdf") == _archive_name(url, ".pdf")
    assert "secret" not in _archive_name(url, ".pdf")
    assert _archive_name(url, ".pdf").endswith(".pdf")


def test_archive_name_preserves_distinct_content_versions():
    url = "https://example.org/dynamic.html"
    first = _archive_name(url, ".html", "a" * 64)
    second = _archive_name(url, ".html", "b" * 64)
    assert first != second
    assert first.endswith("-aaaaaaaaaaaaaaaa.html")


def test_payload_validation_rejects_block_pages_and_false_pdfs():
    with pytest.raises(ValueError, match="access-block"):
        _validate_payload(b"<html>Access Denied" + b"x" * 200, 220, "text/html")
    with pytest.raises(ValueError, match="PDF signature"):
        _validate_payload(b"<html>not a pdf" + b"x" * 200, 220, "application/pdf")


def test_extension_prefers_magic_bytes_over_url_suffix():
    assert _extension(b"%PDF-1.7", "application/octet-stream", "https://example.org/download") == ".pdf"


def test_collect_source_urls_is_deduplicated(tmp_path: Path):
    batch = tmp_path / "batch.csv"
    batch.write_text(
        "source_url,source_sha256\nhttps://example.org/a,\nhttps://example.org/a,\nnot-a-url,\n",
        encoding="utf-8",
    )
    assert collect_source_urls([batch]) == ["https://example.org/a"]


def test_archive_result_defaults_to_auditable_failure():
    result = ArchiveResult("https://example.org")
    assert result.status == "error"
    assert result.sha256 == ""


def test_manifest_round_trip_can_preserve_results_from_other_scopes(tmp_path: Path):
    manifest = tmp_path / "manifest.csv"
    employment = ArchiveResult(
        "https://example.org/employment.pdf",
        status="archived",
        sha256="a" * 64,
        local_path="data/raw/employment.pdf",
        size_bytes=1024,
    )
    ai = ArchiveResult(
        "https://example.org/ai.html",
        status="archived",
        sha256="b" * 64,
        local_path="data/raw/ai.html",
        size_bytes=2048,
    )
    write_manifest(manifest, {employment.source_url: employment, ai.source_url: ai})
    loaded = _load_manifest(manifest)
    write_manifest(manifest, loaded)
    assert set(_load_manifest(manifest)) == {employment.source_url, ai.source_url}


def test_apply_hashes_completes_both_hash_status_fields(tmp_path: Path):
    batch = tmp_path / "batch.csv"
    batch.write_text(
        "source_url,source_sha256,source_hash_status,verification_status\n"
        "https://example.org/report.pdf,,pending_local_download_for_sha256,source_verified_hash_pending\n",
        encoding="utf-8",
    )
    digest = "c" * 64
    result = ArchiveResult("https://example.org/report.pdf", status="archived", sha256=digest)
    rows, files = apply_hashes([batch], {result.source_url: result})
    assert (rows, files) == (1, 1)
    text = batch.read_text(encoding="utf-8")
    assert digest in text
    assert "archived_sha256_verified,source_verified_hash_verified" in text


def test_legacy_archive_name_is_migrated_without_changing_bytes(tmp_path: Path):
    payload = b"%PDF-1.7\n" + b"x" * 200
    digest = __import__("hashlib").sha256(payload).hexdigest()
    old = tmp_path / "archive" / "legacy.pdf"
    old.parent.mkdir()
    old.write_bytes(payload)
    result = ArchiveResult(
        "https://example.org/report.pdf",
        status="archived",
        sha256=digest,
        local_path="archive/legacy.pdf",
        size_bytes=len(payload),
    )
    migrated = _version_cached_result(result, root=tmp_path)
    assert migrated.local_path.endswith(f"-{digest[:16]}.pdf")
    assert (tmp_path / migrated.local_path).read_bytes() == payload
