# 📋 Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

---

## 🔳 Active & Priority

### 🔳 Phase 34: The Herald Integration (CLI-First) [IN-PROGRESS]
> **Source**: `docs/AGENTIC_ARCHITECTURE.md` and `feedback/03_HERALD_INTEGRATION.md`
- [x] **[P0] [AGENT] The Herald Implementation**: Build the `HeraldAgent` for Signal integration.
- [x] **[P0] [INFRA] Telemetry-to-Signal Bridge**: Hook the `TelemetryBus` alerts to the Herald.
- [x] **[P1] [UX] Alert Prepending**: Update `ALERT.md` and `EVOLUTION.md` to use LIFO ordering.
- [x] **[P1] [SECURITY] Transactional ADRs**: Implement the "Transactional ADR" guard.
- [x] **[P1] [DOCS] Threat Model Refinement**: Document "Crunchy Nougat" and "Immune Collective" in `THREAT_MODEL.md`.
- [ ] **[P0] [INFRA] Herald CLI Server**: Implement Unix Domain Socket server (`CLITransport`) and core text router.
- [ ] **[P0] [UX] Herald Client & NeoVIM Logic**: Build `herald_cli.py` and NeoVIM plugins for rapid CLI interactions.
- [ ] **[VERIFY]** End-to-end CLI command flow to local agents.

### 🚧 Phase 25.2: Per-Agent Key Delegation (Crypto Core) [PLANNED]
- [x] **[CRYPTO]** Design HKDF derivation logic in `IntegrityManager`
- [ ] **[CRYPTO]** Implement `tt keys status` (Hierarchy Visualizer)
- [ ] **[CRYPTO]** Generate and anchor sub-keys: **Sentinel**, **Engineer**, **Airlock**
- [ ] **[CRYPTO]** Implement JSON **delegation certificates** (signed by Root)
- [ ] **[VERIFY]** Tests for delegation certificate chain validation

### 🚧 Phase 29: Signal Purification & Integrity Stabilization [PLANNED]
- [ ] **[P0] [BUG] Fix ALERT.md Flooding**: Purge stale CONCURRENCY_TEST, STATE_COMPROMISED logs.
- [ ] **[P0] [SECURITY] Fix PQC/Guardian Race Condition**: Implement **Mutant Lock**.
- [ ] **[P1] [SECURITY] Strip Attack Canary**: Create payload forcing `.sig` truncation test.
- [ ] **[P1] [BUG] Fix `BaseTachyonAgent.get_metadata()`**: Resolve `self.config` lookup error.
- [ ] **[P1] [SECURITY] Rate-Bounded Logging**: Prevent Log Flooding DoS in AlertManager.
- [ ] **[VERIFY]** 24h clean ALERT.md.

### 🚧 Phase 30: Test Debt & Integration Hardening [PLANNED]
- [ ] **[P1] [TEST] Replace `assert True` Stubs**: Apply strict property tests.
- [ ] **[P1] [TEST] Pathogen Mutation Survival Suite**: `--mutation-count 50` in `AutoPatcher.apply_and_test`.
- [ ] **[P2] [TEST] Concurrency Stress Tests**: Resolve git branch thrashing under load.
- [ ] **[P2] [SECURITY] Singleton Immutability Guard**: Freeze `StateManager` fields.
- [ ] **[P2] [SECURITY] Tool Schema Allowlist**: Add schema validation in `ToolRouter`.
- [ ] **[VERIFY]** 100% Regression Pass with no stub tests.

### 🚧 Phase 31: New Agent Deployment [PLANNED]
- [ ] **[AGENT] The Historian**: Temporal pattern analysis across debates & threats.
- [ ] **[AGENT] The Oracle**: Threat Forecasting via arXiv/NVD + local LLM.
- [ ] **[AGENT] The Diplomat**: Inter-agent coordinator to optimize the internal debate paths.
- [ ] **[AGENT] Debate Arena**: External PR Security co-pilot via temporary agent pairs.
- [ ] **[AGENT] Semantic Decoy / Honeypot**: Synthesize fake docs attracting rogue agents.
- [ ] **[VERIFY]** Each agent passes isolated regression.

