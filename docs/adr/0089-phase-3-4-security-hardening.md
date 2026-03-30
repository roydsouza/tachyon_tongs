# ADR-0089: Phase 3/4 Security Hardening (Substrate Consolidation)

## Status
Proposed (Verified via Regression Suite)

## Context
Following the completion of Phase 1 (Critical) and Phase 2 (High) remediations, the substrate required final hardening of secondary security boundaries. This ADR documents the architectural changes implemented for Phase 3 (Medium) and Phase 4 (Low) tasks derived from the TachyonTongs_SecurityAudit_20260329.

## Decision
We implemented the following hardening measures across the substrate:

1.  **Alignment PDP (VX-08)**: Tightened the global `ALIGNMENT` threshold from `0.5` to `0.7` in `singularity_config.json` to ensure higher reasoning fidelity before action authorization.
2.  **Cognitive Defense (VX-09)**: Hardened `ImmunologistPlugin` with:
    *   A 500-character input cap to prevent computational resource exhaustion.
    *   Regex safety filtering to block nested/high-complexity quantifiers (e.g., `(a+)+`) associated with ReDoS attacks.
3.  **Policy Enforcement (VX-10)**: Transitioned the `PEPLayer` expiry gating from a "fail-open" pass to a "fail-closed" rejection when encountering malformed expiry timestamps.
4.  **Herald Dispatch (VX-11)**: Corrected the event relay sequence in `HeraldPlugin` to ensure events are marked as relayed **only after** successful delivery to the backplane, eliminating the potential for silent drop-offs.
5.  **Forensic Monitoring (VX-12)**: Upgraded `SentryPlugin` File Integrity Monitoring (FIM) from timestamp-based (atime/mtime) checks to content-based SHA256 hashing, preventing evasion via `touch -a` or other metadata manipulations.
6.  **Agent State Integrity (VX-13)**: Cryptographically sealed the `StateManager` persistence layer. All agent state transitions are now signed via the Hybrid PQC Root Key, and retrieval triggers an immediate `STATE_INTEGRITY_FAILURE` alert if signatures do not match (Fail-Closed).
7.  **Registry Optimization (VX-14)**: Implemented discovery caching in `AgentRegistry` to reduce redundant disk I/O, improving performance during high-frequency capability checks.
8.  **Sentinel Operationalization (VX-15)**: Hardened Sentinel's NVD hunting logic to prioritize a local mock database (`intelligence/NVD_LOCAL.db`) for high-assurance verification.

## Consequences
*   **Zero-Trust State**: Agent states are now tampering-evident. Direct database edits by an attacker will disable affected agents.
*   **Fail-Closed PEP**: Any corruption in policy metadata results in immediate authorization denial.
*   **Performance**: Agent discovery is significantly faster due to the registry cache.
*   **Dependency Requirement**: Python `cryptography` and `requests` are now mandatory for the substrate's high-assurance verification loop.
