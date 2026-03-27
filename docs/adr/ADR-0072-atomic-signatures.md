# ADR-0072: Structured Atomic Signatures (v2.0)

## Status
Proposed (2026-03-27)

## Context
The current Tachyon Tongs signature system uses raw hex strings in `.sig` sidecars. The `verify_integrity` implementation in `tachyon/core/signing.py` utilizes a retry loop with `time.sleep()` to resolve race conditions with background agents. This creates a **Time-of-Check to Time-of-Use (TOCTOU)** vulnerability where an attacker can replace file content between the sig-check and the final file read.

Audit issue **[C-01]** mandates atomic verification to eliminate this race condition.

## Decision
We will transition from raw hex signature sidecars to a **Structured JSON Signature** format (`.sig.json`). This format will enable atomic "Read-Hash-Verify" operations.

### New Signature Format (`.sig.json`)
```json
{
  "version": "2.0",
  "hash": "sha256:[hex_hash]",
  "signature": "[pqc_signature_hex]",
  "timestamp": "2026-03-27T15:59:00Z",
  "algorithm": "mldsa65",
  "metadata": {
    "size": 1234,
    "origin": "tachyon-core"
  }
}
```

### Atomic Verification Workflow
1. Use `FileLock` (if available) or a single `open(filepath, 'rb')` to read the entire file into memory.
2. Immediately calculate the `sha256` hash of the in-memory content.
3. Read the `.sig.json` sidecar.
4. Compare the in-memory hash against the `hash` field in the sidecar.
5. Verify the PQC `signature` against the in-memory hash.
6. The entire process occurs without yielding control or sleeping, eliminating the TOCTOU window.

## Consequences
- **Security**: Eliminates the TOCTOU race condition in `verify_integrity`.
- **Performance**: High-frequency verification may see a slight increase in memory usage for large files (read entirely into memory), but reduction in disk I/O retries.
- **Compatibility**: Breaking change. Existing `.sig` files must be migrated to `.sig.json`. The `IntegrityManager` will be updated to handle both during a transition period, or a bulk migration script will be provided.
- **Forensics**: Metadata in the JSON format allows for better audit trails of when and where a file was signed.

## Signature
- **Signed By**: AntiGravity (Gemini Flash)
- **Identity**: `tt-agent-antigravity-001`
- **Method**: Hybrid PQC (ML-DSA-65)
