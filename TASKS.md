# Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

---

## 🔳 Active & In-Progress

### 🔳 [IN-PROGRESS]# Phase 22: Self-Evolving Policies & Immune Response [DONE]
- [x] **[ADR]** Author and sign **ADR-0020: Autonomous Immune Response Protocol** [DONE]
- [x] **[CORE]** Implement **ImmuneManager** for autonomic feedback loops [DONE]
- [x] **[STATE]** Add **processed_events** and **patches** tables to StateManager [DONE]
- [x] **[CLI]** Implement **`tt immune`** command [DONE]
- [x] **[VERIFY]** Regression tests for Canary-to-Engineer evolution loop [DONE]
- [x] **[DOCS]** Update ARCHITECTURE, README, and EVOLUTION.md [DONE]

# Phase 21.9: Local Reasoning Substrate (llama.cpp) [COMPLETED]
- [x] **[PLAN]** Research optimal **GGUF quants** for Apple Silicon M5 [DONE]
- [x] **[ADR]** Author and sign **ADR-0026: Local Model Fallback & Routing** [DONE]
- [x] **[CORE]** Implement **LocalModelProvider** via llama-server [DONE]
- [x] **[CORE]** Update **ModelRouter** for high-assurance local-first fallback [DONE]
- [x] **[VERIFY]** Benchmarking and regression testing (3/3 passed) [DONE]

### 🔳 [PLANNED] Phase 23: Hardware-Level Isolation
- [ ] **[SANDBOX]** Prototype WASM-based tool isolation.
- [ ] **[ISOLATION]** Explore MicroVM (Firecracker/Lima) for Tier-0 agents.

### ✅ [COMPLETED] Phase 24: Event-Horizon Command Bridge
- [x] **[API]** Implement **Unified Substrate Daemon** (FastAPI) [DONE]
- [x] **[TUI]** Implement **Textual Dashboard** for real-time telemetry [DONE]
- [x] **[CLI]** Consolidate `tachyon-*` scripts into single **`tt`** command [DONE]
- [x] **[NVIM]** Author **`tachyon.nvim`** pure-Lua plugin for Airlock review [DONE]
- [x] **[ADR]** Author and sign **ADR-0025: Unified Substrate Bridge** [DONE]
- [x] **[VERIFY]** Regression tests for CLI-to-API state bridge [DONE]

---

## 🛠️ Architectural Backlog

### Code Hygiene (P0–P1)
- [ ] **[SECURITY] Fix `ImmutableToolRequest.params`**: Uses mutable `Dict` — defeats the frozen-dataclass TOCTOU defense. Should use `MappingProxyType` or frozen dict.
- [ ] **[SECURITY] Fix `is_package_whitelisted()`**: `StateManager` method always returns `True` — Supply Chain defense is effectively a no-op.
- [ ] **[BUG] Fix `BaseTachyonAgent.get_metadata()`**: References non-existent `self.config` — will crash if called.
- [ ] **[REFACTOR] Extract `DummySanitizer`**: Hardcoded inside `CanaryRole._scout()`. Should be a proper module in `tachyon/core/`.

### Infrastructure (P2–P3)
- [x] **[CHORE] Agent Consolidation**: Unified substrate architecture and 100% logic migration. [DONE]
- [x] **[CHORE] Prune `__init__.py` Shim Layer**: Verified and optimized module exports. [DONE]
- [ ] **[CHORE] Archival Script**: Prune `RUN_LOG.md` (93KB and growing) and implement log rotation.
- [ ] **[OVERSIGHT] Tiered Debates**: Implement risk-based debate tiers (None/Self/Dyad/Triad).
- [ ] **[SECURITY] PQC-Hybrid Attestation**: Implement Dilithium3 signatures for PDP tool-call attestation.
- [ ] **Containerization**: Dockerize the Substrate Daemon for CI/CD.

### 🔭 New Opportunities (Identified 2026-03-19)
- [ ] **[REFACTOR] Registry Pattern for `main.py`**: Replace if/elif role chain with a registry dict or decorator pattern.
- [ ] **[SECURITY] Rate-Bounded Logging**: Extend `AdaptiveRateLimiter` to log-write actions to prevent Log Flooding DoS.
- [ ] **[SECURITY] Singleton Immutability Guard**: Freeze `StateManager` fields after initialization to prevent cross-agent state poisoning.
- [ ] **[SECURITY] Tool Schema Allowlist**: Add strict schema validation in `ToolRouter` to prevent LLM Tool-Use Confusion attacks.
- [ ] **[CHORE] Delete orphan `src/dummy.py`** and junk file `SELECT * FROM authz_ledger` at project root.

---

## ✅ Completed Milestones

