# Question:



This is my Agentic Firewall , "Tachyon Tongs", which I am developing. 
I want to enhance my software development process to make it more modern, 
more secure, maybe even simpler and transparent. 
I currently have ADR records that are signed and written whenever a change 
is made to the architecture for forensics and intrusion detection reasons. 
I would like your help in optimizing my development and testing process for 
delivering (building, deploying, updating, etc...) an Agentic Firewall safely 
and securely, but also efficiently. Currently we use HMAC for the ADR signing, 
and the key management is murky. I'd like to enhance the signing process to be 
more secure - perhaps an asymmetric signature scheme, with keys protected by my Apple macbook. 
(But what if I need to recover to a different macbook from backup?). 
Also is it practical to move to a hybrid, quantum-ready scheme at this time? 
Should we give each agent its own signing keys? etc... 
you see my line of questioning? I want to make the development process more secure, 
and to ensure the Threat Model addresses all possible exploits here. 
If you have ideas about moving files and directories around in the pursuit of 
security and secure development, please let me know. 
I would appreciate a deep and comprehensive markdown file I can feed to Antigravity to execute on.


# Answer:

I'll help you create a comprehensive security enhancement plan for Tachyon Tongs. Let me first examine your current implementation to understand the architecture and then provide detailed recommendations.Now I'll create a comprehensive security enhancement plan for your Tachyon Tongs development process:I've created a comprehensive security enhancement plan for Tachyon Tongs. Here are the key recommendations:

## Critical Upgrades

