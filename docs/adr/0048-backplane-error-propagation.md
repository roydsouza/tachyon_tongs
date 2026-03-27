# ADR-0048: Backplane Error Propagation & Telemetry Signing Correctness

## Status
Accepted

## Context
During the Get-Well audit (Priority 1 and 4), we identified two critical blindspots in the core `BaseAgentPlugin`:
1. **Silent Backplane Errors (GW-04)**: Any exception thrown during a background event callback was printed to `stdout` but otherwise discarded. In a high-assurance substrate, these failures (e.g., a Healer plugin crashing due to a malformed payload) MUST be forensically recorded for auditing and recovery.
2. **Telemetry Signature Mismatch (GW-13)**: The `run_action` method was emitting `ACTION_COMPLETED` events with a raw `signature` parameter instead of the `certificate` parameter required by the PQC-aware EventBus (ADR-0043). This caused every agent action completion event to be suppressed by the bus.

## Decision
1. Update `BaseAgentPlugin._backplane_loop` to emit an `AGENT_CALLBACK_ERROR` event whenever a subscriber callback throws an unhandled exception. These events are signed with the agent's PQC certificate.
2. Update `BaseAgentPlugin.run_action` to pass the `certificate=self.certificate` parameter to the EventBus.
3. The raw signature of the `ActionRecord` (which provides non-repudiation for the specific action) will be included in the signed payload to preserve forensic integrity without breaking bus-level verification.

## Consequences
- **Positive**: Enables automated monitoring of agent crashes via the EventBus.
- **Positive**: Restores full visibility of agent action completions across the substrate.
- **Positive**: Maintains strict PQC verification for all telemetry.
- **Negative**: Adds a small amount of overhead by emitting error events on the bus.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0048",
  "hash": "sha256:3c0a81e4aea21c8c3e28bff9eb40a493fd50036a7561c70ea06158d4254bf1e1",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