### ✅ [COMPLETED] P0: Substrate Integrity & Security Hardening
- [x] **Fix Integrity Loop**: Add `fsync`/`flush` to `state.py` to stop false-positive `STATE_COMPROMISED` alerts. [DONE]
- [x] **Atomic State Access**: Implement file locking for `EXPLOITATION_CATALOG.md`. [DONE]
- [x] **Input Sanitization**: Scaffolding `InputSanitizer` to scrub prompts before policy evaluation. [DONE]
- [x] **BUG: Slash Commands Inaccessible**: Consolidated all workflows to `.agent/workflows/`. [DONE]

### ✅ [COMPLETED] Phase 10: Integrity Gating & Cryptographic State
- [x] **[STATE]** Migrate to SQLite `StateManager` with WAL mode. [COMPLETED]
- [x] **[SIGN]** Implement detached signatures for the Exploit Catalog. [COMPLETED]
- [x] **[ADR]** Create ADR-0004 for State Integrity. [COMPLETED]

### ✅ [COMPLETED] Phase 11: Supply Chain Security
- [x] **[INTEGRITY]** Implement Hallucination Squatting defense and `IntegrityAgent`. [COMPLETED]
- [x] **[AUDIT]** Integrate `pip-audit` for proposed dependency intents. [COMPLETED]

### ✅ [COMPLETED] Phase 12: Sentinel Harvest Mode
- [x] **[HARVEST]** Add `--harvest` mode for payload localization. [COMPLETED]
- [x] **[LOCALIZE]** Save 6 raw payloads to `intelligence/exploits/`. [COMPLETED]

### ✅ [COMPLETED] Phase 12.1: Policy Synthesizers (Rego/Cedar)
- [x] **[EXTRACT]** Implement autonomous policy synthesizers in `tachyon/agents/synthesizer/`. [COMPLETED]
- [x] **[VERIFY]** Auto-load synthesized policies into OPA/Cedar. [COMPLETED]

### ✅ [COMPLETED] Phase 12.2: Multi-Engine PDP & Reverse Firewall
- [x] **[OUTBOUND]** Implement the "Reverse Firewall" (Outbound DLP) logic in `ToolRouter`. [COMPLETED]
- [x] **[RESOLVER]** Implement `SingularityPDP` to federate Rego and Cedar. [COMPLETED]
- [x] **[PII]** Implement `PIIScanner` for outbound telemetry. [COMPLETED]
- [x] **[VERIFY]** Add bi-directional regression tests. [COMPLETED]
- [x] **[ADR]** Create ADR-0005 for PDP/DLP architecture. [COMPLETED]

### ✅ [COMPLETED] Phase 13: Sentinel Hybrid Migration
- [x] **[MANIFEST]** Create `agents/sentinel/SKILL.md` with identity and capabilities. [COMPLETED]
- [x] **[CONFIG]** Externalize hardcoded config into `SKILL.md` YAML. [COMPLETED]
- [x] **[RUNNER]** Create `tachyon/agents/sentinel/runner.py` for hybrid execution. [COMPLETED]
- [x] **[REGISTRY]** Register Sentinel in `/tmp/tachyon/nodes.json`. [COMPLETED]
- [x] **[ADR]** Create ADR-0006 for the architectural transition. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for the hybrid runner. [COMPLETED]

### ✅ [COMPLETED] Phase 15: Adaptive Rate-Limiting Implementation
- [x] **[ADR]** Create ADR-0007 for the Rate-Limiting strategy. [COMPLETED]
- [x] **[CORE]** Implement `AdaptiveRateLimiter` middleware in `tachyon/enforcement/rate_limiter.py`. [COMPLETED]
- [x] **[ROUTING]** Integrate rate-limiting into `ToolRouter`. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for per-agent and per-tool throttling. [COMPLETED]

### ✅ [COMPLETED] Phase 16: Competitive Gap Implementation
- [x] **[ADR]** Create ADR-0008 for Domain Reputation and Static Analysis. [COMPLETED]
- [x] **[REPUTATION]** Implement `domain_reputation.json` and logic for scoring fetch targets in `safe_fetch.py`. [COMPLETED]
- [x] **[SCAN]** Integrate `StaticAnalyzer` into `apple_sandbox.py` for pre-execution static analysis. [COMPLETED]
- [x] **[ALIGNMENT]** Implement `AlignmentChecker` using semantic similarity to detect drift. [COMPLETED]
- [x] **[VERIFY]** Add exhaustive regression tests for reputation, static analysis, and alignment. [COMPLETED]

### ✅ [COMPLETED] Phase 17: Pathogen Adversarial Tuning & Metrics
- [x] **[SKILL]** Implement `high-assurance` skill for mandatory regression/doc automation. [COMPLETED]
- [x] **[ADR]** Create ADR-0009 for Pathogen Adversarial Tuning. [COMPLETED]
- [x] **[SCHEMA]** Implement `pathogen_metrics` table and `init_pathogen_db.py`. [COMPLETED]
- [x] **[MUTATION]** Implement generational `MutationEngine` with ASCII/Unicode bypasses. [COMPLETED]
- [x] **[LEDGER]** Create `PathogenLogger` and verify metrics persistency. [COMPLETED]
- [x] **[VERIFY]** Add exhaustive regression tests for mutation logging and blocking. [COMPLETED]

