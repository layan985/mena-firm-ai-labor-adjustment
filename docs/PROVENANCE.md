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
