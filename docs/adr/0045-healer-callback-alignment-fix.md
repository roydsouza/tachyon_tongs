# ADR-0045: Healer Callback Alignment & PQC Telemetry Fix

## Status
Accepted

## Context
During the Get-Well audit (Priority 1), we identified that the `HealerPlugin` was effectively dead on the EventBus. Two critical issues were found:
1. **Signature Mismatch**: The base class `BaseAgentPlugin` routes events to callbacks with a single `payload` argument. However, `HealerPlugin` was expecting five arguments (`topic`, `sender`, `payload`, etc.), causing immediate `TypeError` crashes which were silently swallowed by the backplane's error handling.
2. **Signature Suppression**: Telemetry events were being emitted with a string literal `signature="INFO"`. The substrate's PQC verifier (as of ADR-0043) rejects any non-cryptographic signature, causing all Healer status reports to be suppressed by the bus.

## Decision
1. Refactor all `HealerPlugin` callbacks to accept only the `payload` dictionary.
2. Extract metadata (like `sender`) from the payload itself using safe `.get()` methods.
3. Update all `emit_event` calls to use `certificate=self.certificate` to ensure PQC-level authenticity.

## Consequences
- **Positive**: Restores event-driven remediation loops.
- **Positive**: Ensures Healer telemetry is verifiable and trusted by the collective.
- **Negative**: Minor decoupling from internal backplane metadata, now reliant on payload structure.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0045",
  "hash": "sha256:109337126d4b64ab7acec2dd95ceb96cfdba26ebb42661738e20fa4013ebe9f1",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
