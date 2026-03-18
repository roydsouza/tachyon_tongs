# ADR-0009: Pathogen Adversarial Tuning & Automated Verification

## Status
Proposed (Phase 17)

## Context
As the substrate hardens, we need a systematic way to test its resistance to bypasses. Manual testing is insufficient for catching regression in complex regex patterns or policy logic. We need an automated adversarial layer ($Pathogen$) that generates mutated payloads and tracks their success.

## Decision
We are implementing the **Pathogen System**:

1.  **Mutation Engine**: A logic layer in `tachyon/agents/pathogen/` that applies ASCII smuggling, Unicode homoglyphs, and prompt injection variants to tool parameters.
2.  **Pathogen Metrics**: A SQLite-backed telemetry system to log every adversarial attempt, its mutation type, and whether it was blocked or successful.
3.  **Mandatory Regression Gating**: Every feature modification must pass the "Pathogen Sweep" to ensure no new bypasses were introduced.

## Consequences
- **Positive**: Proactive identification of weak points in our firewalls; quantitative metrics for substrate "hardness."
- **Negative**: Increased complexity of the test suite; requires maintaining a library of mutation techniques.
