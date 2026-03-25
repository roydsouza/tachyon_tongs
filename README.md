# Securing the Agentic Inversion: An Evolutionary, Post-Quantum Agentic Firewall for Cognitive Threats

The internet is undergoing the **Agentic Inversion**: autonomous AI agents are projected 
to outnumber human users by orders of magnitude, acting as proxies for scheduling, 
DeFi execution, contract negotiation, and sensitive data operations. 
This shift expands the attack surface into a behavioral and cognitive domain that 
traditional static firewalls cannot address. 
Agents are vulnerable to prompt injection, context manipulation, and high-velocity 
polymorphic attacks capable of leaking private keys or draining accounts—threats 
that evolve faster than signature-based or rule-driven defenses.


**Tachyon Tongs** (see [White Paper](docs/WHITEPAPER.md)) is a local, adaptive agentic firewall that treats security as an evolutionary process. 
It combines an air-gapped LLM (llama.cpp) for real-time reasoning, hybrid post-quantum signatures (Ed25519 + ML-DSA-65) 
for cryptographic identity on every internal message, and an internal Pathogen-vs-Sentinel adversarial loop 
for proactive vulnerability discovery and patching. Flexible governance modes—HITL (Human In The Loop), 
HOTL (Human On The Loop), and HOOTL (Human Out Of The Loop) — these ensure 
human oversight remains the ultimate authority via the Herald notification interface.

Designed for zero-trust agentic environments, Tachyon Tongs provides the adaptive immune system 
required to secure digital proxies before widespread compromise occurs.

---

## 🛡️ A Live Threat Model
Every architectural decision is mapped directly to a specific vector in the [THREAT_MODEL.md](docs/THREAT_MODEL.md).

*   🧠 **Semantic Intent Gating**: All tool requests are routed through a Policy Enforcement Point and evaluated by the **Singularity Meta-PDP**.
*   🛡️ **Live, Self-Updating Threat Model**: The substrate's [THREAT_MODEL.md](docs/THREAT_MODEL.md) is not a static document. It is dynamically augmented by the **Pathogen** and **Sentinel**, with each new adversarial discovery mapped to the **OWASP-2026-ASI** taxonomy.
*   🧊 **Tiered Workload Isolation**: High-risk actions run in dynamically generated macOS `sandbox-exec` (Seatbelt) profiles.
*   🔐 **Forensic Integrity Gating**: Every substrate mutation is cryptographically signed using **Ed25519 + ML-DSA-65** hybrid sidecars.

---

## 💎 The Crown Jewels: Proactive Defense & Autoresearch
Tachyon Tongs is not just a reactive proxy; it is a **self-evolving security organism**.

*   🦠 **Pathogen (Metamorphic Adversarial Reasoning)**: Every 24 hours, the Pathogen agent executes a deep adversarial sweep. Moving beyond static templates, it now utilizes a **Reflector Node** to "think" about substrate defenses. It ingests ADRs and blueprints to identify blind spots, synthesizing **Goal-Aliased** attacks that masquerade as legitimate telemetry to bypass intent-based filters.
*   🔭 **Sentinel (Autonomous Intelligence Research)**: The Sentinel performs Karpathy-style "Autoresearch"—not just searching for CVEs, but autonomously browsing, synthesizing, and mapping novel vulnerabilities into high-signal "Adversarial Guidance" for the Pathogen.
*   🧬 **Metamorphic Co-Evolution**: This continuous loop between the Sentinel (Discovery) and the Pathogen (Reasoning & Verification) creates a biological-grade immune response that self-hardens the substrate against human-level adversarial logic.

---

## 🔐 Secure SDLC: Hardware-Anchored Trust
Tachyon Tongs practices forensic security in its own development process. Every mutation is cryptographically signed and hardware-anchored.

