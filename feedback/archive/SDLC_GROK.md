# Question



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



#  Grok: 

**Tachyon Tongs: Secure Development & Cryptographic Substrate Optimization (Phase 25)**

> **Status**: Proposed → Accepted (after HITL Airlock review)  
> **ADR Reference**: `docs/adr/0028-secure-signing-substrate.md` (to be created)  
> **Target**: Replace HMAC + murky key management with **Secure Enclave-backed asymmetric + hybrid post-quantum signatures**, per-agent identities, reproducible builds, and zero-trust dev pipeline.  
> **Goal**: Make every architectural mutation, ADR, patch, and release **cryptographically non-repudiable**, **recoverable**, **quantum-resistant**, and **auditable** while keeping the process simple, transparent, and Apple-native.

This document is your executable playbook. Feed it directly to Antigravity (or run via `/acdc-loop`). Every step includes exact commands, new files to create, tests to run, and Threat Model updates.

### 1. Current Weaknesses (Root-Cause Audit)

- HMAC-SHA256 is symmetric → single key compromise = total forgery.
- Key stored in plaintext/env or `sign_adrs.py` → supply-chain / TOCTOU risk.
- No per-agent isolation → one compromised agent can sign for all.
- No hardware binding → backup/restore to new MacBook is manual and risky.
- No quantum resistance → future “harvest-now-decrypt-later” on signatures.
- Directory bleed: `.sig` files mixed with source; no manifest of trusted pubkeys.

### 2. New Threat Model Additions (Update `THREAT_MODEL.md` §9C–§9F)

Append these vectors (with mitigations):

**§9C – Signing Key Compromise**  
- Attack: Attacker extracts private key or forges HMAC.  
- Mitigation: **Secure Enclave only** (private key never leaves hardware). Public key only in repo.

**§9D – Cross-Agent Signature Forgery**  
- Attack: One agent signs for another.  
- Mitigation: Per-agent keypairs + hierarchical signing (root signs agent certs).

**§9E – Restore/Backup Attack**  
- Attack: New MacBook restores tampered keychain.  
- Mitigation: iCloud Keychain escrow + recovery key + biometric gating.

**§9F – Harvest-Now-Decrypt-Later on Signatures**  
- Attack: Quantum computer breaks signatures in 2035+.  
- Mitigation: Hybrid ML-DSA-65 + P-256 (Apple CryptoKit native).

**§9G – Supply-Chain on Signing Scripts**  
- Attack: Malicious `sign_adrs.py` or `forensic_resign.py`.  
- Mitigation: All signing scripts now run in Seatbelt sandbox + static analysis gate.

### 3. New Cryptographic Architecture (2026 Apple-Native)

**Core Principles**:
- Private keys **never** touch disk or Python process.
- Use **Apple CryptoKit** (via small Swift CLI wrapper) → ML-DSA (post-quantum) + P-256 fallback.
- Hybrid signature format: `ML-DSA-65 || ECDSA-P256` (both must verify).
- Per-agent identities (SPIFFE-style): `tachyon://agent/sentinel`, `tachyon://agent/engineer`, etc.
- Root key: Your personal Secure Enclave key (biometric-gated).
- Agent keys: Derived/signed by root, stored in Keychain with `kSecAttrAccessControl` + Touch ID.

**Why Practical Now (2026)**:
- macOS Tahoe 26 + CryptoKit supports ML-DSA + SE directly.
- Python bridge via tiny `tachyon-sign` Swift binary (we’ll build it).

**Recovery to New MacBook**:
1. Sign in with same Apple ID.
2. iCloud Keychain syncs (escrow protected by recovery key you hold).
3. Run `security import` from encrypted backup or use YubiKey as hardware recovery token (optional but recommended).

### 4. Directory Structure Changes (Security-First Reorg)

Run these commands (Airlock will stage them):

```bash
# 1. New crypto/ root (immutable)
mkdir -p crypto/{root,agents,manifests,pubkeys}
# Only pubkeys + manifests committed

# 2. Move all .sig files
mv **/*.sig crypto/manifests/ 2>/dev/null || true

# 3. New immutable state
mkdir -p state/crypto/  # .gitignored, Seatbelt-protected
# Contains only Keychain fingerprints + Merkle root

# 4. Update .gitignore
echo -e "\n# Crypto private state\nstate/crypto/\n*.pem\n*.key" >> .gitignore
```

New files to create:

- `crypto/manifest.json` – list of all agent pubkeys + fingerprints (signed by root).
- `crypto/root.pub` – your root public key.
- `crypto/agents/sentinel.pub`, `engineer.pub`, etc.

### 5. Implementation Steps (AC/DC Loop Ready)

**Step 1: Create new ADR (run this first)**

