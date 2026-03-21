# Tachyon Tongs: Cryptographic Key Lifecycle & Management

**Version:** 1.0 (Phase 25 Specification)
**Date:** 2026-03-20
**Security Classification:** INTERNAL
**ADR Reference:** ADR-0028
**Operator Guide:** [docs/GENESIS_RECOVERY_CEREMONY.md](GENESIS_RECOVERY_CEREMONY.md)

---

## 1. Overview: The Trust Anchor

Tachyon Tongs employs a **tiered, hardware-bound cryptographic architecture** to ensure the integrity of its architectural decisions, code patches, and autonomic immune responses. This document details the lifecycle of every private key within the substrate, emphasizing our **Zero-Leak Policy** to ensure private keys never touch GitHub.

---

## 2. The Chain of Trust (Hierarchical Delegation)
Phase 25.2 introduces a **Vassal-Sovereign Delegation Model** to minimize the exposure of the hardware Root Key.

### 2.1 The Sovereign (Root Key)
- **Status**: [✓] **ANCHORED** to macOS Keychain.
- **Role**: Signs the `ROOT_MANIFEST.json` and delegates authority to agent sub-keys.
- **Protection**: Secure Enclave (SEP) hardware isolation.

### 2.2 The Vassals (Agent Keys)
- **Status**: [✓] **DERIVED** via HKDF-SHA256 from the Root.
- **Roles**:
    - **Sentinel**: Signs threat intelligence artifacts.
    - **Engineer**: Signs patch proposals and code mutations.
    - **Developer**: Signs administrative records and ADRs.
- **Protection**: Ephemeral (In-Memory Only). No disk persistence.

---

## 3. Key Inventory & Lifecycles

| Key Name | Role | Technology | Storage | Lifecycle | Rotation |
|----------|------|------------|---------|-----------|----------|
| **ROOT KEY** | The Trust Anchor | Ed25519 | **Apple Secure Enclave** | 10+ years | Never |
| **DEV KEY** | Daily Operations | Ed25519 | macOS Keychain | 90 days | Quarterly |
| **SENTINEL** | Threat Intel | Ed25519 | Resident Memory | 24 hours | Daily |
| **ENGINEER** | Auto-Patching | Ed25519 | Resident Memory | 7 days | Weekly |
| **AIRLOCK** | HITL Approval | Ed25519 | macOS Keychain | 7 days | Weekly |

---

## 3. Detailed Key Lifecycle Procedures

### 3.1 ROOT KEY (The Sovereign)
*   **Generation (The Genesis Ceremony)**: [✓] **VERIFIED**. Established on 2026-03-20.
*   **Fingerprint**: `1a2ff0fd4ab235bb010d76e3363d9d906ec88a4a9b86cebb61f48dea5ae81047`
*   **Hardware Binding**: [✓] **ANCHORED** to macOS Keychain via `pyobjc-framework-Security`.
*   **Backup (One-Time Execution)**: Immediately after generation, the **Seed** is split into 5 Shamir shares. These shares are displayed **once** in the terminal (hidden by default, revealed via Touch ID).
    *   **Receiving Shares**: You must manually copy each share to its designated cold-storage location. The substrate **never** writes these shares to disk.
*   **Protection**: Hardware-isolated. Operations (signing) happen inside the Enclave and are Touch ID-gated.
*   **Recovery (The Resurrection Ceremony)**: Triggered via `tt keys recovery`. You are prompted to input any 3 of the 5 shares.
    *   **Mechanism**: The substrate reconstructs the 256-bit Seed in memory, then re-derives and re-imports the key into the (new) hardware's Secure Enclave.
    *   **Conflict Resolution**: On an existing laptop, the OS will prompt before overwriting an existing key of the same name.
