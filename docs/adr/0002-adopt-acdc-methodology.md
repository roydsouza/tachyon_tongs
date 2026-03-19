# ADR-0002: Adopt AC/DC Methodology

## Status
Accepted

## Context
Security-critical agents require a deterministic verification loop to prevent hallucinations from being committed to the core substrate.

## Decision
Adopt the **Agent Centric Development Cycle (AC/DC)**:
1. **Guide**: Plan in `memory/task_plan.md`.
2. **Generate**: Implementation via Agentic TDD (Test-First).
3. **Verify**: Deterministic validation via `pytest` and OPA audit.
4. **Solve**: Final memory reconciliation and task completion.

## Consequences
- **Positive**: High-assurance code quality.
- **Positive**: Forces verification before commitment.
- **Negative**: Slower development velocity compared to "vibe-coding."

## Integrity Attestation

```json
{
  "adr_id": "ADR-0002",
  "hash": "sha256:cca1a6b79e4005d1ff5fdec2d09873d8595a19b02fa42eb8c46de0e1a013148d",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
