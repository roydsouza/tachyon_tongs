# 📋 Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact (OWASP-ASI) and infrastructural prerequisites.

---

## 🔳 Active & Priority (Sprint 2026-03)


### 🔑 Phase 43: PQC Mandate & Model Integrity [IN-PROGRESS]
> **Source**: Grok & Gemini Audit — "Quantum-Safe Assurance"
- [x] **[P1] [SECURITY] Fail-Closed PQC Policy**: Modify `hybrid.py` to reject any ActionRecord that lacks a valid `ML-DSA-65` signature (strip-attack protection).
- [x] **[P1] [SECURITY] Model Integrity Warden**: Nightly cryptographic hashing of `mlx_lm` weights signed by the Root PQC identity.
- [ ] **[P2] [LEARNING] LoRA Fine-Tuning Loop**: Implement `lora_finetune_loop.py` to derive local model updates from human-approved Airlock outcomes.
- [ ] **[VERIFY]** Substrate halts on model weight drift or signature strip simulation.


### 🔳 Phase 35: Agent Plugin Architecture (ADR-0033) [IN-PROGRESS]
- [ ] **[REFACTOR]** Complete migration of all agents to the top-level `agents/` directory.
- [/] **[CORE]** Update `BaseAgent` and `AgentRegistry` to support the Event-First Backplane.

### 🔳 Phase 25.2: Per-Agent Key Delegation [IN-PROGRESS]
- [x] **[CRYPTO]** Design HKDF derivation logic in `IntegrityManager` [DONE]
- [ ] **[CRYPTO]** Implement `tt keys status` (Hierarchy Visualizer)
- [ ] **[CRYPTO]** Generate and anchor sub-keys: **Sentinel**, **Engineer**, **Airlock**
- [ ] **[CRYPTO]** Implement JSON **delegation certificates** (signed by Root)
- [ ] **[VERIFY]** Tests for delegation certificate chain validation

---

## 🏗️ Architectural & Operational Backlog

### 🤖 Intelligence & Forensic Collective
- [ ] **[AGENT] Chronicle**: Temporal pattern analysis across 72h horizons to detect slow-burn attacks.
- [ ] **[AGENT] Supply-Chain Oracle**: **SLSA Level 3** + SBOM attestation for all Claw and pip imports.
- [ ] **[AGENT] Quarantine Auditor (v2)**: Live static + dynamic analysis (Frida) on sandboxed payloads.
- [ ] **[AGENT] The Oracle/Diplomat/Debate Arena**: Social-fabric agent suite (Status: Draft).

### 📺 Operational Transparency (CLI/TUI)
- [ ] **[CLI] `tt debate replay <id>`**: Stream full, PQC-verified transcripts of Triad reasoning loops.
- [ ] **[TUI] Health Score Dashboard**: Dashboard for PQC Coverage, Pathogen Block Rate, and Alignment Drift.
- [ ] **[CLI] `tt forensic bundle`**: Generate signed export bundles for third-party audits.
- [ ] **[CLI] `tt bus explore`**: JSONL-paginated view of signed EventBus events.

### 🧪 Verification & Hardening
- [ ] **[VERIFY] Formal Verification**: TLA+ models for EventBus + Mutant-Lock interaction.
- [ ] **[VERIFY] Adversarial Fuzzing**: Integrate **AFL++** against the Pathogen/Reflector engines.
- [ ] **[BUILD] SBOM Automation**: CycloneDX generation + signing on every push.
- [ ] **[REFACTOR] Registry Pattern**: Modernize `main.py` role discovery.

---

## ✅ Historical Roadmap (Completed Phases)
*Historical records are candidates for migration to [ROADMAP.md](docs/ROADMAP.md).*


### ✅ Phase 42: Forensic Persistence - Unified Ledger & Mutant-Lock (2026-03)
- [x] **Unified Forensic Ledger**: Consolidated Markdown logs into a PQC-signed SQLite table.
- [x] **Mutant-Lock Service**: Hardened lock management with auto-expiry and token-based protection.
- [x] **Herald Bridge**: SQL-native visibility for actionable status reports and alerts.
- [x] **Forensic Verification**: Validated PQC integrity and SQL query logic in `scripts/verification/`.
- [x] **Unified State**: Integrated `TelemetryBus` and `StateManager` with the new ledger.

### ✅ Phase 41: Adaptive Intelligence - Semantic-Drift Bypass (2026-03)
- [x] **Alignment PDP**: Replaced probabilistic gating with a reasoning-driven Singularity engine.
- [x] **Adversarial Refinement**: Implemented multi-turn intent verification (Analyst/Reflector).
- [x] **Fail-Closed Intent**: Mandatory intent-gating for high-risk tools.

### ✅ Phase 40: Metamorphic Adversarial Reasoning (2026-03)
- [x] **AdversarialReflector**: Implemented "Think-Criticize-Attack" loop in Pathogen.
- [x] **Herald Feedback**: Integrated reflection telemetry via the Herald bridge.

### ✅ Phase 39: Sentinel Autoresearch (2026-03)
- [x] **ResearchSynthesizer**: Native synthesis node for ASI-mapped intelligence.
- [x] **High-Signal Catalog**: Refactored `CATALOG.md` for prioritized metadata.

### ✅ Phase 38: Pathogen v2 (2026-03)
- [x] **Hybrid Sweep**: ASU-mapped Red Teaming loop with 24-hour periodic trigger.

### ✅ Phase 37: OWASP Agentic Threat Hub (2026-03)
- [x] **Threat Synthesis**: Established 11 ASI playbooks in `exploits/`.

### ✅ Phase 33: The Immune Collective (Core Framework)
- [x] **EventBus Implementation**: SQLite-WAL event broker.
- [x] **BaseAgent Protocol**: Standardized `ActionRecord` generation.

### ✅ Phase 30: Test Debt & Integration Hardening
- [x] **Real Assertions**: Replaced `assert True` with Guardian-driven E2E tests.
- [x] **Concurrency**: Stress tested SQLite WAL under 10-thread parallel load.

### ✅ Phase 29: Signal Purification & Integrity Stabilization
- [x] **Mutant Lock**: Implemented PQC/Guardian race condition fix.
- [x] **Rate Limiting**: Bounded logging in AlertManager.

### ✅ Phase 28: Substrate Maintenance & Governance
- [x] **Topological Cleanup**: Root directory reorganization.
- [x] **Governance**: Implement AC/DC workflow and agentic rules.

### ✅ Phase 25: Cryptographic Substrate (Hybrid PQC)
- [x] **Hybrid Signatures**: Ed25519 + ML-DSA-65 implementation.
- [x] **Hardware Anchor**: Secure Enclave root keys and SSS recovery.

### ✅ Phase 24: Event-Horizon Command Bridge
- [x] **Substrate Daemon**: FastAPI interception proxy.
- [x] **Airlock UI**: GPU-accelerated TUI and Neovim plugin.

*Older phases (1-23) available in the [ROADMAP.md](docs/ROADMAP.md) archive.*