### 🚧 Phase 32: Operational Excellence & Graduated Autonomy [PLANNED]
- [ ] **[OVERSIGHT] Tiered Debates**: Risk-based tier bypasses.
- [ ] **[OVERSIGHT] Formalize HOTL Transition**: 95% auto-approve milestone metrics.
- [ ] **[CLI] Formalize `/debate` Command**: Stream agent disputes live.
- [ ] **[TUI] Health Score Dashboard**: Monitor PQC Coverage %, Airlock Queue Age.
- [ ] **[DOCS] SBOM with Cryptographic Attestation**: CycloneDX + Sigstore integration.

### 🚧 Phase 33: The Immune Collective (Core Framework) [PLANNED]
- [ ] **[P0] [INFRA] EventBus Implementation**: Build SQLite-WAL broker.
- [ ] **[P0] [INFRA] BaseAgent Protocol**: Base module handling PQC signatures & `ActionRecord`.
- [ ] **[P1] [AGENT] The Firewall Administrator**: Orchestrator via `mlx_lm`.

### 🚧 Phase 35: Forensic Reconstruction & Learning [PLANNED]
- [ ] **[P1] [FORENSICS] Action Replay**: `reconstruct_agent_decision(record_id)`.
- [ ] **[P1] [CORE] Adaptive Learning**: Implement Administrator's `KnowledgeBase`.
- [ ] **[P2] [SECURITY] Mutant Lock v2**: Cryptographically signed mutation tokens.

### 🚧 Phase 36: Substrate Robustness & Silent Failure Audit [PLANNED]
- [ ] **[P1] [AUDIT] Silent Failure Sweep**: Identify no-op `except` blocks.
- [ ] **[P1] [FIX] Robust Error Handling**.
- [ ] **[P2] [FIX] Dead Code Purge**.

### 🚧 Phase 37: Resilience & Graceful Degradation [PLANNED]
> **Source**: `feedback/01_ARCHITECTURE_ENHANCEMENTS.md`
- [ ] **[P1] [CORE] Capability Tiers**: Establish structured emergency degradation tiers.
- [ ] **[P1] [CORE] Circuit Breakers**: Agent-to-agent failure circuit breaks.
- [ ] **[P2] [INFRA] Agent Health Monitors**: Implement liveness pulse checks.

### 🚧 Phase 38: System Durability & Persistent State [PLANNED]
> **Source**: `feedback/01_ARCHITECTURE_ENHANCEMENTS.md`
- [ ] **[P1] [INFRA] Persistent Agent Memory**: Add durable checkpointing to agent logic arrays.
- [ ] **[P1] [INFRA] Write-Ahead Logging (WAL)**: Guard critical state changes with WAL.
- [ ] **[VERIFY]** Chaos testing agent death-and-restore loops.

### 🚧 Phase 39: Transparent Audit & Explainability [PLANNED]
> **Source**: `feedback/01_ARCHITECTURE_ENHANCEMENTS.md`
- [ ] **[P1] [OBSERVABILITY] Causal Lineage Chains**: Link agent generation outputs historically.
- [ ] **[P1] [DASHBOARD] Explainability Dashboard**: Display human-readable LLM reasoning summaries.
- [ ] **[VERIFY]** Export standardized daily audit trails.

---

## 🏛️ Partially Completed & Backlog

- [ ] **[REFACTOR] Extract `DummySanitizer`**: Should be a standalone module in `tachyon/core/`.
- [ ] **[REFACTOR] Registry Pattern for `main.py`**: Clean up role if/elif blocks.
- [ ] **[CHORE] Archival Script Enhancement**: Implement intelligent LLM summarization of pruned `RUN_LOG.md`.
- [ ] **Containerization**: Dockerize the Substrate Daemon for strictly isolated sandbox CD.

---

## ✅ Chronological Archive (Completed Phases)

