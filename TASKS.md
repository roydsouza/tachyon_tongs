# Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

## Security Task Progress

### 🚨 [URGENT] Substrate Operator Interface (Slash Commands)
- [ ] **BUG: Slash Commands Inaccessible**: Commands in `.agents/workflows/` (`/help`, `/catalog`, etc.) are not being recognized by the AntiGravity environment. Investigate system-level registration and caching.

### 📊 [PLANNED] Phase 15: Adaptive Rate-Limiting Implementation
- [ ] **[ADR]** Create ADR-0007 for the Rate-Limiting strategy.
- [ ] **[CORE]** Implement `AdaptiveRateLimiter` middleware in `tachyon/enforcement/rate_limiter.py`.
- [ ] **[ROUTING]** Integrate rate-limiting into `ToolRouter`.
- [ ] **[VERIFY]** Add regression tests for per-agent and per-tool throttling.

### 🔍 [PLANNED] Phase 16: Competitive Gap Implementation
- [ ] **[REPUTATION]** Implement `domain_reputation.json` and logic for scoring fetch targets in `safe_fetch.py`.
- [ ] **[SCAN]** Integrate `bandit` / `semgrep` for pre-execution static analysis of `safe_execute` payloads.
- [ ] **[ALIGNMENT]** Implement `AlignmentChecker` using local embeddings to detect semantic drift in tool use.
- [ ] **[SEQUENCES]** Implement sequence-based OPA policies to block multi-stage exfiltration chains.

### 🦠 [PLANNED] Phase 17: Pathogen Adversarial Tuning & Metrics
- [ ] **[SCHEMA]** Implement `pathogen_metrics` table for tracking attack success and mutation lineage.
- [ ] **[MUTATION]** Implement generational `MutationEngine` with ASCII/Unicode bypasses.
- [ ] **[LEDGER]** Create `RED_TEAM_LEDGER.md` for attack history auditing.

### 🌌 [PLANNED] Phase 18: Singularity Meta-PDP Server
- [ ] **[SERVER]** Create FastAPI Meta-PDP server in `singularity/server.py` to federate engine queries.
- [ ] **[LEDGER]** Implement `authorization_ledger` in SQLite for 100% auditability of policy decisions.

---

## ✅ Completed Milestones

### ✅ Phase 13: Sentinel Hybrid Migration
- [x] **[MANIFEST]** Create `agents/sentinel/SKILL.md` with identity and capabilities. [COMPLETED]
- [x] **[CONFIG]** Externalize hardcoded config into `SKILL.md` YAML. [COMPLETED]
- [x] **[RUNNER]** Create `tachyon/agents/sentinel/runner.py` for hybrid execution. [COMPLETED]
- [x] **[REGISTRY]** Register Sentinel in `/tmp/tachyon/nodes.json`. [COMPLETED]
- [x] **[ADR]** Create ADR-0006 for the architectural transition. [COMPLETED]
- [x] **[VERIFY]** Add regression tests for the hybrid runner. [COMPLETED]

### ✅ Phase 12.2: Multi-Engine PDP & Reverse Firewall
- [x] **[OUTBOUND]** Implement the "Reverse Firewall" (Outbound DLP) logic in `ToolRouter`. [COMPLETED]
- [x] **[RESOLVER]** Implement `SingularityPDP` to federate Rego and Cedar. [COMPLETED]
- [x] **[PII]** Implement `PIIScanner` for outbound telemetry. [COMPLETED]
- [x] **[VERIFY]** Add bi-directional regression tests. [COMPLETED]
- [x] **[ADR]** Create ADR-0005 for PDP/DLP architecture. [COMPLETED]

### ✅ Phase 12.1: Policy Synthesizers (Rego/Cedar)
- [x] **[EXTRACT]** Implement autonomous policy synthesizers in `tachyon/agents/synthesizer/`. [COMPLETED]
- [x] **[VERIFY]** Auto-load synthesized policies into OPA/Cedar. [COMPLETED]

### ✅ Phase 12: Sentinel Harvest Mode
- [x] **[HARVEST]** Add `--harvest` mode for payload localization. [COMPLETED]
- [x] **[LOCALIZE]** Save 6 raw payloads to `intelligence/exploits/`. [COMPLETED]

### ✅ Phase 11: Supply Chain Security
- [x] **[INTEGRITY]** Implement Hallucination Squatting defense and `IntegrityAgent`. [COMPLETED]
- [x] **[AUDIT]** Integrate `pip-audit` for proposed dependency intents. [COMPLETED]

### ✅ Phase 10: Integrity Gating & Cryptographic State
- [x] **[STATE]** Migrate to SQLite `StateManager` with WAL mode. [COMPLETED]
- [x] **[SIGN]** Implement detached signatures for the Exploit Catalog. [COMPLETED]
- [x] **[ADR]** Create ADR-0004 for State Integrity. [COMPLETED]

---

## 🛠️ Architectural Backlog
- [ ] **Containerization**: Dockerize the Substrate Daemon for CI/CD.
- [ ] **Visualization**: Append Mermaid orchestration diagrams to `ARCHITECTURE.md`.
- [ ] **Archival Script**: Prune historical phases to `ACCOMPLISHMENTS.md`.
