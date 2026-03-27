# ADR-0029: Agentic Observability, Telemetry, and Control

## Status
Accepted

## Context
As Tachyon Tongs matures toward Human-On-The-Loop (HOTL) and Human-Out-Of-The-Loop (HOOTL) operational modes, the observability of autonomous agents becomes a critical attack surface. Specifically, we identified three threat vectors related to Agentic Visibility and Control (Threat Model §13):
1. **Agent Observability Blindspot**: No centralized logging for agent tool invocations, key usage, or signature generation.
2. **Key Delegation Orphaning**: HKDF-derived agent keys have no formal certificate binding them to the Root, meaning there is no revocation mechanism.
3. **Agent Identity Spoofing**: No cryptographic binding between an agent's configured identity and its derived sub-key.

## Decision
We will implement an integrated Agentic Observability and Control layer:

1. **Structured Telemetry Bus**: Introduce `TelemetryBus` (`tachyon/core/telemetry.py`) to emit structured JSONL events (`memory/operational/telemetry.jsonl`) for all critical agent actions, including tool routing (both allowed and blocked) and cryptographic signatures (`AGENT_SIGNATURE`).
2. **JSON Delegation Certificates**: Introduce `DelegationCertificate` (`tachyon/core/keys/certificates.py`). When assigning a key to an agent, the Root will sign a JSON dict containing the agent's role, public key fingerprint, issue time, and expiration time.
3. **Agent Heartbeat Protocol**: Agents (`BaseTachyonAgent`) will periodically emit an `AGENT_HEARTBEAT` event validating their certificate against a centralized Certificate Revocation List (CRL).

## Consequences
- **Positive**: Complete forensic visibility into agent actions. Eradicates the observability blindspot.
- **Positive**: Long-lived agent keys can be reliably revoked.
- **Positive**: `ToolRouter` and `IntegrityManager` gain standardized, machine-readable audit trails.
- **Negative**: Adds overhead to tool routing and agent initialization, though JSONL writing is fast.

## Implementation Notes
The Telemetry Bus uses an atomic append strategy to `telemetry.jsonl` to ensure high-frequency multi-agent concurrency without SQLite locking overhead. Delegation certificates leverage the newly hardened Hybrid PQC (Ed25519 + ML-DSA-65) pipeline established in Phase 25.5.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0029",
  "hash": "sha256:ebd09d3ca55439683de31a0f97e3577948b3cb4540c8311653a36eab470cfb9c",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
