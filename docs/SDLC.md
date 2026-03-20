# Tachyon Tongs: Secure Software Development Lifecycle (SDLC)

**Version:** 1.0
**Date:** 2026-03-20
**ADR Reference:** ADR-0028 (Proposed)
**Status:** Roadmap Defined — Implementation Pending (Phase 25)

---

## 1. Philosophy: Security as Biology

Tachyon Tongs is not merely *secured* — it is a **living immune system** whose development process must embody the same principles it enforces at runtime. Every mutation to the substrate — whether a new OPA policy, a refactored agent, or a documentation update — passes through the same cryptographic gauntlet that protects production tool-calls.

**Core Tenets:**
1. **Tamper-Evident Everything**: No artifact exists without a verifiable signature.
2. **Zero Trust Between Components**: Even internal agents cannot sign on behalf of each other.
3. **Hardware-Rooted Trust**: Private keys live in silicon, not in environment variables.
4. **Recoverable Without Weakening**: Losing a MacBook must not mean losing the project.
5. **Auditable by Design**: The development history is a forensic asset, not just version control.

---

## 2. Cryptographic Architecture

### 2.1 Current State (HMAC-SHA256)

The substrate currently uses symmetric HMAC-SHA256 for all signing operations via `tachyon/core/signing.py`:

```python
# Current Implementation (IntegrityManager)
digest = hmac.new(self.secret_key, content, hashlib.sha256).hexdigest()
```

**Weaknesses:**
- **No Non-Repudiation**: Shared secret means anyone with the key can forge signatures.
- **Key Distribution Risk**: Key stored in `TACHYON_SECRET_KEY` env var with an insecure fallback.
- **No Identity Binding**: Cannot prove *who* signed — only that *someone* with the key signed.
- **No Quantum Resistance**: HMAC is not vulnerable to Shor's algorithm, but the overall signing model lacks forward-looking PQC defense.

### 2.2 Target State: Ed25519 + ML-DSA-44 (Hybrid)

The migration target is a **hybrid asymmetric + post-quantum** signature scheme:

| Property | Ed25519 (Classical) | ML-DSA-44 (Post-Quantum) |
|----------|--------------------:|-------------------------:|
| **Standard** | RFC 8032 | NIST FIPS 204 |
| **Security** | ~128-bit classical | ~128-bit quantum |
| **Signature Size** | 64 bytes | ~2,420 bytes |
| **Public Key Size** | 32 bytes | ~1,312 bytes |
| **Signing Speed** | ~50,000/sec | ~800/sec |
| **Quantum Safe** | ❌ | ✅ |

**Hybrid Verification Rule:**
```
Signature = Ed25519(content) || ML-DSA-44(content)
Valid = Verify(Ed25519) AND Verify(ML-DSA-44)
```

**Why Hybrid?**
- If PQC implementations prove buggy, Ed25519 still provides classical security.
- If quantum computers arrive, ML-DSA-44 provides post-quantum defense.
- Both NIST standards are finalized (FIPS 186-5 for Ed25519, FIPS 204 for ML-DSA).
- Overhead is negligible for document signing (~2.5KB per signature, <5ms on M5).

### 2.3 Migration Timeline

| Phase | Scope | Priority |
|-------|-------|----------|
| **Phase 25.1** | Ed25519 foundation + Secure Enclave root key | Immediate |
| **Phase 25.2** | Per-agent keys + delegation certificates | High |
| **Phase 25.3** | ML-DSA-44 hybrid overlay + forensic ADR chaining | Medium |
| **Phase 26** | CI/CD hardening + SBOM + reproducible builds | Future |

---

## 3. Key Hierarchy & Trust Model

