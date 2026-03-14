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

### [PLANNED] Phase 8: Off-Machine Cloud Architecture
- [ ] **Matchlock Cryptographic Identity**: Use tokens for `safe_fetch` authentication.
- [ ] **Tailscale RPC Network**: Remote deployment of multi-repo agents via Tailscale interface.

---

## Architectural Backlog
- [ ] **Containerization**: Dockerize the Substrate Daemon for CI/CD.
- [ ] **Visualization**: Append Mermaid orchestration diagrams to `ARCHITECTURE.md`.
- [ ] **Archival Script**: Create `scripts/archive_tasks.py` to prune `[COMPLETED]` phases to `ACCOMPLISHMENTS.md`.
