# Changelog

## 2.1.10 - 2025-11-14

- Bumped gosu runtime helper to v1.19 in Docker image.
- Version metadata updated for new release cycle.

## 2.1.9 - 2025-11-14

- Added Postman collection (`postman/ApiToolbox.postman_collection.json`) with sample requests for health, Base64, CSV, and admin endpoints.
- CSV to XLS workflow now supports multiple uploaded files, unique/sanitized sheet names, and unique table names per sheet.
- Admin UI warns when the default password (`change_me`) is still active.
- Added `AGENTS.md` with contributor guidelines and highlighted the Postman collection and CSV service behavior.
- Hardened config bootstrap (`config.py`) and entrypoint directory setup.

## 2.1.8 - 2025-11-14

- CSV to XLS service allows custom sheet names and sets proper MIME type for downloads.
- Base64 service enforces size limits even when `Content-Length` is missing.

## 2.1.7 - 2025-11-14

- Entry point ensures config/log directories exist before chown, fixing first-run crashes.
- README version alignment and settings auto-bootstrap.

## 2.1.6 - 2025-11-14

- Initial Codex-session baseline: Redis-backed sessions, admin panel, Base64 & CSV services.
