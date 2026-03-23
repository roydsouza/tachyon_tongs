# 🧼 Substrate Hygiene Protocol (SHP)

## Status
Active

## Goal
To maintain 100% architectural purity in the Tachyon Tongs substrate by preventing file clutter, stale test artifacts, and unmanaged temporary data.

## Rules
1.  **Root Purity**: The project root directory MUST remain clean. Only core configuration (`.yaml`, `README.md`, `TASKS.md`, `SYNC_LOG.md`) and package roots are permitted.
2.  **Test Isolation**: ALL permanent tests must reside in the `tests/` directory.
3.  **Transient Data**: Any temporary files, reproduction scripts, or transient test databases MUST be written to the `tmp/` directory.
4.  **No "test_*" in Root**: Files prefixed with `test_` or `repro_` are strictly prohibited in the root directory.
5.  **Automated Sanitation**: Use `python3 scripts/cleanup_substrate.py` periodically to purge `tmp/` and enforce root purity.
6.  **Library Organization**: All static and dynamic libraries (`.dylib`, `.so`, `.a`) MUST reside in the `lib/` directory.

---
*Signed by: Sentinel Agent*
*Date: 2026-03-23*
