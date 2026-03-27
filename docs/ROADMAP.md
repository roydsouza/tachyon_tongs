# Tachyon Tongs: Evolutionary Architecture Roadmap

This roadmap outlines the systematic progression of the **Tachyon Tongs** architecture. The framework is developed through iterative phases to build a high-assurance, defense-in-depth pipeline that secures autonomous AI agents against Agent Hijacking, Prompt Injection, and Memory Poisoning.

## Stage 1: Prerequisites (The Foundation)

### 1. Hardware-Bound Authentication (FIDO2)
- **Objective:** Establish physical presence as a mathematically proven defense against remote agent hijacking.
- **Implementation:** YubiKey 5C NFC integration for hardware-bound SSH keys, Git commits, and intent-gate execution approvals.

### 2. Apple Silicon Virtualization (Lima)
- **Objective:** Isolate untrusted execution payloads from the host Darwin kernel.
- **Implementation:** Lima instances utilizing Apple's `Hypervisor.framework` to spawn Linux MicroVMs at near-native speeds.

### 3. Metal 4 Neural Engine Optimization
- **Objective:** Eliminate cloud telemetry leaks and guarantee data privacy through localized inference bounding.
- **Implementation:** Optimization profiles routing reasoning MLX logic through the M5 Neural Engine architecture.

### 4. Multi-Tenant Substrate Daemon [OPERATIONAL]
- **Objective:** Amortize security hardening across all autonomous agents within the workspace via a centralized proxy.
- **Implementation:** Secure localhost proxy daemon orchestrating the Guardian Triad.

## Stage 2: The Core Pipeline

### 1. Tri-Stage Architecture
- **Objective:** Isolate raw internet payload fetches from cognitive reasoning models.
- **Implementation:** Fetcher (Network only), Sanitizer (Regex scrubbing), and Analyzer (Air-gapped reasoning boundary).

### 2. Capability Tool Firewalls
- **Objective:** Prevent raw access to operating system components.
- **Implementation:** Wrapping utility functions (e.g., `safe_fetch`) within strict Open Policy Agent verification layers.

### 3. Machine-Enforced Instruction Boundaries
- **Objective:** Preempt Indirect Prompt Injection (IPI) by decoupling system instructions from retrieved network contexts.
- **Implementation:** Wrapping untrusted strings in non-printable, machine-verifiable Unicode delimiters.

## Stage 3: Advanced Contextual Security

### 1. Contextual Intent Scoring & Bypass Detection
- **Objective:** Supplement static Rego rules with temporal and contextual scoring heuristics.
- **Implementation:** Risk calculation engine evaluating cross-domain anomalies.

### 2. Result Verification (Stage 4 Verifier)
- **Objective:** Prevent a compromised reasoning layer from embedding hidden execution triggers into the final returned output.
- **Implementation:** Isolated verification node scanning outputs for trailing shell commands or malicious payloads prior to system execution.

## Stage 4: Evolutionary Substrate & Operational Maturity

### Phase 6: Skills Engine & Adversarial Simulator (Pathogen) [OPERATIONAL]
- **Objective:** Eliminate brittle, hardcoded python deployments and establish continuous regression testing.
- **Implementation:** Declarative `SKILL.md` parsing. The Pathogen reads the `EXPLOITATION_CATALOG.md` and iteratively mutates vulnerabilities into active penetration tests against the local daemon.

### Phase 6.5: Multitenant Infrastructure & The Live Organism [OPERATIONAL]
- **Objective:** Support high-concurrency scaling, and transition the static dashboard into a self-healing biological paradigm.
- **Implementation:** 
  - Tiered isolation utilizing macOS iOS Seatbelt profiles.
  - SQLite Write-Ahead-Log `StateManager` for multi-tenant safety.
  - `AutoPatcher`: Sentinel actively writes mitigation patches into the Substrate, validates them via `pytest`, and updates Pathogen's target identity.
  - `EVOLUTION.md`: The active somatic ledger recording autonomous discoveries and modifications.

### Phase 7: The Airlock Interface (TUI & MCP) [OPERATIONAL]
- **Objective:** Eliminate "Knowledge Debt" by providing a Human-in-the-Loop staging ground where the Engineer Agent proposes, explains, and negotiates architectural mitigations before committing them.
- **Implementation:**
  - **Terminal UI (`textual`):** A high-fidelity split-pane terminal interface for reviewing `.patch` diffs and chatting with the Engineer.
  - **MCP Gateway:** Exposing un-patched CVEs as resources and the Engineer as a tool via the Model Context Protocol for direct IDE integration.

