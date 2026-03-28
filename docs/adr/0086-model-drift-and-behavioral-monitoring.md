# ADR-0086: Model Drift & Behavioral Monitoring

## Context
Subtle compromises to models (local or remote) can manifest as "behavioral drift" (e.g., increased risk tolerance, verbosity shifts, performance anomalies) rather than hard failures. Detecting this requires statistical monitoring of agent metrics.

## Decision
We implement a **BehavioralMonitor** within the System Integrity tier:
1.  Collection of baseline metrics (mean/std dev) for agent `response_time`, `verbosity`, and `entropy`.
2.  Periodic (per-event) comparison of new metrics against the baseline.
3.  Emission of a `SECURITY_ALERT_DRIFT` if a 3-sigma deviation is detected over a window.

## Consequences
-   **Security**: Detects "Poisoning Attacks" and sophisticated "Cognitive Hijacking."
-   **Observability**: Provides insights into model quality and reliability over time.
-   **Performance**: Requires lightweight statistical tracking in the `StateManager`.

## Status
Approved (Phase 4)