*   🆔 **Hardware-Backed Signing**: Root keys live in the Apple **Secure Enclave** (Touch ID-gated, non-extractable).
*   ⚛️ **Hybrid Post-Quantum Cryptography**: Signatures use **Ed25519 + ML-DSA-65** (NIST FIPS 204, Level 3).
*   ⛓️ **Forensic ADR Chaining**: Every Architecture Decision Record references the hash of its predecessor, anchored to the Merkle root in `MANIFEST.json`.

👉 **[docs/SDLC.md](docs/SDLC.md)** — *The full Secure SDLC reference.*

---

## 🧩 Agent Plugin Architecture

Tachyon Tongs uses a modular, role-based plugin system (ADR-0033). Agents are categorized into three tiers for optimal isolation and flexibility:

- **💻 Code-Only Agents**: Pure Python implementations (e.g., `engineer`, `pathogen`, `guardian`).
- **📜 Skill-Only Agents**: Declarative agents defined by their `SKILL.md` manifests (e.g., lightweight reconnaissance).
- **🧬 Hybrid Agents**: Combine complex code logic with declarative skills (e.g., `sentinel`).

### 📦 Default Agent Collective
The substrate ships with a pre-configured sets of "Immune Cells":
- **Sentinel**: The autonomous sensory heart.
- **Engineer**: The surgical auto-patcher.
- **Guardian**: The high-assurance integrity enforcer.
- **Herald**: The secure C2 and notification gateway.
- *...and more (see [AGENTS.md](docs/AGENTS.md))*

### 🦞 The Claw Ecosystem Bridge
Import 5,700+ skills from the [ClawHub](docs/CLAWS.md) ecosystem.
- **Safe Import**: Automatic translation from Claw formats to Tachyon plugins.
- **Quarantine Mode**: Imported agents are restricted by the Substrate Firewall until manually graduated.
- **Airlock Vetting**: Every import undergoes a 5-stage safety check (Translate -> Scan -> Sandbox -> Airlock -> Quarantine).

---

## 📁 Substrate Topology

The Tachyon Tongs filesystem is designed for high-assurance modularity:

```text
├── agents/             # The Immune Cell Collective (Pathogen, Sentinel, etc.)
├── daemons/            # macOS LaunchAgent & System Daemon configurations
├── docs/               # Architecture, ADRs, and API documentation
├── exploits/           # Master CATALOG.md and raw research payloads.
├── logs/               # ALERT.md, RUN_LOG.md, and EVOLUTION.md (Forensic ledgers).
├── memory/             # tachyon_state.db (Operational DB) and archive/ (Pruned logs).
├── policies/           # OPA-Rego policies and Enforcer configurations.
├── libs/               # Architecture-specific binaries (e.g., liboqs.dylib for PQC).
├── tests/              # Comprehensive regression suites (Functional & Adversarial).
```

---

## ⚡ Quick Start: The Herald Setup

Tachyon Tongs implements a high-assurance, defense-in-depth agentic architecture modeled after the autonomic immune system.

*   🏰 **Defense in Depth**: High-value administrative components (like the **Firewall Administrator**) are air-gapped from the network.
*   📡 **The Herald Proxy**: All external communication (Signal) is proxied through the Herald agent.
*   🏥 **Immune Response**: Specialized agents (Sentinel, Sentry, Healer, Engineer) collaborate to detect and remediate threats.

👉 **[AGENTIC_ARCHITECTURE.md](docs/AGENTIC_ARCHITECTURE.md)** — *Deep dive into the 6-tier taxonomy.*

---

## 🤖 The Agent Collective
*   🔭 **The Sentinel**: Discovers and signs novel AI exploits into the [EXPLOITATION_CATALOG.md](EXPLOITATION_CATALOG.md).
*   🧪 **The Sentry**: Unified active probing and passive semantic honeypotting for early intrusion detection.
*   🧬 **The Forge**: Adversarial architect generating synthetic zero-day scenarios and stress-testing substrate logic.
*   🦠 **The Pathogen**: Red-team mutation engine for autonomously evolving exploit variants to find bypasses.
*   🛠️ **The Engineer**: Self-synthesizes infrastructure patches and policy mutations.
*   ⚖️ **The Guardian**: Performs real-time forensic audits of the architectural substrate.
*   🏥 **The Healer**: Autonomous somatic repair and automated patch coordination.
*   📬 **The Herald**: Translates alerts into diplomatic dispatches delivered via Signal.

