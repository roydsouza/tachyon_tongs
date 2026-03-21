# Tachyon Tongs: Admin Playbook & Operational Governance

This document establishes the official operational protocols for the **Tachyon Tongs** security substrate. It is intended for the human operator and the agent collective.

## 1. Cryptographic Governance
The substrate uses a hierarchical, hardware-bound signing model (Phase 25.2+).

### 1.1 Root of Trust (The Sovereign)
- **Primary**: Ed25519 key bound to macOS Keychain (Secure Enclave).
- **Secondary**: ML-DSA-65 (NIST Level 3) for PQC-Hybrid assurance. 
- **Recovery**: 3-of-5 Shamir Secret Sharing (SSS) of the **Expanded Secret Key** (4032 bytes).

### 1.2 Agent Delegation (The Vassals)
Agents do not hold the Root Key. They hold ephemeral Ed25519 sub-keys derived from the Root via HKDF.
- **Sentinel**: Signs threat intelligence and policy recommendations.
- **Engineer**: Signs patch proposals and code mutations.
- **Developer**: Signs session logs and administrative changes.

## 2. Emergency Procedures

### 2.1 The Resurrection Ceremony (Key Recovery)
If the host hardware is lost or compromised:

#### TIER 1: Ed25519 Root (Physical Anchor)
1. Retrieve 3 of 5 Ed25519 Shamir shares.
2. Run `tt keys recover`.
3. Provide shares to reconstruct the **Root Seed**.

#### TIER 2: ML-DSA-65 Root (Quantum Anchor)
1. Retrieve 3 of 5 PQC Shamir shares.
2. Run `tt keys verify-pqc`.
3. Provide shares to reconstruct the **Quantum Seed**.
4. Anchor to the new hardware Keychain.

### 2.2 Forensic Breach Response
If an ADR signature or Manifest checksum fails:
1. **HALT**: The substrate will enter safe-mode/Strict Mode automatically.
2. **AUDIT**: Inspect `memory/audit/signing_log.jsonl` for failed attestation attempts.
3. **ROTATE**: Perform a "Ritual" (`tt keys rotate`) to invalidate leaked sub-keys and derive new delegations.

## 3. Environment Integrity (SEC-001)
Operating the substrate requires absolute environment identity.
- **Mandatory Path**: `./venv/bin/python3 -m tachyon.cli.main`
- **Shell Shims**: Never run generic `python3` or `pip` without absolute pathing to avoid PEP 668 (externally-managed-environment) collisions and PATH shadowing.

## 4. Manifest Maintenance
The `ROOT_MANIFEST.json` is the sole source of truth for public key pinning.
- Any change to the Root Key requires a manual update and signing of the manifest.
- ADRs must be re-signed after structural modifications to maintain the forensic chain.

---
**[✓] SIGNED BY ROOT KEY 1a2ff0...81047**
*Timestamp: 2026-03-20*
