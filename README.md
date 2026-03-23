# 🌌 Tachyon Tongs: Multi-Agent Security Substrate

Tachyon Tongs is a high-performance, Apple Silicon-native security substrate. It protects autonomous agents by enforcing strict isolation, semantic intent gating, and active threat intelligence aggregation.

---

## 🛡️ Live Threat Model
Every architectural decision is mapped directly to a specific vector in the [THREAT_MODEL.md](docs/THREAT_MODEL.md).

*   🧠 **Semantic Intent Gating**: All tool requests are routed through a Policy Enforcement Point and evaluated by the **Singularity Meta-PDP**.
*   🧊 **Tiered Workload Isolation**: High-risk actions run in dynamically generated macOS `sandbox-exec` (Seatbelt) profiles.
*   🔐 **Forensic Integrity Gating**: Every substrate mutation is cryptographically signed using **Ed25519 + ML-DSA-65** hybrid sidecars.

---

## 💎 The Crown Jewels: Proactive Defense & Autoresearch
Tachyon Tongs is not just a reactive proxy; it is a **self-evolving security organism**.

*   🦠 **Pathogen (Proactive Adversarial Substrate)**: Every 24 hours, the Pathogen agent executes a full-spectrum adversarial sweep. It uses 11 authoritative **OWASP ASI Playbooks** (ASI01–ASI11) to synthesize and mutate hybrid attacks, ensuring the substrate's defenses stay ahead of emergent AI-native threats.
*   🔭 **Sentinel (Autonomous Intelligence Research)**: The Sentinel performs Karpathy-style "Autoresearch"—not just searching for CVEs, but autonomously browsing, synthesizing, and mapping novel vulnerabilities into high-signal "Adversarial Guidance" for the Pathogen.
*   🧬 **Adversarial Co-Evolution**: This continuous loop between the Sentinel (Discovery) and the Pathogen (Verification) creates a biological-grade immune response that hardens the substrate in real-time.

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

## 🗺️ Project Geography
The Tachyon Tongs substrate and its operational artifacts are organized for scale and forensic integrity:

| Directory | Purpose | Key Contents |
|-----------|---------|--------------|
| `agents/` | **Plugins** | Unified agent collective with colocated tests and docs. |
| `docs/` | **Knowledge** | ADRs, system architecture, and security threat models. |
| `exploits/` | **Intelligence** | Master `CATALOG.md` and raw research payloads. |
| `logs/` | **History** | `ALERT.md`, `RUN_LOG.md`, and `EVOLUTION.md` (Forensic ledgers). |
| `memory/` | **State** | `tachyon_state.db` (Operational DB) and `archive/` (Pruned logs). |
| `tests/` | **Verification** | Comprehensive regression suites (Functional & Adversarial). |
| `policies/` | **Guardrails** | OPA-Rego policies and Enforcer configurations. |
| `libs/` | **Support** | Architecture-specific binaries (e.g., `liboqs.dylib` for PQC). |

---

## 🏛️ Agentic Architecture: The Immune Collective
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
*   🎯 **[THREAT_MODEL.md](docs/THREAT_MODEL.md)**: Foundational Live Threat Model.
*   🗺️ **[ROADMAP.md](docs/ROADMAP.md)**: Phased evolution roadmap.
*   🔑 **[KEYS.md](docs/KEYS.md)**: Hybrid PQC key taxonomy.
*   📻 **[SYNC_LOG.md](SYNC_LOG.md)**: Inverse-chronological record of all agentic breakthroughs.
*   📋 **[TASKS.md](TASKS.md)**: Active engineering sprint backlog.
