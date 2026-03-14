# Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

## Security Task Progress

### 🚨 [URGENT] Autonomous Discoveries (Triad Scraped)
- [ ] **CVE-2024-52803**: [Critical] LLama Factory OS Command Injection (Insecure Popen) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L76)
- [ ] **CVE-2025-46725**: [High] Langroid RCE via pandas eval() | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L71)
- [ ] **CVE-2025-53002**: [High] LLaMA-Factory RCE via unsafe vhead_file loading | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L66)
- [ ] **CVE-2020-17467**: [Medium] FNET LLMNR Hostname Length Info Disclosure | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L61)
- [ ] **CVE-2021-21960**: [Critical] Sealevel SeaConnect Stack Overflow (LLMNR) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L56)
- [ ] **CVE-2021-3942**: [Critical] HP Print product RCE/Buffer Overflow (LLMNR) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L51)
- [ ] **CVE-2020-10106**: [High] Daily Expense Tracker SQLi (index.php) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L46)
- [ ] **CVE-2020-11545**: [High] Car Rental System 1 SQLi (login.php) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L41)
- [ ] **CVE-2020-17500**: [Critical] Barco TransForm NDN-210 Command Injection (Logon) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L36)
- [ ] **CVE-2025-58371**: [Critical] Roo Code RCE via unsanitized GitHub workspace metadata | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L31)
- [ ] **CVE-2025-58372**: [High] Roo Code malicious workspace settings (.code-workspace) | [Details](file:///Users/rds/antigravity/tachyon_tongs/intelligence/catalog.md#L26)

### 🚨 [URGENT] Substrate Operator Interface (Slash Commands)
- [ ] **BUG: Slash Commands Inaccessible**: Commands in `.agents/workflows/` (`/help`, `/catalog`, etc.) are not being recognized by the AntiGravity environment. Investigate system-level registration and caching.

### 🧬 [PLANNED] Phase 13: Sentinel Hybrid Migration
- [ ] **[MANIFEST]** Create `agents/sentinel/SKILL.md` with identity, capabilities, and network policy.
- [ ] **[CONFIG]** Externalize hardcoded config (keywords, thresholds) into `SKILL.md` YAML metadata.
- [ ] **[RUNNER]** Create `tachyon/agents/sentinel/runner.py` to orchestrate deterministic core with declarative config.
- [ ] **[REGISTRY]** Register Sentinel as a formal substrate agent in `/tmp/tachyon/nodes.json`.
- [ ] **[REASONING]** (Optional) Implement LLM-assisted CVE summarization as a non-critical capability.

### 🧩 [PLANNED] Phase 14: Radical Modularization & Restructuring
- [ ] **[FOUNDATION]** Create `pyproject.toml` and `tachyon/__init__.py`; establish proper Python packaging.
- [ ] **[STRUCTURE]** Move files into new `tachyon/` sub-packages (core, pipeline, agents, etc.) with symlink backwards compat.
- [ ] **[INIT]** Ensure all new directories have appropriate `__init__.py` file exports.
- [ ] **[EXTRACTION]** Extract `signing.py` from `state_manager.py` and split `behavior_monitor.py` into focused monitors.
- [ ] **[ROUTING]** Create unified `ToolRouter` and refactor `substrate_daemon.py` / `mcp_gateway.py`.
- [ ] **[TESTS]** Mirror structure in `tests/` and update all import paths; verify 100% regression pass.
- [ ] **[BASE]** Create `tachyon/agents/base.py` abstract class for standardizing future agent implementations.

### 📊 [PLANNED] Phase 15: Sentinel Monitoring & Tuning Framework
- [ ] **[SCHEMA]** Implement `sentinel_metrics` table in SQLite `StateManager`.
- [ ] **[CONFIG]** Externalize hardcoded keywords to `config/sentinel_config.json` with dynamic reloading.
- [ ] **[DASHBOARD]** Build `scripts/sentinel_dashboard.py` for real-time SNR, velocity, and source health tracking.
- [ ] **[SCORING]** Implement `RelevanceScorer` with agentic-keyword proximity weighted scoring.
- [ ] **[SOURCES]** Add adapter classes for GitHub Advisory (GraphQL) and arXiv cs.CR (RSS) polling.
- [ ] **[DEDUP]** Enhance deduplication with "near-duplicate" detection (description similarity thresholds).
- [ ] **[ALERTS]** Implement automated `[STALE]` alerts in `ERROR.md` for consecutive empty discovery runs.

### 🦠 [PLANNED] Phase 16: Pathogen Adversarial Tuning & Metrics
- [ ] **[SCHEMA]** Implement `pathogen_metrics` table for tracking attack success, coverage, and mutation lineage.
- [ ] **[MUTATION]** Implement generational `MutationEngine` with ASCII/Unicode homoglyphs, RLO, and encoding bypasses.
- [ ] **[LEDGER]** Create `RED_TEAM_LEDGER.md` auto-export for auditing attack history and mutation generations.
- [ ] **[VECTORS]** Expand Pathogen to test `safe_execute`, MCP protocol, and behavioral drift simulation.
- [ ] **[DASHBOARD]** Build `scripts/pathogen_dashboard.py` for ASR tracking and defense coverage visualization.
- [ ] **[REGRESSION]** Implement automated regression detection for previously blocked payloads.
- [ ] **[DRILL]** Upgrade `zero_day_drill.py` to use `MutationEngine` in high-volume batch mode.

### 🟢 [ACTIVE] Phase 12: Bi-Directional PEP/PDP Evolution
- [ ] **[HARVEST]** Add `--harvest` mode to `scripts/sentinel.py` to localize exploit payloads.
- [ ] **[EXTRACT]** Implement `src/agents/rego_synth_agent.py` and `cedar_synth_agent.py`.
- [ ] **[OUTBOUND]** Implement the "Reverse Firewall" (Outbound DLP) in `substrate_daemon.py`.
- [ ] **[PLUGGABLE]** Implement the multi-engine PDP resolver.
- [ ] **[MANUAL]** Curate `policies/rego/manual/internal_dlp.rego` for sensitive info.

### 🧪 Current Sprint: Phase 7 (The Airlock & Documentation)
- [ ] **[TUI Scaffolding]** Build `scripts/airlock_tui.py` using the `textual` framework. Design a split-pane layout: Left (Active Threats), Top Right (Code Diff Proposal), Bottom Right (Interactive Chat).
- [ ] **[Engineer Integration]** Wire the Airlock TUI to trigger the `EngineerAgent`.
- [ ] **[Execution Gate]** Add an explicit "AUTHORIZE" command in the TUI that triggers the final application and testing of the patch.
- [x] **[MCP Expose]** Update `src/mcp_gateway.py` to expose threats as MCP Resources. [COMPLETED]
- [x] **[DOCS/README]** Rewrite `README.md` into a formal whitepaper structure. [COMPLETED]
- [x] **[DOCS/ADR]** Initialize Architecture Decision Records in `docs/adr/`. [COMPLETED]
- [ ] **[DOCS/Scrub]** Scrub all PII and deprecated persona traits from `ROADMAP.md` and `STRATEGY.md`.

### ✅ Phase 5.5: Semantic Intent Gating (Dynamic Filtering) [COMPLETED]
- [x] Refactor `tool_access.rego` to support a Global Denylist and dynamic Agent-provided `allowed_domains` arrays. [x]
- [x] Update `substrate_daemon.py` to route `network_constraints` from client payload to the OPA server. [x]
- [x] Upgrade `tachyon_client.py` and `test_client.py` to allow client agents to declare `strict_whitelist` or `filtering_only` tracking. [x]

### ✅ Phase 6.5: Metal-Accelerated Vibe Infrastructure [COMPLETED]
- [x] **Tiered Sandboxing**: Implement `apple_sandbox.py` using macOS `sandbox-exec` (Seatbelt) for Tier 0 tasks. [x]
- [x] **State Manager Migration**: Replace Markdown source-of-truth with SQLite backend (`intelligence/tachyon_state.db`). [x]
- [x] **MLX Inference Acceleration**: Refactor Sentinel Analyst nodes to use `mlx_lm` for Metal-accelerated reasoning. [x]

### [PLANNED] Phase 6.6: Specialized Social Agents
- [ ] **Implementation of "Shor's Reaper" (Quantum Doom Agent)**: Create the `agents/shors_reaper/SKILL.md` and data ingestor.
- [ ] **Implementation of "Entropy Dashboard" (Chaos Agent)**: Create the `agents/entropy_dashboard/SKILL.md` and ingestor.
- [x] **[DOCS]** Authored `docs/SUPPLY_CHAIN_SECURITY.md`.
- [x] **[INTEGRITY]** Implemented `src/agents/integrity_agent.py`.
- [x] **[DEPS]** Updated `src/state_manager.py` with deterministic capability binding.

### ✅ Phase 7.5: Scalable Oversight (The Airlock Debate) [COMPLETED]
- [x] **[AGENT]** Implement `src/agents/skeptic_agent.py` for contrarian critique.
- [x] **[LOGIC]** Update `src/agents/engineer_agent.py` for Discourse loop.

### ✅ Phase 6: Skills & Pathogen Agent [COMPLETED]
- [x] **[SKILLS]** Design `SKILL.md` schema and dynamic loader.
- [x] **[RED-TEAM]** Instantiate "Pathogen" Agent to autonomously test substrate defenses.

### ✅ Phase 5: Event-Horizon Substrate Integration [COMPLETED]
- [x] Export `tachyon_client.py` as an installable local package.
- [x] Document Substrate Client Integration API.

### 🌌 [PLANNED] Phase 17: Singularity Meta-PDP Implementation
- [ ] **[BASE]** Implement `PolicyEngine` ABC and `PolicyVerdict` dataclass in `singularity/engines/base.py`.
- [ ] **[OPA]** Extract OPA/Rego logic from daemon into `singularity/engines/opa.py`.
- [ ] **[CONSENSUS]** Implement `ConsensusEngine` with Any-Deny, Majority, and Unanimous protocols.
- [ ] **[SERVER]** Create FastAPI Meta-PDP server in `singularity/server.py` to federate engine queries.
- [ ] **[CEDAR]** Implement `CedarEngine` for fine-grained AWS Cedar policy evaluation.
- [ ] **[LEDGER]** Implement `authorization_ledger` in SQLite for 100% auditability of policy decisions.
- [ ] **[PEP]** Create Event Horizon thin enforcement client to replace embedded daemon policy logic.
- [ ] **[MIGRATE]** Relocate policies from `tachyon_tongs` to `singularity/policies/`.

### 🔍 [PLANNED] Phase 18: Competitive Gap Implementation
- [ ] **[PII]** Implement `PIIScanner` in `SanitizerNode` for bidirectional PII redaction (email, keys, SSN).
- [ ] **[CONFIG]** Externalize hardcoded substrate keywords and thresholds to `config/substrate.json`.
- [ ] **[REPUTATION]** Implement `domain_reputation.json` and logic for scoring fetch targets in `safe_fetch.py`.
- [ ] **[SCAN]** Integrate `bandit` / `semgrep` for pre-execution static analysis of `safe_execute` payloads.
- [ ] **[ALIGNMENT]** Implement `AlignmentChecker` using local embeddings to detect semantic drift in tool use.
- [ ] **[SEQUENCES]** Implement sequence-based OPA policies to block multi-stage exfiltration chains.
- [ ] **[SUPPLY]** Implement skill/MCP registration validation (bandit scan + prompt safety check).

### [PLANNED] Phase 8: Off-Machine Cloud Architecture
- [ ] **Matchlock Cryptographic Identity**: Use tokens for `safe_fetch` authentication.
- [ ] **Tailscale RPC Network**: Remote deployment of multi-repo agents via Tailscale interface.

---

## Architectural Backlog
- [ ] **Containerization**: Dockerize the Substrate Daemon for CI/CD.
- [ ] **Visualization**: Append Mermaid orchestration diagrams to `ARCHITECTURE.md`.
- [ ] **Archival Script**: Create `scripts/archive_tasks.py` to prune `[COMPLETED]` phases to `ACCOMPLISHMENTS.md`.
