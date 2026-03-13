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
