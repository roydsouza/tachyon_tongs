# ADR-0055: Agent Action Stub Standardization

## Status
Accepted

## Context
During the Get-Well audit (Priority 3), we identified a "correctness trap" in the `SynthesizerPlugin` and `ScoutPlugin`. Several experimental or future actions (network scouting, policy synthesis) were implemented as stubs that returned `{"status": "SUCCESS"}` alongside placeholder data. 
Downstream agents (like the `Engineer`) often check for `result["status"] == "SUCCESS"` before proceeding with structural changes or deployments. By returning a fake success signal, these stubs could mislead the collective into operating on placeholder data as if it were valid intelligence, leading to logical drift or security regressions.

## Decision
1. Normalize all non-functional agent stubs to return an explicit `NOT_IMPLEMENTED` status.
2. Include an informative `message` field explaining that the capability is not yet implemented.
3. This ensures that any calling agent's success-checks will correctly fail, preventing the propagation of placeholder data through the substrate.

## Consequences
- **Positive**: Eliminates a major source of potential logical drift in agentic orchestration.
- **Positive**: clearly distinguishes between "implemented and successful" and "legacy/future stub" paths.
- **Negative**: May cause existing draft integrations to fail early (this is the desired behavior).


## Integrity Attestation

```json
{
  "adr_id": "ADR-0055",
  "hash": "sha256:2a65b106f9249f345ed0e38c9fe8e7bf666e6b74d13a73342a2fe9037fe68578",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