### ✅ Phase 34 (Partial): The Herald & Signal Purification
- [x] **[P0] [AGENT] The Herald Implementation**: Build the `HeraldAgent` for Signal integration. 
- [x] **[P0] [INFRA] Telemetry-to-Signal Bridge**: Hook the `TelemetryBus` alerts to the Herald. 
- [x] **[P1] [UX] Alert Prepending**: Update `ALERT.md` and `EVOLUTION.md` to use LIFO ordering. 
- [x] **[P1] [SECURITY] Transactional ADRs**: Implement the "Transactional ADR" guard. 
- [x] **[P1] [DOCS] Threat Model Refinement**: Document "Crunchy Nougat" and "Immune Collective" in `THREAT_MODEL.md`. 

### ✅ Phase 28: Substrate Maintenance & Governance
- [x] **[CHORE]** Reorganize root directory (Move logs/memory/libs) 
- [x] **[DOCS]** Refactor `TASKS.md` for clarity and hierarchy 
- [x] **[GOVERNANCE]** Implement `TASKS_GOVERNANCE.md` and `HYGIENE.md` agent rules 
- [x] **[GOVERNANCE]** Implement AC/DC workflow 
- [x] **[VERIFY]** Final Sentinel health check pass 

### ✅ Phase 27: Feedback-Driven Hardening & Agentic Expansion
- [x] **[SECURITY] Signal Purification**: Implement "Mutant Lock" to suppress false alarms.
- [x] **[SECURITY] Supply Chain Defense**: Graduate to real DB-backed check.
- [x] **[CORE] TOCTOU Hardening**: Fix `ImmutableToolRequest.params` via `MappingProxyType`.
- [x] **[AGENT] Auditor**: Implement Compliance/Audit agent.
- [x] **[AGENT] Forge**: Implement Synthetic Adversary Generator.
- [x] **[CHORE] Archival**: Implement `RUN_LOG.md` auto-pruning.
- [x] **[VERIFY]** 100% Regression Pass.

### ✅ Phase 26: CI/CD Hardening & Supply Chain Defense
- [x] **[HOOKS]** Implement signature verification in pre-commit.
- [x] **[CI]** Integrity verification workflows.
- [x] **[SBOM]** CycloneDX signing.
- [x] **[BUILD]** Hash-pinned requirements.

### ✅ Phase 25.5: Deep Audit & Hardening
- [x] **[P0]** Fix dead PQC signing path
- [x] **[P0]** PQC Rekey: Dual-entry Keychain model
- [x] **[P1]** Documentation sync: ML-DSA-44 → ML-DSA-65

### ✅ Phase 25.2 (Partial): Per-Agent Key Delegation
- [x] **[CRYPTO]** Design HKDF derivation logic in `IntegrityManager`

### ✅ Phase 25: Cryptographic Substrate (Hybrid PQC)
- [x] **[CRYPTO]** Ed25519 + ML-DSA-65 Hybrid Signatures.
- [x] **[CRYPTO]** Secure Enclave root anchoring.
- [x] **[CRYPTO]** Shamir Secret Sharing for recovery.
- [x] **[CLI]** Key hierarchy visualization and verification.

### ✅ Phase 24: Event-Horizon Command Bridge
- [x] **[API]** Unified Substrate Daemon (FastAPI).
- [x] **[TUI]** GPU-accelerated Textual Dashboard.
- [x] **[CLI]** Single `tt` command consolidation.
- [x] **[NVIM]** `tachyon.nvim` Lua plugin for Airlock.

### ✅ Phase 23: Hardware-Level Isolation
- [x] **[CORE]** WasmRunner (Tier 1) + VmRunner (Tier 0)
- [x] **[VERIFY]** 100% Regression Pass (169/169)

### ✅ Phase 22: Self-Evolving Policies & Immune Response
- [x] **[CORE]** ImmuneManager for autonomic feedback loops.
- [x] **[VERIFY]** Canary-to-Engineer evolution validation.

### ✅ Phase 21.9: Local Reasoning Substrate (llama.cpp)
- [x] **[CORE]** LocalModelProvider + ModelRouter local-first fallback

*(Phases 1-21 available in [ROADMAP.md](docs/ROADMAP.md) history)*
