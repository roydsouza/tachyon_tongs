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

### 2. Stage 4 Verifier (Result Verification)
- **Objective:** Prevent a compromised reasoning layer from embedding hidden execution triggers into the final returned output.
- **Implementation:** Isolated verification node scanning outputs for trailing shell commands or malicious payloads prior to system execution.

## Stage 4: Evolutionary Substrate & Cloud Mesh

### Phase 6: Skills Engine & Adversarial Simulator (Pathogen) [OPERATIONAL]
- **Objective:** Eliminate brittle, hardcoded python deployments and establish continuous regression testing.
- **Implementation:** Declarative `SKILL.md` parsing. The Pathogen reads the `EXPLOITATION_CATALOG.md` and iteratively mutates vulnerabilities into active penetration tests against the local daemon.

### Phase 6.5: Multitenant Infrastructure Upgrade & The Live Organism [OPERATIONAL]
- **Objective:** Support high-concurrency scaling, and transition the static dashboard into a self-healing biological paradigm.
- **Implementation:** 
  - Tiered isolation utilizing macOS iOS Seatbelt profiles.
  - SQLite Write-Ahead-Log `StateManager` for multi-tenant safety.
  - `AutoPatcher`: Sentinel actively writes mitigation patches into the Substrate, validates them via `pytest`, and updates Pathogen's target identity.
  - `EVOLUTION.md`: The active somatic ledger recording autonomous discoveries and modifications.

### Phase 8: Zero-Day Resilience (Cryptographic Gating & Fuzzing) [OPERATIONAL]
- **Objective:** Eliminate recursive supply-chain hijacking vectors and ensure the Substrate Daemon can be provably tested against undocumented threats.
- **Implementation:**
  - **Cryptographic State Integrity:** The SQLite backend enforces detached HMAC signatures for critical threat feeds to prevent offline state-tampering bypasses.
  - **Human-in-the-Loop Gateway:** The `AutoPatcher` generates `PENDING_MERGE.md` manifests instead of executing autonomous Git commits, preserving self-healing while mitigating self-compromise.
  - **Zero-Day Fuzzer:** `zero_day_drill.py` continuously harnesses the Pathogen to stress the Llama 3.2 logic with completely hallucinated, un-cataloged combinations.

### Phase 7: The Airlock Interface (TUI & MCP) [UP NEXT]
- **Objective:** Eliminate "Knowledge Debt" by providing a Human-in-the-Loop staging ground where the Engineer Agent proposes, explains, and negotiates architectural mitigations before committing them.
- **Implementation:**
  - **Terminal UI (`textual`):** A high-fidelity split-pane terminal interface for reviewing `.patch` diffs and chatting with the Engineer.
  - **MCP Gateway:** Exposing un-patched CVEs as resources and the Engineer as a tool via the Model Context Protocol for direct IDE integration.

### Phase 7.5: Scalable Oversight (The Airlock Debate) [UP NEXT]
- **Objective:** Eliminate "Knowledge Debt" and bridge the "Verification Bottleneck" by providing a multi-agent adversarial discourse (Analyst vs. Skeptic) with a 12-hour temporal fallback.
- **Implementation:**
  - **The Discourse Triad:** Analyst (optimistic impact evaluation) and Skeptic (contrarian critique) debating proposed patches.
  - **Temporal Fallback:** Automated merge of unreviewed patches after 12 hours of human inactivity to maintain substrate evolution speed.
  - **Audit Provenance:** Full aggregation of debate transcripts into a permanent architectural ledger.

### Phase 8: Conversational Triage (CLI Skills) [PLANNED]
- **Objective:** Seamlessly integrate Triad interactions into existing chat interfaces.
- **Implementation:** Develop an AntiGravity Skill allowing developers to use `/engineer triage` to interactively discuss Substrate vulnerabilities from within their primary command line interface.

### Phase 9: The Dashboard (Rich Web GUI) [PLANNED]
- **Objective:** Provide a comprehensive, visually rich enterprise dashboard for non-terminal architectural review.
- **Implementation:** A local FastAPI + Next.js web interface offering side-by-side graphical diffs, threat dependency graphs, and historical mitigation metrics.

### Phase 10: The Private Fleet (Tailscale Mesh) [PLANNED]
- **Objective:** Expand the Substrate perimeter beyond a single host machine, allowing lightweight edge clients to utilize the centralized MLX security pipeline.
- **Implementation:** Binding the Substrate Daemon to a `100.x.y.z` Tailscale interface to enable secure Publish/Discover/Subscribe capabilities over a trusted WireGuard backbone.