### Phase 7.5: Scalable Oversight (The Airlock Debate) [OPERATIONAL]
- **Objective:** Eliminate "Knowledge Debt" and bridge the "Verification Bottleneck" by providing a multi-agent adversarial discourse (Analyst vs. Skeptic) with a 12-hour temporal fallback.
- **Implementation:**
  - **The Discourse Triad:** Analyst (optimistic impact evaluation) and Skeptic (contrarian critique) debating proposed patches.
  - **Temporal Fallback:** Automated merge of unreviewed patches after 12 hours of human inactivity to maintain substrate evolution speed.
  - **Audit Provenance:** Full aggregation of debate transcripts into a permanent architectural ledger.

### Phase 8: Zero-Day Resilience (Cryptographic Gating & Fuzzing) [OPERATIONAL]
- **Objective:** Eliminate recursive supply-chain hijacking vectors and ensure the Substrate Daemon can be provably tested against undocumented threats.
- **Implementation:**
  - **Cryptographic State Integrity:** The SQLite backend enforces detached HMAC signatures for critical threat feeds to prevent offline state-tampering bypasses.
  - **Human-in-the-Loop Gateway:** The `AutoPatcher` generates `PENDING_MERGE.md` manifests instead of executing autonomous Git commits, preserving self-healing while mitigating self-compromise.
  - **Zero-Day Fuzzer:** `zero_day_drill.py` continuously harnesses the Pathogen to stress the Llama 3.2 logic with completely hallucinated, un-cataloged combinations.

### Phase 9: Conversational Triage (CLI Skills) [PLANNED]
- **Objective:** Seamlessly integrate Triad interactions into existing chat interfaces.
- **Implementation:** Develop an AntiGravity Skill allowing developers to use `/engineer triage` to interactively discuss Substrate vulnerabilities from within their primary command line interface.

### Phase 10: The Dashboard (Rich Web GUI) [PLANNED]
- **Objective:** Provide a comprehensive, visually rich enterprise dashboard for non-terminal architectural review.
- **Implementation:** A local FastAPI + Next.js web interface offering side-by-side graphical diffs, threat dependency graphs, and historical mitigation metrics.

### Phase 11: The Private Fleet (Tailscale Mesh) [PLANNED]
- **Objective:** Expand the Substrate perimeter beyond a single host machine, allowing lightweight edge clients to utilize the centralized MLX security pipeline.
- **Implementation:** Binding the Substrate Daemon to a `100.x.y.z` Tailscale interface to enable secure Publish/Discover/Subscribe capabilities over a trusted WireGuard backbone.

### Phase 12: Hostile Cloud Organism (Zero-Trust Mesh) [PLANNED]
- **Objective:** Secure the mesh against internal Man-in-the-Middle configuration drift via strict identity assertion.
- **Implementation:** Evolving the intent gateway using:
  - **Matchlock:** Cryptographic workload identities.
  - **mTLS:** Cryptographic verification of node identity.
  - **OAuth2/OIDC:** Identifying explicit tenant attribution.

---

## Stage 5: High-Assurance Hardening

### Phase 13: Sentinel Hybrid Migration [COMPLETED]
- **Objective:** Transition the Sentinel from a monolithic script to a declarative, substrate-managed agent.
- **Implementation:** `SKILL.md` manifest parsing, `runner.py` for hybrid execution, and ADR-0006.
- **Cross-ref:** See [TASKS_BOOTSTRAP.md](../TASKS_BOOTSTRAP.md).

### Phase 14: Bi-Directional Capability Firewall (Scale-Out PDP/PEP) [COMPLETED]
- **Objective:** Establish a centralized Meta-PDP (Singularity) that federates policy across multiple engines (Rego/Cedar).
- **Implementation:** FastAPI-based server with a Consensus local engine and a SQL Authorization Ledger for 100% auditability.

### Phase 15: Adaptive Rate-Limiting [COMPLETED]
- **Objective:** Prevent resource exhaustion and abuse via per-agent, per-tool throttling.
- **Implementation:** `AdaptiveRateLimiter` middleware integrated into `ToolRouter`. ADR-0007.

### Phase 16: Competitive Gap Closure (Domain Reputation & Static Analysis) [COMPLETED]
- **Objective:** Close competitive gaps with domain reputation scoring, static analysis, and alignment checking.
- **Implementation:** `domain_reputation.json`, `StaticAnalyzer`, `AlignmentChecker`. ADR-0008.

### Phase 17: Pathogen Adversarial Tuning & Metrics [COMPLETED]
- **Objective:** Generational mutation engine with persistent red-team metrics.
- **Implementation:** `MutationEngine`, `PathogenLogger`, `pathogen_metrics` table. ADR-0009.

### Phase 18: Singularity Meta-PDP Server [COMPLETED]
- **Objective:** Centralized, auditable authorization server for all policy decisions.
- **Implementation:** FastAPI Meta-PDP, `authorization_ledger` in SQLite, `RemoteSingularityPDP`. ADR-0010.

