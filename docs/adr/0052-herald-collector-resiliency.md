# ADR-0052: Herald Collector Resiliency

## Status
Accepted

## Context
The Herald agent's primary function is to aggregate findings from multiple data sources (collectors) and relay them to dispatchers. During the Get-Well audit (Priority 2), we identified a critical architectural weakness: any unhandled exception in a single collector (e.g., a locked SQLite database or a missing log file) would cause the entire `_collect_all` loop to terminate. This meant that a minor failure in "nice-to-have" telemetry (like `TaskCollector`) would blind the substrate to critical security alerts from the `AirlockCollector` or `ForensicCollector`.

## Decision
1. Implement individual `try-except` blocks for every collector invocation in `HeraldPlugin._collect_all`.
2. Failures are now isolated: if one collector crashes, the loop continues to the next, preserving maximum possible substrate awareness.
3. Every collector-level failure now emits a `HERALD_COLLECTOR_ERROR` event.
4. These error events are cryptographically signed with the agent's PQC certificate to ensure forensic auditability.

## Consequences
- **Positive**: Restores substrate resilience by preventing cascading failures in the telemetry relay.
- **Positive**: Enables automated "fail-loud" reporting for individual telemetry channels.
- **Negative**: May result in duplicate error reports if collectors fail persistently across relay cycles.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0052",
  "hash": "sha256:e6429b63379ba2ca48fc04a8fd38bb0ab084e580ccb008d7c61e20f7e8e5fd4c",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
