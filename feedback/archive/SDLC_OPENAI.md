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

# OpenAI:

Alright — this is a really solid foundation already. You’ve basically built a *proto high-assurance system*, but your weakest link right now is exactly what you pointed out: **key management + signing model + supply chain discipline**.

I’m going to give you a **deep, structured markdown** you can drop straight into AntiGravity. This focuses on:

* Replacing HMAC → asymmetric + hardware-backed trust
* Clean key hierarchy (per-agent optional)
* Recovery model (new MacBook scenario)
* Dev / CI / deployment hardening
* Threat model expansion (you *are* missing some big ones)
* Repo / directory restructuring for trust boundaries

---

# 🛡️ Tachyon Tongs — Secure Development & Signing Architecture (vNext)

## 0. Design Goals

* **Tamper-evident everything**
* **Zero trust between components (even internal agents)**
* **Deterministic + reproducible builds**
* **Hardware-rooted trust where possible**
* **Recoverable without weakening guarantees**
* **Auditable by design (not by effort)**

---

# 1. Replace HMAC → Asymmetric Signing (Critical)

## Problem with Current HMAC

* Shared secret = **single point of catastrophic failure**
* No non-repudiation
* Key distribution is unsafe / unclear
* Doesn’t scale across agents or machines

## Recommendation: Hybrid Signing Stack

### Tier 1 (Now): Ed25519

* Fast
* Small signatures
* Widely supported
* Ideal for:

  * ADR signing
  * manifest signing
  * agent attestations

### Tier 2 (Optional Upgrade): Ed25519 + X.509 wrapper

* Enables:

  * identity binding
  * rotation tracking
  * revocation

---

# 2. Hardware-Backed Keys on macOS

Use:

* **Secure Enclave via Keychain**

### Design

* Private key:

  * **non-exportable**
  * lives in Secure Enclave
* Public key:

  * stored in repo (`keys/trusted/`)

### Signing Flow

```
ADR.md → hash → sign via Secure Enclave → ADR.md.sig
```

---

## ⚠️ Recovery Problem (New MacBook)

You *cannot export Secure Enclave keys* → so:

### Solution: Root + Delegation Model

#### Root Key (Offline)

* Generated once
* Stored:

  * hardware token (YubiKey) OR
  * encrypted offline backup

Used ONLY for:

* signing developer keys
* revocation

---

#### Developer Key (MacBook)

* Lives in Secure Enclave
* Signed by root

```
root_key → signs → dev_key_1.pub
```

---

#### Trust Model

```
ADR.sig verified by:
    dev_key → trusted because → signed by root_key
```

---

## Result

* You can lose your MacBook
* Recreate new key
* Re-sign it with root
* System remains trusted

---

# 3. Per-Agent Keys (Should You Do It?)

Short answer: **Yes, but selectively**

## Recommended Model

| Component | Key                    |
| --------- | ---------------------- |
| Guardian  | dedicated key          |
| Engineer  | dedicated key          |
| Sentinel  | dedicated key          |
| Canary    | ephemeral key          |
| Pathogen  | isolated / sandbox key |

---

## Why?

* Limits blast radius
* Enables behavioral attribution
* Prevents lateral trust abuse

---

## Important Constraint

DO NOT allow:

* agents to sign *other agents’ outputs*

Only:

* self-sign
* or sign through Airlock (central authority)

---

# 4. Airlock as Root of Trust

Your Airlock should become:

> **The only authority allowed to mutate trusted state**

## New Rule

Nothing is trusted unless:

```
signed_by(agent)
AND
approved_by(airlock)
AND
co-signed_by(airlock_key)
```

---

## Dual Signature Model

```
artifact.sig = agent_signature + airlock_signature
```

---

## Benefit

* Compromised agent ≠ compromised system
* Human oversight becomes cryptographically enforced

---

# 5. Quantum-Ready (Do This Carefully)

Short answer:

> Don’t go full PQ yet — go **hybrid**

## Recommended Hybrid

* Ed25519 (primary)
* * Dilithium2 (secondary, optional)

Sign both:

```
.sig = ed25519_sig + dilithium_sig
```

---

## Why Hybrid?

* PQ algorithms still evolving
* Larger signatures (performance hit)
* Tooling immature

---

## Where to Apply PQ First

* ADRs
* MANIFEST root
* key certificates

NOT:

* high-frequency logs
* runtime agent chatter

---

# 6. Supply Chain Hardening (You’re Close, But Not Complete)

You already have:

* signatures
* manifest
* integrity checks

