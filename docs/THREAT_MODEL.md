# Tachyon Tongs: Comprehensive Threat Model

This document outlines the adversarial landscape for **Tachyon Tongs**. It identifies critical attack vectors, trust boundaries, and mitigation strategies for both Inbound (Threat Mitigation) and Outbound (Data Loss Prevention) security flows.

## 1. Trust Boundaries

- **Boundary A: The Internet (Untrusted)**: Remote data sources, APIs, and LLM providers.
- **Boundary B: The Substrate PEP (Substrate Daemon)**: The policy enforcement point running on the host.
- **Boundary C: The Protected Agent (Vulnerable)**: The cognitive reasoning layer susceptible to injection.
- **Boundary D: The Organizational Workspace (Sensitive)**: Local files, secrets, and proprietary code.

## 2. Inbound Threat Vectors (External to Agent)

### A. Indirect Prompt Injection (IPI)
- **Description**: An attacker embeds malicious instructions in external data (e.g., a website's metadata or a poisoned GitHub README) that the agent fetches.
- **Impact**: The agent's core system prompt is overridden, allowing the attacker to hijack the agent's tools (e.g., "Expose all local environment variables").
- **Tachyon Mitigation**: The **Guardian Triad** isolates data fetching. The **Analyst** uses Metal-accelerated MLX models to scan for instruction-drift within strict delimiters.

### B. Server-Side Request Forgery (SSRF)
- **Description**: An attacker tricks the agent into making requests to internal infrastructure (e.g., `169.254.169.254` for cloud metadata or `localhost:8181` for OPA).
- **Impact**: Exposure of secrets, internal network mapping, or unauthorized policy modification.
- **Tachyon Mitigation**: The **SafeFetch OPA Gate** enforces strict domain/IP allowlists and explicitly blocks local/private IP ranges.

### C. Agent Hijacking
- **Description**: Gaining control over an agent's execution loop via remote code execution (RCE) in a tool dependency.
- **Impact**: Full host compromise if the agent has unrestricted OS access.
- **Tachyon Mitigation**: **Tier 0 Sandboxing** (macOS Seatbelt) denies network access to compute tasks and restricts filesystem writes to a temporary, randomized workspace.

### D. Memory / Vector Poisoning
- **Description**: Inserting "sleeper" instructions into a long-term memory store (Vector DB).
- **Impact**: The agent remains safe until it retrieves the poisoned memory, at which point it executes the malicious "old" instruction as a "new" command.
- **Tachyon Mitigation**: All data retrieved from *any* external tool (including database fetches) is treated as untrusted and passed through the **Intent Gate**.

## 3. Supply Chain Threat Vectors (Substrate & Managed Agents)

### A. Hallucination Squatting
- **Description**: An agent "hallucinates" a non-existent package name. An attacker proactively registers this name on PyPI with a malicious payload.
- **Impact**: Arbitrary code execution within the agent's environment or host compromise.
- **Tachyon Mitigation**: **Deterministic Capability Binding** via the `StateManager` whitelist. Only cryptographically verified or manually approved libraries are permitted for installation/import.

### B. Dependency Confusion / Poisoning
- **Description**: An agent fetches a malicious public package that shadows a private internal one, or a legitimate dependency is compromised upstream.
- **Impact**: Exfiltration of environment variables, secrets, or data.
- **Tachyon Mitigation**: The **Integrity Agent** performs real-time `pip-audit` scans before allowing any installation into the Tier 0 sandbox.

### C. Agent Supply Chain (SKILL.md Poisoning)
- **Description**: An attacker modifies a `SKILL.md` file in the repository (e.g., via a compromised PR) to include malicious system prompts or tool-call triggers.
- **Impact**: Persistent hijacking of any agent utilizing that skill.
- **Tachyon Mitigation**: All `SKILL.md` files are cryptographically signed. The `IntegrityManager` prevents the execution of any skill whose signature does not match the known developer key.

## 4. Outbound Threat Vectors (Agent to External)

### A. Data / Telemetry Exfiltration
- **Description**: A malicious or compromised agent attempts to send sensitive organizational data (API keys, PII, internal logs) to an attacker-controlled endpoint or a public LLM provider.
- **Impact**: Breach of organizational confidentiality and data sovereignty.
- **Tachyon Mitigation**: The **Reverse Firewall (Outbound PEP)** introspects outbound requests, using Rego/Cedar policies to scan for sensitive tokens and patterns before they leave the substrate.

### B. Prompt Leakage
- **Description**: An agent incorrectly includes its private system prompt or internal reasoning in a message sent to an external user or API.
- **Impact**: Exposure of intellectual property and defensive strategies.
- **Tachyon Mitigation**: **Output Sanitization** at the Verifier Node scans outgoing text for signatures of system instructions.

## 5. Substrate-Specific Exploits

### A. OPA/Cedar Policy Bypass
- **Description**: Crafting a request that satisfies the literal syntax of a policy but violates its semantic intent.
- **Tachyon Mitigation**: **Semantic Intent Mapping**.

### B. Architectural Drift / Forensic Evasion
- **Description**: Unauthorized structural changes to the substrate to bypass security gates or elude detection.
- **Tachyon Mitigation**: **ADR-as-IDS**. Cryptographic signing of architecture records ensures any out-of-band mutation is detected as a forensic anomaly.

### C. MLX Inference Evasion
- **Description**: Adopting "Jailbreak" techniques (e.g., Base64 encoding, roleplay) to hide malicious instructions from the Analyst's LLM-based scan.
- **Tachyon Mitigation**: **Scalable Oversight (The Airlock Debate)** pits an Analyst against a Skeptic agent to catch subtle evasions through adversarial discourse.

### D. Airlock Dashboard Hijacking
- **Description**: An attacker with local access or a compromised browser tab attempts to interact with the Airlock GUI via CSRF or XSS.
- **Impact**: Unauthorized authorization of a malicious patch or deletion of security logs.
- **Tachyon Mitigation**: The Airlock resides exclusively on `127.0.0.1`. All WebSocket/API calls require a short-lived **Substrate Session Token** and enforced Content Security Policy (CSP) headers.

## 6. Model-Level & Cognitive Attacks

### A. Latent Instruction Activation
- **Description**: Exploiting "jailbroken" states or hidden triggers in the base LLM weights that bypass system-prompt constraints.
- **Tachyon Mitigation**: **Differential Reasoning**. Comparing outputs from Gemini (Google), Claude (Anthropic), and GPT (OpenAI) to detect anomalous deviations in behavior.

### B. Evolution Loop Poisoning
- **Description**: Injecting "subtle failures" into the Pathogen's red-teaming logic to cause the Sentinel to generate weak or permissive policies.
- **Tachyon Mitigation**: **Signed Mutation Intents** ensure all evolutionary changes are attributed to a verified execution run, with automated "Fitness Audits" by an independent Meta-Critic.

### C. LLM Tool-Use Confusion / Schema Injection
- **Description**: An attacker crafts inputs that exploit ambiguity in tool schemas, causing the LLM to invoke the wrong tool, pass malicious parameters, or chain tools in an unintended sequence (e.g., routing a `safe_fetch` result directly into `safe_execute`).
- **Impact**: Policy bypass via legitimate-looking tool calls that compose into an attack chain.
- **Tachyon Mitigation**: **ImmutableToolRequest** freezes all parameters at the routing boundary. The `ToolRouter` validates action+parameter combinations against a strict schema allowlist. The Airlock Debate Triad provides a secondary cognitive check on proposed tool sequences.

## 7. Key-Centric Threat Vectors (The Root of Trust)

As Tachyon Tongs moves toward a forensic IDS model, the protection of cryptographic keys is paramount.

### A. Accidental Secret Leakage (Credential Exposure)
- **Description**: The `TACHYON_SECRET_KEY` is accidentally committed to GitHub via a `.env` file or hardcoded in a script.
- **Impact**: Attacker can forge valid `.sig` files for any ADR or catalog entry, neutralizing the substrate's forensic integrity.
- **Tachyon Mitigation**: 
    - **Anti-Entropy Protocol**: Keys are never stored in the repo. 
    - **Automated Verification**: `IntegrityManager` checks for environment injection only.
    - **Reference**: See [Generation & Storage](file:///Users/rds/antigravity/tachyon_tongs/docs/KEYS.md#storage--injection-anti-entropy-protocol).

### B. Malicious Key Exfiltration (Local Malware)
- **Description**: Malware running on the host attempts to read environment variables or memory to steal the `TACHYON_SECRET_KEY`.
- **Impact**: Attacker gains the ability to forge architectural records or bypass integrity gates until the key is rotated.
- **Tachyon Mitigation**: 
    - **Volatile Injection**: The key exists only in the environment/memory of the daemon.
    - **Hardware Moat (Planned)**: Transition to asymmetric hardware signing (Yubikey/Secure Enclave) ensures that the private key is never exposed to the OS-level memory, even to the substrate itself.
    - **Reference**: See [Evolutionary Roadmap](file:///Users/rds/antigravity/tachyon_tongs/docs/KEYS.md#phase-3-hardware-root-vision).

## 8. Supply Chain & Repository Integrity (GitHub)

The GitHub repository is the "Source of Truth" for the substrate's architecture. Compromise of the repo affects all managed agents.

### A. Malicious Commit Injection
- **Description**: An attacker gains write access to the repository and modifies an ADR to loosen security constraints or injects a "Trojan" tool.
- **Tachyon Mitigation**: 
    - **Merkle Anchoring**: The `docs/adr/MANIFEST.json` cumulative root detects any structural or content drift in the ADR history.
    - **OOB Attestation (Gated)**: Planned remote storage of the Merkle Root ensures detection even if the local manifest is also tampered with.

### B. CI/CD Pipeline Hijacking
- **Description**: Attackers modify the GitHub Actions workflow to bypass regression tests or inject malicious binaries during deployment.
- **Tachyon Mitigation**: **Agentic Verification**. The substrate performs its own `Guardian IDS` audit during startup, independent of the external CI/CD state.

## 9. Operational & Infrastructure Threats

### A. Append-Only Log Flooding (DoS on HITL)
- **Description**: An adversary (or a misconfigured agent) triggers massive volumes of `EVOLUTION.md`, `CANARY_LOG.md`, or `RUN_LOG.md` entries. This overwhelms the Human-In-The-Loop operator with noise, creating a "fog of war" that masks genuine security events.
- **Impact**: Degraded forensic review capacity. Alert fatigue leading to missed critical events. Potential filesystem exhaustion (e.g., `RUN_LOG.md` already at 93KB after limited operation).
- **Tachyon Mitigation**:
    - **Rate-Bounded Logging**: The `AdaptiveRateLimiter` should be extended to cover log-write actions, not just tool calls.
    - **Log Rotation**: Implement the planned archival script to prune historical phases to `ACCOMPLISHMENTS.md` and rotate `RUN_LOG.md` at a configurable size threshold.
    - **Anomaly Detection**: The Guardian audit should flag unusual log-write velocity as a potential DoS indicator.

## 10. Key Delegation & Sub-Key Compromise (Phase 25.2)

The transition to a hierarchical key model introduces specific risks regarding derived agent keys.

### A. Sub-Key Exfiltration (Sentinel/Engineer)
- **Description**: An attacker compromises an active agent session and steals the derived Ed25519 sub-key from volatile memory.
- **Impact**: Attacker can forge signatures for that specific agent (e.g., a Sentinel can forge a "Clean" report). However, they CANNOT forge the Root Key or other agent keys.
- **Tachyon Mitigation**: 
    - **Ephemeral Sub-Keys**: Agent keys are derived from the hardware Root Key on-demand and are never persisted to disk.
    - **Session Gating**: Sub-key derivation requires a hardware "unlock" (Touch ID) if strict mode is enabled.

### B. Keychain Poisoning (Local Persistence)
- **Description**: An attacker with local admin access modifies the macOS Keychain entry to replace the legitimate Root Seed with a malicious one.
- **Impact**: The substrate continues to function but signs against an attacker-controlled key, allowing for "Shadow Substrate" operations.
- **Tachyon Mitigation**:
    - **Manifest Pinning**: The `ROOT_MANIFEST.json` contains the expected Public Key fingerprint. The substrate performs a "Sanity Check" on boot; if the Keychain key does not match the pinned manifest, it triggers a `TRUST_BREACH` halt.

## 11. Environment Identity & Path Hijacking (N-Version)
- **Description**: An attacker exploits an "Environmental Disconnect" (like the Phase 25.2 debacle) to run a malicious version of the substrate in a shadow environment (e.g., a poisoned `pyenv` shim) that the user mistakes for the real one.
- **Tachyon Mitigation**:
    - **SEC-001 (Environment Identity)**: Mandatory zero-mock E2E testing against the user's active `python3` binary.
    - **Signed Path Discovery**: The `tt` command verifies its own absolute path against a signed manifest on startup.

## 12. Post-Quantum Cryptography Threats (Phase 25.4)

The Hybrid PQC overlay introduces specific risks around the ML-DSA-65 layer.

### A. PQC Algorithm Downgrade (Signature Stripping)
- **Description**: An attacker modifies a `.sig` file to remove the `mldsa65:` layer, leaving only `ed25519:`. If the substrate does not enforce the dual-signature mandate, the verification passes with only classical security.
- **Impact**: Silent downgrade to non-quantum-resistant integrity.
- **Tachyon Mitigation**: The **Dual-Signature Mandate** in `verify_integrity()` checks `_pqc_private_key_bytes and not pqc_checked` — if PQC keys are loaded but the signature lacks a PQC component, a `SECURITY BREACH` is raised.

### B. Expanded Key Buffer Corruption
- **Description**: The 4032-byte ML-DSA-65 expanded secret key stored in the macOS Keychain is corrupted (truncated, zeroed, or partially overwritten).
- **Impact**: The `oqs.Signature(PQC_ALGORITHM, sk)` constructor silently accepts malformed keys. Signatures produced with a corrupt key are valid but cannot be verified with the original public key, effectively orphaning the entire signature chain.
- **Tachyon Mitigation**: **Dual-Entry Keychain Model** stores SK and PK as separate entries. The `_load_pqc_keys()` method performs a roundtrip probe: sign with loaded SK, verify with loaded PK. Failure triggers a `TRUST_BREACH` halt.

### C. liboqs Version Drift
- **Description**: The `liboqs` native library (0.15.0) differs from `liboqs-python` (0.14.1). A major API change (e.g., argument order in `verify()`, key format changes) could cause silent verification bypass or signing failures.
- **Impact**: Signatures generated with one version may not verify with another.
- **Tachyon Mitigation**: Version mismatch warning is logged (not suppressed). The `PQC_ALGORITHM` constant ensures consistent algorithm naming. Planned: pin `liboqs-python==0.15.0` when stable.

### D. PQC State Contamination
- **Description**: The `oqs.Signature` C wrapper is **stateful** — reusing a single instance across sign and verify operations can produce incorrect results due to internal buffer reuse.
- **Impact**: False negatives in verification (file passes integrity check when it shouldn't).
- **Tachyon Mitigation**: All PQC operations use ephemeral `with oqs.Signature(...) as sig:` context managers, ensuring the C state is freed after each operation.

## 13. Agentic Visibility & Control Threats

As Tachyon Tongs matures toward HOTL/HOOTL autonomy, the observability and control of autonomous agents becomes a critical attack surface.

### A. Agent Observability Blindspot
- **Description**: There is no centralized telemetry for agent key usage, tool invocations, or signature operations. An attacker who compromises an agent session has no audit trail beyond filesystem entries.
- **Impact**: Forensic analysis after a breach is limited to file-level diffs and git history, with no structured event timeline.
- **Tachyon Mitigation (Implemented in Phase 26.1)**: **Agent Telemetry Bus** — structured JSONL event emission from `ToolRouter`, `IntegrityManager`, and `BaseTachyonAgent` directly to the `TelemetryBus` isolating the exact step of attack vectors.

### B. Key Delegation Orphaning
- **Description**: HKDF-derived agent keys have no formal certificate binding them to the Root. There is no revocation mechanism short of rotating the Root Key itself.
- **Impact**: A compromised agent key remains valid indefinitely. There is no way to express "Sentinel key #3 is revoked but Engineer key #2 is still valid."
- **Tachyon Mitigation (Implemented in Phase 26.1)**: **JSON Delegation Certificates** — issued by the `DelegationCertificateAuthority`, dynamically signed by the Hybrid Root, scoping each agent's signing authority with automatic heartbeats validating against a CRL.

### C. Agent Identity Spoofing
- **Description**: There is no cryptographic binding between an agent's `SKILL.md` identity (e.g., `role: sentinel`) and its derived sub-key. An attacker who gains access to the Root Key (or its HKDF derivation path) can impersonate any agent.
- **Impact**: False-flag operations: a compromised Sentinel could sign artifacts as the Engineer.
- **Tachyon Mitigation (Implemented in Phase 26.1)**: Each agent dynamically stores its `DelegationCertificate`. The Key itself is generated uniquely per-agent-role, mathematically sealing the output signatures to the specific agent executing the computation.
