# 🛡️ Phase: Security Evolution [ ]

> [!IMPORTANT]
> **MASTER SECURITY RECORD**: This file tracks the strategic hardening of Tachyon Tongs into a kernel-grade trust layer for Google AntiGravity.
> - **Inspiration**: OpenFangs 16-Layer Defense-in-Depth + Novel Agentic Security.
> - **Ritual**: Every completed security block requires a re-signing of the substrate state.
> - **Assurance**: Security features must have associated "Pathogen Test Cases" (synthetic exploits).

---

## 📋 Ground Rules for Security Engineering

1. **Fail-Closed**: All new security gates (SSRF, Taint, WASM) must fail-closed.
2. **PQC First**: Every new event or audit record must be anchored with Hybrid PQC signatures.
3. **Byzantine Resilience**: Critical actions require N-of-M consensus, not single-agent approval.
4. **Forensic Transparency**: All denials must be logged to the `ForensicLedger` with metadata.
5. **Least Privilege**: Move from coarse-grained OS sandboxing to fine-grained WASM capabilities.

---

## 🏗️ Evolution Roadmap: The Hardening Tiers

### 🔴 Phase 1: Critical Gaps (P0) — Immediate Hardening
**Preamble**: Tachyon Tongs currently has "Substrate Integrity" but lacks "Semantic Defense." Phase 1 closes the two most exploited vectors in agentic systems: SSRF (Network) and Prompt Injection (Intelligence).

#### [S-01] SSRF Protection & Network Hygiene (Layer 5/8/9/14)
- **Goal**: Prevent the Herald or any networked agent from accessing private IPs, cloud metadata, or falling victim to DNS rebinding.
- [ ] Implement `NetworkPolicy` engine in `tachyon/enforcement/network.py`.
- [ ] Add `validate_url` to Herald outbound paths (Block private ranges: `10.0.0.0/8`, `169.254.169.254`, etc.).
- [ ] Implement DNS-before-connect (resolve hostname and verify IP before allowing the request).
- [ ] Implement redirect limit (Max 3 hops) and Content-Type validation.
- **Acceptance Criteria**:
  - [ ] `test_ssrf_metadata_block`: Attempt to fetch `http://metadata.google.internal` and assert rejection.
  - [ ] `test_dns_rebinding_defense`: Simulate a DNS rebinding attack and verify the secondary IP check blocks the request.

#### [S-02] The Immunologist: Prompt Injection Defense (Layer 12)
- **Goal**: Detect and neutralize "Indirect Prompt Injection" where tool outputs manipulate the agent's next reasoning step.
- [ ] Create `agents/immunologist/agent.py`.
- [ ] Subscribe to all `AGENT_COMPLETED` events on the EventBus.
- [ ] Implement semantic scanning for override patterns (e.g., "Ignore previous instructions").
- [ ] Integrate with Guardian for immediate agent quarantine on detection.
- **Acceptance Criteria**:
  - [ ] `test_injection_detection`: Feed a tool result containing a "system override" string and assert the Immunologist emits a `SECURITY_ALERT`.

---

### 🟠 Phase 2: Resource & Execution Isolation (P1)
**Preamble**: Protective isolation is currently OS-dependent (Apple Sandbox). Phase 2 introduces platform-agnostic, metered execution to handle untrusted Pathogen-generated code and prevent resource exhaustion.

#### [S-03] WASM Sandboxing & Fuel Metering (Layer 1/11/15)
- **Goal**: Move Tier 1 execution to a WASM environment with deterministic resource limits.
- [ ] Implement `WasmSandbox` using `wasmtime` or `wasmer`.
- [ ] Add "Fuel Metering" (instruction counting) to prevent infinite loops.
- [ ] Implement wall-clock watchdog (Epoch Interruption) for runaway processes.
- **Acceptance Criteria**:
  - [ ] `test_wasm_fuel_exhaustion`: Run a WASM binary with an infinite loop and verify it is killed after fuel depletion.

#### [S-04] Loop Guard & Deduplication (Layer 13)
- **Goal**: Prevent resource-draining argumentation loops between agents in the Debate Arena.
- [ ] Implement `DeduplicationCache` in `EventBus` using SHA256 payload fingerprinting.
- [ ] Define threshold: 3 identical events within 300s triggering a `LOOP_DETECTED` circuit break.
- **Acceptance Criteria**:
  - [ ] `test_loop_breaker`: Emit 5 identical events rapidly and assert the EventBus suppresses the 4th and 5th.

