# ADR-0063: Chronicle: Temporal Oversight Mandate

## Status
Accepted

## Context
Standard firewalls and policy engines (like OPA) are typically stateless and evaluate actions in isolation. This makes them blind to "low-and-slow" attacks where a malicious agent performs a series of benign-looking actions that, in aggregate, represent a critical security breach (e.g., exfiltrating a dataset across 1,000 small fetches).

## Decision
1.  **Temporal Observability**: The substrate MUST maintain a persistent `forensic_events` ledger that records all high-signal agentic interactions.
2.  **Chronicle Agent**: A dedicated `Chronicle` agent will be deployed to continuously audit these trajectories.
3.  **Anomaly Detection**:
    - **Velocity Gate**: Detect agents performing actions at an impossible or suspicious frequency.
    - **Role Drift**: Detect agents performing actions that deviate from their historical "behavioral fingerprint."
4.  **Forensic Feedback**: Any detected temporal anomaly MUST be escalated to `ALERT.md` as a `TEMPORAL_ANOMALY`.

## Consequences
- **Positive**: Provides defense against multi-session attacks and compromised agent accounts.
- **Positive**: Enhances the forensic audit trail for post-incident investigation.
- **Negative**: Adds persistent storage requirements for the event history (mitigated by rotating/pruning secondary logs).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0063",
  "hash": "sha256:c2d107be328ce3a776901418645ae9f268371827af2203d176baf4a937daf960",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
