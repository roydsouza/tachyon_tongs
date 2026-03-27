# ADR-0061: BaseAgentPlugin Fail-Loud Mandate

## Status
Accepted

## Context
In a complex agentic substrate, failures in individual plugins (such as execution errors or background loop crashes) can be difficult to monitor if they are only emitted as events to an asynchronous bus. High-priority forensic visibility is required to ensure that malfunctioning agents are immediately identified and audited.

## Decision
1.  **Fail-Loud Escalation**: All `BaseAgentPlugin` subclasses inherit a mandatory escalation path to the central `ALERT.md` hub.
2.  **Action Gating**: If a call to `run_action` results in an `ERROR` or `FATAL` status, the plugin MUST call `StateManager.emit_alert()` to record the failure in the forensic ledger.
3.  **Backplane Resilience**: Any unhandled exception in the background `_backplane_loop` must be escalated as an `AGENT_BACKPLANE_CRASH` alert.
4.  **Forensic Richness**: Alerts must include the `agent_id`, `plugin_name`, and the nature of the failure (e.g., the specific action or exception message).

## Consequences
- **Positive**: Eliminates "Silent but Broken" agent states where an agent stops responding or fails actions without alerting the human/master-agent.
- **Positive**: Centralizes all substrate-wide failures in a single high-signal file (`ALERT.md`).
- **Negative**: Adds a direct dependency on `StateManager` in the `BaseAgentPlugin` core (mitigated by existing singleton patterns).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0061",
  "hash": "sha256:a995c55021f73768e7c383fa44e95eedfd8a237bba486f4a055f51a7d67e78cd",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