### ✅ [COMPLETED] Phase 18: Singularity Meta-PDP Server
- [x] **[ADR]** Create ADR-0010 for Meta-PDP Server & Ledger. [COMPLETED]
- [x] **[SERVER]** Create FastAPI Meta-PDP server in `singularity/server.py`. [COMPLETED]
- [x] **[LEDGER]** Implement `authorization_ledger` in SQLite for 100% auditability. [COMPLETED]
- [x] **[CLIENT]** Implement `RemoteSingularityPDP` with Fail-Closed logic. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for remote evaluation and ledger persistence. [COMPLETED]

### ✅ [COMPLETED] Phase 19: Immutable Actions & Substrate Hardening
- [x] **[ADR]** Create ADR-0011: Immutable Actions & TOCTOU-Resistant Routing. [COMPLETED]
- [x] **[ADR]** Create ADR-0012: State Layer Hardening & Integrity Gating. [COMPLETED]
- [x] **[CORE]** Refactor `ToolRouter` to use frozen `ImmutableToolRequest` (TOCTOU Defense). [COMPLETED]
- [x] **[PERFORMANCE]** Implement LRU caching in `RegoPolicyEngine`. [COMPLETED]
- [x] **[SECURITY]** Implement field-level encryption hooks in `StateManager`. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for router robustness and state integrity. [COMPLETED]

### ✅ [COMPLETED] Phase 20: Substrate Optimization (Quota Management)
- [x] **[MANIFEST]** Create `agents/skills/substrate-optimizer/SKILL.md` with routing logic and LPM triggers. [COMPLETED]
- [x] **[ROUTER]** Implement `ModelRouter` in `tachyon/core/routing.py` to evaluate task complexity. [COMPLETED]
- [x] **[INTEGRATION]** Update `substrate_daemon.py` to route queries through the `ModelRouter`. [COMPLETED]
- [x] **[PROTOCOLS]** Implement Context Pruning and Low-Power Mode (LPM) logic. [COMPLETED]
- [x] **[ADR]** Author and sign ADR-0013: Substrate-Aware Model Routing. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for the hybrid runner. [COMPLETED]

### ✅ [COMPLETED] Phase 21: Forensic Hardening & Agent Consolidation
- [x] **[SECURITY]** HMAC Signature sidecars for all ADRs. [DONE]
- [x] **[SECURITY]** High-Assurance Input Sanitization (ADR-0017). [DONE]
- [x] **[SKILLS]** Airlock Management Skills (List/Inspect/Approve/Deny). [DONE]
- [x] **[ARCH] Phase 21.5: Agent Consolidation**: Unified `BaseTachyonAgent` and `Role` architecture. 100% logic migration. [DONE]
- [x] **[GOVERNANCE]** Initialize `CHANGE_CONTROL.md` and `PATHS_NOT_TAKEN.md`. [DONE]
- [x] **[CHORE]** Substrate Re-Sign and Documentation Reorg. [DONE]
- [x] **[DOCS]** Agent Collective Documentation (AGENT_*.md and AGENTS.md). [DONE]

### ✅ [COMPLETED] Phase 21.7: The Canary Honeypot (Active Probe)
- [x] **[ADR]** Sign and anchor ADR-0019 (Canary Protocol) and ADR-0023/0024. [DONE]
- [x] **[ROLE]** Implement `CanaryRole` (Scout & Harvest logic). [DONE]
- [x] **[LEDGER]** Create forensic `CANARY_LOG.md`. [DONE]
- [x] **[ARCH]** Root symlink for `CANARY_LOG.md`. [DONE]
- [x] **[AUTO]** Automate Canary scout via macOS `launchd` (4hr interval). [DONE]
- [x] **[VERIFY]** Validate "Honeypot-to-Immune-System" feedback loop. [DONE]

### ✅ [COMPLETED] Architectural Backlog (Done)
- [x] **[CHORE] Documentation Reorg**: Create `docs/INDEX.md` and collapse `.agents/`. [DONE]
- [x] **[SECURITY] Immutable Actions**: Refactor `ToolRouter` to use `frozen` dataclasses to prevent TOCTOU bypasses. [COMPLETED]
- [x] **[OVERSIGHT] Airlock Debate Triad**: Implement the `Skeptic` and `Meta-Critic` agents in `agents/sentinel/`. [COMPLETED]
- [x] **Visualization**: Append Mermaid orchestration diagrams to `ARCHITECTURE.md`. [COMPLETED]
