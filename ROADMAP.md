# 🛸 Tachyon Tongs: Evolutionary Architecture Roadmap

This roadmap outlines the progression of the **Tachyon Tongs** architecture—a high-assurance, defense-in-depth framework for autonomous AI agents running on Apple Silicon. The roadmap is structured in four stages to build a trustworthy pipeline that resists Agent Hijacking, Prompt Injection, and Memory Poisoning.

## Stage 1: Prerequisites (The Foundation)

### 1. Hardware-Bound Authentication (FIDO2)
- **Motivation:** Physical presence is the only mathematically proven defense against remote agent hijacking. We need an unbreakable L0 defense.
- **Implementation:** YubiKey 5C NFC for hardware-bound SSH keys, Git commits, and intent-gate approvals.
- **Alternatives Considered:** 
  - *Biometrics (FaceID/TouchID):* Useful for convenience, but less portable and harder to integrate deeply into headless agent pipelines than a dedicated PIV/Smart Card module. 
  - *Password Managers:* Vulnerable to host-level memory scraping if the machine is compromised.

### 2. Apple Silicon Virtualization (Lima)
- **Motivation:** Running untrusted agents directly on macOS or in Docker shares the kernel, leaving the system vulnerable to container escapes.
- **Implementation:** Lima using Apple's `Hypervisor.framework` to spin up Linux MicroVMs at near-native speeds.
- **Alternatives Considered:** 
  - *Docker Desktop:* Rejected because it shares the macOS kernel natively and struggles with passing through YubiKeys to inner containers.

### 3. Metal 4 Neural Engine Optimization
- **Motivation:** Local inference reduces data exfiltration risks by not sending raw sensitive data to third-party cloud APIs.
- **Implementation:** AntiGravity configured to use `metal_4` backends utilizing the M5 Neural Engine.
- **Alternatives Considered:** 
  - *CUDA/Vulkan:* High overhead and translation latency on Apple Silicon.

## Stage 2: Basics (The Core Pipeline)

### 1. Tri-Stage "Safe-Search" Architecture
- **Motivation:** Agents fetching internet data cannot be trusted to reason or execute commands simultaneously.
- **Implementation:**
  - **Fetcher (Untrusted):** Downloads raw HTML/JS. Has network egress, but no filesystem or execution rights.
  - **Sanitizer (Deterministic):** Strips `<script>`, `<iframe>`, and common injection patterns. 
  - **Analyzer (Air-gapped):** Processes cleaned text. No network access.
- **Alternatives Considered:** 
  - *Single-Agent Browser Tools (e.g., MultiOn):* Rejected because a single prompt injection grants the agent full control over logged-in sessions.

### 2. Capability Firewalls for Tools
- **Motivation:** Agents should never have raw access to system commands like `curl` or `bash`.
- **Implementation:** Wrap every tool in a policy layer (e.g., `safe_fetch(url)` instead of `curl`). The firewall validates all parameters against a whitelist before the tool executes.
- **Alternatives Considered:** 
  - *System-level network blockers (Little Snitch):* They block at the IP/Port level but do not understand the *semantic intent* of the LLM.

### 3. Matchlock Sandboxing & Intent Gates
- **Motivation:** We need network port-blocking that understands LLM intent.
- **Implementation:** Matchlock profiles that freeze on unauthorized egress and require a physical hardware touch to proceed.
- **Alternatives Considered:** 
  - *Standard Firecracker:* Highly secure VM but lacks semantic LLM intent-aware rules. 

### 4. Machine-Enforced Instruction Boundaries (Context Labeling)
- **Motivation:** Stop the LLM from confusing untrusted data with system prompts.
- **Implementation:** Wrap untrusted content in non-printable, machine-verifiable Unicode delimiters.

## Stage 3: Advanced (Contextual Security)

