# ADR-0010: Centralized Meta-PDP Server and Authorization Ledger

## Status
Proposed (Phase 18)

## Context
As the Tachyon Tongs substrate scales, local policy evaluation becomes fragmented. We need a unified "Source of Truth" for authorization that is decoupled from the execution nodes. Furthermore, we need an "Absolute Audit" capability to prove *why* a decision was made, especially for regulatory compliance (HITL/HOTL/HOOTL).

## Decision
We are transitioning the policy layer to a **Centralized Meta-PDP Server**:

1.  **FastAPI Meta-Server**: A centralized service (running in `tachyon/policy/singularity/server.py`) that federates OPA, Cedar, Reputation, and Alignment engines.
2.  **Authorization Ledger**: A mandatory SQLite ledger (`memory/authorization_ledger.db`) that records every policy request and its full context (verdict, reason, timestamp, agent_id).
3.  **Fail-Closed Client**: The substrate-level PDP client will use REST to query the Meta-Server. If the server is unreachable, the client will **FAIL CLOSED** to maintain a zero-trust posture.

## Consequences
- **Positive**: Centralized policy management; 100% auditability; decoupled enforcement logic.
- **Negative**: Adds a network dependency for authorization; requires robust error handling for "Fail-Closed" scenarios.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0010",
  "hash": "sha256:2bc2d474d4cb80f92f846aa16c37ee3affebe5e987c07a02581faad2efdc33c5",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
