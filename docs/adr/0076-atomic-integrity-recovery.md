# ADR-0076: Atomic Integrity Recovery for Environmental Chaos

## Status
Proposed

## Context
Substrate integrity checks (PQC sigs) were previously vulnerable to TOCTOU and file-io race conditions. Specifically, a 150ms retry window allowed for file swapping after hash-check but before execution, and the bus verifier was non-deterministic due to whitespace variations.

## Decision
We will implement an **Atomic Read-Hash-Verify** pattern in `IntegrityManager.verify_integrity`.
1. **Read Entire Content**: The file is read into memory once.
2. **Hash and Verify**: The hash is computed and the signature is verified against the *identical* in-memory bytes, preventing any subsequent disk manipulation from corrupting the outcome.
3. **Fail-Closed Strategy**: Any disk-io error (e.g., Disk Full) results in a `DENIED` status, never allowing partially verified actions.

## Consequences
- **Security**: TOCTOU race window is eliminated.
- **Resilience**: The system is now robust against disk pressure during signature verification.
- **Observability**: Added forensic alerts for atomic hash mismatches.