**1. Cryptographic Migration: HMAC → Ed25519 + ML-DSA-44 (Hybrid)**
- Move from symmetric HMAC to asymmetric signatures for true non-repudiation
- Add quantum-resistant ML-DSA-44 (NIST's post-quantum standard) for future-proofing
- Hybrid approach gives you classical security now + quantum resistance later

**2. Apple Secure Enclave for Root Keys**
- Store your master signing key in Secure Enclave (hardware-protected, non-extractable)
- Requires Touch ID for signing operations
- Survives OS compromise and malware

**3. Key Recovery Strategy**
- Shamir Secret Sharing: split root key into 5 shares, any 3 reconstruct
- Distribute across: 1Password, trusted colleague, bank safe, YubiKey, encrypted S3
- Development keys sync via iCloud Keychain for easy recovery

**4. Per-Agent Key Hierarchy**
```
Root Key (Secure Enclave) → Development Key (Keychain) → Agent Keys (Daily rotation)
```
- Sentinel gets its own key, rotates daily, limited to signing debates/catalog
- Airlock gets separate key requiring human approval
- Delegation certificates define exact authorization scope

**5. Project Restructuring**
- Separate `runtime/` (logs, debates, tasks) from source code
- Encrypt secrets with `age`, keep encrypted versions in Git
- Move sensitive data out of main repo structure

## Is PQC Practical Now?

**YES** - for a security-critical project like an agentic firewall:
- NIST standards finalized August 2024
- ML-DSA-44 adds only ~2.4KB per signature and ~1ms overhead
- Libraries available (`liboqs-python`, OpenSSL 3.2+)
- "Harvest now, decrypt later" attacks are real
- Hybrid mode means you lose nothing if PQC proves buggy

## Implementation Timeline

The plan includes a 12-week phased rollout:
- **Weeks 1-2:** Ed25519 foundation + Secure Enclave + key backup
- **Weeks 3-4:** Per-agent keys + delegation certificates
- **Weeks 5-6:** Add ML-DSA-44 hybrid signatures
- **Weeks 7-8:** Directory restructure + secrets encryption
- **Weeks 9-10:** CI/CD hardening + pre-commit hooks
- **Weeks 11-12:** Documentation + team training

## Immediate Next Steps

Feed the markdown file to Antigravity and start with Phase 1:
1. Install dependencies: `cryptography`, `pynacl`, `liboqs-python`
2. Generate root key in Secure Enclave
3. Create Shamir shares (3-of-5) and distribute securely
4. Implement basic Ed25519 signing/verification scripts

The document includes complete code examples, migration scripts, threat model updates, and operational runbooks ready for implementation.

# Tachyon Tongs: Security Enhancement & Modernization Plan

**Version:** 1.0  
**Date:** 2026-03-20  
**Status:** Proposal for Implementation via Antigravity

---

## Executive Summary

This document provides a comprehensive roadmap to transform Tachyon Tongs' development and security posture from HMAC-based symmetric signing to a modern, quantum-ready, hardware-backed asymmetric signature infrastructure. The plan addresses key management, recovery scenarios, per-agent key delegation, threat modeling, and architectural reorganization.

**Key Objectives:**
1. Upgrade from HMAC to asymmetric signatures (Ed25519 + optional PQC)
2. Leverage Apple Secure Enclave for root key protection
3. Implement robust key recovery and multi-device support
4. Establish per-agent key hierarchy with clear audit trails
5. Reorganize project structure for security and operational clarity
6. Update threat model to address modern supply chain and agent-based attacks

---

## 1. Cryptographic Migration Strategy

### 1.1 Current State Assessment

**Problems with HMAC Signatures:**
- **No Non-Repudiation:** Symmetric keys mean anyone with the key can forge signatures
- **Key Distribution Risk:** HMAC key must be shared across systems
- **No Identity Binding:** Can't prove *who* signed, only that *someone* with the key signed
- **Recovery Complexity:** Losing the key means losing all signature verification capability
- **Murky Key Management:** As you noted, unclear where keys live and how they're rotated

**Current Signing Artifacts:**
```
debates/DEBATE_*.md.sig
EXPLOITATION_CATALOG.md.sig
docs/adr/*.sig (presumably)
```

### 1.2 Target Architecture: Hybrid Asymmetric + Post-Quantum

**Primary Recommendation: Ed25519 + ML-DSA-44 (Hybrid)**

**Ed25519 Benefits:**
- Fast, small signatures (64 bytes)
- Deterministic (no random number generator failures)
- Side-channel resistant implementation available
- Well-supported in macOS, Python, and Git ecosystem
- Industry standard (SSH keys, GPG, etc.)

**ML-DSA-44 (Module-Lattice Digital Signature Algorithm - FIPS 204):**
- Formerly CRYSTALS-Dilithium
- NIST-selected post-quantum signature scheme
- Security Category 2 (~128-bit security)
- Practical signature size (~2420 bytes for ML-DSA-44)
- Available in `liboqs-python` and OpenSSL 3.2+

**Hybrid Approach:**
```
Final Signature = Ed25519(content) || ML-DSA-44(content)
Verification = Verify(Ed25519) AND Verify(ML-DSA-44)
```

**Migration Timeline:**
- **Phase 1 (Immediate):** Deploy Ed25519 signing for all new artifacts
- **Phase 2 (3 months):** Add ML-DSA-44 alongside Ed25519 (hybrid mode)
- **Phase 3 (6 months):** Re-sign all historical artifacts with hybrid signatures
- **Phase 4 (Ongoing):** Monitor NIST PQC standards evolution, prepare for ML-DSA-65 if needed

### 1.3 Practical Considerations for PQC Adoption

**Is it Practical Now?**
- **YES for high-security contexts** like security substrate/agentic firewall
- **Libraries Available:**
  - `liboqs-python`: Open Quantum Safe project
  - `PQClean`: Reference implementations
  - OpenSSL 3.2+ with OQS provider
- **Performance:** ML-DSA-44 signing ~1.2ms, verification ~0.9ms (modern CPU)
- **Size Overhead:** ~2.4KB per signature (manageable for Git repo)

**Why Hybrid vs Pure PQC?**
- **Defense in Depth:** If PQC breaks, Ed25519 still provides security
- **Compatibility:** Ed25519 works everywhere now; PQC tooling still maturing
- **Standards Stability:** NIST standards finalized Aug 2024, but implementation bugs still being found
- **Migration Path:** Can drop Ed25519 later if PQC proves reliable

---

## 2. Apple Secure Enclave Integration

### 2.1 Secure Enclave Capabilities

**What is Secure Enclave?**
- Hardware security module built into Apple Silicon (M1/M2/M3) and T2 chips
- Isolated crypto processor with own secure boot chain
- Keys never leave the enclave (operations happen inside)
- Biometric-protected access (Touch ID / Face ID)
- Survives OS compromises and malware

**Use Cases for Tachyon Tongs:**
- **Root Signing Key:** Master key for ADR records and releases
- **Airlock Approval Key:** Human-in-the-loop approvals require biometric auth
- **Recovery Attestation:** Prove legitimacy of key recovery operations

### 2.2 Implementation via macOS Keychain

**Key Storage Strategy:**
```
Secure Enclave (Apple Silicon)
    └── Root Signing Key (Ed25519 private key)
        ├── Protected by: Touch ID / Face ID
        ├── Extractable: NO
        └── Backup: Via iCloud Keychain (encrypted to user's Apple ID)

macOS Keychain (Software-backed)
    └── Development Signing Key (Ed25519 private key)
        ├── Protected by: Keychain password + encryption
        ├── Extractable: YES (for backup)
        └── Rotated: Every 90 days
```

**Python Integration:**
```python
# Using Security framework via pyobjc
from Security import *
from Cocoa import *

def sign_with_secure_enclave(data: bytes, key_label: str) -> bytes:
    """
    Sign data using Secure Enclave-protected key.
    Requires biometric auth via Touch ID.
    """
    query = {
        kSecClass: kSecClassKey,
        kSecAttrLabel: key_label,
        kSecAttrKeyType: kSecAttrKeyTypeECSECPrimeRandom,
        kSecAttrTokenID: kSecAttrTokenIDSecureEnclave,
        kSecReturnRef: True,
        kSecUseAuthenticationUI: kSecUseAuthenticationUIAllow,
        kSecUseAuthenticationContext: create_auth_context()
    }
    
    status, key_ref = SecItemCopyMatching(query, None)
    if status != 0:
        raise KeyError(f"Secure Enclave key not found: {status}")
    
    # Sign using SecKeyCreateSignature (requires Touch ID)
    signature = SecKeyCreateSignature(
        key_ref,
        kSecKeyAlgorithmECDSASignatureMessageX962SHA256,
        data,
        None
    )
    
    return signature
```

**CLI Wrapper for Signing:**
```bash
#!/bin/bash
# scripts/sign_artifact.sh

ARTIFACT="$1"
KEY_TYPE="${2:-development}"  # 'root' or 'development'

if [ "$KEY_TYPE" == "root" ]; then
    # Use Secure Enclave (requires Touch ID)
    python3 scripts/sign_enclave.py "$ARTIFACT"
else
    # Use keychain-backed key
    python3 scripts/sign_keychain.py "$ARTIFACT"
fi
```

### 2.3 Recovery Strategy for Secure Enclave Keys

**Problem:** Secure Enclave keys are non-extractable. What if you need to recover to a new MacBook?

**Solution: Multi-Layered Recovery**

**Approach 1: iCloud Keychain Sync (Recommended for Development Keys)**
- Enable iCloud Keychain on macOS
- Development keys sync automatically to new devices
- Protected by Apple ID + 2FA
- **Limitation:** Only works for keychain items, not Secure Enclave keys

**Approach 2: Key Ceremony + Shamir Secret Sharing (For Root Keys)**
```
Root Key Split into 5 Shares (3-of-5 threshold)
    ├── Share 1: Your personal secure storage (1Password/iCloud)
    ├── Share 2: Trusted colleague/backup person
    ├── Share 3: Bank safe deposit box
    ├── Share 4: Hardware security key (YubiKey) backup
    └── Share 5: Encrypted cloud storage (S3 + GPG)

Recovery Process:
1. Obtain any 3 of 5 shares
2. Reconstruct root private key
3. Import into new MacBook's Secure Enclave
4. Generate new shares, destroy old shares (share rotation)
```

**Python Implementation:**
```python
from secrets import token_bytes
from shamirs import split_secret, recover_secret

# Generate root key
root_key = token_bytes(32)  # Ed25519 seed

# Split into 5 shares, requiring 3 to reconstruct
shares = split_secret(root_key, threshold=3, num_shares=5)

# Distribute shares...
# shares[0] -> 1Password vault
# shares[1] -> email to trusted colleague
# shares[2] -> print to paper, store in safe
# shares[3] -> backup to YubiKey
# shares[4] -> encrypt and upload to S3

# Recovery (on new MacBook)
recovered_shares = [shares[0], shares[2], shares[4]]  # Any 3
reconstructed_key = recover_secret(recovered_shares)

# Import to Secure Enclave on new device
import_to_secure_enclave(reconstructed_key, label="tachyon-root-key")
```

**Approach 3: Hardware Token Backup (YubiKey 5 Series)**
- Store backup of root key on FIDO2/PIV-compatible YubiKey
- Requires physical possession + PIN to use
- Survives MacBook loss/theft
- Can be stored in safe deposit box

**Recommended Strategy:**
```
Root Signing Key:
    - Primary: Secure Enclave (Touch ID protected)
    - Backup 1: Shamir shares (3-of-5 split)
    - Backup 2: YubiKey 5 NFC (PIN protected)

Development Signing Key:
    - Primary: macOS Keychain
    - Backup: iCloud Keychain sync
    - Rotation: Every 90 days (old keys archived)

Agent Keys:
    - Generated on demand, short-lived (24-48 hours)
    - No backup needed (re-issue from development key)
```

---

## 3. Per-Agent Key Hierarchy

### 3.1 Key Hierarchy Design

**Goal:** Each agent gets its own signing key, delegated from your development key, with clear scope and audit trail.

```
┌─────────────────────────────────────────┐
│   Root Key (Secure Enclave)             │
│   - ADR final approval                  │
│   - Release signing                     │
│   - Key delegation authority            │
│   - Rotate: Never (use for life of     │
│     project, backup via Shamir)         │
└─────────────────┬───────────────────────┘
                  │
                  │ delegates to
                  ▼
┌─────────────────────────────────────────┐
│   Development Key (Keychain)            │
│   - Daily ADR signing                   │
│   - Code commit signing                 │
│   - Agent key issuance                  │
│   - Rotate: Every 90 days               │
└─────────────────┬───────────────────────┘
                  │
                  │ issues
                  ▼
        ┌─────────┴──────────┐
        ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│ Sentinel Agent   │  │ Airlock Agent    │
│ Key              │  │ Key              │
│                  │  │                  │
│ - CVE catalog    │  │ - Patch approval │
│   updates        │  │ - Deployment     │
│ - Threat intel   │  │   execution      │
│ - Auto-signing   │  │ - Requires HITL  │
│   debates        │  │   confirmation   │
│ - Rotate: Daily  │  │ - Rotate: Weekly │
└──────────────────┘  └──────────────────┘
```

### 3.2 Key Delegation Certificates

**Implementation: X.509-like Certificate Chain**

Each agent key is accompanied by a delegation certificate:

```json
{
  "version": 1,
  "agent_id": "sentinel-001",
  "public_key": "ed25519:AgF7nK...",
  "authorized_operations": [
    "sign:debates/*",
    "sign:EXPLOITATION_CATALOG.md",
    "write:memory/run_log.md"
  ],
  "not_before": "2026-03-20T00:00:00Z",
  "not_after": "2026-03-21T23:59:59Z",
  "issued_by": "development-key:c4f3a2...",
  "signature": "ed25519:nQ8xL..."  // Signed by development key
}
```

**Verification Process:**
```python
def verify_agent_signature(artifact_path: str, signature_path: str, cert_path: str) -> bool:
    """
    Verify an artifact signed by an agent key.
    
    Returns True if:
    1. Agent cert is signed by valid development key
    2. Agent cert authorizes operation on this artifact
    3. Agent signature on artifact is valid
    4. Current time is within cert validity period
    """
    cert = load_certificate(cert_path)
    
    # Check cert signature (development key → agent key)
    if not verify_ed25519(cert.signature, cert.payload, development_pubkey):
        return False
    
    # Check cert validity period
    if not (cert.not_before <= now() <= cert.not_after):
        return False
    
    # Check operation authorization
    if not cert.authorizes(artifact_path):
        return False
    
    # Check artifact signature (agent key → artifact)
    signature = load_signature(signature_path)
    artifact = read_file(artifact_path)
    return verify_ed25519(signature, artifact, cert.public_key)
```

### 3.3 Agent Key Management

**Automatic Key Rotation:**
```python
# scripts/rotate_agent_keys.py

import os
from datetime import datetime, timedelta
from pathlib import Path

def rotate_sentinel_key():
    """
    Rotate Sentinel agent key daily.
    Old key is archived for signature verification.
    """
    agent_id = "sentinel-001"
    
    # Generate new Ed25519 keypair
    private_key, public_key = generate_ed25519_keypair()
    
    # Create delegation certificate (valid for 24 hours)
    cert = create_delegation_cert(
        agent_id=agent_id,
        public_key=public_key,
        authorized_ops=[
            "sign:debates/*",
            "sign:EXPLOITATION_CATALOG.md",
            "write:memory/run_log.md"
        ],
        not_before=datetime.utcnow(),
        not_after=datetime.utcnow() + timedelta(hours=24),
        issuing_key=load_development_key()
    )
    
    # Store new key and cert
    keystore_path = Path("~/.tachyon/keys/agents").expanduser()
    keystore_path.mkdir(parents=True, exist_ok=True)
    
    save_private_key(private_key, keystore_path / f"{agent_id}.key")
    save_certificate(cert, keystore_path / f"{agent_id}.cert")
    
    # Archive old key (for verification of old signatures)
    archive_old_key(agent_id, keystore_path)
    
    print(f"✅ Rotated key for {agent_id}")
    print(f"   Valid until: {cert.not_after}")
    print(f"   Public key: {public_key.hex()[:16]}...")

# Run daily via cron or launchd
if __name__ == "__main__":
    rotate_sentinel_key()
```

**Launch Agent for Automatic Rotation (macOS):**
```xml
<!-- ~/Library/LaunchAgents/com.tachyon.key-rotation.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tachyon.key-rotation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/rds/antigravity/tachyon_tongs/scripts/rotate_agent_keys.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/tachyon-key-rotation.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/tachyon-key-rotation-error.log</string>
</dict>
</plist>
```

### 3.4 Per-Agent Signing Authority

**Recommended Per-Agent Scopes:**

| Agent | Signing Authority | Rotation | Notes |
|-------|------------------|----------|-------|
| **Sentinel** | `debates/*`, `EXPLOITATION_CATALOG.md`, `memory/run_log.md` | Daily | Fully autonomous |
| **Airlock** | `docs/patches/*`, `memory/strategic/CHANGE_CONTROL.md` | Weekly | Requires HITL approval |
| **Development** | `docs/adr/*`, `src/*`, `*.py` | 90 days | Your personal key |
| **CI/CD** | `releases/*`, `dist/*` | 180 days | GitHub Actions runner |
| **Root** | `*` (all files) | Never | Secure Enclave, emergency only |

**Audit Logging:**
```python
# Every signature operation logs to memory/audit/signing_log.jsonl

{
  "timestamp": "2026-03-20T10:15:30Z",
  "agent": "sentinel-001",
  "operation": "sign",
  "artifact": "debates/DEBATE_20260320_101530_CVE-2026-1234.md",
  "signature": "ed25519:8f3a...",
  "cert_fingerprint": "sha256:a4b9...",
  "result": "success"
}
```

---

## 4. Development Process Security Enhancements

### 4.1 Git Commit Signing

**Enable SSH Commit Signing (macOS 13+):**

```bash
# Generate SSH signing key (or reuse existing)
ssh-keygen -t ed25519 -C "dev@tachyon-tongs" -f ~/.ssh/tachyon_signing

# Configure Git to use SSH for signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/tachyon_signing.pub
git config --global commit.gpgsign true

# Configure allowed signers file
echo "$(git config user.email) $(cat ~/.ssh/tachyon_signing.pub)" > ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers

# Test
git commit --allow-empty -m "test: signed commit"
git verify-commit HEAD
```

**Combine with File Signatures:**
- **Git commits** = code provenance and integrity
- **File signatures** = artifact-level attestation for ADRs, catalogs, debates

### 4.2 Pre-Commit Hooks

**Install pre-commit framework:**
```bash
pip install pre-commit
```

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: local
    hooks:
      # Verify all .sig files are valid
      - id: verify-signatures
        name: Verify file signatures
        entry: python3 scripts/verify_all_signatures.py
        language: system
        pass_filenames: false
        
      # Ensure ADRs are signed before commit
      - id: sign-adrs
        name: Sign new ADR files
        entry: python3 scripts/sign_adrs.py
        language: system
        files: '^docs/adr/.*\.md$'
        
      # Prevent commits of unsigned agent certificates
      - id: verify-agent-certs
        name: Verify agent certificates
        entry: python3 scripts/verify_agent_certs.py
        language: system
        files: '\.cert$'
        
      # Detect hardcoded secrets
      - id: detect-secrets
        name: Detect hardcoded secrets
        entry: detect-secrets-hook
        language: system
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-yaml
      - id: check-json
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

**Enable hooks:**
```bash
cd ~/antigravity/tachyon_tongs
pre-commit install
pre-commit run --all-files  # Test on existing files
```

### 4.3 CI/CD Pipeline Hardening

**GitHub Actions Workflow with Signature Verification:**

```yaml
# .github/workflows/verify-integrity.yml
name: Verify Integrity

on: [push, pull_request]

jobs:
  verify-signatures:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install cryptography pynacl liboqs-python
      
      - name: Verify all signatures
        run: |
          python3 scripts/verify_all_signatures.py --strict
      
      - name: Verify agent certificates
        run: |
          python3 scripts/verify_agent_certs.py --strict
      
      - name: Check for unsigned ADRs
        run: |
          for adr in docs/adr/*.md; do
            if [ ! -f "$adr.sig" ]; then
              echo "❌ Unsigned ADR: $adr"
              exit 1
            fi
          done
      
      - name: Audit log integrity check
        run: |
          python3 scripts/verify_audit_log.py

  reproducible-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build with fixed timestamps
        run: |
          export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
          python3 -m build
      
      - name: Generate SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py -o sbom.json
      
      - name: Sign SBOM with CI key
        run: |
          python3 scripts/sign_artifact.py sbom.json --key ci-key
      
      - name: Upload signed SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom-signed
          path: sbom.json*
```

### 4.4 Secrets Management

**Current Problem:** No clear secrets management strategy

**Proposed Solution: Encrypted Config Files + macOS Keychain**

**Directory Structure:**
```
configs/
├── public/                    # Non-sensitive configs (commit to Git)
│   ├── domain_reputation.json
│   └── pytest.ini
├── secrets/                   # Sensitive configs (Git-ignored, encrypted)
│   ├── .gitkeep
│   └── README.md             # Instructions for recreating
└── secrets.enc/               # Encrypted secrets (commit to Git)
    ├── api_keys.json.age      # Encrypted with age
    ├── signing_keys.json.age
    └── mcp_config.json.age
```

**Encryption with `age`:**
```bash
# Install age
brew install age

# Generate recipient key
age-keygen -o ~/.tachyon/age-key.txt

# Encrypt secrets
age -r $(cat ~/.tachyon/age-key.txt | grep public | cut -d: -f2) \
    -o configs/secrets.enc/api_keys.json.age \
    configs/secrets/api_keys.json

# Decrypt on new machine
age -d -i ~/.tachyon/age-key.txt \
    -o configs/secrets/api_keys.json \
    configs/secrets.enc/api_keys.json.age
```

**Bootstrap Script for New Machines:**
```bash
#!/bin/bash
# scripts/bootstrap_secrets.sh

set -e

echo "🔐 Tachyon Tongs Secrets Bootstrap"
echo "=================================="

# Check for age key
if [ ! -f ~/.tachyon/age-key.txt ]; then
    echo "❌ Age key not found at ~/.tachyon/age-key.txt"
    echo "   Restore from backup or regenerate secrets"
    exit 1
fi

# Decrypt all secrets
for encrypted in configs/secrets.enc/*.age; do
    filename=$(basename "$encrypted" .age)
    age -d -i ~/.tachyon/age-key.txt \
        -o "configs/secrets/$filename" \
        "$encrypted"
    echo "✅ Decrypted $filename"
done

echo ""
echo "✅ Secrets restored successfully"
echo "   Location: configs/secrets/"
```

---

## 5. Project Restructuring for Security

### 5.1 Current Structure Issues

**Problems:**
1. **Mixing concerns:** Code, debates, logs, and configs all at root level
2. **Sensitive data exposure:** Debates might contain exploit details
3. **No clear runtime vs. source separation:** Logs mixed with code
4. **Signature files scattered:** `.sig` files everywhere, hard to audit
5. **No dedicated security artifacts directory**

### 5.2 Proposed Directory Reorganization

```
tachyon_tongs/
├── .git/
├── .github/
│   └── workflows/              # CI/CD pipelines
├── .antigravity.yml            # Keep at root
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── src/                        # Source code (commit to Git)
│   ├── tachyon/
│   │   ├── __init__.py
│   │   ├── sentinel/          # Sentinel agent code
│   │   ├── airlock/           # Airlock agent code
│   │   ├── crypto/            # Signing/verification utilities
│   │   └── config/            # Config loading logic
│   └── tests/
│       ├── unit/
│       └── integration/
│
├── docs/                       # Documentation (commit to Git)
│   ├── adr/                   # Architecture Decision Records
│   │   ├── 0001-initial.md
│   │   ├── 0001-initial.md.sig
│   │   └── ...
│   ├── threat-model/          # Threat modeling docs
│   ├── runbooks/              # Operational procedures
│   └── api/                   # API documentation
│
├── configs/                   # Configuration (commit to Git)
│   ├── public/                # Non-sensitive configs
│   │   ├── domain_reputation.json
│   │   └── pytest.ini
│   └── secrets.enc/           # Encrypted secrets (commit to Git)
│       ├── api_keys.json.age
│       └── README.md
│
├── scripts/                   # Automation scripts (commit to Git)
│   ├── sign_artifact.py
│   ├── verify_signatures.py
│   ├── rotate_agent_keys.py
│   ├── bootstrap_secrets.sh
│   └── ...
│
├── .agent/                    # Agent configurations (commit to Git)
│   ├── workflows/
│   └── skills/
│
├── dashboard/                 # Web UI (commit to Git)
│   ├── src/
│   └── package.json
│
├── runtime/                   # Runtime data (Git-ignored)
│   ├── logs/                  # All logs go here
│   │   ├── sentinel/
│   │   ├── airlock/
│   │   └── audit/
│   ├── debates/               # Moved from root
│   │   ├── DEBATE_*.md
│   │   └── DEBATE_*.md.sig
│   ├── tasks/                 # Active task tracking
│   │   ├── TASKS.md
│   │   └── PENDING_*.md
│   ├── memory/                # Strategic memory
│   │   ├── evolution.md
│   │   └── run_log.md
│   └── tmp/                   # Temporary files
│       └── airlock/           # Patch staging
│
├── data/                      # Static data assets (commit to Git)
│   ├── exploitation_catalog/
│   │   ├── EXPLOITATION_CATALOG.md
│   │   └── EXPLOITATION_CATALOG.md.sig
│   └── threat_intel/
│
├── security/                  # Security artifacts (commit to Git)
│   ├── keys/                  # Public keys and certificates
│   │   ├── root.pub
│   │   ├── development.pub
│   │   └── agents/
│   │       ├── sentinel-001.cert
│   │       └── airlock-001.cert
│   ├── signatures/            # Centralized signature index
│   │   └── manifest.json      # Maps files → signatures
│   └── sbom/                  # Software Bill of Materials
│       └── sbom-latest.json
│
└── build/                     # Build artifacts (Git-ignored)
    ├── dist/
    └── wheels/
```

### 5.3 Migration Script

```bash
#!/bin/bash
# scripts/migrate_directory_structure.sh

set -e

echo "🏗️  Migrating Tachyon Tongs directory structure..."

# Create new directories
mkdir -p src/tachyon/{sentinel,airlock,crypto,config}
mkdir -p src/tests/{unit,integration}
mkdir -p docs/{adr,threat-model,runbooks,api}
mkdir -p configs/{public,secrets.enc}
mkdir -p runtime/{logs,debates,tasks,memory,tmp/airlock}
mkdir -p runtime/logs/{sentinel,airlock,audit}
mkdir -p data/{exploitation_catalog,threat_intel}
mkdir -p security/{keys/agents,signatures,sbom}
mkdir -p build/{dist,wheels}

# Move existing files
echo "📦 Moving debates..."
mv debates/* runtime/debates/ 2>/dev/null || true

echo "📦 Moving logs..."
mv SYNC_LOG.md runtime/logs/ 2>/dev/null || true
mv CANARY_LOG.md runtime/logs/ 2>/dev/null || true
mv *_LOG.md runtime/logs/ 2>/dev/null || true

echo "📦 Moving tasks..."
mv TASKS.md runtime/tasks/ 2>/dev/null || true
mv PENDING_*.md runtime/tasks/ 2>/dev/null || true

echo "📦 Moving memory..."
mv EVOLUTION.md runtime/memory/evolution.md 2>/dev/null || true

echo "📦 Moving exploitation catalog..."
mv EXPLOITATION_CATALOG.md* data/exploitation_catalog/ 2>/dev/null || true

echo "📦 Moving configs..."
mv configs/domain_reputation.json configs/public/ 2>/dev/null || true
mv configs/pytest.ini configs/public/ 2>/dev/null || true
mv configs/singularity_config.json configs/public/ 2>/dev/null || true

echo "📦 Moving Python source..."
mv sentinel.py src/tachyon/sentinel/ 2>/dev/null || true

# Update .gitignore
cat >> .gitignore << 'EOF'

# Runtime data
runtime/
!runtime/.gitkeep
!runtime/README.md

# Build artifacts
build/
dist/
*.egg-info/

# Secrets (keep encrypted versions)
configs/secrets/
!configs/secrets.enc/
.tachyon/

# Temporary files
*.tmp
.DS_Store
EOF

# Create .gitkeep files
touch runtime/.gitkeep
touch configs/secrets.enc/.gitkeep
touch security/keys/.gitkeep

echo ""
echo "✅ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Review the new structure: tree -L 3"
echo "2. Update import paths in Python code"
echo "3. Update .antigravity.yml with new paths"
echo "4. Test all workflows to ensure they work"
echo "5. Commit the restructure: git add . && git commit -m 'refactor: restructure for security'"
```

### 5.4 Updated `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# Runtime data (not committed)
runtime/
!runtime/.gitkeep
!runtime/README.md

# Secrets
configs/secrets/
.tachyon/
*.key
*.pem
!configs/secrets.enc/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Testing
.coverage
.pytest_cache/
htmlcov/

# Temporary
*.tmp
*.log
!runtime/logs/.gitkeep

# Build artifacts
*.whl
*.tar.gz
```

---

## 6. Enhanced Threat Model

### 6.1 Threat Actors

| Threat Actor | Motivation | Capability Level | Primary Targets |
|-------------|------------|------------------|-----------------|
| **Malicious Agent** | Autonomy escalation, sandbox escape | Medium-High | Agent code, signing keys, ADR files |
| **Supply Chain Attacker** | Backdoor insertion, dependency poisoning | High | Dependencies, CI/CD pipeline, build artifacts |
| **Insider Threat** | Data exfiltration, sabotage | Medium | Source code, configs, debates, ADRs |
| **Nation State** | Long-term persistence, intelligence gathering | Very High | All assets, especially key material |
| **Opportunistic Malware** | Credential theft, ransomware | Low-Medium | Developer workstation, Git credentials |

### 6.2 Attack Scenarios

#### Scenario 1: Compromised Development Machine

**Attack Path:**
1. Attacker gains access to developer's MacBook (malware, physical access, etc.)
2. Attempts to steal signing keys from Keychain
3. Forges signatures on malicious ADRs or code commits
4. Pushes malicious changes to Git repo

**Mitigations:**
- ✅ **Secure Enclave Protection:** Root key cannot be extracted even from compromised OS
- ✅ **Keychain Encryption:** Development keys encrypted with user password
- ✅ **Biometric Auth:** Signing operations require Touch ID
- ✅ **Audit Logging:** All signature operations logged to append-only audit log
- ✅ **Git Commit Signing:** Attacker needs both signing key and Git credentials
- ✅ **Time-based Certificates:** Agent keys expire in 24 hours, limiting window

**Detection:**
- Audit log shows unauthorized signing operations
- GitHub detects commits from unusual IP addresses
- Pre-commit hooks detect signatures that don't match expected keys

#### Scenario 2: Agent Key Theft

**Attack Path:**
1. Attacker compromises Sentinel agent process
2. Steals agent signing key from memory
3. Uses stolen key to sign malicious debates or catalog entries
4. Injects false threat intelligence to trigger incorrect mitigations

**Mitigations:**
- ✅ **Short-Lived Keys:** Sentinel key rotates daily (max damage window: 24h)
- ✅ **Limited Scope:** Sentinel key only authorized for specific files (debates/*, EXPLOITATION_CATALOG.md)
- ✅ **Delegation Certificates:** Stolen key cannot sign arbitrary files
- ✅ **Certificate Revocation:** Can revoke stolen key's delegation cert immediately
- ✅ **Audit Trail:** All operations logged with cert fingerprint

**Detection:**
- Unusual signing patterns (e.g., signing outside authorized file patterns)
- Signatures after cert expiry
- Multiple signatures from same key in rapid succession (rate limiting)

#### Scenario 3: Supply Chain Attack on Dependencies

**Attack Path:**
1. Attacker compromises Python package (e.g., PyPI package)
2. Malicious version installed via `pip install`
3. Package exfiltrates signing keys or injects backdoor during import
4. CI/CD pipeline builds and signs compromised artifact

**Mitigations:**
- ✅ **Dependency Pinning:** `requirements.txt` with exact versions and hashes
- ✅ **SBOM Generation:** Track all dependencies with signatures
- ✅ **Reproducible Builds:** Verify builds produce identical artifacts
- ✅ **Isolated Build Environment:** CI runs in clean container each time
- ✅ **Separate CI Key:** CI/CD uses separate signing key with limited scope

**Detection:**
- SBOM changes trigger manual review
- Hash mismatches in `requirements.txt`
- Unexpected network connections during build
- File signature verification fails for released artifacts

#### Scenario 4: Replay Attack on Signed Files

**Attack Path:**
1. Attacker obtains old version of signed ADR file
2. Replaces current ADR with old version
3. Signature validates correctly (old signature, old content)
4. System trusts old, potentially insecure architectural decision

**Mitigations:**
- ✅ **Timestamp in Signatures:** Signatures include signing timestamp
- ✅ **Monotonic Counters:** ADR sequence numbers must increase
- ✅ **Git History:** Commits are signed and ordered by Git DAG
- ✅ **Signature Freshness Check:** Reject signatures older than X days for critical files

**Implementation:**
```python
def verify_signature_freshness(signature_path: str, max_age_days: int = 30) -> bool:
    """Verify signature is recent enough to trust."""
    sig_data = load_signature(signature_path)
    
    if 'timestamp' not in sig_data:
        raise ValueError("Signature missing timestamp")
    
    sig_age = datetime.utcnow() - sig_data['timestamp']
    if sig_age > timedelta(days=max_age_days):
        raise ValueError(f"Signature too old: {sig_age.days} days")
    
    return True
```

#### Scenario 5: Quantum Computer Breaks Ed25519

**Attack Path:**
1. In the future, practical quantum computers become available
2. Attacker uses Shor's algorithm to break Ed25519 signatures
3. Can forge signatures on any historical or new artifacts
4. All past ADRs, commits, and debates become untrusted

**Mitigations:**
- ✅ **Hybrid Signatures:** Ed25519 + ML-DSA-44 protects against quantum attacks
- ✅ **Crypto Agility:** Signature verification supports multiple algorithms
- ✅ **Re-signing Campaign:** Can re-sign all historical artifacts with PQC when needed
- ✅ **Monitoring NIST:** Track quantum computing progress and NIST PQC standards

**Timeline:**
- 2026: Deploy hybrid signatures (current plan)
- 2028-2030: If quantum threats materialize, drop Ed25519, keep ML-DSA
- 2030+: Migrate to next-generation PQC if needed

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Establish asymmetric signing infrastructure

**Tasks:**
- [ ] Install required libraries: `cryptography`, `pynacl`, `liboqs-python`
- [ ] Generate root Ed25519 keypair in Secure Enclave
- [ ] Generate development Ed25519 keypair in Keychain
- [ ] Implement basic Ed25519 signing/verification in Python
- [ ] Create key backup using Shamir's Secret Sharing (3-of-5)
- [ ] Store shares securely (1Password, colleague, safe deposit, YubiKey, S3)
- [ ] Test key recovery from shares

**Deliverables:**
- `scripts/sign_artifact.py` - Sign files with Ed25519
- `scripts/verify_signature.py` - Verify Ed25519 signatures
- `scripts/generate_keys.py` - Key generation utility
- `scripts/backup_keys.py` - Shamir share generation
- `scripts/recover_keys.py` - Key recovery from shares

**Success Criteria:**
- ✅ Can sign arbitrary file with Touch ID-protected root key
- ✅ Can verify signatures in CI/CD pipeline
- ✅ Can recover root key from any 3 of 5 shares
- ✅ All signatures under 1KB (Ed25519 only)

### Phase 2: Agent Keys (Weeks 3-4)

**Goal:** Implement per-agent key delegation

**Tasks:**
- [ ] Design delegation certificate schema (JSON format)
- [ ] Implement certificate generation signed by development key
- [ ] Create agent key rotation script for Sentinel
- [ ] Set up launchd for daily Sentinel key rotation
- [ ] Implement signature verification with certificate chain validation
- [ ] Add audit logging for all signature operations
- [ ] Test agent key revocation

**Deliverables:**
- `scripts/issue_agent_cert.py` - Issue delegation certificates
- `scripts/rotate_agent_keys.py` - Automatic key rotation
- `security/keys/agents/` - Agent public keys and certificates
- `~/Library/LaunchAgents/com.tachyon.key-rotation.plist` - Rotation scheduler

**Success Criteria:**
- ✅ Sentinel can sign debates with its own key
- ✅ Signature verification validates certificate chain
- ✅ Stolen agent key cannot sign unauthorized files
- ✅ Audit log tracks all signature operations

### Phase 3: Hybrid PQC (Weeks 5-6)

**Goal:** Add quantum-resistant signatures

**Tasks:**
- [ ] Install and test `liboqs-python` ML-DSA implementation
- [ ] Implement hybrid signing: Ed25519 + ML-DSA-44
- [ ] Update verification to check both signatures
- [ ] Benchmark signing/verification performance
- [ ] Re-sign all existing ADRs with hybrid signatures
- [ ] Update CI/CD to verify hybrid signatures

**Deliverables:**
- `src/tachyon/crypto/hybrid_signer.py` - Hybrid signing implementation
- Updated `scripts/sign_artifact.py` - Now creates dual signatures
- Updated `scripts/verify_signature.py` - Verifies both algorithms

**Success Criteria:**
- ✅ All new signatures are hybrid (Ed25519 + ML-DSA-44)
- ✅ Can verify signatures even if one algorithm breaks
- ✅ Signing performance < 5ms on M3 MacBook
- ✅ Signature size < 3KB (64B + 2420B)

### Phase 4: Restructure & Secrets (Weeks 7-8)

**Goal:** Reorganize project for security

**Tasks:**
- [ ] Run migration script to reorganize directories
- [ ] Update all import paths in Python code
- [ ] Encrypt sensitive configs with `age`
- [ ] Create bootstrap script for new machines
- [ ] Update `.gitignore` to protect runtime data
- [ ] Move debates and logs to `runtime/` directory
- [ ] Update .antigravity.yml with new paths

**Deliverables:**
- New directory structure as documented above
- `scripts/migrate_directory_structure.sh` - Migration automation
- `scripts/bootstrap_secrets.sh` - Secrets recovery
- Updated `.gitignore`

**Success Criteria:**
- ✅ `git status` shows no sensitive files
- ✅ Runtime data separated from source code
- ✅ Can bootstrap on new machine with age key + Git clone
- ✅ All tests pass with new structure

### Phase 5: CI/CD Hardening (Weeks 9-10)

**Goal:** Integrate signature verification into automated pipelines

**Tasks:**
- [ ] Set up pre-commit hooks for signature verification
- [ ] Create GitHub Actions workflow for integrity checks
- [ ] Implement reproducible build process
- [ ] Generate and sign SBOM for each release
- [ ] Add signature freshness checks to verification
- [ ] Configure Dependabot for dependency updates

**Deliverables:**
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.github/workflows/verify-integrity.yml` - CI/CD pipeline
- `.github/workflows/release.yml` - Signed release workflow
- `security/sbom/` - Software Bill of Materials

**Success Criteria:**
- ✅ Unsigned commits are rejected by CI
- ✅ Pull requests require signature verification
- ✅ Releases include signed SBOM
- ✅ Reproducible builds produce identical artifacts

### Phase 6: Documentation & Training (Weeks 11-12)

**Goal:** Ensure team understands new security procedures

**Tasks:**
- [ ] Write threat model documentation
- [ ] Create key management runbook
- [ ] Document agent key rotation procedures
- [ ] Write incident response plan for key compromise
- [ ] Create key recovery drill procedure
- [ ] Update README with security overview

**Deliverables:**
- `docs/threat-model/THREAT_MODEL.md` - Comprehensive threat analysis
- `docs/runbooks/KEY_MANAGEMENT.md` - Operational procedures
- `docs/runbooks/KEY_RECOVERY.md` - Recovery procedures
- `docs/runbooks/INCIDENT_RESPONSE.md` - Compromise scenarios

**Success Criteria:**
- ✅ Can recover from lost MacBook in < 1 hour
- ✅ Can detect and respond to key compromise in < 15 minutes
- ✅ All team members understand signing process
- ✅ Threat model covers all identified attack scenarios

---

## 8. Operational Procedures

### 8.1 Daily Operations

**Developer Workflow:**
```bash
# Morning: Start work
cd ~/antigravity/tachyon_tongs

# Check signature status
python3 scripts/verify_all_signatures.py

# Make changes to code...
# git add, git commit (automatically signed via SSH)

# Sign new ADR
python3 scripts/sign_artifact.py docs/adr/0042-new-feature.md

# Push changes
git push origin main

# Evening: Verify all signatures before end of day
python3 scripts/verify_all_signatures.py --strict
```

**Agent Key Rotation (Automated):**
```bash
# Runs daily at 3 AM via launchd
# ~/Library/LaunchAgents/com.tachyon.key-rotation.plist

# Manual rotation (if needed)
python3 scripts/rotate_agent_keys.py --agent sentinel-001
python3 scripts/rotate_agent_keys.py --agent airlock-001
```

### 8.2 Key Compromise Response

**If Development Key is Compromised:**
```bash
# 1. Immediately revoke compromised key
python3 scripts/revoke_key.py --key development-key --reason "Compromise detected"

# 2. Generate new development key
python3 scripts/generate_keys.py --type development --output ~/.tachyon/keys/

# 3. Re-sign all recent ADRs with new key
python3 scripts/resign_artifacts.py --since "2026-03-15" --key new-development-key

# 4. Notify via GitHub issue
gh issue create --title "Security: Development key rotated" --body "$(cat incident.md)"

# 5. Update audit log
echo "$(date -u): Development key rotated due to compromise" >> runtime/logs/audit/key_events.log

# 6. Force all agents to re-generate keys
python3 scripts/rotate_all_agent_keys.py --force
```

**If Root Key is Compromised (Catastrophic):**
```bash
# 1. Retrieve Shamir shares (need 3 of 5)
# - Share 1: From 1Password
# - Share 2: From trusted colleague
# - Share 3: From bank safe deposit box

# 2. Reconstruct root key
python3 scripts/recover_keys.py \
    --shares share1.txt share2.txt share3.txt \
    --output root-key-reconstructed.key

# 3. Generate new root key
python3 scripts/generate_keys.py --type root --secure-enclave

# 4. Create new Shamir shares
python3 scripts/backup_keys.py --key new-root-key --shares 5 --threshold 3

# 5. Destroy old shares and distribute new ones

# 6. Re-sign ENTIRE repository with new root key
python3 scripts/resign_all.py --key new-root-key

# 7. Update public key in GitHub
# 8. Notify all stakeholders
```

### 8.3 New Machine Setup

**Bootstrap on New MacBook:**
```bash
# 1. Clone repository
git clone git@github.com:roydsouza/tachyon_tongs.git
cd tachyon_tongs

# 2. Restore age key (from backup)
mkdir -p ~/.tachyon
# Copy age-key.txt from backup (1Password, USB, etc.)
cp /Volumes/Backup/age-key.txt ~/.tachyon/

# 3. Decrypt secrets
./scripts/bootstrap_secrets.sh

# 4. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Import root key to Secure Enclave (from Shamir shares if needed)
# OR sync development key via iCloud Keychain

# 6. Verify signatures
python3 scripts/verify_all_signatures.py

# 7. Test signing
python3 scripts/sign_artifact.py test-file.txt
python3 scripts/verify_signature.py test-file.txt test-file.txt.sig

# 8. Set up pre-commit hooks
pre-commit install
```

### 8.4 Audit Procedures

**Weekly Signature Audit:**
```bash
# Run every Monday via cron
python3 scripts/audit_signatures.py --generate-report

# Checks:
# - All .md files in docs/adr/ have valid signatures
# - All signatures are < 30 days old
# - All agent certificates are within validity period
# - No unauthorized signature operations in audit log
# - Git commit signatures match file signatures
```

**Monthly Security Review:**
```bash
# 1. Review audit logs
cat runtime/logs/audit/signing_log.jsonl | jq '.' | less

# 2. Check for expired or expiring keys
python3 scripts/check_key_expiry.py --warn-days 30

# 3. Verify SBOM integrity
python3 scripts/verify_sbom.py security/sbom/sbom-latest.json

# 4. Run dependency vulnerability scan
pip-audit

# 5. Review GitHub Actions logs for anomalies
gh run list --workflow verify-integrity.yml

# 6. Test key recovery procedure (drill)
python3 scripts/test_recovery.py --dry-run
```

---

## 9. Cost-Benefit Analysis

### 9.1 Security Improvements

| Improvement | Current Risk | Mitigated Risk | Effort | Impact |
|------------|--------------|----------------|--------|--------|
| **Asymmetric signatures** | High (HMAC forgery) | Low (Ed25519 secure) | Medium | ⭐⭐⭐⭐⭐ |
| **Secure Enclave keys** | High (key theft) | Very Low (hardware-protected) | Low | ⭐⭐⭐⭐⭐ |
| **Per-agent keys** | Medium (agent compromise) | Low (limited scope) | Medium | ⭐⭐⭐⭐ |
| **Hybrid PQC** | Low now (quantum far off) | Very Low (future-proof) | Medium | ⭐⭐⭐ |
| **Key recovery** | High (lost key = lost project) | Low (multiple backups) | Medium | ⭐⭐⭐⭐⭐ |
| **Directory restructure** | Medium (sensitive data exposure) | Low (proper separation) | High | ⭐⭐⭐⭐ |
| **CI/CD hardening** | Medium (supply chain) | Low (verified builds) | Medium | ⭐⭐⭐⭐ |

### 9.2 Development Efficiency

**Efficiency Gains:**
- ✅ **Faster onboarding:** New developers can bootstrap in < 30 minutes
- ✅ **Automated rotation:** No manual key rotation needed
- ✅ **Clear audit trail:** Easier debugging and compliance
- ✅ **Reproducible builds:** Fewer "works on my machine" issues

**Efficiency Costs:**
- ⚠️ **Initial setup time:** ~2-3 weeks for full implementation
- ⚠️ **Learning curve:** Team needs to understand new signing process
- ⚠️ **Biometric prompts:** Touch ID required for root key operations (adds ~2 seconds)
- ⚠️ **Signature size:** Files grow by ~3KB each (negligible for Git)

**Net Impact:** Positive after initial implementation period

### 9.3 Quantum Readiness

**Is PQC Worth It Now?**

**Arguments FOR:**
- ✅ "Harvest now, decrypt later" attacks are real
- ✅ NIST standards are finalized (Aug 2024)
- ✅ Minimal performance overhead (< 5ms per signature)
- ✅ Future-proofs against quantum threats
- ✅ Security-critical project (agentic firewall)

**Arguments AGAINST:**
- ⚠️ PQC implementations still maturing (bugs likely)
- ⚠️ Signature size overhead (~2.4KB vs 64B)
- ⚠️ Quantum computers not near-term threat (10-20 years)
- ⚠️ Can add PQC later if needed

**Recommendation:** Implement hybrid signatures (Ed25519 + ML-DSA-44) now
- Best of both worlds: proven security + future-proofing
- Can drop Ed25519 later if quantum threat materializes
- Shows forward-thinking security posture

---

## 10. Conclusion & Next Steps

### 10.1 Summary of Recommendations

**Highest Priority (Implement Immediately):**
1. ✅ Migrate from HMAC to Ed25519 signatures
2. ✅ Store root key in Apple Secure Enclave
3. ✅ Implement Shamir Secret Sharing for key backup (3-of-5)
4. ✅ Set up per-agent key delegation with certificates
5. ✅ Enable Git commit signing (SSH)

**High Priority (Implement Within 1 Month):**
6. ✅ Add hybrid PQC signatures (Ed25519 + ML-DSA-44)
7. ✅ Restructure project directories
8. ✅ Encrypt secrets with `age`
9. ✅ Implement pre-commit hooks
10. ✅ Set up CI/CD signature verification

**Medium Priority (Implement Within 3 Months):**
11. ✅ Automated agent key rotation
12. ✅ Comprehensive audit logging
13. ✅ SBOM generation and signing
14. ✅ Reproducible builds
15. ✅ Incident response runbooks

**Low Priority (Nice to Have):**
16. ⚠️ Hardware token backup (YubiKey)
17. ⚠️ Multi-signature approvals for critical changes
18. ⚠️ Time-locked key escrow
19. ⚠️ Formal security audit by third party

### 10.2 Success Metrics

**After Implementation:**
- ✅ **100% signature coverage:** All ADRs, debates, and catalogs signed
- ✅ **<1 hour recovery time:** Can restore on new MacBook in under 1 hour
- ✅ **<15 min detection time:** Key compromise detected within 15 minutes
- ✅ **Zero unsigned commits:** Pre-commit hooks enforce signing
- ✅ **Quantum-ready:** All signatures include PQC component
- ✅ **Clear audit trail:** Every signature operation logged

### 10.3 Immediate Action Items

**For Antigravity to Execute:**

1. **Create implementation branch:**
   ```bash
   git checkout -b security/asymmetric-signing
   ```

2. **Install dependencies:**
   ```bash
   pip install cryptography pynacl liboqs-python age-encryption pre-commit
   brew install age
   ```

3. **Generate root key:**
   ```bash
   python3 scripts/generate_keys.py --type root --secure-enclave
   ```

4. **Create Shamir shares:**
   ```bash
   python3 scripts/backup_keys.py --key root-key --shares 5 --threshold 3
   ```

5. **Distribute shares securely:**
   - Share 1 → 1Password vault
   - Share 2 → Email to trusted colleague
   - Share 3 → Print and store in bank safe deposit box
   - Share 4 → Backup to YubiKey (if available)
   - Share 5 → Encrypt and upload to S3 bucket

6. **Begin Phase 1 implementation** (see Section 7.1)

7. **Schedule weekly check-ins** to track progress

---

## Appendices

### Appendix A: Cryptographic Primitives

**Ed25519:**
- **Type:** Elliptic Curve Digital Signature Algorithm
- **Curve:** Curve25519 (Edwards form)
- **Security:** ~128-bit classical security
- **Signature Size:** 64 bytes
- **Public Key Size:** 32 bytes
- **Performance:** ~50,000 signatures/sec, ~20,000 verifications/sec (modern CPU)
- **Quantum Resistance:** ❌ Vulnerable to Shor's algorithm

**ML-DSA-44 (CRYSTALS-Dilithium):**
- **Type:** Lattice-based signature (Module-LWE)
- **NIST Category:** 2 (~128-bit security)
- **Signature Size:** ~2420 bytes
- **Public Key Size:** ~1312 bytes
- **Performance:** ~800 signatures/sec, ~1100 verifications/sec
- **Quantum Resistance:** ✅ Secure against quantum attacks

**Shamir's Secret Sharing:**
- **Type:** Information-theoretic secret sharing
- **Security:** Unconditionally secure
- **Threshold:** K-of-N (e.g., 3-of-5)
- **Property:** Any K shares reconstruct secret, K-1 shares reveal nothing

### Appendix B: Threat Model Templates

**ADR Threat Model Template:**
```markdown
# ADR-XXXX: [Title] - Threat Analysis

## Attack Surface
- Files: [List of files this ADR affects]
- Access: [Who/what can access these files]
- Trust Boundary: [Where does trust end]

## Threat Scenarios
1. **[Threat Name]**
   - Actor: [Who]
   - Motivation: [Why]
   - Capability: [How skilled]
   - Attack Path: [Steps]
   - Impact: [Consequences]
   - Likelihood: [High/Medium/Low]
   - Mitigation: [How we defend]

## Security Controls
- [Control 1]: [Description]
- [Control 2]: [Description]

## Residual Risk
[What risk remains after mitigations]

## Monitoring & Detection
[How we detect attacks]
```

### Appendix C: Key Rotation Schedule

| Key Type | Rotation Frequency | Backup Strategy | Recovery Time |
|----------|-------------------|-----------------|---------------|
| Root | Never (project lifetime) | Shamir 3-of-5 + YubiKey | < 1 hour |
| Development | 90 days | iCloud Keychain | < 5 minutes |
| Sentinel Agent | Daily | N/A (re-issue) | Instant |
| Airlock Agent | Weekly | N/A (re-issue) | Instant |
| CI/CD | 180 days | GitHub Secrets | < 30 minutes |

### Appendix D: Compliance Mapping

**If Tachyon Tongs Requires Compliance:**

| Standard | Requirement | Implementation |
|----------|-------------|----------------|
| **SOC 2** | Cryptographic key management | Secure Enclave + Keychain |
| | Change control | Signed ADRs + audit log |
| | Access controls | Per-agent keys + delegation |
| **ISO 27001** | Cryptographic controls | Ed25519 + ML-DSA-44 |
| | Key lifecycle | Rotation + backup procedures |
| | Incident response | Key compromise runbooks |
| **NIST 800-53** | Cryptographic mechanisms | FIPS 186-5 (Ed25519), FIPS 204 (ML-DSA) |
| | Audit and accountability | Comprehensive logging |

### Appendix E: Reference Implementation

**Minimal Signing Script (Ed25519 only):**

```python
#!/usr/bin/env python3
"""
Minimal Ed25519 signing implementation for Tachyon Tongs.
Usage: python3 sign.py <file_to_sign>
"""

import sys
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hashes
import json
import base64

def load_private_key(key_path: Path) -> ed25519.Ed25519PrivateKey:
    """Load Ed25519 private key from file."""
    with open(key_path, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def sign_file(file_path: Path, private_key: ed25519.Ed25519PrivateKey) -> dict:
    """Sign a file and return signature metadata."""
    # Read file content
    content = file_path.read_bytes()
    
    # Create signature
    signature = private_key.sign(content)
    
    # Create signature metadata
    sig_data = {
        'version': 1,
        'algorithm': 'ed25519',
        'file': str(file_path),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'signature': base64.b64encode(signature).decode('ascii'),
        'public_key': base64.b64encode(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode('ascii')
    }
    
    return sig_data

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 sign.py <file_to_sign>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Load signing key (in production, use Keychain)
    key_path = Path.home() / '.tachyon' / 'keys' / 'development.key'
    if not key_path.exists():
        print(f"Error: Signing key not found: {key_path}")
        print("Generate with: python3 scripts/generate_keys.py")
        sys.exit(1)
    
    private_key = load_private_key(key_path)
    
    # Sign file
    sig_data = sign_file(file_path, private_key)
    
    # Write signature file
    sig_path = file_path.with_suffix(file_path.suffix + '.sig')
    with open(sig_path, 'w') as f:
        json.dump(sig_data, f, indent=2)
    
    print(f"✅ Signed: {file_path}")
    print(f"   Signature: {sig_path}")
    print(f"   Algorithm: {sig_data['algorithm']}")
    print(f"   Timestamp: {sig_data['timestamp']}")

if __name__ == '__main__':
    main()
```

---

## Document Metadata

**Author:** Claude (Anthropic AI)  
**Reviewed By:** [Your Name]  
**Version:** 1.0  
**Last Updated:** 2026-03-20  
**Classification:** Internal Use  
**Distribution:** Tachyon Tongs Development Team

**Changelog:**
- 2026-03-20: Initial draft created based on security enhancement requirements
- [Future updates will be logged here]

---

**End of Document**