### 🔳 Stage 4: Autonomous Maturity (HITL → HOTL → HOOTL)
*   [ ] **Hybrid Oversight Platform**: Transition from manual "Airlock" clicks to "Policy-Based Exceptions."
*   [ ] **Oversight Trajectory Definition**:
    - **HITL (Human-In-The-Loop)**: Fail-closed on every anomaly.
    - **HOTL (Human-On-The-Loop)**: Bounded risk with automated 72-hour rollback window.
    - **HOOTL (Human-Out-Of-The-Loop)**: Probabilistic gating + post-hoc audit.
*   [ ] **Retrospective Audit Engine**: Implement the 72-hour rollback window for autonomous patches.
*   [ ] **Formal Verification Integration**: Auto-generating formal proofs for substrate mutations.
*   [ ] **Self-Healing Substrate**: Zero-latency autonomous mitigation.

### Phase 11: Hostile Cloud Organism (Zero-Trust Mesh) [PLANNED]
- **Objective:** Secure the mesh against internal Man-in-the-Middle configuration drift via strict identity assertion.
- **Implementation:** Evolving the intent gateway using:
  - **Matchlock:** Cryptographic workload identities.
  - **mTLS:** Cryptographic verification of node identity.
  - **OAuth2/OIDC:** Identifying explicit tenant attribution.

### Phase 13: Substrate-Aware Quota Management [PLANNED]
- **Objective:** Eliminate "Quota Blackouts" by autonomously routing reasoning tasks between cost-effective (Flash/Local) and high-reasoning (Pro/Ultra) models.
- **Implementation:**
  - **Autonomous Model Router:** Evaluates prompt complexity and selects the optimal model substrate.
  - **Context Pruning:** Minimizes token consumption by surgically loading only required task fragments.
  - **Low-Power Mode (LPM):** Automatically disables non-critical background processes (e.g., Pathogen drills) based on quota availability.

### Phase 21: Local LLM Substrate (llama.cpp) [PLANNED]
- **Objective:** Eliminate cloud dependencies for core security reasoning, providing a zero-latency, offline fallback.
- **Implementation:**
  - **Llama 3.2 MLX/llama.cpp**: Local inference engine for L1/L2 tasks.
  - **Substrate-Bridge**: Middleware to route `ModelRouter` requests to the local socket when quota is low or network is absent.
  - **Context-Surgical Pruning**: Optimized local prompt templates for M5 Neural Engine.

### Phase 14: Bi-Directional Capability Firewall (Scale-Out PDP/PEP) [OPERATIONAL]
- **Objective:** Establish a centralized Meta-PDP (Singularity) that federates policy across multiple engines (Rego/Cedar).
- **Implementation:** FastAPI-based server with a Consensus local engine and a SQL Authorization Ledger for 100% auditability.

### Phase 15: PQC-Hybrid Tool Attestation [PLANNED]
- **Objective:** Preemptively secure the tool-call chain against quantum threats and provide cryptographic "intent-gate" proofs.
- **Implementation:** Hybrid Ed25519/Dilithium3 signatures for all `RemoteSingularityPDP` requests.

### Phase 16: TOCTOU-Resistant Enforcement (Immutable Actions) [PLANNED]
- **Objective:** Eliminate race conditions where a tool request is modified between policy check and execution.
- **Implementation:** Transition `ToolRouter` to use `frozen` dataclasses and hash-verified immutable payloads.

### Phase 17: Scalable Oversight (The Airlock Debate Triad) [IN-PROGRESS]
- **Objective:** Eliminate "Verification Bottlenecks" by using multi-agent adversarial discourse (Analyst vs. Skeptic) to surface high-value insights to the operator.
- **Implementation:**
  - **The Discourse Triad:** Analyst (Optimistic) vs. Skeptic (Pessimistic) debating proposed patches.
  - **Meta-Critic:** Distills debate into a concise "Verification Summary" for the human operator.
  - **Mastery Erosion Guard:** Periodic "Deliberate Friction" prompts to keep human calibration sharp.

### Phase 22: Self-Evolving Policies (The Immune System) [PLANNED]
- **Objective:** Shift from reactive firewalling to an adaptive, self-improving security layer.
- **Implementation:**
  - **Pathogen Fitness Scoring**: Only persist attacks that stress state boundaries.
  - **Policy Evolution Loop**: Automated Rego/Cedar synthesis based on Pathogen failures.
  - **Constitutional AI**: Runtime policy critiquing based on high-level security principles.

### Phase 23: Isolation & Attestation [PLANNED]
- **Objective:** Eliminate substrate escape vectors and guarantee tool-call integrity.
- **Implementation:**
  - **WASM Tool Sandbox**: Isolate lightweight tool execution.
  - **MicroVM (Firecracker) Bounding**: Extreme isolation for high-risk reasoning tasks.
  - **PQC-Hybrid Attestation**: Dilithium3 signatures for all tool-gate interactions.