```
┌─────────────────────────────────────────────────┐
│   ROOT KEY (Apple Secure Enclave)                │
│   • Non-extractable, biometric-gated (Touch ID)  │
│   • Signs: ADR final approval, releases, certs   │
│   • Rotation: Never (project lifetime)           │
│   • Recovery: Shamir 3-of-5 split                │
└───────────────────────┬─────────────────────────┘
                        │ delegates to
                        ▼
┌─────────────────────────────────────────────────┐
│   DEVELOPMENT KEY (macOS Keychain)               │
│   • Daily ADR signing, code commit signing        │
│   • Agent key issuance authority                  │
│   • Rotation: Every 90 days                       │
│   • Recovery: iCloud Keychain sync                │
└───────────────────────┬─────────────────────────┘
                        │ issues
            ┌───────────┼───────────┐
            ▼           ▼           ▼
┌────────────────┐ ┌─────────────┐ ┌──────────────┐
│ SENTINEL KEY   │ │ AIRLOCK KEY  │ │ ENGINEER KEY │
│                │ │              │ │              │
│ • Debates      │ │ • Patch      │ │ • Code       │
│ • Catalog      │ │   approval   │ │   patches    │
│ • Threat intel │ │ • Requires   │ │ • Rego       │
│ • Rotate: 24h  │ │   HITL ACK   │ │   synthesis  │
│                │ │ • Rotate: 7d │ │ • Rotate: 7d │
└────────────────┘ └─────────────┘ └──────────────┘
```

**Key Principle:** An agent can only **self-sign** artifacts within its authorized scope. Cross-agent signing is cryptographically impossible because each agent holds a unique private key.

---

## 4. Apple Secure Enclave Integration

### 4.1 Why Secure Enclave?

The Apple Secure Enclave is a dedicated cryptographic coprocessor in Apple Silicon:
- **Hardware Isolation**: Keys never leave the enclave — operations happen inside the chip.
- **Biometric Gating**: Signing requires Touch ID / Face ID physical confirmation.
- **Survives OS Compromise**: Even root-level malware cannot extract enclave keys.
- **Apple Silicon Native**: M1–M5 all include Secure Enclave with identical APIs.

### 4.2 Recovery Strategy

**Problem**: Secure Enclave keys are non-extractable. A new MacBook means a new key.

**Solution: Root Key + Delegation Model**

The Root Key is generated once and split using **Shamir's Secret Sharing (3-of-5 threshold)**:

| Share | Location | Access Method |
|-------|----------|---------------|
| Share 1 | 1Password vault | Password manager login |
| Share 2 | Physical safe deposit | Physical presence |
| Share 3 | Encrypted cloud (S3 + GPG) | GPG passphrase |
| Share 4 | YubiKey 5 NFC | Physical possession + PIN |
| Share 5 | Printed paper backup | Physical possession |

**Recovery Flow:**
1. Obtain any 3 of 5 shares.
2. Reconstruct root private key via `scripts/recover_keys.py`.
3. Import into new MacBook's Secure Enclave.
4. Generate new Shamir shares, securely destroy old shares.
5. Re-sign the development key certificate with the new root.

**Development Key Recovery**: Syncs automatically via iCloud Keychain. Sign into the same Apple ID on a new MacBook and development keys restore instantly.

---

## 5. Per-Agent Signing Authority

### 5.1 Delegation Certificates

