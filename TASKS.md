# 📋 Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

---

## 🔳 Active & Priority

### 🚧 Phase 29: Signal Purification & Integrity Stabilization [PLANNED]
> **Source**: Grok & Gemini feedback — "#1 blocker to moving beyond HITL"

- [ ] **[P0] [BUG] Fix ALERT.md Flooding**: Purge 1,176 lines of stale CONCURRENCY_TEST, STATE_COMPROMISED, and DOS_ATTACK test entries from `logs/ALERT.md`
- [ ] **[P0] [SECURITY] Fix PQC/Guardian Race Condition**: Guardian fires STATE_COMPROMISED alerts during legitimate Engineer mutations. Implement **Mutant Lock** (Gemini's "Gold" suggestion) — a signed lock acquired by the Engineer during `apply_and_test` that Guardian respects
- [ ] **[P1] [SECURITY] Strip Attack Canary**: Create a dedicated test payload that truncates `.sig` files and verifies Guardian halts instantly (9 false-positive strip attacks detected in current ALERT.md)
- [ ] **[P1] [BUG] Fix `BaseTachyonAgent.get_metadata()`**: References non-existent `self.config` — will crash if called
- [ ] **[P1] [SECURITY] Rate-Bounded Logging**: Implement per-category rate limiting in AlertManager to prevent Log Flooding DoS
- [ ] **[VERIFY]** 24h clean ALERT.md (zero false-positive integrity alerts)

### 🚧 Phase 30: Test Debt & Integration Hardening [PLANNED]
> **Source**: Grok feedback — "test debt" and "concurrency races"

- [ ] **[P1] [TEST] Replace `assert True` Stubs**: Fill in `test_immune_*.py` with real assertions
- [ ] **[P1] [TEST] Pathogen Mutation Survival Suite**: Add `--mutation-count 50` for critical CVEs in `AutoPatcher.apply_and_test`
- [ ] **[P2] [TEST] Concurrency Stress Tests**: Fix Airlock staging + git branch thrashing under load (CONCURRENCY_TEST alerts)
- [ ] **[P2] [SECURITY] Singleton Immutability Guard**: Freeze `StateManager` fields after initialization
- [ ] **[P2] [SECURITY] Tool Schema Allowlist**: Add strict schema validation in `ToolRouter`
- [ ] **[VERIFY]** 100% Regression Pass with no stub tests remaining

### 🚧 Phase 31: New Agent Deployment [PLANNED]
> **Source**: Claude, Grok, & Gemini feedback — agent proposals

- [ ] **[AGENT] The Historian** (Claude): Temporal pattern analysis across debates & threats. Detects slow-moving attacks invisible in single-incident analysis
- [ ] **[AGENT] The Oracle** (Grok): Threat Forecasting agent. Pulls arXiv + NVD + catalog, runs lightweight Llama-3.2-3B forecasting, pre-stages "what-if" policy skeletons in Airlock
- [ ] **[AGENT] The Diplomat** (Claude): Inter-agent coordinator. Reduces debate overhead via pre-filtering obvious decisions, optimizes agent invocation order, implements backpressure
- [ ] **[AGENT] Debate Arena** (Grok): Spawns temporary Skeptic/Meta-Critic pairs for *external* patches (e.g., PRs from other projects). Turns Tachyon into a "PR security co-pilot"
- [ ] **[AGENT] Semantic Decoy / Honeypot** (Gemini): Synthesizes "fake internal documentation" that attracts IPI-controlled agents, triggering lockdown on access
- [ ] **[AGENT] Quota Warden** (Gemini): Game-theoretic token reasoning budget allocation between Skeptic and Analyst during zero-day response
- [ ] **[VERIFY]** Each agent passes isolated regression + Pathogen stress test

### 🚧 Phase 32: Operational Excellence & Graduated Autonomy [PLANNED]
> **Source**: Claude & Gemini feedback — "HOTL transition" and "performance visibility"

- [ ] **[OVERSIGHT] Tiered Debates**: Risk-based debate tiers (None/Self/Dyad/Triad) — not all operations need full adversarial oversight
- [ ] **[OVERSIGHT] Formalize HOTL Transition**: Define quantified milestones (95% auto-approve rate, 0 critical incidents in 30 days, debate agreement >90%)
- [ ] **[CLI] Formalize `/debate` Command**: Expose `tt debate <patch-id>` as first-class command that streams Skeptic/Meta-Critic/Engineer exchange in real-time
- [ ] **[TUI] Health Score Dashboard**: Surface PQC Coverage %, Catalog Integrity Age, Airlock Queue Age, and Pathogen Block Rate in TUI
- [ ] **[DOCS] SBOM with Cryptographic Attestation**: Generate automated SBOMs (CycloneDX) with Sigstore/SLSA build provenance
### 🚧 Phase 33: The Immune Collective (Core Framework) [PLANNED]
> **Source**: `docs/AGENTIC_ARCHITECTURE.md` — Synthesized v2.0
- [ ] **[P0] [INFRA] EventBus Implementation**: Build the SQLite-WAL event broker in `tachyon/core/bus.py`.
- [ ] **[P0] [INFRA] BaseAgent Protocol**: Implement the `BaseAgent` ABC with mandatory PQC signature verification and `ActionRecord` generation.
- [ ] **[P1] [AGENT] The Firewall Administrator (v1)**: Local `llama.cpp` integration via `mlx_lm` for executive orchestration.
- [ ] **[P1] [AGENT] The Herald (v2)**: Formalize Signal C2 proxy with strict network isolation.
- [ ] **[VERIFY]** Successful Sentinel-to-Administrator event loop.

### 🔳 Phase 34: The Herald & Signal Purification [IN-PROGRESS]
> **Source**: `docs/AGENTIC_ARCHITECTURE.md` — Synthesized v2.0
- [x] **[P0] [AGENT] The Herald Implementation**: Build the `HeraldAgent` for Signal integration. [DONE]
- [x] **[P0] [INFRA] Telemetry-to-Signal Bridge**: Hook the `TelemetryBus` alerts to the Herald. [DONE]
- [x] **[P1] [UX] Alert Prepending**: Update `ALERT.md` and `EVOLUTION.md` to use LIFO (Last-In-First-Out) ordering. [DONE]
- [x] **[P1] [SECURITY] Transactional ADRs**: Implement the "Transactional ADR" guard in `IntegrityManager`. [DONE]
- [x] **[P1] [DOCS] Threat Model Refinement**: Document "Crunchy Nougat" and "Immune Collective" in `THREAT_MODEL.md`. [DONE]
- [ ] **[VERIFY]** End-to-end Signal alert flow.

### 🚧 Phase 35: Forensic Reconstruction & Learning [PLANNED]
> **Source**: `docs/AGENTIC_ARCHITECTURE.md` — Synthesized v2.0
- [ ] **[P1] [FORENSICS] Action Replay**: Implement `reconstruct_agent_decision(record_id)` to audit historical traces.
- [ ] **[P1] [CORE] Adaptive Learning**: Implement the Administrator's `KnowledgeBase` and `AdaptiveLearning` effectiveness tracker.
- [ ] **[P2] [SECURITY] Mutant Lock v2**: Cryptographically sign mutation tokens issued by the Administrator.
- [ ] **[VERIFY]** 100% forensic coverage for all Pilot Agent actions.

### 🚧 Phase 36: Substrate Robustness & Silent Failure Audit [PLANNED]
- [ ] **[P1] [AUDIT] Silent Failure Sweep**: Identify all no-op `except` blocks and silent failure modes.
- [ ] **[P1] [FIX] Robust Error Handling**: Implement structured alerting for all substrate-level failures.
- [ ] **[P2] [FIX] Dead Code Purge**: Remove any leftover shims or stubs identified as "Silent Failure" risks.
- [ ] **[VERIFY]** Comprehensive "Chaos Test" suite.

### 🔳 Phase 25.2: Per-Agent Key Delegation [IN-PROGRESS]
- [x] **[CRYPTO]** Design HKDF derivation logic in `IntegrityManager` [DONE]
- [ ] **[CRYPTO]** Implement `tt keys status` (Hierarchy Visualizer)
- [ ] **[CRYPTO]** Generate and anchor sub-keys: **Sentinel**, **Engineer**, **Airlock**
- [ ] **[CRYPTO]** Implement JSON **delegation certificates** (signed by Root)
- [ ] **[VERIFY]** Tests for delegation certificate chain validation

---

## 🚧 Partially Completed & Backlog

### 🏛️ Architectural Backlog
- [ ] **[REFACTOR] Extract `DummySanitizer`**: Hardcoded inside `CanaryRole._scout()`. Should be a proper module in `tachyon/core/`
- [ ] **[REFACTOR] Registry Pattern for `main.py`**: Replace if/elif role chain
- [ ] **[CHORE] Archival Script Enhancement**: Improve `RUN_LOG.md` auto-pruning with intelligent summarization (LLM-compressed executive summaries)
- [ ] **Containerization**: Dockerize the Substrate Daemon for CI/CD

---

## ✅ Chronological Archive (Completed Phases)

### ✅ Phase 28: Substrate Maintenance & Governance
- [x] **[CHORE]** Reorganize root directory (Move logs/memory/libs) [DONE]
- [x] **[DOCS]** Refactor `TASKS.md` for clarity and hierarchy [DONE]
- [x] **[GOVERNANCE]** Implement `TASKS_GOVERNANCE.md` and `HYGIENE.md` agent rules [DONE]
- [x] **[GOVERNANCE]** Implement AC/DC workflow [DONE]
- [x] **[VERIFY]** Final Sentinel health check pass [DONE]

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

### ✅ Phase 25.5: Deep Audit & Hardening
- [x] **[P0]** Fix dead PQC signing path
- [x] **[P0]** PQC Rekey: Dual-entry Keychain model
- [x] **[P1]** Documentation sync: ML-DSA-44 → ML-DSA-65

### ✅ Phase 21.9: Local Reasoning Substrate (llama.cpp)
- [x] **[CORE]** LocalModelProvider + ModelRouter local-first fallback

---
*Older phases (1-21) available in [ROADMAP.md](docs/ROADMAP.md) history.*