---

## 🦠 The OWASP Agentic Threat Hub (ASI01-ASI11)
The substrate is pre-loaded with an operational knowledge base of the **OWASP Top 10 for Agentic Applications (2026)**. Each playbook (`exploits/ASI*.md`) contains:
- **Official Descriptions**: The industry-standard definition of the threat.
- **Expert Synthesis**: Adversarial guidance aggregated from Claude, OpenAI, and Grok.
- **Adversarial Guides**: Actionable synthesis heuristics used by the Pathogen to mutate its attacks.
- **Defensive Matrix**: Precise mapping to substrate-level mitigations (Sentinel, Guardian, PEP).

---

## 🚦 Operational Maturity
Tachyon Tongs follows a tiered evolution path toward fully autonomous security governance:

*   🟢 **HITL (Human-In-The-Loop) - [CURRENT]**: Every mutation requires explicit human approval.
*   🟡 **HOTL (Human-On-The-Loop) - [EVOLVING]**: Low-risk patches apply automatically with a veto window.
*   🔴 **HOOTL (Human-Out-Of-The-Loop) - [VISION]**: Full autonomous detection and remediation.

---

## ⌨️ Command & Control: Event-Horizon Bridge
The **Event-Horizon Command Bridge** provides a NeoVIM-first interface for substrate oversight.

*   🧠 **Local Reasoning**: High-assurance offline reasoning via `llama.cpp` on M5.
*   🧱 **Singularity PDP**: High-assurance Policy Decision Point for LLM tool-calling.
*   📡 **Unified Console**: Composable `tt` CLI, GPU-accelerated TUI, and `tachyon.nvim`.

---

## 📚 Documentation Index
*   📖 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Core Daemon and Guardian Triad.
*   🧬 **[AGENTIC_ARCHITECTURE.md](docs/AGENTIC_ARCHITECTURE.md)**: Deep dive into the autonomic immune system design.
*   🧩 **[AGENTS.md](docs/AGENTS.md)**: The 6-tier agentic taxonomy and immune collective.
*   🎯 **[THREAT_MODEL.md](docs/THREAT_MODEL.md)**: Foundational Live Threat Model.
*   🔐 **[SDLC.md](docs/SDLC.md)**: Secure SDLC and Hardware-Anchored Trust.
*   🦞 **[CLAWS.md](docs/CLAWS.md)**: The Claw ecosystem and safe import bridge.
*   🗺️ **[ROADMAP.md](docs/ROADMAP.md)**: Phased evolution roadmap.
*   🔑 **[KEYS.md](docs/KEYS.md)**: Hybrid PQC key taxonomy.
*   📻 **[SYNC_LOG.md](SYNC_LOG.md)**: Inverse-chronological record of all agentic breakthroughs.
*   📋 **[TASKS.md](TASKS.md)**: Active engineering sprint backlog.
*   📜 **[ADRs](docs/adr/)**: Complete history of signed Architectural Decision Records.

---

## 🧪 Experiments: Autonomous Auto-Research

Tachyon Tongs serves as a laboratory for evaluating promising avenues in published AI security research (e.g., *Automated Design of Agentic Systems*, *The HyperAgent Principle*). We conduct autonomous ("auto research") experiments to find the next generation of substrate-level defenses.

*   🔭 **[Experiments Master Index](experiments/README.md)**: The central registry of all active and archived autonomous research strains.
    *   🧬 **[Darwin-Gödel Machine (DGM)](experiments/darwin_godel_machine/README.md)**: A self-referential evolutionary loop that uses a local MLX-native LLM to rewrite its own detection logic in response to synthesized adversarial pressure.