---

### 🟡 Phase 3: Forensic Integrity & Privacy (P2)
**Preamble**: Transition from "Append-only logs" to "Cryptographically linked history." This ensures that even a root-level compromise cannot alter the forensic record of what the agents did.

#### [S-05] Merkle Audit Trail (Layer 2)
- **Goal**: Link all `ActionRecord` entries into a Merkle hash-chain.
- [ ] Extend `ActionRecord` schema with `previous_record_hash`.
- [ ] Implement Merkle root publication in the `FirewallAdministrator`.
- [ ] Create `scripts/forensics/verify_chain.py` for incremental verification.
- **Acceptance Criteria**:
  - [ ] `test_audit_chain_integrity`: Manually alter a historic record in the DB and verify the chain verification fails.

#### [S-06] Semantic Taint Tracking (Layer 3)
- **Goal**: Prevent data exfiltration by labeling sensitive data (API keys, PII) and tracking them through the system.
- [ ] Implement `TaintPolicy` in the `StateManager/ToolRouter`.
- [ ] Label data from `memory/keys/` and `configs/` as `TAINTED_SECRET`.
- [ ] Block `Herald` from relaying any payload containing `TAINTED_SECRET` strings.
- **Acceptance Criteria**:
  - [ ] `test_taint_exfiltration_block`: Attempt to send an API key via the Herald and verify the `NetworkPolicy` blocks it.

---

### 🔵 Phase 4: Advanced Agentic Defenses (P3)
**Preamble**: Novel security mechanisms designed specifically for autonomous collectives, addressing Model Drift and Byzantine failures.

#### [S-07] The Watcher: Capability Verification (ACV)
- **Goal**: Runtime behavioral auditing to ensure agents don't exceed their delegated permissions.
- [ ] Create `agents/watcher/agent.py`.
- [ ] Parse `actions_taken` from `AGENT_COMPLETED` records.
- [ ] Compare against the agent's delegation certificate `allowed_actions`.
- **Acceptance Criteria**:
  - [ ] `test_privilege_escalation_detection`: Mock an agent performing a `FILE_WRITE` when it only has `RESEARCH` and verify the Watcher flags it.

#### [S-08] Consensus-Based Gating (Byzantine Fault Tolerance)
- **Goal**: Require N-of-M signatures for high-risk actions (e.g., substrate mutations).
- [ ] Implement `ConsensusEngine` in `tachyon/core/consensus.py`.
- [ ] Update `Airlock` to require 3 signatures (e.g., Auditor + Skeptic + Admin) for "Approve Patch" actions.
- **Acceptance Criteria**:
  - [ ] `test_consensus_failure`: Provide 2 of 3 required signatures and verify the action remains staged.

#### [S-09] Model Drift & Behavioral Monitoring
- **Goal**: Detect if a model (local or cloud) has been subtly compromised or "poisoned."
- [ ] Implement `BehavioralMonitor` in the System Integrity tier.
- [ ] Store statistical fingerprints of agent response times, verbosity, and risk tolerance.
- **Acceptance Criteria**:
  - [ ] `test_drift_detection`: Simulate a sudden shift in model verbosity and verify an anomaly record is created.

---

### ⚪ Phase 5: Supply Chain & Exfiltration
**Preamble**: Hardening the "Chain of Custody" for agent code and detecting sophisticated exfiltration (e.g. Steganography).

#### [S-10] Agent Provenance & SBOM (Layer 6/16)
- [ ] Integrate code signing into the `AgentRegistry`.
- [ ] Implement hash verification on every agent load (referenced against `metadata/agent_hashes.json`).

#### [S-11] Exfiltration Noise Detection
- [ ] Implement Shannon entropy analysis in the Herald.
- [ ] Flag payloads with unusually high entropy (indicative of encrypted/encoded exfiltration).

---

## ✅ Final Security Verification Checklist
- [ ] 100% of P0 gaps closed.
- [ ] Merkle chain passes full depth verification.
- [ ] Pathogen-generated prompt injection suite passes (0 leaks).
- [ ] All security agents (Immunologist, Watcher, Monitor) are active.
