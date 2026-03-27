# ADR-0050: Engineer Agent Forensic Reporting & Signing

## Status
Accepted

## Context
During the Get-Well audit (Priority 2), we identified that the `EngineerPlugin`'s `AutoPatcher` operations lacked forensic visibility:
1. **Silent Test Failures**: If a patch application was followed by a failing regression test, the `EngineerPlugin` would return a failure status to the caller but would **not** emit an event on the substrate's EventBus. This prevented the `Healer` or other defensive agents from automatically observing and responding to regression risks.
2. **Missing PQC Signing**: The Engineer agent was not participating in the cryptographically anchored telemetry chain for its lifecycle events.

## Decision
1. Implement mandatory EventBus emissions for all `AutoPatcher` outcomes.
2. Specifically, emit `ENGINEER_PATCH_COMPLETED` on success and `ENGINEER_TEST_FAILURE` on verification failure.
3. Ensure all emissions carry the agent's `certificate` for PQC-verifiability.

## Consequences
- **Positive**: Restores substrate-wide visibility into the health of the automated patching pipeline.
- **Positive**: Enables automated "patch rollback" or "healing retry" logic in future phases.
- **Positive**: Anchors the Engineer's activities in the forensic audit trail.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0050",
  "hash": "sha256:fb0801bbfcf1c7af2aa621c5f3ca2844ca31e3c23a588268878617fae94677aa",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
