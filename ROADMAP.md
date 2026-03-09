# 🛸 Tachyon Tongs: Evolutionary Architecture Roadmap

> *"A system is only as secure as the developer's willingness to not bypass the firewall to test something 'real quick'." - Ancient DevOps Proverb*

This roadmap outlines the progression of the **Tachyon Tongs** architecture—a high-assurance, defense-in-depth framework for autonomous AI agents running on Apple Silicon. The roadmap is structured in four stages to build a trustworthy pipeline that resists Agent Hijacking, Prompt Injection, and Memory Poisoning. Let's build a Space Organism!

## Stage 1: Prerequisites (The Foundation)

### 1. Hardware-Bound Authentication (FIDO2)
- **Why we are doing this:** Physical presence is the only mathematically proven defense against remote agent hijacking. Unless the hacker is in your living room, they can't push code.
- **How:** YubiKey 5C NFC for hardware-bound SSH keys, Git commits, and intent-gate approvals.
- **Why we didn't just use BioMetrics:** TouchID is great, but incredibly annoying to pass through to headless Linux micro-VMs. 

### 2. Apple Silicon Virtualization (Lima)
- **Why we are doing this:** Running untrusted agents directly on macOS or in Docker shares the kernel. If the kernel goes down, the whole ship goes down.
- **How:** Lima using Apple's `Hypervisor.framework` to spin up Linux MicroVMs at near-native speeds. (The panic room).
- **Why we didn't just use Docker Desktop:** See above regarding "sharing the kernel." Plus, YubiKey passthrough on Docker for Mac makes me want to cry.

### 3. Metal 4 Neural Engine Optimization
- **Why we are doing this:** Local inference means we don't send raw, sensitive data to third-party cloud APIs that will inevitably get breached in three years.
- **How:** AntiGravity configured to use `metal_4` backends utilizing the M5 Neural Engine.

## Stage 2: Basics (The Core Pipeline)

### 1. Tri-Stage "Safe-Search" Architecture
- **Why we are doing this:** Agents fetching internet data cannot be trusted to reason about it at the same time. They are easily distracted.
- **How:**
  - **Fetcher (Untrusted):** Downloads raw HTML/JS. Has network but no brain.
  - **Sanitizer (The Janitor):** Strips `<script>` and `<iframe>` tags. 
  - **Analyzer (Air-gapped):** Processes the cleaned text. Has a brain, but no network.
- **Why we didn't just use MultiOn:** Giving a single agent access to the DOM, cookies, and network is terrifying. 

### 2. Capability Firewalls for Tools
- **Why we are doing this:** Agents should never have raw access to system commands like `bash`. Do you want Skynet? Because that's how you get Skynet.
- **How:** Wrap every tool in a policy layer (e.g., `safe_fetch(url)`). The firewall validates all parameters before the tool is allowed to execute.

### 3. Matchlock Sandboxing & Intent Gates
- **Why we are doing this:** We need network port-blocking that understands *what the LLM is actually trying to do*, rather than just blocking IP addresses.
- **How:** Matchlock profiles that freeze on unauthorized egress and require you to physically touch the YubiKey to proceed.

### 4. Machine-Enforced Instruction Boundaries
- **Why we are doing this:** Stop the LLM from confusing untrusted data with system prompts. 
- **How:** Wrap untrusted content in non-printable, machine-verifiable Unicode delimiters. Magic invisible boxes.

## Stage 3: Advanced (Contextual Security)

### 1. Contextual Intent Scoring & Bypass Detection
- **Why we are doing this:** Static rules are brittle. Deleting a log file at 2 PM is maintenance. Deleting it at 2 AM is a cover-up.
- **How:** A scoring engine that calculates risk based on time of day, recent user activity, and cross-domain actions. 

### 2. Token Decay and Action Budgets
- **Why we are doing this:** A 72-minute ephemeral token is still dangerous if hijacked in minute 1.
- **How:** "Capability Tokens" that lose privileges over time. Think of it like a shrinking allowance.

### 3. Stage 4 Verifier (Result Verification)
- **Why we are doing this:** A compromised analyzer could embed hidden instructions in its output. We need a bouncer at the exit door.
- **How:** A final, isolated agent that checks the Analyzer's output for factual claims and hidden execution triggers before the human ever sees it.

### 4. Behavioral Monitoring (Reasoning Chain Analysis)
- **Why we are doing this:** We want to catch the agent lying to itself.
- **How:** A monitor that flags anomalies in tool sequence, decision branching, and goal drift.

## Stage 4: Future (Next-Gen Adaptability)

### 1. The Sentinel Agent (Self-Enhancing loop)
- **Why we are doing this:** Security is a moving target. We are tired of updating firewalls manually.
- **How:** A highly restricted agent that scours CVE feeds and proposes architectural updates to our local `TASKS.md`. It literally patches itself.

### 2. Post-Quantum (PQC) Hybrid Authentication
- **Why we are doing this:** Things that sound cool but aren't urgent. Also, because quantum computers will eventually break our YubiKeys.
- **How:** Implement a dual-signature scheme: hardware-backed ECC + software-backed Dilithium3.

### 3. WASM Sandboxing for Tool Execution
- **Why we are doing this:** Booting a full VM just to run `curl` is overkill.
- **How:** Use Wasmtime to compile and run individual tools in tight WebAssembly boundaries.

### 4. Secure Enclave (SEP) Key Storage & Audit Logging
- **Why we are doing this:** If a hacker gets root, they usually delete the logs. We want logs they physically cannot delete.
- **How:** Forward cryptographic signing of agent actions to the Apple Secure Enclave Processor (SEP) to create unforgeable, append-only audit traces.

---

## 🗑️ The Graveyard (Discarded Ideas)

- **Colima with gVisor as the primary sandbox**: gVisor is great, but Lima with `Hypervisor.framework` is hardware-virtualized. It's just inherently stronger against kernel escapes.
- **Cloud-based Content Sanitizers**: Sending our scraped data to OpenAI violates our security model. Metal 4 keeps our secrets secret.
- **Standard Docker Containers**: Shares the MacOS host kernel. A kernel exploit in Docker compromises the entire Mac. No thanks.
