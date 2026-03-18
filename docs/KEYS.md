# Tachyon Tongs: Cryptographic Key Management & Lifecycle

This document serves as the authoritative reference for the cryptographic keys protecting the Tachyon Tongs substrate. It outlines the generation, rotation, and protection of these keys to maintain a high-assurance forensic baseline.

For a detailed analysis of attacks targeting these keys (e.g., exfiltration and leakage), see the [Key-Centric Threat Vectors](file:///Users/rds/antigravity/tachyon_tongs/THREAT_MODEL.md#5-key-centric-threat-vectors-the-root-of-trust) section of the Threat Model.

## 🛡️ Key Registry

| Key Name | Type | Purpose | Quantization | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TACHYON_SECRET_KEY` | HMAC-SHA256 (Symmetric) | Root of Trust for ADRs and Exploitation Catalog. | 256-bit | ACTIVE |
| `TACHYON_SESSION_TOKEN` | Bearer Token | Airlock Dashboard API Authentication. | 128-bit | PLANNED |
| `TACHYON_PQC_IDENTITY` | Dilithium3 (Asymmetric) | Post-Quantum Agent Attestation. | Asymmetric | BACKLOG |

## 🧬 Lifecycle Management

### 1. Generation
- **Method**: Keys MUST be generated using cryptographically secure random number generators (CSPRNG).
- **Tooling**: `openssl rand -hex 32` or equivalent OS-level entropy source.
- **Environment**: Generation should occur on a trusted local machine.

### 2. Storage & Injection (Anti-Entropy Protocol)
> [!IMPORTANT]
> **KEYS ARE NEVER STORED IN VERSION CONTROL.**
- **Storage**: Keys should be stored in a secured local password manager or hardware vault (e.g., Apple Keychain, Yubikey).
- **Injection**: Injected into the substrate via Environment Variables only.
- **Anti-Leakage**: The `.gitignore` and `IntegrityManager` specifically monitor for and block key file leakage.

### 3. Rotation & Compromise Response
- **Trigger**: Keys should be rotated if there is a suspected environment breach or as a quarterly security ritual.
- **Procedure**:
    1. Generate a new key.
    2. Update the local environment variable.
    3. Run `python3 scripts/sign_adrs.py` to re-baseline all forensic records.
    4. Commit the new `.sig` files to GitHub.

## 🚀 Evolutionary Roadmap

### Phase 1: Symmetric Root (Current)
- Usage of `HMAC-SHA256` for deterministic integrity.
- Focus on "Fail-Loudly" halt on missing keys.

### Phase 2: Asymmetric Attestation (Upcoming)
- Introduction of Dilithium3 (PQC) or Ed25519 (Classical) asymmetric pairs.
- Enables public verification and private signing, isolating the signing root.

### Phase 3: Hardware Root (Vision)
- Integration with Secure Enclaves or Yubikeys for physical-presence signing.
- Mandatory physical interaction for architectural mutations.

## ⚖️ Governance Workflow
Any modification to how keys are generated, stored, or utilized MUST be reflected in this document. The **`keybench-governor`** skill enforces consistency between the implementation and this registry.
