# Tachyon Tongs: Execution Backlog

This document tracks the active execution backlog for the Tachyon Tongs security substrate. Tasks are prioritized based on immediate threat impact and infrastructural prerequisites.

## Security Task Progression

### 🚨 [URGENT] Autonomous Discoveries (Triad Scraped)
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2024-52803 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2025-46725 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2025-53002 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2020-17467 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2021-21960 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2021-3942 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2020-10106 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2020-11545 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2020-17500 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2025-58371 from Unknown.
- [ ] **Triad Mitigation Mandate**: Review and patch Substrate Daemon against CVE-2025-58372 from Unknown.

### 🧹 [HOUSEKEEPING] Sprint Archival
- [ ] **Write Archival Script/Workflow:** Create a tool or workflow (e.g., `scripts/archive_tasks.py` or an AntiGravity skill) to automatically prune `[COMPLETED]` phases from `TASKS.md` and append them to a new `ACCOMPLISHMENTS.md` file. This prevents `TASKS.md` from becoming a monolithic, unreadable document.

### 🧪 Current Sprint: Phase 7 (The Airlock Interface: TUI & MCP)
- [ ] **[TUI Scaffolding]** Build `scripts/airlock_tui.py` using the `textual` framework. Design a split-pane layout: Left (Active Threats), Top Right (Code Diff Proposal), Bottom Right (Interactive Chat).
- [ ] **[Engineer Integration]** Wire the Airlock TUI to trigger the `EngineerAgent`. Instead of AutoPatcher immediately staging `PENDING_MERGE.md`, it should stream the proposed `.patch` to the TUI.
- [ ] **[Negotiation Chat]** Implement a chat loop in the TUI allowing the human to ask the Engineer questions about the patch and request modifications.
- [ ] **[Execution Gate]** Add an explicit "AUTHORIZE" command in the TUI that triggers the final application and testing of the patch.
- [ ] **[MCP Expose]** Update `src/mcp_gateway.py` to expose the pending threats as MCP Resources, and the Engineer's "Propose Patch" and "Discuss Patch" abilities as MCP Tools for IDE users.
- [ ] **[Knowledge Debt Ledger]** Require the Engineer to automatically synthesize and append an entry to `ARCHITECTURAL_DECISIONS.md` after an authorized patch, detailing the vulnerability, human modifications, and final rationale.

### [COMPLETED] Core Infrastructure
- [x] Initialize repository structure (`src/`, `policies/`, `scripts/`, `docs/`).
- [x] Establish `matchlock-agent.yaml` Lima configuration for hardware-virtualized sandboxing.
- [x] Configure `metal_4` acceleration profile for local inference.


### [COMPLETED] Phase 1: The Core Pipeline
- [x] Implement the **Tri-Stage "Safe-Search" Architecture**: Fetcher (Network only), Sanitizer (Regex + deterministic stripping), Analyzer (Air-gapped reasoning).
- [x] Write Open Policy Agent (Rego) intent policies (`policies/tool_access.rego`).
- [x] Wrap basic tools (e.g., `curl`) in Capability Firewalls (e.g., `safe_fetch`).


### [COMPLETED] Phase 1.5: Reality Checks (The "Stop Mocking Me" Sprint)
- [x] **Real Threat Intel Scraping:** Rip out the mock JSON in `cve_scraper.py` and replace it with actual `requests` calls to the NVD API (Filtered for AI/Agent hijacking). 
- [x] **Real OPA Integration:** Stop pretending to use OPA in Python. Make `safe_fetch.py` actually query a local OPA server (`http://localhost:8181/v1/data/authz/tools`) before executing.


### [COMPLETED] Phase 2: Advanced Protections
- [x] Implement **Verifiable Context Boundaries** (non-printable Unicode delimiters) in the Agent's system prompt to prevent IPI.
- [x] Create **Capability Tokens** with action budgets and time-based decay.
- [x] Establish **Contextual Intent Scoring** logic for the L1 and L2 Intent Gates.
- [x] Deploy the **Stage 4 Verifier** agent to check outputs before returning to the user.
- [x] **Action Broker/Substrate Migration:** Centralized tool execution through `substrate_daemon.py` using capability-based access.


### 🟢 [MEDIUM] Phase 2.5: Guardian Triad Splitting
- [x] **The Guardian Triad Split:** Break the Sentinel's privilege collapse. Split it into three sub-agents: *Scout*, *Analyst*, and *Engineer*. (Implemented in Phase 2)


### 🟢 [MEDIUM] Google ADK Implementation
- [x] Instantiate the **Sentinel Agent** using the `google-adk` framework.
- [x] Write ADK tool definitions for the `safe_fetch` firewall.
- [x] Orchestrate the Tri-Stage pipeline routing (Fetcher -> Sanitizer -> Analyzer) via ADK state graphs.
- [x] **The Guardian Triad Split:** Break the Sentinel's privilege collapse. Split it into three sub-agents: *Scout* (finds threats limitlessly), *Analyst* (classifies them entirely air-gapped), and *Engineer/Broker* (safely proposes the policy updates).


