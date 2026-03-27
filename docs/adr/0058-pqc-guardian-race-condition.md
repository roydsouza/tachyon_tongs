# ADR-0058: PQC/Guardian Race Condition Resolution

## Status
Accepted

## Context
High-velocity substrate mutations (such as automated patching by the **Engineer**) can trigger a race condition where the **Guardian** (or other auditing agents) attempts to verify a file's integrity immediately after the content is modified but before the detached signature (`.sig`) has been fully flushed to the filesystem. This results in false-positive `INTEGRITY_VIOLATION` alerts.

## Decision
1.  Implement a **3-stage strategic retry loop** with exponential backoff in `IntegrityManager.verify_integrity`.
2.  **Stage 1**: Check for `.sig` file existence. If missing, wait 50ms.
3.  **Stage 2**: Second check for `.sig`. If still missing, wait 100ms.
4.  **Stage 3**: Final verification of content against the signature. If a verification exception or mismatch occurs, perform one final 50ms wait and retry to account for pending disk flushes.
5.  All signature writing operations (`sign_document`) must continue to use `os.fsync` to minimize the race window at the storage tier.

## Consequences
- **Positive**: Significantly increases the reliability of the "Fail-Loud" architecture by eliminating signal noise from I/O latency.
- **Positive**: Standardizes how the substrate handles asynchronous filesystem events.
- **Negative**: Adds a negligible latency (max 150ms-200ms) to verification calls only in the case of a missing signature.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0058",
  "hash": "sha256:656475405acdbf8c77637d1fa4d5e55b2ebc6d2fe123cfa42df7f609ced18c0c",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
