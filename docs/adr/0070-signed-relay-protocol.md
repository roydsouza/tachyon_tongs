# ADR-0070: Signed Command Relay Protocol

## Status
Proposed (2026-03-27)

## Context
Tachyon Tongs must act as a Single Pane of Glass for a distributed network of AI sensors and agents. Commands received from remote sensors (Transit Traffic) must be authenticated with absolute cryptographic certainty to prevent malicious injection or replay attacks in a post-quantum landscape.

## Decision
We implement a "Signed Relay" pattern in the `PEPLayer`. 

1. **Hybrid Signatures**: All remote commands must be enveloped in a `SignedCommand` structure containing a hybrid signature (Ed25519 + ML-DSA-65).
2. **Monotonic Nonce**: Each sensor must maintain a strictly increasing nonce to prevent replay attacks. The `StateManager` tracks the last-seen nonce for each trusted sensor.
3. **Public Key Exchange**: Sensors must register their public keys via `/api/v1/auth/exchange` before their relayed commands are accepted.
4. **Forensic Attribution**: Relayed commands are automatically tagged with `tenant_id` and marked as `source="transit"` in the forensic ledger.

## Consequences
- Remote sensors must be capable of generating hybrid signatures.
- Replayed commands are blocked at the PEP layer before reaching any isolation tier (WASM/VM).
- Every remote action is cryptographically anchored to a specific `signer_id`.
