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

### 5. Multi-Tenant Substrate Daemon (v1.0) [ACTIVE]
- **Why we did this:** Amortize security hardening across all agents in the workspace. One Sentinel to Rule Them All.
- **How:** Local FastAPI daemon at `:60461` orchestrating the Guardian Triad.

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

### 1. The Sentinel Triad (Self-Enhancing loop)
- **Why we are doing this:** The current Sentinel suffers from "Privilege Collapse." A single agent shouldn't hunt for threats *and* write the mitigation code simultaneously.
- **How:** Split the Sentinel into a Guardian Agent Pattern:
    - *Scout*: Network-enabled, monitors the internet.
    - *Analyst*: Air-gapped, classifies the threats.
    - *Engineer*: Proposes mitigations without network access.

### 2. Post-Quantum (PQC) Hybrid Authentication
- **Why we are doing this:** Things that sound cool but aren't urgent. Also, because quantum computers will eventually break our YubiKeys.
- **How:** Implement a dual-signature scheme: hardware-backed ECC + software-backed Dilithium3.

### 3. WASM Sandboxing for Tool Execution
- **Why we are doing this:** Booting a full VM just to run `curl` is overkill.
- **How:** Use Wasmtime to compile and run individual tools in tight WebAssembly boundaries.

### 4. Secure Enclave (SEP) Key Storage & Audit Logging
- **Why we are doing this:** If a hacker gets root, they usually delete the logs. We want logs they physically cannot delete.
- **How:** Forward cryptographic signing of agent actions to the Apple Secure Enclave Processor (SEP) to create unforgeable, append-only audit traces.

### 5. Research Pulsar & Synthetic Attack Engine [OPERATIONAL]
- **Why we are doing this:** To spot academic exploits (arXiv cs.CR, USENIX) 6-18 months before they become active CVEs in the wild.
- **How:** An automated parser that distills Daily Preprint Signals into `EXPLOITATION_CATALOG.md` entries (completed Phase 4.2). *Pending:* Synthetic Attack Engine (ZeroDayBench methodology) to auto-test policies against them.

## Phase 5: Event-Horizon Substrate (Workspace-Wide) [OPERATIONAL]
- **Why we are doing this:** Sentinel is lonely. We want other agents in `~/antigravity/` to be able to use the same safety bumpers without having to copy-paste the whole repo like it's 2004.
- **How:** A local "Tachyon Daemon" (`localhost:60461`) that agents can ping for safe tool execution. One Sentinel Hardening to Rule Them All.

## Phase 5.5: Semantic Intent Gating (Dynamic Networking) [UP NEXT]
- **Why we are doing this:** The Phase 1 Global Whitelist is too brittle. Some external agents (like a Research Bot) need full web access, while internal agents (like DevOpsBot) need strict bounding. 
- **How:** Shifting the Substrate from a default-deny whitelist to a Dual-Mode Pipeline:
  - **Sentinel Denylist:** A dynamically updated list of known malicious domains.
  - **Client-Provided Constraints:** Clients send their own `allowed_domains` config when requesting a resource. If open, the Daemon relies entirely on the heavy Semantic Filter + Bouncer Triad.

## Phase 6: The Data-Driven "Skills" Engine (Orthogonal Extensibility)
- **Why we are doing this:** Hardcoding agent logic in Python is brittle. We want to be able to introspect, clone, and modify agent behaviors purely via text.
- **How:** Distill the Sentinel (and future agents) into independent "Skills plugins" (e.g., `SKILL.md`). Tachyon Tongs will use these markdown configurations—which codify behaviors, structure, target sites, and actions—to dynamically materialize new agents within the Substrate.

## Phase 7: The Private Fleet (Tailscale Mesh)
- **Why we are doing this:** You want your travel laptop to benefit from the heavyweight Sentinel analysis running on the M2 Ultra Desktop without duplicating the entire compute pipeline.
- **How:** Binding the Substrate Daemon to the VPN interface (`100.x.y.z`) to allow inter-device Publish/Discover/Subscribe capabilities over a trusted WireGuard backbone.

## Phase 8: Hostile Cloud Organism (Zero-Trust Mesh)
- **Why we are doing this:** Eventually, we want to scale. The network is untrusted, and hackers might actively try to poison the Intent Gates via Man-in-the-Middle or Replay attacks.
- **How:** Evolving the Publish/Discover/Subscribe model into a Zero-Trust Gateway:
  - **mTLS:** Cryptographic verification of client identity.
  - **OAuth2/OIDC:** Identifying exactly *which* tenant and agent is making the request.
  - **Hardware Signatures:** Bounding global threat reporting to YubiKey or Post-Quantum (PQC) Multi-Sig approvals.

---

### 🏛️ Strategic Intel Archive (Archive from Stage 2)
- **STIX/TAXII Integration:** For structured threat exchange in a multi-tenant cloud mesh.
- **Onion-Gateway Isolation:** If dark-web scraping is ever legalized by our legal team, use a dedicated micro-VM with seccomp filters.
- **ML-Based Anomaly Detection:** Using Isolation Forests to flag weird agent behaviors that don't match our `verified_traffic.json` baseline.
- **Watermarking Prompts:** Using Diffusers-style watermarks for tracing the origin of an injection through multiple agent hops.

## 🗑️ The Graveyard (Discarded Ideas from LLM Review)

- **Agent-to-Agent (A2A) as a replacement for the Substrate (OpenAI/Gemini feedback):**
  - **Status:** REJECTED.
  - **Reason:** A2A is great for agents gossiping with each other, but it doesn't provide the *physical kernel isolation* and *Intent Gating* that Tachyon Tongs specializes in. We will support A2A *on top* of the substrate, not instead of it.
- **Distributed Sentinel Instances (Grok/Claude feedback):**
  - **Status:** REJECTED.
  - **Reason:** Running 50 Sentinels for 50 agents is a great way to melt your battery and have 50 slightly different versions of the truth. We are going with a **Centralized Substrate** to amortize the reasoning cost.
- **Cloud-only Sanitization:**
  - **Status:** REJECTED (Obviously).
  - **Reason:** If we send our dirty data to the cloud to be cleaned, we've already lost the privacy game. Mental 4 or bust.
