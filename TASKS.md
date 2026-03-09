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
- [ ] **Action Broker Migration:** Centralize all tool execution through a single Action Broker instead of letting the agent call tools directly. Implement a strict "Capability" based permission model instead of just URL allowlists.

### 🟢 [MEDIUM] Google ADK Implementation
- [x] Instantiate the **Sentinel Agent** using the `google-adk` framework.
- [x] Write ADK tool definitions for the `safe_fetch` firewall.
- [x] Orchestrate the Tri-Stage pipeline routing (Fetcher -> Sanitizer -> Analyzer) via ADK state graphs.
- [ ] **The Guardian Triad Split:** Break the Sentinel's privilege collapse. Split it into three sub-agents: *Scout* (finds threats limitlessly), *Analyst* (classifies them entirely air-gapped), and *Engineer/Broker* (safely proposes the policy updates).

### 🟢 [LOW] Phase 3: Future-Proofing
- [x] Set up the autonomous **Sentinel Agent** to scrape CVE feeds and GitHub advisories, updating this `TASKS.md` file with new threats. *(It's self-aware!)*
- [x] Benchmark WASM tools (Wasmtime) for lightweight, capability-based tool execution inside the sandbox.
- [x] Investigate hybrid ECC/PQC signatures for hardware authentication. *(Math that makes my head hurt).*
- [x] Implement behavioral monitoring to detect unexpected reasoning chains. *(Catching the agent lying to itself).*
- [ ] **Implement Research Pulsar:** Add arXiv (cs.CR, cs.AI) and OpenReview integration to the `intel_ingest.py` architecture for early-warning academic exploits.
- [ ] **Agent Security Benchmarking:** Run local Sentinel policies against established adversarial benchmarks like WASP, VPI-Bench (Visual Prompt Injection), and BrowseSafe.

### 🟢 [MEDIUM] Phase 4: Zero-Trust Networking
- [x] Integrate a **Tailscale** sidecar into the `matchlock-agent.yaml` Lima sandbox for cryptographic intra-node identity and MagicDNS routing. *(VPNs, but make them magic).*
- [x] *(Rider)*: Upon completion or modification of the Tailscale integration, the executor **MUST recursively update** `docs/TAILSCALE.md`. *(Keeping the blueprints honest).*

---

## 🚗 The Parking Lot (Great Ideas, Low Priority)
- Add a `--dev-mode` flag or a `docker-compose.yml` to run the Sentinel without the Heavy Lima/Matchlock dependencies to speed up onboarding for new contributors.
- Add Mermaid diagrams to `ARCHITECTURE.md` to visually document the data flow and policy enforcement points.

---
*This file is continuously updated by the Sentinel Agent. If you see it editing itself rapidly, don't panic. Probably.*