### [COMPLETED] Phase 3/4: Future-Proofing & Intelligence
- [x] Set up the autonomous **Sentinel Agent** to scrape CVE feeds and GitHub advisories, updating this `TASKS.md` file with new threats.
- [x] Benchmark WASM tools (Wasmtime) for lightweight, capability-based tool execution inside the sandbox.
- [x] Investigate hybrid ECC/PQC signatures for hardware authentication.
- [x] Implement behavioral monitoring to detect unexpected reasoning chains.
- [x] **Implement Research Pulsar:** Added arXiv (cs.CR, cs.AI) integration to the `intel_ingest.py` architecture for early-warning academic exploits.
- [x] **Granular Agent Transparency & Verbose Logging:** Enforced strict JSON payload introspection into `RUN_LOG.md`.
- [ ] **Agent Security Benchmarking:** Run local Sentinel policies against established adversarial benchmarks like WASP, VPI-Bench (Visual Prompt Injection), and BrowseSafe.


### 🟢 [MEDIUM] Phase 5: Event-Horizon Substrate Integration
- [x] Export `tachyon_client.py` as an installable local package for other agents in `~/antigravity/`.
- [x] Document the Substrate Client Integration API so external agents know how to proxy requests.
- [x] Test cross-agent traffic distinguishing inside `RUN_LOG.md`.


### 🟢 [HIGH] Phase 5.5: Semantic Intent Gating (Dynamic Filtering)
- [ ] Refactor `tool_access.rego` to support a Global Denylist and dynamic Agent-provided `allowed_domains` arrays.
- [ ] Update `substrate_daemon.py` to route `network_constraints` from client payload to the OPA server.
- [ ] Upgrade `tachyon_client.py` and `test_client.py` to allow client agents to declare `strict_whitelist` or `filtering_only` tracking.


### 🟢 [HIGH] Phase 6: The "Skills" Extensibility Engine & The Pathogen Agent (DOMINATED)
- [x] Design the `SKILL.md` schema to encapsulate Agent directives, allowed sites, and structural behaviors.
- [x] Write a dynamic instantiation loader in the Substrate that parses a Skill and mounts a new agent context.
- [x] Configure `launchd` to periodically trigger agents like Sentinel and Pathogen via the Substrate.
- [x] Instantiate the **"Pathogen"** Agent (Red Team) via the new Skills system.
- [x] Equip Pathogen to autonomously read the `EXPLOITATION_CATALOG.md` and generate/execute complex adversarial attacks against the Substrate.


### 🟢 [CRITICAL] Phase 6.5: The Vibe Coding Infrastructure (Optimization & Multi-Agent)
- [ ] **Tiered Sandboxing:** Implement `apple_sandbox.py` using macOS `sandbox-exec` (Seatbelt) for Tier 0 (Compute-only) tasks.
- [ ] **Multi-Tenant State Manager:** Replace Markdown source-of-truth with a SQLite backend to handle concurrent agent writes without corruption.
- [ ] **MLX Inference Acceleration:** Refactor the Sentinel Analyst nodes to use `mlx_lm` for Metal-accelerated reasoning on Apple Silicon.
- [ ] **Implementation of "Shor's Reaper" (Quantum Doom Agent):** Create the `agents/shors_reaper/SKILL.md` and data ingestor for quantum milestones.
- [ ] **Implementation of "Entropy Dashboard" (Chaos Agent):** Create the `agents/entropy_dashboard/SKILL.md` and ingestor for geopolitical chaos.


### [ACTIVE] Phase 7: Documentation Standardization
- [x] Rewrite `README.md` into a formal whitepaper structure.
- [x] Create `CONTENTS.md` bird's-eye directory mapping.
- [x] Author `ARCHITECTURE.md` to detail OPA and Guardian Triad mechanics.
- [x] Author `DEPLOYMENT.md` to provide Builders Guides for In-Band and Out-of-Band agents.
- [ ] Scrub all PII and deprecated persona traits from `ROADMAP.md` and `STRATEGY.md`.


### [PLANNED] Phase 8: Off-Machine Cloud Architecture
- [ ] **Matchlock Cryptographic Identity:** Require Out-of-Band agents to authenticate to the Substrate using cryptographic tokens before accessing `safe_fetch`.
- [ ] **Tailscale RPC Network:** Bind the `substrate_daemon.py` to a `100.x.y.z` Tailscale interface, allowing remote deployment of Multi-Repo agents across disparate compute nodes.
- [ ] **Zero-Trust Enhancements:** Prototype mTLS handshakes between distinct external agents and the Substrate proxy. 

---

## Architectural Backlog
- Containerize the Substrate Daemon via `docker-compose.yml` to minimize dependency footprints for CI/CD deployments.
- Append Mermaid orchestration diagrams to `ARCHITECTURE.md` to visualize dynamic sandbox boundaries.