Each agent key is accompanied by a JSON delegation certificate signed by the development key:

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
  "signature": "ed25519:nQ8xL..."
}
```

### 5.2 Agent Signing Scopes

| Agent | Signing Authority | Rotation | Notes |
|-------|------------------|----------|-------|
| **Sentinel** | `debates/*`, `EXPLOITATION_CATALOG.md` | Daily | Fully autonomous |
| **Airlock** | `docs/patches/*`, `CHANGE_CONTROL.md` | Weekly | Requires HITL confirmation |
| **Engineer** | Code patches, Rego policies | Weekly | Staged via Airlock |
| **Development** | `docs/adr/*`, all source | 90 days | Your personal key |
| **Root** | Everything (emergency) | Never | Secure Enclave, biometric |

### 5.3 Verification Chain

A signed artifact is verified by checking the full certificate chain:

1. **Agent cert** is signed by a valid development key ✓
2. **Agent cert** authorizes the operation on this specific artifact ✓
3. **Agent signature** on the artifact matches the cert's public key ✓
4. **Current time** is within the cert's validity period ✓

If any check fails, the artifact is rejected.

---

## 6. Forensic ADR Chaining

Extending the existing `MANIFEST.json` Merkle tree, each ADR will reference the hash of its predecessor, creating an **immutable forensic timeline**:

```json
{
  "adr": "docs/adr/0028-secure-signing-substrate.md",
  "hash": "sha256:a3f8...",
  "parent_hash": "sha256:7b2c... (ADR-0027)",
  "signatures": {
    "agent": "ed25519:...",
    "airlock": "ed25519:..."
  },
  "timestamp": "2026-03-20T13:55:00Z"
}
```

**Benefit**: Tampering with any historical ADR breaks the chain. The Guardian IDS detects this during every `tt ritual` boot ceremony.

---

## 7. Airlock as Certificate Authority

The Airlock evolves from a workflow staging area to a **cryptographic authority**. No artifact is considered "deployed" until it carries dual signatures:

```
artifact.sig = agent_signature + airlock_signature
```

**Enforcement Rule:**
```
signed_by(agent)
AND approved_by(airlock)
AND co-signed_by(airlock_key)
→ TRUSTED
```

**Benefit**: A compromised agent alone cannot deploy malicious changes. The human operator's Airlock approval is cryptographically bound to the artifact.

---

## 8. Development Workflow

### 8.1 The Signing Ceremony (Per-Commit)

```
1. Agent proposes change (code, ADR, policy)
2. Agent self-signs with its delegated key
3. Proposal staged in Airlock
4. Human reviews via NeoVIM / TUI / CLI
5. Airlock co-signs upon approval
6. Commit allowed (Git commit signing via SSH)
7. MANIFEST.json updated with hash chain entry
8. tt ritual verifies full Merkle integrity
```

### 8.2 Pre-Commit Hooks

Automated verification gates before any code enters the repository:

- **Signature Verification**: All `.sig` files are cryptographically valid.
- **Unsigned ADR Detection**: New ADRs without signatures are rejected.
- **Agent Certificate Validation**: Expired or unauthorized certs are flagged.
- **Secret Detection**: Hardcoded keys or tokens are blocked.

### 8.3 CI/CD Principles

> **Rule: CI is hostile.** Even GitHub Actions is not a trusted signing environment.

- CI **builds**, **tests**, and **verifies** signatures.
- CI **NEVER signs** production artifacts.
- All signing happens locally on the developer's MacBook (Secure Enclave).
- Releases require offline, biometric-gated signing.

---

## 9. Threat Model Additions

The following threat vectors are added to `THREAT_MODEL.md` as part of Phase 25:

### §9C — Signing Key Compromise
- **Attack**: Attacker extracts private key or forges HMAC.
- **Mitigation**: Secure Enclave (private key never leaves hardware). Public key only in repo.

### §9D — Cross-Agent Signature Forgery
- **Attack**: One agent signs artifacts on behalf of another.
- **Mitigation**: Per-agent keypairs + scoped delegation certificates. Cryptographically impossible to cross-sign.

### §9E — Key Substitution Attack
- **Attack**: Attacker replaces public keys in the repository.
- **Mitigation**: Root key hash pinned in code. Trust anchor hardcoded in `signing.py`.

### §9F — Signing Oracle Attack
- **Attack**: Agent tricks the system into signing malicious content.
- **Mitigation**: Airlock displays diff, semantic summary, and risk score before co-signing.

### §9G — Replay Attack on Signed Artifacts
- **Attack**: Old signed artifact reused to revert security improvements.
- **Mitigation**: Timestamp + monotonic ADR sequence + hash chain in MANIFEST.json.

### §9H — Harvest-Now-Decrypt-Later
- **Attack**: Quantum computer breaks classical signatures in the future.
- **Mitigation**: Hybrid Ed25519 + ML-DSA-44 signatures. Both must verify.

---

## 10. Operational Procedures

### 10.1 Daily Operations
```bash
# Morning: Verify substrate integrity
tt ritual

# After changes: Sign new ADR
python3 scripts/sign_artifact.py docs/adr/0028-secure-signing.md

# Evening: Full signature audit
python3 scripts/verify_all_signatures.py --strict
```

### 10.2 Key Rotation Schedule

| Key Type | Frequency | Backup Strategy | Recovery Time |
|----------|-----------|-----------------|---------------|
| Root | Never | Shamir 3-of-5 + YubiKey | < 1 hour |
| Development | 90 days | iCloud Keychain | < 5 minutes |
| Sentinel | Daily | N/A (re-issue from dev key) | Instant |
| Airlock | Weekly | N/A (re-issue from dev key) | Instant |
| Engineer | Weekly | N/A (re-issue from dev key) | Instant |

### 10.3 Key Compromise Response

**Development Key Compromised:**
1. Revoke key immediately via `scripts/revoke_key.py`
2. Generate new development key from root
3. Re-sign recent artifacts with new key
4. Force rotate all agent keys
5. Audit signing log for unauthorized operations

**Root Key Compromised (Catastrophic):**
1. Retrieve 3 of 5 Shamir shares
2. Reconstruct root key
3. Generate new root key in Secure Enclave
4. Create new Shamir shares, destroy old shares
5. Re-sign entire repository
6. Rotate all downstream keys

---

## 11. Consensus & Attribution

This SDLC strategy was synthesized from independent assessments by four LLMs:

| Contributor | Key Contribution |
|-------------|-----------------|
| **Claude** | Cryptographic specification (Ed25519 + ML-DSA-44), Shamir recovery, phased implementation roadmap |
| **OpenAI** | Forensic ADR hash-chaining, Airlock as Certificate Authority, dual-signature model |
| **Grok** | Apple-native CryptoKit awareness, per-agent SPIFFE-style identities, CLI-first patterns |
| **Gemini** | Comparative analysis, winner selection (Claude), augmentation synthesis |
| **Antigravity** | Final synthesis, "Path Not Taken" curation, alignment with existing substrate architecture |

---

## 12. Path Not Taken

The following ideas were proposed by the LLM panel but **deferred or rejected** for documented reasons:

### 12.1 Swift `tachyon-sign` CLI (Grok)
**Proposal**: Build a Swift CLI using Apple CryptoKit for native Secure Enclave access and ML-DSA signing.
**Why Deferred**: Introduces a second language (Swift) into a Python-centric codebase. The maintenance burden outweighs the benefit. Python's `cryptography` library + `pyobjc-framework-Security` provides equivalent Keychain access. If CryptoKit-exclusive features are needed later, this can be revisited as a thin shim.

### 12.2 Full Directory Restructure (Claude)
**Proposal**: Reorganize the entire repo into `src/`, `runtime/`, `security/`, `data/`, `build/` directories, moving debates, logs, and tasks out of the root.
**Why Deferred**: Too disruptive for a mature, actively developed codebase with 170+ tests, extensive import paths, and multiple agent configurations. The *principles* of trust segmentation (signed vs. unsigned data separation) are adopted, but the *physical reorganization* is not worth the breakage risk. May revisit in a major version bump.

### 12.3 Nix for Reproducible Builds (Grok)
**Proposal**: Use `nix-darwin` to guarantee deterministic, reproducible builds on Apple Silicon.
**Why Rejected**: Over-engineered for a single-developer, HITL-mode experimentation lab. The complexity of maintaining Nix flakes outweighs the reproducibility benefit at this stage. Python's `pip freeze` + hash pinning in `requirements.txt` provides sufficient reproducibility for now.

### 12.4 12-Week Phased Rollout (Claude)
**Proposal**: A 12-week, 6-phase implementation timeline including team training.
**Why Compressed**: Tachyon Tongs is a single-developer project with a high-velocity development cycle. The 12-week timeline is calibrated for enterprise teams. We compress this into 3 focused phases (25.1, 25.2, 25.3) without sacrificing security rigor.

### 12.5 X.509 Certificate Wrapping (OpenAI Tier 2)
**Proposal**: Wrap Ed25519 keys in X.509 certificates for identity binding, rotation tracking, and revocation infrastructure.
**Why Deferred**: X.509 PKI is a significant infrastructure commitment (CRLs, OCSP responders, cert chains). Our lightweight JSON delegation certificates achieve the same per-agent scoping with far less operational overhead. If Tachyon Tongs evolves into a multi-operator deployment, X.509 can be layered on.

### 12.6 Daily Agent Key Rotation via LaunchDaemon (Claude)
**Proposal**: Automatic daily key rotation for Sentinel via a macOS LaunchAgent at 3 AM.
**Why Deferred**: Automated key rotation without operator awareness creates a silent failure mode. If the rotation fails (disk full, keychain locked), the Sentinel silently loses signing capability. We prefer explicit rotation triggered during `tt ritual` so failures are immediately visible.

---

**End of Document**