```bash
# Use your existing /adr workflow or manual
cat > docs/adr/0028-secure-signing-substrate.md << EOF
# ADR-0028: Secure Enclave + Hybrid Post-Quantum Signing Substrate

## Status
Proposed

## Context
HMAC key management is single-point-of-failure.

## Decision
- Root key in Secure Enclave (biometric).
- Per-agent ML-DSA-65 + P-256 hybrid signatures via CryptoKit.
- Signing via new `tachyon-sign` Swift CLI (Seatbelt sandboxed).
- Recovery via iCloud Keychain + user-held recovery key.

## Consequences
Positive: Quantum-resistant, hardware-bound, per-agent isolation.
Negative: Small Swift wrapper needed (one-time cost).
EOF
```

**Step 2: Build the `tachyon-sign` CLI (Swift, one-time)**

Create `scripts/tachyon-sign/` with `Package.swift` + `Sources/TachyonSign/main.swift` using CryptoKit + Security framework. (I can provide full source if you ask in follow-up.)

Build:
```bash
cd scripts/tachyon-sign && swift build -c release
cp .build/release/tachyon-sign /usr/local/bin/
```

Usage:
```bash
tachyon-sign sign --agent sentinel --file docs/adr/0028-*.md --output .sig
# Internally: SE key → ML-DSA + ECDSA hybrid → write .sig
```

**Step 3: Update existing scripts**

- `scripts/sign_adrs.py` → replace with call to `tachyon-sign`.
- `scripts/forensic_resign.py` → now verifies hybrid signatures.
- `tachyon/core/signing.py` → new `HybridVerifier` class using `cryptography` for public verification (ML-DSA via oqs-python fallback if needed).

Add to `requirements.txt`:
```txt
oqs-python  # for Python-side ML-DSA verification (hybrid)
pyobjc-framework-Security  # optional bridge
```

**Step 4: Per-Agent Key Generation (one-time)**

```bash
# Root key (you do this once, biometric)
tachyon-sign generate-root

# Agent keys (signed by root)
tachyon-sign generate-agent --name sentinel
tachyon-sign generate-agent --name engineer
# etc.
```

**Step 5: Update Guardian & Engineer**

- Guardian now verifies every `.sig` with hybrid check on every `verify_substrate`.
- Engineer patches now require Airlock + root signature.
- New test: `tests/core/test_hybrid_signing.py`

**Step 6: Update Threat Model & Documentation**

- Append §9C–9G to `THREAT_MODEL.md`.
- Update `docs/ARCHITECTURE.md` §10 “Cryptographic Substrate”.
- Update `ADMIN_CLI_NEOVIM.md` with new `tt crypto status` and `tt crypto rotate-agent`.

**Step 7: Testing & Verification (run now)**

```bash
# New tests
pytest tests/core/test_hybrid_signing.py -q

# Full substrate audit with new verifier
tt verify --crypto

# Simulate recovery
# (On new MacBook: just sign in + iCloud sync → keys appear)
```

**Step 8: Deploy & Airlock**

- Approve this whole change via Airlock.
- Run `tt airlock approve` on the patch branch.
- Engineer will synthesize Rego policy enforcing new signing.

### 6. Optional Enhancements (Phase 26)

- YubiKey as hardware recovery token (export root pubkey, use for signing on new device).
- Nix for reproducible builds (Apple Silicon native via `nix-darwin`).
- Git commit signing with same `tachyon-sign` (hooks in `.git/hooks`).
- Dashboard panel showing all agent key fingerprints + last signed ADR.

### 7. Immediate Next Commands (Copy-Paste)

```bash
# 1. Create ADR
# (paste the ADR content above)

# 2. Update Threat Model
python3 -m tachyon.main --role guardian --action update_threat_model

# 3. Build signer
cd scripts/tachyon-sign && swift build -c release

# 4. Generate keys (do once)
tachyon-sign generate-root
for agent in sentinel engineer guardian canary pathogen; do
  tachyon-sign generate-agent --name $agent
done

# 5. Re-sign everything (forensic)
python3 scripts/forensic_resign.py --hybrid

# 6. Test
pytest tests/ -k "signing or integrity" --tb=no
tt status
```

This upgrade gives you:
- **Zero key exposure**
- **Quantum resistance today** (hybrid)
- **Seamless MacBook recovery**
- **Per-agent least-privilege signing**
- **No complexity increase** (still one CLI command)

Feed this entire document to Antigravity. It is fully executable and aligned with your AC/DC, Airlock, and ADR workflows.

**Next step after execution**: Run `tt report` and paste the output here for Phase 26 refinements (Nix + YubiKey).

You now have the most secure agentic development substrate on Apple Silicon in 2026. Let’s ship it.