*   **Verification (The Proof of Recovery)**: After recovery, the substrate performs a **Signing Check**. It generates a dummy challenge, signs it with the recovered key, and verifies the signature against the **Public Key** stored in the repository. If `SIGN_OK`, the recovery is proven successful.
*   **Security Breach Protection**: The shares are generated **once only**. If an attacker obtains <3 shares, they have zero information. If you suspect compromise, you must perform a **Root Rotation** (Phase 25.1.5).

### 3.2 DEVELOPMENT KEY (The Operator)
*   **Generation**: Created in the macOS **System Keychain**.
*   **Protection**: Encrypted by the user's login password + Apple's Secure Enclave for wrapping.
*   **Usage**: Signs all ADRs (`docs/adr/`), `MANIFEST.json`, and issues temporary certificates to autonomous agents.
*   **Rotation**: Rotated every 90 days via `tt keys rotate --dev`.
*   **Roll**: Automated via CRL (Certificate Revocation List) update in the substrate's local state.

### 3.3 PHASE 3: Post-Quantum Hybrid (PQC)
*   **Target**: Quantum Resistance (NIST FIPS 204).
*   **Algorithm**: **ML-DSA-44** (Dilithium3).
*   **Hardware Limitation**: Current Apple Silicon (M5) does not natively support ML-DSA-44 in the Secure Enclave.
*   **Hybrid Strategy**: **The Hybrid Root**. We will use a dual-signature model:
    1.  `Signature A`: Hardware-bound Ed25519 (Security).
    2.  `Signature B`: Software-managed ML-DSA-44 (Quantum Resistance).
*   **Verification**: The substrate requires **both** signatures to pass for high-assurance artifacts.

### 3.3 AGENT KEYS (Sentinel / Engineer)
*   **Generation**: Ephemeral keys generated in-memory upon agent invocation.
*   **Protection**: Lives only in the agent's process memory (`Resident Memory`). Never written to disk.
*   **Usage**: The agent self-signs its discoveries (debates, catalog entries, proposed patches).
*   **Rotation**: Sentinel rotates daily; Engineer rotates weekly.
*   **Roll**: Old keys are simply discarded; the Development key issues a new delegation certificate for the next window.

---

## 4. Ironclad Protection: Prevent GitHub Leakage

We enforce a **Hard Isolation Boundary** to ensure no private key material is ever accidentally committed to version control.

### 4.1 Technical Gating (The "Zero-Leak" Boundary)
1. **Physical Isolation**: All private keys are stored in the **macOS Keychain** or **Secure Enclave**. These are OS-level databases that Git cannot even "see." No `.key` or `.pem` files exist in the project root.
2. **Deterministic `.gitignore`**: Our `.gitignore` enforces a "Deny-by-Default" policy for all potential key extensions:
   ```bash
   # Block all common key formats
   *.key
   *.pem
   *.sig_key
   *.pkcs8
   # Block entire local security directories
   .tachyon/keys/
   memory/keys/
   ```
3. **Pre-Commit Entropy Scan**: Every `git commit` triggers a `tt audit` hook that scans for high-entropy strings, blocking any line that looks like a private key.
4. **Agent Memory Purity**: Agents are architected to use `tachyon.core.signing` via a socket or internal API. They never physically touch a file containing a private key.

### 4.2 GitHub Action "Verify-Only" Policy
The CI environment (GitHub Actions) contains **Public Keys only**. 
*   **Action**: CI runs `tt verify` to check ADR and code signatures.
*   **Constraint**: CI lacks any private key. It is cryptographically incapable of signing. If an agent tries to "forge" a commit in CI, the verification step in the next local `tt ritual` will fail.

---

## 5. Summary: Key Flow

1. **You** authenticate via Touch ID to the **Root Key**.
2. **Root Key** authorizes the **Dev Key** for 90 days.
3. **Dev Key** authorizes the **Sentinel** to sign the Catalog for 24 hours.
4. **Sentinel** signs an exploit discovered in the wild.
5. **Airlock** (you + Touch ID) co-signs the mitigation.
6. **Result**: A forensically traceable, hardware-anchored security chain.

---
**End of Document**
