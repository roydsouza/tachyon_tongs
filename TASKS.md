# 📝 Tachyon Tongs: The Backlog of Doom

> *"A roadmap is just a list of promises you make to your future self, right before your future self cries." - Ancient DevOps Proverb*

Welcome to the active execution backlog! This is where the autonomous **Sentinel Agent** translates its paralyzing fear of new zero-day exploits into actionable bullet points for AntiGravity (and the human-in-the-loop) to implement. Let's harden the perimeter, shall we?

## 🚀 Priority Security Tasks

### 🟢 [CRITICAL] Core Infrastructure (We Did It!)
- [x] Initialize repository structure (`src/`, `policies/`, `scripts/`, `docs/`, `.agent/rules/MISSION.md`). *(Because starting without folders is anarchy).*
- [x] Establish `matchlock-agent.yaml` Lima configuration for hardware-virtualized sandboxing. *(Our disposable panic room).*
- [x] Configure `metal_4` acceleration profile for local inference. *(Cloud telemetry leaks are so 2024).*

### 🟢 [HIGH] Phase 1: The Core Pipeline
- [x] Implement the **Tri-Stage "Safe-Search" Architecture**: Fetcher (Network only), Sanitizer (Regex + deterministic stripping), Analyzer (Air-gapped reasoning).
- [x] Write Open Policy Agent (Rego) intent policies (`policies/tool_access.rego`). *(Because we don't trust the agent. At all).*
- [x] Wrap basic tools (e.g., `curl`) in Capability Firewalls (e.g., `safe_fetch`).

### 🟢 [HIGH] Phase 1.5: Reality Checks (The "Stop Mocking Me" Sprint)
- [ ] **Real Threat Intel Scraping:** Rip out the mock JSON in `cve_scraper.py` and replace it with actual `requests` calls to the NVD API (Filtered for AI/Agent hijacking). 
- [ ] **Real OPA Integration:** Stop pretending to use OPA in Python. Make `safe_fetch.py` actually query a local OPA server (`http://localhost:8181/v1/data/authz/tools`) before executing.

### 🟢 [MEDIUM] Phase 2: Advanced Protections
- [x] Implement **Verifiable Context Boundaries** (non-printable Unicode delimiters) in the Agent's system prompt to prevent IPI. *(Magic invisible text boxes).*
- [x] Create **Capability Tokens** with action budgets and time-based decay. *(Tokens: The ultimate allowance system).*
- [x] Establish **Contextual Intent Scoring** logic for the L1 and L2 Intent Gates.
- [x] Deploy the **Stage 4 Verifier** agent to check outputs before returning to the user. *(The bouncer at the exit).*
- [x] **Action Broker/Substrate Migration:** Centralized tool execution through `substrate_daemon.py` using capability-based access.

### 🟢 [MEDIUM] Phase 2.5: Guardian Triad Splitting
- [x] **The Guardian Triad Split:** Break the Sentinel's privilege collapse. Split it into three sub-agents: *Scout*, *Analyst*, and *Engineer*. (Implemented in Phase 2)

### 🟢 [MEDIUM] Google ADK Implementation
- [x] Instantiate the **Sentinel Agent** using the `google-adk` framework.
- [x] Write ADK tool definitions for the `safe_fetch` firewall.
- [x] Orchestrate the Tri-Stage pipeline routing (Fetcher -> Sanitizer -> Analyzer) via ADK state graphs.
- [ ] **The Guardian Triad Split:** Break the Sentinel's privilege collapse. Split it into three sub-agents: *Scout* (finds threats limitlessly), *Analyst* (classifies them entirely air-gapped), and *Engineer/Broker* (safely proposes the policy updates).

### 🟢 [LOW] Phase 3/4: Future-Proofing & Intelligence
- [x] Set up the autonomous **Sentinel Agent** to scrape CVE feeds and GitHub advisories, updating this `TASKS.md` file with new threats. *(It's self-aware!)*
- [x] Benchmark WASM tools (Wasmtime) for lightweight, capability-based tool execution inside the sandbox.
- [x] Investigate hybrid ECC/PQC signatures for hardware authentication. *(Math that makes my head hurt).*
- [x] Implement behavioral monitoring to detect unexpected reasoning chains. *(Catching the agent lying to itself).*
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

### 🟢 [MEDIUM] Phase 7: Tailscale Fleet Mesh Setup
- [ ] Enable the `substrate_daemon.py` to bind securely to a `100.x.y.z` Tailscale interface.
- [ ] Establish environment variable routing (`TACHYON_SUBSTRATE_URL`) for remote laptops.

### 🟢 [LOW] Phase 8: Hostile Cloud Architecture (Zero Trust R&D)
- [ ] Prototype mTLS handshakes between clients and the `substrate_daemon`.
- [ ] Investigate OAuth2/OIDC JWT injection for multi-tenant tracing.
- [ ] Draft specifications for hardware-backed Request Signing.

---

## 🚗 The Parking Lot (Great Ideas, Low Priority)
- Add a `--dev-mode` flag or a `docker-compose.yml` to run the Sentinel without the Heavy Lima/Matchlock dependencies to speed up onboarding for new contributors.
- Add Mermaid diagrams to `ARCHITECTURE.md` to visually document the data flow and policy enforcement points.

---
*This file is continuously updated by the Sentinel Agent. If you see it editing itself rapidly, don't panic. Probably.*