You’re missing:

## 6.1 Reproducible Builds

* lock dependencies (you already partially do)
* add:

```
pip-tools OR uv lock
```

* hash every dependency

---

## 6.2 Build Attestation

Every build should produce:

```
build.json:
  git_commit
  dependency_hashes
  builder_identity
  timestamp
  signature
```

---

## 6.3 Verify Before Run

At runtime:

```
if not verify(build.json):
    abort
```

---

# 7. CI/CD Hardening (Critical Gap)

## Rule: CI is hostile

Even GitHub Actions is not trusted.

---

## Required Changes

### 7.1 No Signing in CI

CI:

* builds
* tests
* verifies

BUT:

❌ NEVER signs production artifacts

---

### 7.2 Offline Signing Step

Flow:

```
CI build → artifact
↓
manual / local signing (Secure Enclave)
↓
publish
```

---

## 7.3 Provenance Tracking

Store:

```
/provenance/
  artifact.hash
  artifact.sig
  build.json
```

---

# 8. Directory Restructuring (Security Boundaries)

Your repo is good, but not **trust-segmented**.

## Proposed Layout

```
/trust/
  /root/
    root.pub
  /developers/
    dev1.pub
  /agents/
    guardian.pub
    engineer.pub

/signed/
  /adr/
  /debates/
  /catalog/

/unsigned/
  /incoming/
  /canary/

/build/
  /artifacts/
  /provenance/

/runtime/
  /ephemeral/
```

---

## Key Principle

> Signed and unsigned data must NEVER mix.

---

# 9. Threat Model Additions (You’re Missing These)

## 9.1 Key Substitution Attack

Attacker replaces public keys.

Mitigation:

* pin root key hash in code
* hardcode trust anchor

---

## 9.2 Signing Oracle Attack

Agent tricks system into signing malicious content.

Mitigation:

* Airlock must display:

  * diff
  * semantic summary
  * risk score

---

## 9.3 Replay Attack

Old signed artifact reused maliciously.

Mitigation:

* include:

  * timestamp
  * monotonic version
  * hash chain

---

## 9.4 Cross-Agent Privilege Escalation

Agent uses another agent’s authority.

Mitigation:

* strict key separation
* policy-level identity binding

---

## 9.5 Build System Compromise

Malicious dependency injected.

Mitigation:

* hash pinning
* offline verification
* allowlist registries

---

## 9.6 TOCTOU on Signed Artifacts

File modified after verification.

Mitigation:

* verify at:

  * load time
  * execution time

---

# 10. ADR Signing Upgrade (Concrete Spec)

## File Format

```
ADR.md
ADR.md.sig
ADR.meta.json
```

---

## ADR.meta.json

```json
{
  "author": "engineer_agent",
  "key_id": "engineer_key_v3",
  "timestamp": 1710000000,
  "hash": "sha256:...",
  "parent_hash": "previous ADR hash",
  "signatures": {
    "agent": "...",
    "airlock": "..."
  }
}
```

---

## Chain Them

You already have Merkle roots — extend this:

* each ADR references previous
* full audit chain

---

# 11. Dev Workflow (Secure + Fast)

## New Flow

```
1. Agent proposes change
2. Engineer generates ADR
3. Signed by agent
4. Sent to Airlock
5. Human review (NeoVIM UI)
6. Airlock signs
7. Commit allowed
8. Manifest updated
```

---

## Optional Upgrade

Auto-reject if:

* unsigned
* key unknown
* signature invalid

---

# 12. Testing Enhancements

Add:

### 12.1 Signature Fuzzing

* corrupted sigs
* swapped keys
* replay attempts

---

### 12.2 Red Team: Signing Attacks

Pathogen should attempt:

* fake ADR injection
* signature stripping
* key confusion

---

### 12.3 Continuous Verification

Run:

```
verify_substrate()
```

on:

* startup
* every N minutes
* before critical actions

---

# 13. Opinionated Takes (You Asked For It)

* Moving off HMAC → **non-negotiable**
* Per-agent keys → **worth it**
* Secure Enclave → **huge win**
* PQ crypto → **only hybrid for now**
* CI signing → **absolutely not**
* Airlock → should become **cryptographic authority**, not just workflow

---

# 14. If You Want Next Step

I can go one level deeper and give you:

* exact Python code for:

  * Secure Enclave signing
  * Ed25519 + Dilithium hybrid
  * ADR verification pipeline
* OR redesign your `sign_adrs.py` + `verify_substrate.py` to match this

Just say which direction 👍


