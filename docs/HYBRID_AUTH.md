# 🔐 Tachyon Tongs: Hybrid ECC/PQC Authentication Architecture

To defend the L1 and L2 Intent Gates against "Harvest Now, Decrypt Later" cryptographic attacks by adversarial nation-states, **tachyon_tongs** assumes the imminent obsolescence of pure Elliptic-Curve Cryptography (ECC) for hardware handshakes.

This document outlines the upgrade path for the physical capability tokens (e.g., YubiKey FIDO2 integration).

## The Threat Landscape

Current Intent Gates request a physical touch to sign an attestation proving that a human authorized a high-risk sandbox execution (e.g., modifying system files). 
If an attacker harvests the agent's intent-logs, computational breakthroughs in quantum factoring (Shor's Algorithm) could allow them to spoof the signature in the future.

## Hybrid Signature Schema

Tachyon Tongs will transition to a **Hybrid Authentication Envelope**:

1. **Classical Signature (ECDSA / Ed25519)**
   - Maintains compatibility with existing FIDO2/WebAuthn hardware infrastructure.
   - Provides immediate, proven defense against classical computing attacks.

2. **Post-Quantum Signature (ML-KEM / Kyber)**
   - A lattice-based cryptographic signature wrapped *around* or *alongside* the ECC signature.
   - Requires an updated hardware enclave (e.g., next-generation smart cards or local Apple Silicon Secure Enclave wrappers) capable of Lattice operations.

### Implementation Blueprint

When an Agent attempts a highly-destructive action, the `ContextualIntentGate` scores the risk > 0.4 and triggers the `CHALLENGE` state.

```json
{
  "action": "CHALLENGE",
  "reason": "Unusual context boundaries triggered L1 Gate.",
  "required_auth": "HYBRID_ECC_PQC"
}
```

The Matchlock VM will pause execution until the host OS receives *both* a valid Ed25519 signature and a valid Kyber signature proving the human's intent to proceed.
