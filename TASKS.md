# 📝 Tachyon Tongs: Evolutionary Architecture Tasks

This is the local list of pending tasks for the **Sentinel Agent** and **AntiGravity** to extend the trustworthy pipeline for `tachyon_tongs`.

## 🚀 Priority Security Tasks

### [CRITICAL] Core Infrastructure
- [ ] Initialize repository structure (`src/`, `policies/`, `scripts/`, `docs/`, `.agent/rules/MISSION.md`).
- [ ] Establish `matchlock-agent.yaml` Lima configuration for hardware-virtualized sandboxing.
- [ ] Configure `metal_4` acceleration profile for local inference.

### [HIGH] Phase 1: The Core Pipeline
- [ ] Implement the **Tri-Stage "Safe-Search" Architecture**: Fetcher (Network only), Sanitizer (Regex + deterministic stripping), Analyzer (Air-gapped reasoning).
- [ ] Write Open Policy Agent (Rego) intent policies (`policies/tool_access.rego`).
- [ ] Wrap basic tools (e.g., `curl`) in Capability Firewalls (e.g., `safe_fetch`).

### [MEDIUM] Phase 2: Advanced Protections
- [ ] Implement **Verifiable Context Boundaries** (non-printable Unicode delimiters) in the Agent's system prompt to prevent IPI.
- [ ] Create **Capability Tokens** with action budgets and time-based decay.
- [ ] Establish **Contextual Intent Scoring** logic for the L1 and L2 Intent Gates.
- [ ] Deploy the **Stage 4 Verifier** agent to check outputs before returning to the user.

### [MEDIUM] Google ADK Implementation
- [ ] Instantiate the **Sentinel Agent** using the `google-adk` framework.
- [ ] Write ADK tool definitions for the `safe_fetch` firewall.
- [ ] Orchestrate the Tri-Stage pipeline routing (Fetcher -> Sanitizer -> Analyzer) via ADK state graphs.

### [LOW] Phase 3: Future-Proofing
- [ ] Set up the autonomous **Sentinel Agent** to scrape CVE feeds and GitHub advisories, updating this `TASKS.md` file with new threats.
- [ ] Benchmark WASM tools (Wasmtime) for lightweight, capability-based tool execution inside the sandbox.
- [ ] Investigate hybrid ECC/PQC signatures for hardware authentication.
- [ ] Implement behavioral monitoring to detect unexpected reasoning chains.

---

*This file is continuously updated by the Sentinel Agent.*
