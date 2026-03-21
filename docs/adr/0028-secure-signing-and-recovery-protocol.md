# ADR-0028: Secure Signing & Recovery Protocol (Genesis)

## Status
Proposed (Phase 25.1)

## Context
Tachyon Tongs is migrating from a flat HMAC-SHA256 "shared secret" model to a tiered, hardware-bound asymmetric architecture (Ed25519 + ML-DSA-44). The Root Key will reside in the Apple Silicon **Secure Enclave (SEP)**, making it physically non-extractable. This creates a critical availability risk: if the host hardware is lost or destroyed, the immutable chain of trust is broken.

## Decision
We will implement a **Genesis & Recovery Ceremony** that utilizes **Shamir's Secret Sharing (SSS)** over a 3-of-5 threshold to protect the Root Key derivation secret.

### 1. The Genesis Ceremony
1. **Derivation**: A high-entropy 256-bit `Root Seed` is generated.
2. **SSS Splitting**: the `Root Seed` is split into 5 shares using a `k=3` threshold.
3. **Hardware Anchoring**: the `Root Seed` is used to derive the Ed25519 private key *inside* the Secure Enclave. The seed is then scrubbed from memory.
4. **Share Distribution**: The 5 shares are stored in the following "Cold Storage" locations:
   - **Share 1**: Primary 1Password Vault (Digital Vault)
   - **Share 2**: Physical Safe Deposit (Physical Air-gap)
   - **Share 3**: Encrypted Cloud Archive (GPG-encrypted to Operator Key)
   - **Share 4**: Hardware Security Module (YubiKey 5 NFC)
   - **Share 5**: Printed Paper Backup (QR Code / Base58)

### 2. The Verification Ritual (Proof of Recovery)
To guarantee that the backup is ironclad without permanently storing the secret on disk, we implement a **Recovery Drill**:
1. **Drill Trigger**: Initiated via `tt keys verify-recovery`.
2. **Share Collection**: The operator provides 3 of 5 shares.
3. **Reconstruction**: The `Root Seed` is reconstructed in-memory.
4. **Signature Verification**: The reconstructed seed derives the *Public Key*. This Public Key is compared against the one currently on the `main` branch.
5. **Success**: If they match, the backup is proven valid. The reconstructed seed is immediately scrubbed from volatile memory.

### 3. Protection Against External Exposure (GitHub)
- **Zero Disk Persistence**: Private shares and seeds are NEVER written to the localized project directory.
- **Environment Isolation**: Temporary variables used during reconstruction are prefixed with `_TACHYON_MEM_` and explicitly cleared.
- **Git Hooks**: Pre-commit hooks specifically scan for the Shamir share format (typically prefixed with `sss-v1:`).

## Consequences
- **Positive**: 100% hardware isolation for active signing keys.
- **Positive**: Provable recovery path independent of host hardware.
- **Negative**: High operational "Ceremony" overhead (requires 3 locations/devices to be accessed).
- **Negative**: Risk of "Share Loss" if more than 2 locations are compromised or destroyed.

## Integrity Attestation
*(To be signed upon Phase 25.1 execution)*
