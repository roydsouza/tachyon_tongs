# ADR-0053: Herald Legacy Dispatcher Forensic Alignment

## Status
Accepted

## Context
The legacy `herald_agent.py`, which operates as a standalone listener for external notifications, was found to have two critical issues:
1. **Broken Imports**: It referenced the pre-consolidation `tachyon.agents` package, causing a `ModuleNotFoundError` in the current environment.
2. **Invisible Misconfiguration**: If the `TACHYON_HERALD_ENDPOINT` environment variable was missing, the agent would logically fail to dispatch alerts and only record the failure on the internal EventBus. Since this agent is the primary bridge to external visibility, a misconfiguration in its setup is a recursive blindspot—it cannot use the channel it is supposed to bridge to report its own failure to exist.

## Decision
1. Normalize `herald_agent.py` imports to use the unified `agents._core.base` architecture.
2. Update the `_broadcast_alert` method to catch endpoint misconfigurations and write a high-priority forensic entry to `ALERT.md`.
3. Ensure the EventBus emission for the misconfiguration is correctly signed with the agent's PQC certificate.

## Consequences
- **Positive**: Restores functionality to the standalone Herald dispatcher.
- **Positive**: Ensures that the failure of the "External Visibility Bridge" is itself visible in the local forensic log.
- **Positive**: Aligns the legacy agent with the substrate's PQC-signing mandates.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0053",
  "hash": "sha256:163e4c5a5089c24213d72f8763d6d6cdfd7f7de5834d2b49b95e32abe669c8f7",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
