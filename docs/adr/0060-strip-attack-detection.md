# ADR-0060: Strip Attack Detection & Keychain Context Hardening

## Status
Accepted

## Context
Background daemons (e.g., `launchd` Canaries) lack access to the interactive macOS Keychain, causing hardware-bound PQC and Ed25519 key loading to fail. This led to false-positive "PQC Signature MISSING" alerts because the verifying agent lacked the keys to acknowledge the PQC layer. Conversely, a true "Strip Attack" (maliciously removing the PQC layer) must be detected even by agents without private keys.

## Decision
1.  **Headless Key Fallback**: Implement a secure fallback in `KeychainProvider` that searches `memory/keys/` for Ed25519 and PQC keys if the Keychain is inaccessible.
2.  **Mandatory Signature Schema**: Enhance `HybridSigner.verify` to enforce PQC verification if a PQC component (`mldsa65:`) is present in the signature packet.
3.  **Cross-Context Verification**: If the verifying agent has the PQC public key (even without the private key), it MUST verify the PQC layer. Failure to verify a present PQC component is treated as a high-priority integrity breach.
4.  **STRICT_MODE Enforcement**: In `TACHYON_PQC_STRICT` mode, the PQC component is mandatory regardless of the signer's local key state.

## Consequences
- **Positive**: Eliminates false-positive signal fatigue in background security daemons.
- **Positive**: Hardens the substrate against "Strip Attacks" by making the PQC layer a mandatory, verifiable requirement across all contexts.
- **Negative**: Requires careful management of the `memory/keys/` directory for headless agents (mitigated by existing substrate-wide ADRs).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0060",
  "hash": "sha256:fbcaaba2ed82b46305b3058b5a01b6f6668747acc8d97908e6c6df43f5aad0a9",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
