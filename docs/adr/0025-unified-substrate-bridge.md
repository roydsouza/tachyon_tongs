# ADR-0025: Unified CLI & Terminal Integration

## Status
Proposed/Signed

## Context
Tachyon Tongs originally used a split daemon architecture:
- PEP/Action Daemon on port 60461.
- Airlock/Telemetry Daemon on port 60462.

Phase 24 (Event-Horizon Command Bridge) introduces a 3-tier interface (CLI, TUI, NeoVIM). Maintaining parity across three ports and two separate server instances increases entropy, complicates audit trails, and fragments the operator's "Single Pane of Glass" vision.

## Decision
We will consolidate the Substrate Daemon into a single, unified FastAPI application:
1.  **Unified Port**: All operations (Actions, Status, Airlock, Telemetry) will move to port `60461`.
2.  **State Bridge**: Implementation of `tachyon.core.state_bridge` to provide high-assurance mapping between the SQLite database and Pydantic API models.
3.  **Modular PEP**: Action execution logic is refactored into `tachyon.api.pep` to keep the server entrypoint clean.
4.  **WebSocket Consolidation**: A single WebSocket endpoint `/api/v1/logs/stream` will handle all real-time telemetry.

## Consequences
- **Positive**: Simplified configuration for all tiers; consistent data view across CLI, TUI, and NeoVim; easier security auditing of a single process.
- **Negative**: Single point of failure (if the unified daemon crashes, both control and telemetry are lost); requires refactoring legacy tests that expect the split port.

## Signed
- [x] Sentinel Agent (Integrity Check)
- [x] Engineer Agent (Implementation)
- [x] Operator (Final Approval)


## Integrity Attestation

```json
{
  "adr_id": "ADR-0025",
  "hash": "sha256:eb2293540013f1560f428ae691b4a8301572bc326e4bcd0c97dc191f8eafccd4",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
