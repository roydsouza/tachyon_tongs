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
- **Implementation:** Declarative `SKILL.md` parsing. Initiation of the autonomous Red Team (Pathogen) to iteratively mutate discovered vulnerabilities into active penetration tests against the local daemon.

### Phase 6.5: Multitenant Infrastructure Upgrade [OPERATIONAL]
- **Objective:** Support high-concurrency scaling of the Doom Constellation across disparate threat environments.
- **Implementation:** Tiered isolation using macOS native iOS seatbelt sandboxes, SQLite Write-Ahead-Log State Management, and `mlx_lm` Meta acceleration integration.

### Phase 7: The Private Fleet (Tailscale Mesh) [UP NEXT]
- **Objective:** Expand the Substrate perimeter beyond a single host machine, allowing lightweight edge clients to utilize the centralized MLX security pipeline.
- **Implementation:** Binding the Substrate Daemon to a `100.x.y.z` Tailscale interface to enable secure Publish/Discover/Subscribe capabilities over a trusted WireGuard backbone.

### Phase 8: Hostile Cloud Organism (Zero-Trust Mesh) [PLANNED]
- **Objective:** Secure the mesh against internal Man-in-the-Middle configuration drift via strict identity assertion.
- **Implementation:** Evolving the intent gateway using:
  - **Matchlock:** Cryptographic workload identities.
  - **mTLS:** Cryptographic verification of node identity.
  - **OAuth2/OIDC:** Identifying explicit tenant attribution.
