# ADR-0065: Forensic UI and Telemetry Integration

## Status
Accepted

## Context
With the introduction of the `Chronicle` agent and DB-backed whitelisting, the substrate now generates high-signal forensic telemetry. This telemetry must be surfaced to the operator in real-time within the primary dashboard (`tt dash`) to ensure rapid response to anomalies and supply chain violations.

## Decision
1.  **Forensic Endpoint**: The Substrate API shall expose a `/api/v1/forensics` endpoint via the `StateBridge`.
2.  **Unified Schema**: Forensic events shall be standardized under the `ForensicAlert` Pydantic model.
3.  **TUI Integration**: The `TachyonDash` (Textual) shall include a dedicated `Forensic Feed` manifold displaying the last 5-10 high-signal events (e.g., `TEMPORAL_ANOMALY`, `SUPPLY_CHAIN_VIOLATION`).
4.  **Visual Semantics**: High-risk alerts (VIOLATION/ANOMALY) shall be highlighted within the TUI using Textual's rich formatting.

## Consequences
- **Positive**: Reduces "Time to Detection" (TTD) by providing immediate visual feedback on substrate-wide threats.
- **Positive**: Centralizes operational visibility in a single unified interface.
- **Negative**: Adds slight complexity to the TUI polling loop (mitigated by parallel `asyncio.gather`).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0065",
  "hash": "sha256:9ffcdfdb84a6242f68583bda090e84a982dc18458a497177819e2caf6bb72bfc",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
