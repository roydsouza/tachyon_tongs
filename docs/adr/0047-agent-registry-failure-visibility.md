# ADR-0047: Agent Registry Load Failure Visibility

## Status
Accepted

## Context
During the Get-Well audit (Priority 1), we identified that the `AgentRegistry` was failing silently when a plugin could not be imported (e.g., due to a `SyntaxError` or missing dependency). The failure was merely printed to `stdout` and then discarded. Since these failures often occur during automated substrate startup, the operator would have no way of knowing that the defense collective was incomplete or compromised.

## Decision
1. Implement a module-level helper `_write_load_failure_alert` in `agents/_core/registry.py`.
2. This helper will append a structured `AGENT_LOAD_FAILURE` entry to `ALERT.md` whenever an agent plugin fails to load.
3. This provides a persistent forensic record that survives the process exit and is visible to forensic tools like the Herald.

## Consequences
- **Positive**: Eradicates the silent "missing agent" blindspot.
- **Positive**: Provides a diagnostic trail for broken agent plugins even before the EventBus is initialized.
- **Negative**: Adds a direct file dependency on `ALERT.md` within the registry logic, though this aligns with the substrate's "Fail-Loud" mandate.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0047",
  "hash": "sha256:915780508aeb8813f623d25103fbc256343a125af0798c66c126571b3e3f5042",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
