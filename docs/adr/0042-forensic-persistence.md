# ADR-0042: Unified Forensic Ledger & Mutant-Lock Service

## Status
Proposed (Phase 42)

## Context
Current substrate logging is decentralized across multiple Markdown files (`ALERT.md`, `RUN_LOG.md`, `EVOLUTION.md`). While human-readable, this approach has several technical limitations:
1.  **Concurrency Fragility**: Relying on `flock()` for Markdown files is prone to race conditions under high agentic load (e.g., Pathogen + Sentry + Engineer running simultaneously).
2.  **TOCTOU Risks**: Markdown files can be modified out-of-band without the substrate's immediate knowledge, creating a forensic gap.
3.  **Search Performance**: Aggregating actionable summaries (The Herald) requires parsing thousands of lines of Markdown, which scales poorly.
4.  **Locking Logic**: The current "Mutant-Lock" is a simple lock-file mechanism that lacks auto-expiry, risking substrate-wide deadlocks if an agent crashes while holding a lock.

## Decision
We will consolidate forensic persistence into a **Unified SQLite Ledger** and a dedicated **Mutant-Lock Service**.

### 1. Unified Forensic SQLite Ledger
We will implement `tachyon/core/forensics.py` which manages `memory/operational/forensics.db`.
- **Schema**: `forensic_log(id PRIMARY KEY, timestamp, agent_id, event_type, action, status, details JSON, signature BLOB)`.
- **Integrity**: Every entry will be cryptographically signed (ML-DSA-65) by the substrate or the originating agent before insertion.
- **Materialization**: To maintain human-readability, a background cleaner will "materialize" critical events back into Markdown summaries for quick review.

### 2. Mutant-Lock Service
A new `LockManager` will replace the file-based logic in `StateManager`:
- **Secure Enclave Tokens**: Locks will be issued with unique UUIDs.
- **Auto-Expiry**: All locks will have a mandatory TTL (default 60s). An agent must heart-beat to keep a lock if an operation takes longer.
- **Fail-Safe**: Any attempt to acquire an expired lock will trigger a re-tabulation of the lock state.

### 3. Herald SQL Monitor
**The Herald** will be refactored to use the SQL Ledger as its primary data source.
- `tt_herald status` will query for the latest high-priority alerts across all categories.
- `tt_herald tail` will use SQLite's `RETURNING` or periodic polling of the ID sequence to stream new events.

## Consequences
- **Robustness**: Significant improvement in concurrent log integrity.
- **Visibility**: Faster, richer status reporting for the operator via Herald.
- **Complexity**: Introducing SQLite as a hard dependency (already used by `TachyonEventBus`, so this is a consolidation).
- **Forensics**: Guaranteed append-only behavior for signed audits.