### 1. Contextual Intent Scoring & Bypass Detection
- **Motivation:** Static rules are brittle. Legitimate actions at 2 PM might be malicious at 2 AM.
- **Implementation:** A scoring engine that calculates risk based on time of day, recent user activity, and cross-domain actions. Furthermore, an analyzer that detects "action fragmentation" (TOCTOU attacks).
- **Alternatives Considered:** 
  - *Hardcoded Rego Policies:* Good for baseline, but easily bypassed by a smart attacker chaining multiple "low-risk" intents.

### 2. Token Decay and Action Budgets
- **Motivation:** A 72-minute ephemeral token is still dangerous if hijacked in minute 1.
- **Implementation:** "Capability Tokens" that lose privileges over time (e.g., losing 'admin' rights after 10 minutes).
- **Alternatives Considered:** 
  - *Standard Short-Lived Tokens:* Offers no progressive safety; it's a binary valid/invalid state.

### 3. Stage 4 Verifier (Result Verification)
- **Motivation:** A compromised analyzer could embed hidden instructions in its output to the user.
- **Implementation:** A final, isolated agent that checks the Analyzer's output for factual claims and hidden execution triggers before it reaches the human.
- **Alternatives Considered:** 
  - *Sanitizing final output:* Harder to do deterministically without stripping the useful information the user actually wants.

### 4. Behavioral Monitoring (Reasoning Chain Analysis)
- **Motivation:** Detect compromised agents *before* they act by analyzing how they think.
- **Implementation:** A monitor that flags anomalies in tool sequence, decision branching, and goal drift.

## Stage 4: Future (Next-Gen Adaptability)

### 1. The Sentinel Agent (Self-Enhancing loop)
- **Motivation:** Security is a moving target. The system must adapt to 2026+ threats without constant manual tuning.
- **Implementation:** A highly restricted, read-only agent that scours CVE feeds, GitHub advisories, and AI safety papers, then proposes architectural updates to a local `TASKS.md` for human review.

### 2. Post-Quantum (PQC) Hybrid Authentication
- **Motivation:** Current ECC hardware keys will eventually fall to quantum decryption.
- **Implementation:** Implement a dual-signature scheme: hardware-backed ECC from the YubiKey + software-backed Dilithium3 (PQC) running locally, until PQC hardware keys are standardized.

### 3. WASM Sandboxing for Tool Execution
- **Motivation:** VMs are heavy for single-tool executions.
- **Implementation:** Use Wasmtime/Wasmer to compile and run individual tools in capability-based WebAssembly boundaries instead of full Linux subprocesses.
- **Alternatives Considered:** 
  - *gVisor:* Good, but WASM provides a strictly tighter memory and I/O capability model for pure functions.

### 4. Secure Enclave (SEP) Key Storage & Audit Logging
- **Motivation:** Root-level compromise within the VM shouldn't allow log tampering.
- **Implementation:** Forward cryptographic signing of agent actions to the Apple Secure Enclave Processor (SEP) to create unforgeable, append-only audit traces (e.g., via Sigstore/immudb).

---

## 🗑️ Discarded / Deprecated Ideas

1. **Colima with gVisor as the primary sandbox**
   - *Justification:* While gVisor is great for multi-tenant high-density fleets, Lima using `Hypervisor.framework` provides hardware-virtualized isolation which is objectively stronger against kernel escapes for single-user "vibe coding" sessions.
2. **Cloud-based Content Sanitizers (e.g., OpenAI API for sanitization)**
   - *Justification:* Sending untrusted, potentially sensitive web scraped data back to a third party violates our operational security model. Metal 4 local inference makes this unnecessary.
3. **Single-Agent Browser Automation**
   - *Justification:* Giving a single agent access to DOM, cookies, and network is too dangerous. We enforce the Tri-stage Fetcher/Sanitizer/Analyzer pipeline instead.
4. **Relying solely on "Ignore Previous Instructions" text filters**
   - *Justification:* These are easily bypassed by Unicode tricks and steganography. We chose verifiable context boundaries and cryptographic delimiters instead.
5. **Standard Docker Containers**
   - *Justification:* Shares the MacOS host kernel. A kernel exploit could compromise the entire machine.
