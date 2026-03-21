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

## 5. Agentic Observability & Control Operations
Phase 26.1 established a hardened Agent Control Plane. Operators must utilize the following subsystems to monitor and revoke autonomous behavior.

### 5.1 The Telemetry Bus
All agent actions, tool blocks, and cryptographic signatures are emitted as structured JSON objects.
- **Location**: `memory/operational/telemetry.jsonl`
- **Tailing Live Traffic**: 
  ```bash
  tail -f memory/operational/telemetry.jsonl | jq '.'
  ```
- **Auditing Blocked Intents**: To see exactly *why* the Policy Decision Point (PDP) rejected an agent's reasoning:
  ```bash
  cat memory/operational/telemetry.jsonl | jq 'select(.event_type == "TOOL_CALL" and .status == "BLOCKED")'
  ```
- **Forensic Key Binding**: Every time an agent signs an ADR or debate, it logs to the `AGENT_SIGNATURE` event stream, allowing operators to definitively assign algorithmic accountability to a specific sub-key.

### 5.2 Agent Revocation (The Kill Switch)
If an agent begins exhibiting severe alignment drift or if its ephemeral sub-key is compromised, the operator can isolate it instantly without needing to rotate the Sovereign Root Key.

1. **Locate the Fingerprint**: 
   Find the rogue agent's key fingerprint via the Telemetry Bus:
   ```bash
   cat memory/operational/telemetry.jsonl | jq 'select(.event_type == "AGENT_HEARTBEAT" and .agent_id == "rogue_agent_id")'
   ```
2. **Execute Revocation**:
   Open the Certificate Revocation List (CRL) at `memory/operational/revocation_list.json`.
   Add the fingerprint:
   ```json
   {
     "revoked_fingerprints": {
       "a1b2c3d4e5f6g7h8": {
         "revocation_date": "2026-03-20T23:00:00Z",
         "reason": "Severe Contextual Alignment Drift"
       }
     }
   }
   ```
3. **Heartbeat Failure**: Within seconds, the compromised agent's `async heartbeat()` will fail validation against the CRL, and it will be systematically isolated from the substrate.

---
**[✓] SIGNED BY ROOT KEY 1a2ff0...81047**
*Timestamp: 2026-03-20*
