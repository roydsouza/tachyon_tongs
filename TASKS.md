# 📝 Tachyon Tongs: Evolutionary Architecture Tasks

This is the local list of pending tasks for the **Sentinel Agent** and **AntiGravity** to extend the trustworthy pipeline for `tachyon_tongs`.

## 🚀 Priority Security Tasks

### [CRITICAL] Core Infrastructure
- [x] Initialize repository structure (`src/`, `policies/`, `scripts/`, `docs/`, `.agent/rules/MISSION.md`).
- [x] Establish `matchlock-agent.yaml` Lima configuration for hardware-virtualized sandboxing.
- [x] Configure `metal_4` acceleration profile for local inference.

### [HIGH] Phase 1: The Core Pipeline
- [x] Implement the **Tri-Stage "Safe-Search" Architecture**: Fetcher (Network only), Sanitizer (Regex + deterministic stripping), Analyzer (Air-gapped reasoning).
- [x] Write Open Policy Agent (Rego) intent policies (`policies/tool_access.rego`).
- [x] Wrap basic tools (e.g., `curl`) in Capability Firewalls (e.g., `safe_fetch`).

### [MEDIUM] Phase 2: Advanced Protections
- [x] Implement **Verifiable Context Boundaries** (non-printable Unicode delimiters) in the Agent's system prompt to prevent IPI.
- [x] Create **Capability Tokens** with action budgets and time-based decay.
- [x] Establish **Contextual Intent Scoring** logic for the L1 and L2 Intent Gates.
- [x] Deploy the **Stage 4 Verifier** agent to check outputs before returning to the user.

### [MEDIUM] Google ADK Implementation
- [x] Instantiate the **Sentinel Agent** using the `google-adk` framework.
- [x] Write ADK tool definitions for the `safe_fetch` firewall.
- [x] Orchestrate the Tri-Stage pipeline routing (Fetcher -> Sanitizer -> Analyzer) via ADK state graphs.

### [LOW] Phase 3: Future-Proofing
- [x] Set up the autonomous **Sentinel Agent** to scrape CVE feeds and GitHub advisories, updating this `TASKS.md` file with new threats.
- [x] Benchmark WASM tools (Wasmtime) for lightweight, capability-based tool execution inside the sandbox.
- [x] Investigate hybrid ECC/PQC signatures for hardware authentication.
- [x] Implement behavioral monitoring to detect unexpected reasoning chains.

### [MEDIUM] Phase 4: Zero-Trust Networking
- [ ] Integrate a **Tailscale** sidecar into the `matchlock-agent.yaml` Lima sandbox for cryptographic intra-node identity and MagicDNS routing. 
- [ ] *(Rider)*: Upon completion or modification of the Tailscale integration, the executor **MUST recursively update** `docs/TAILSCALE.md` to ensure the design document maps perfectly to the live implementation architecture.

---

*This file is continuously updated by the Sentinel Agent.*
