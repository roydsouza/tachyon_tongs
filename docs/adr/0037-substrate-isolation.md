# ADR-0037: Substrate Isolation & Document Hardening

## Status
**ACCEPTED** (2026-03-26)

## Context
During the Phase 35 Agent Consolidation (2026-03-23), the mechanical refactoring of the agent directory structure led to two critical failures:
1.  **Logic Regression**: The sophisticated reconnection capabilities of the Scout agent were partially lost, overwritten by a placeholder stub.
2.  **Document Pollution**: The Scout agent's test suite contained unisolated side-effects (hardcoded relative paths to production documentation). When tests were executed, "Mock" data was appended to the live `docs/COMPETITIVE_ANALYSIS.md`.

## Decision
We will implement a two-tier hardening strategy to prevent documentation pollution and ensure environmental isolation.

1.  **Environment Guards**: All agents that perform side-effects on production documentation (e.g., Scout, Sentinel) MUST check for `TACHYON_ENV=test` or `PYTEST_CURRENT_TEST`. If detected, these side-effects must be suppressed or redirected.
2.  **Test Isolation**: All test suites MUST use `pytest` fixtures (e.g., `tmp_path`, `tmp_path_factory`) for any file-writing tests. Hardcoded relative paths to root documentation are strictly prohibited in test code.
3.  **Handoff Integrity**: Agent consolidation must include a checklist to verify that all methods from the previous "code-only" or "hybrid" implementations are fully ported to the unified plugin.

## Consequences
- **Positive**: Documentation remains a high-signal, forensic record, free from test data.
- **Positive**: Tests are truly hermetic and portable.
- **Neutral**: Implementing new agents requires an extra step to handle environmental state.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0037",
  "hash": "sha256:01fc46881e1562cdf1dd2bde9b7dfd8d6fad42ef65e9896aede25182e4a8db77",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