### Phase 19: Immutable Actions & Substrate Hardening [COMPLETED]
- **Objective:** Eliminate TOCTOU vulnerabilities and harden state integrity.
- **Implementation:** `ImmutableToolRequest`, LRU caching in `RegoPolicyEngine`, field-level encryption hooks. ADR-0011, ADR-0012.

### Phase 20: Substrate Optimization (Quota Management) [COMPLETED]
- **Objective:** Autonomous model routing based on intent complexity and quota awareness.
- **Implementation:** `ModelRouter`, Context Pruning, Low-Power Mode. ADR-0013.

### Phase 21: Forensic Hardening & Agent Consolidation [COMPLETED]
- **Objective:** Unified agent architecture, HMAC signatures for ADRs, and governance documentation.
- **Implementation:** `BaseTachyonAgent` ABC, `Role` architecture, Airlock Skills, `CHANGE_CONTROL.md`.

### Phase 21.7: The Canary Honeypot (Active Probe) [COMPLETED]
- **Objective:** Proactive threat scouting via sandboxed honeypot endpoints.
- **Implementation:** `CanaryRole`, `CANARY_LOG.md`, `launchd` automation. ADR-0019.
- **Validated:** Honeypot-to-Immune-System feedback loop operational.

---

## Stage 6: Autonomous Evolution

### Phase 22: Self-Evolving Policies & Immune Response [OPERATIONAL]
- **Objective:** Shift from reactive firewalling to an adaptive, self-improving security layer.
- **Implementation:**
  - **ImmuneManager**: Orchestrates the Canary→Engineer feedback loop.
  - **Policy Evolution Loop**: Automated OPA-Rego synthesis staged via the Airlock.
  - **Pathogen Fitness Scoring**: Only persist attacks that stress state boundaries.
  - **Constitutional AI**: Runtime policy critiquing based on high-level security principles.

### Phase 21.9: Local Reasoning Substrate (mlx_lm) [PLANNED]
- **Objective:** Eliminate cloud dependencies for core security reasoning, providing a zero-latency, offline fallback using Apple Silicon Native architecture.
- **Implementation:**
  - **Llama 3.2 via mlx_lm**: Local inference engine for L1/L2 tasks, leveraging Apple Unified Memory.
  - **Substrate-Bridge**: Middleware to route `ModelRouter` requests to the local `mlx_lm` engine when quota is low or network is absent.
  - **Context-Surgical Pruning**: Optimized local prompt templates for M5 Neural Engine.

### Phase 24: Event-Horizon Command Bridge (CLI/TUI/NeoVIM) [OPERATIONAL]
- **Objective:** Provide a unified, NeoVIM-first command-and-control interface for the substrate — replacing ad-hoc scripts with a single, composable `tt` entrypoint.
- **Implementation:**
  - **Tier 1 — CLI (`tt`):** Typer-based UNIX-composable commands with JSON output mode. [DONE]
  - **Tier 2 — TUI (`tt dash`):** Textual-framework dashboard with live manifolds and unified API telemetry. [DONE]
  - **Tier 3 — NeoVIM Plugin (`tachyon.nvim`):** Pure Lua plugin with floating dashboard, Telescope integration, and syntax highlighting. [DONE]
  - **Unified Daemon:** Consolidates PEP and Airlock layers on port 60461. [DONE]
- **Reference:** See [ADMIN.md](../ADMIN.md) for the full operator reference.

### Phase 23: Hardware-Level Isolation [COMPLETED]
- **Objective:** Eliminate substrate escape vectors and guarantee tool-call integrity via hardware-level boundaries.
- **Implementation:**
  - **WASM Tool Sandbox (Tier 1)**: `WasmRunner` via `wasmtime` for memory-safe, deterministic tool execution.
  - **MicroVM Isolation (Tier 0)**: `VmRunner` via Apple Virtualization.framework (`lima`) for full agent-level isolation.
  - **Substrate Stabilization**: 169/169 regression tests passing, `tt ritual` boot ceremony verified.
- **ADR:** ADR-0027: Hardware Isolation Protocol.

