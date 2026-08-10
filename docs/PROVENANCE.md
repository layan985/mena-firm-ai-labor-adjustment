# Provenance

Every raw document receives:

- source name
- canonical URL
- retrieval UTC timestamp
- SHA-256
- MIME type
- access/license note
- parser version

Every extracted value receives, where possible:

- raw document hash
- page number
- extraction method (`table`, `regex`, `manual`, `ocr_last_resort`)
- evidence passage hash
- manual-review status

Corrections never overwrite silently. Add a correction record with old value, new value, reason, reviewer and timestamp.

## Public-source archival

`python scripts/archive_pilot_sources.py --scope all --apply` downloads each public
employment and AI-evidence source into the ignored local archive, validates that
the response is not an access-block page, calculates SHA-256 on the exact bytes,
writes a versioned `data/pilot/source_archive_manifest.csv`, and binds the hash
back to every matching research row.

The byte archive remains uncommitted until redistribution rights are reviewed.
Its filenames combine a URL-derived key with a content-hash version key, so a
refresh of a dynamic web page cannot overwrite the exact bytes retrieved earlier.
The manifest is public: it records canonical and final URLs, retrieval time,
MIME type, byte size, ETag/Last-Modified metadata when supplied, SHA-256, and any
retrieval failure. Existing valid but conflicting hashes are never overwritten.

`python scripts/validate_source_manifest.py --verify-files` re-hashes every local
archive file and fails if a batch row's SHA-256 is malformed, absent from the
manifest, or different from the archived bytes bound to that source URL.
