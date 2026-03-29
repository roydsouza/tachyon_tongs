# ADR-0087: Codified Substrate Hardening & Fail-Closed Mandates

## Status
Proposed

## Context
Following the Phase 1 and 2 security remediation, several critical anti-patterns were identified and permanently removed from the Tachyon Tongs substrate (e.g., Mutant Lock, silent exceptions, fail-open defaults). To prevent regressions by future agent sessions or automated models, these constraints must be codified into the core agent rules and workflows.

## Decision
We will formalize the "5 Absolute Prohibitions" into a new core security rule file (`.agent/rules/SEC-002.md`) and update the primary developer workflows.

### The 5 Absolute Prohibitions:
1.  **Mutant Lock Elimination**: Non-blocking integrity checks are strictly prohibited.
2.  **Explicit Error Handling**: Silent `pass` or `print()` in security-critical `except` blocks is banned; `logging.critical()` and re-raise is mandatory.
3.  **Environment-Gated Test Modes**: Class constructors must not accept test-flags; `TACHYON_TEST_MODE=1` is the sole source of truth.
4.  **Fail-Closed Defaulting**: All PDP/PEP logic must default to `DENY`.
5.  **Reliable Alerting**: Critical alerts must use synchronous fallbacks to ensure delivery.

### Mandatory Verification Ritual:
Every modification to agent code or core components must be followed by:
1.  `scripts/calibrate_sbom.py` (Provenance check)
2.  `scripts/forensics/resign_docs.py` (Audit anchoring)

## Consequences
- **Positive**: Prevents the re-introduction of "Deceptively Simple" vulnerabilities. Ensures all development is cryptographically traceable.
- **Negative**: Adds a minor overhead (15-30s) to each development cycle for hash calibration and re-signing.

---
*Signed by: Sentinel Agent*
*Date: 2026-03-28*
