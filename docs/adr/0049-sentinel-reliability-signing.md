# ADR-0049: Sentinel Reliability & Hybrid PQC Signing

## Status
Accepted

## Context
During the Get-Well audit (Priority 2), we identified critical observability blindspots in the `SentinelPlugin` and `NVDClient`:
1. **Silent Failures**: The `hunt_new_threats` loop swallowed all per-keyword exceptions with a bare `continue`. If the NVD API failed for specific keywords (e.g., due to rate limits or malformed responses), the operator remained entirely unaware of the reduced scan coverage.
2. **Unsigned Telemetry**: Multiple lifecycle events (`SENTINEL_SCAN_STARTED`, `SENTINEL_THREAT_FOUND`, `SENTINEL_SCAN_COMPLETED`, `SENTINEL_COMM_FAILURE`) were being emitted without the agent's PQC delegation certificate. These events were subsequently suppressed by the EventBus verifier (ADR-0043).

## Decision
1. Implement structured error reporting in `NVDClient.hunt_new_threats`. Every keyword failure now emits a `SENTINEL_KEYWORD_FAILURE` event.
2. Update all telemetry emissions in the Sentinel agent to pass the `certificate=self.certificate` parameter.
3. Pass the agent's certificate down to the `NVDClient` to ensure its internal alerts are also verifiable.

## Consequences
- **Positive**: Restores full visibility into Sentinel scan coverage and API reliability.
- **Positive**: Ensures all vulnerability intelligence discovered by Sentinel is cryptographically trusted and verified by the substrate.
- **Negative**: Adds minor bus overhead for granular failure reports.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0049",
  "hash": "sha256:0053524f912bd0515bb9499d95cdb5f26b3607246e6761757ef532662d18df0e",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
