# ADR-0085: Consensus-Based Gating (Byzantine Fault Tolerance)

## Context
Critical substrate mutations (e.g., patching, policy updates) are currently single-agent approval actions. This creates a single point of failure and vulnerability to compromised administrators. Byzantine Fault Tolerance (BFT) requires a quorum for state transitions.

## Decision
We implement a **Consensus Engine** and integrate it with the **Airlock**:
1.  High-privilege actions (e.g., `APPROVE_PATCH`) enter a `PENDING` state.
2.  The `ConsensusEngine` collects votes (PQC-signed signatures) from multiple authorized roles (Admin, Auditor, Skeptic).
3.  The mutation is only applied to the database when a predefined quorum (e.g., 3/3 or 3/5) is reached.

## Consequences
-   **Security**: Prevents unauthorized substrate changes by a single compromised account.
-   **Stability**: Ensures multi-perspective review of security patches.
-   **Complexity**: Introduces state management for pending votes and quorum logic.

## Status
Approved (Phase 4)