### Phase 25: Cryptographic Substrate & Secure SDLC [OPERATIONAL]
- **Objective:** Migrate from HMAC-SHA256 to a hardware-backed, post-quantum-ready asymmetric signing infrastructure with per-agent key isolation.
- **Reference:** See [SDLC.md](SDLC.md) for the full specification.
- **Implementation:**
  - **Phase 25.1 — Ed25519 Foundation**: Replace `IntegrityManager` HMAC with Ed25519 asymmetric signatures. Root key stored in Apple Keychain (Touch ID-gated). Shamir 3-of-5 key backup. [DONE]
  - **Phase 25.2 — Per-Agent Key Hierarchy**: HKDF delegation scoping each agent's signing authority. Sentinel signs debates, Engineer signs patches, Airlock co-signs everything. [DONE]
  - **Phase 25.3 — Hybrid PQC**: Add ML-DSA-65 (NIST FIPS 204, Level 3) as hybrid overlay. Implement ADR hash-chaining in MANIFEST.json for immutable forensic timeline. [DONE]
  - **Phase 25.4 — Deterministic PQC Anchoring**: Store expanded ML-DSA-65 secret key (4032 bytes) AND public key (1952 bytes) as dual Keychain entries. PQC Rekey ceremony with full roundtrip verification. [DONE]

### Phase 26.1: Agentic Observability & Control [OPERATIONAL]
- **Objective:** Eliminate agentic observability blindspots and cryptographically bind agent identities to sub-keys.
- **Reference:** See [adr/0029-agentic-observability-and-control.md](adr/0029-agentic-observability-and-control.md).
- **Implementation:**
  - **Telemetry Bus**: Structured JSONL forensic logging for all tool blocks, approvals, and cryptographic signatures.
  - **Delegation Certificates**: Hybrid-signed JSON certificates containing scoped HKDF keys, proving agent identity and role.
  - **Heartbeat Protocol**: Agents perform periodic checking against a Certificate Revocation List (CRL) to proactively isolate compromised keys.
  - **Cryptographic Modularity**: Hardened `signing.py` by extracting `KeychainProvider` and `HybridSigner`.

### Phase 27: Reliability Hardening (Event Sourcing & WAL) [PLANNED]
- **Objective**: Ensure 100% auditability and crash resilience for all agent actions.
- **Implementation**:
  - **EventStore**: Append-only ledger for all agent intents and tool executions.
  - **WAL**: Write-Ahead Logging for high-concurrency substrate mutations.

### Phase 28: SDLC Determinism (TDAD & Spec-First) [PLANNED]
- **Objective**: Eliminate "AntiGravity Flakiness" through machine-verifiable requirements.
- **Implementation**:
  - **TechnicalSpecification**: Pydantic-based requirements modeling.
  - **Test-Driven Agent Development**: Generation of verification tests *before* implementation code.

### Phase 29: Resilience Layers (Capability Tiers) [PLANNED]
- **Objective**: Establish graceful degradation protocols for autonomous security.
- **Implementation**:
  - **Tiered Response**: Automated fallbacks (Full -> Supervised -> Lockdown) based on substrate health metrics.

### Phase 26: CI/CD Hardening & Supply Chain Defense [PLANNED]
- **Objective:** Extend the Secure SDLC into automated pipelines and third-party dependency governance.
- **Implementation:**
  - **Pre-Commit Hooks**: Signature verification, unsigned ADR detection, secret scanning.
  - **GitHub Actions Verification**: CI verifies signatures but NEVER signs (signing is local-only, Secure Enclave).
  - **SBOM Generation**: CycloneDX Software Bill of Materials signed with each release.
  - **Reproducible Builds**: Hash-pinned `requirements.txt` and deterministic build attestation.
  - **Supply Chain Graduation**: Upgrade `is_package_whitelisted()` from stub to DB-backed check.

---

## Stage 7: Autonomous Maturity (HITL → HOTL → HOOTL)

- [ ] **Phase 31: The Immune Collective (Architecture v2.0)**: Transition from monolithic role-based scripts to a formal, event-driven agentic collective.
    - **EventBus**: SQLite-WAL based pub/sub for all agent coordination.
    - **BaseAgent Protocol**: Standardized signature-verifying, intent-gated execution lifecycle.
    - **Firewall Administrator**: The "Thinker" LLM Agent powered locally exclusively by `mlx_lm` for executive decisioning and traffic observation.
    - **The Herald**: The "Mouth/Ear" Custom Agent acting as the deterministic air-gapped proxy for UI, CLI, NeoVIM and secure C2 and alerts.
- [ ] **High-Assurance Gateway Optimization**: Optimizing the substrate for dedicated, secure hardware gateway deployments.
### Phase 41: Claw Ecosystem Compatibility (The 5,700-Skill Bridge) [PLANNED]
- **Objective:** Securely ingest and run 5,700+ open-source agents from the ClawHub repository while maintaining substrate-level intent gating.
- **Implementation:**
  - **ClawTranslator**: Auto-mapping from Claw `SOUL.md` → Tachyon `SKILL.md`.
  - **5-Stage Vetting Pipeline**: Translation, Static Analysis, Sandbox, Airlock, and Quarantine.
  - **Import Utility**: `scripts/import_claw_agent.py` with security profiling.
