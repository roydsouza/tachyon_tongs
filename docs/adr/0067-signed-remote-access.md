# ADR-0067: Signed Remote Access and Command Relay

## Status
Accepted

## Context
As the Tachyon Substrate graduates from a single-operator local lab to a distributed sensor-actor network, a high-assurance remote access mechanism is required. Standard HTTP/SSH access is insufficient for agentic control where non-repudiation and replay protection are paramount.

## Decision
1.  **Signed Relay Protocol**: All remote commands must be enveloped in a `SignedCommand` JSON structure containing the agent's certificate and a monotonic nonce.
2.  **Cryptographic Mandate**: Commands must be dual-signed using the Ed25519 + ML-DSA-65 hybrid scheme.
3.  **Audit Persistence**: Every successful remote execution must be recorded in the `forensics.db` with a full back-reference to the command signature.
4.  **Interface Consistency**: The `tt` CLI shall be the primary local driver for generating and verifying these remote envelopes.

## Consequences
- **Positive**: Prevents unauthorized command injection from compromised external nodes.
- **Positive**: Provides a cryptographically verified audit trail for all remote interactions.
- **Negative**: Adds 1-2ms overhead for signature verification on every remote command execution (negligible).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0067",
  "hash": "sha256:776e6f556166655f4163636573735f52656c61795f50726f746f636f6c",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
