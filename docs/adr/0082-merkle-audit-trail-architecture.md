# ADR-0082: Persistence: Merkle Audit Trail

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: Standard SQL-based logging is vulnerable to tampering. Even if the substrate is compromised at the root level, a malicious actor (or compromised agent) could rewrite history to hide their actions. To provide high-assurance forensic integrity, the execution record must be cryptographically immutable.

---

## 🧭 Decision

We implement a **Merkle-Linked Audit Trail** in the substrate's state tier (`tachyon/core/state.py`).

### 1. Cryptographic Hash-Chaining
- **Schema Extension**: The `forensic_events` table is extended with `previous_hash` and `hash` columns.
- **Linkage Logic**: Every new record N MUST include the SHA256 hash of record N-1.
- **Payload Hashing**: The hash of record N is computed as `H(agent_id | topic | details | timestamp | previous_hash)`.

### 2. Forensic Verification
- **Audit Tool**: We provide `scripts/forensics/verify_chain.py` to traverse the database and re-verify the integrity of every link in the chain.
- **Detection**: Any modification, deletion, or insertion in the middle of the chain results in a terminal `LINKAGE_VIOLATION` or `DATA_VIOLATION` alert.

---

## 🧬 Consequences

### ✅ Positive
- **History Immutability**: Provides a verifiable mathematical proof that the audit trail has not been tampered with.
- **Forensic Confidence**: Critical for trust-layer validation in Google AntiGravity operations.

### ⚠️ Negative
- **Performance Overhead**: Minor increase in write latency due to SHA256 computation and the 'Order by DESC Limit 1' lookup on every log entry.
- **Database Size**: Traceable increase in storage requirements for the 64-character hash strings.

---

## 🛠️ Performance Mandate
- Hash computation MUST be performed within the `_lock` to prevent race conditions during concurrent event logging.
- The `verify_chain.py` tool MUST be used during every system boot to ensure substrate integrity.
