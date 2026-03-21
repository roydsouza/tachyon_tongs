# 🌌 Tachyon Tongs: Multi-Agent Security Substrate

> [!IMPORTANT]
> **Development Status**: Tachyon Tongs is an **Agent Firewall Experimentation Lab** operating in **HITL (Human-In-The-Loop)** mode. It is a high-assurance substrate designed for protecting autonomous agent architectures via strict isolation and semantic intent gating.

Tachyon Tongs is a high-performance, Apple Silicon-native security substrate. It protects autonomous agents by enforcing strict isolation, semantic intent gating, and active threat intelligence aggregation.

---

## 🛡️ Live Threat Model
Every architectural decision is mapped directly to a specific vector in the [THREAT_MODEL.md](file:///Users/rds/antigravity/tachyon_tongs/THREAT_MODEL.md).

*   🧠 **Semantic Intent Gating**: All tool requests are routed through a Policy Enforcement Point and evaluated by the **Singularity Meta-PDP**.
*   🧊 **Tiered Workload Isolation**: High-risk actions run in dynamically generated macOS `sandbox-exec` (Seatbelt) profiles.
*   🔐 **Forensic Integrity Gating**: Every substrate mutation is cryptographically signed using **Ed25519 + ML-DSA-65** hybrid sidecars.

---

## 🔐 Secure SDLC: Hardware-Anchored Trust
Tachyon Tongs practices forensic security in its own development process. Every mutation is cryptographically signed and hardware-anchored.

*   🆔 **Hardware-Backed Signing**: Root keys live in the Apple **Secure Enclave** (Touch ID-gated, non-extractable).
*   ⚛️ **Hybrid Post-Quantum Cryptography**: Signatures use **Ed25519 + ML-DSA-65** (NIST FIPS 204, Level 3).
*   ⛓️ **Forensic ADR Chaining**: Every Architecture Decision Record references the hash of its predecessor, anchored to the Merkle root in `MANIFEST.json`.
*   🛃 **Airlock co-signing**: No artifact is deployed without dual signatures (proposing agent + Airlock).

👉 **[docs/SDLC.md](docs/SDLC.md)** — *The full Secure SDLC reference.*

---

## 🏛️ Agentic Architecture: The Immune Collective
Tachyon Tongs implements a high-assurance, defense-in-depth agentic architecture modeled after the autonomic immune system.

*   🏰 **Defense in Depth**: High-value administrative components (like the **Firewall Administrator**) are air-gapped from the network.
*   📡 **The Herald Proxy**: All external communication (Signal, Webhooks) is proxied through the Herald agent, ensuring no direct network exposure for the brain.
*   🏥 **Immune Response**: Specialized agents (Sentinel, Pathogen, Engineer) collaborate to detect, simulate, and remediate threats autonomously.
*   📼 **Immutable Forensics**: Every agent interaction creates a tamper-evident audit trail for post-facto decision reconstruction.

👉 **[AGENTIC_ARCHITECTURE.md](docs/AGENTIC_ARCHITECTURE.md)** — *Deep dive into the 6-tier taxonomy and trust boundaries.*

---

## 🤖 The Agent Collective
*   🔭 **The Sentinel**: Discovers and signs novel AI exploits into the [EXPLOITATION_CATALOG.md](file:///Users/rds/antigravity/tachyon_tongs/EXPLOITATION_CATALOG.md).
*   🧪 **The Pathogen**: Synthesizes mutated injection payloads to stress-test the substrate.
*   🦢 **The Canary**: Proactively scouts malicious endpoints in secure sandboxes.
*   🛠️ **The Engineer**: Self-synthesizes infrastructure patches and policy mutations.
*   ⚖️ **The Guardian**: Performs real-time forensic audits of the architectural substrate.
*   📬 **The Herald**: Translates alerts into diplomatic dispatches delivered via Signal.

---

## 🚦 Operational Maturity
Tachyon Tongs follows a tiered evolution path toward fully autonomous security governance:

*   🟢 **HITL (Human-In-The-Loop) - [CURRENT]**: Every mutation requires explicit human approval in the **Airlock**.
*   🟡 **HOTL (Human-On-The-Loop) - [EVOLVING]**: The substrate autonomously applies low-risk patches with a reversibility window.
*   🔴 **HOOTL (Human-Out-Of-The-Loop) - [VISION]**: Full autonomous detection, synthesis, and remediation.

---

## ⌨️ Command & Control: Event-Horizon Bridge
The **Event-Horizon Command Bridge** provides a NeoVIM-first, CLI-forward interface for substrate oversight.

*   🧠 **Local Reasoning**: High-assurance offline reasoning via `llama.cpp` on M5.
*   🧱 **Singularity PDP**: High-assurance Policy Decision Point for LLM tool-calling.
*   📡 **Unified Console**: Composable `tt` CLI, GPU-accelerated TUI, and `tachyon.nvim` Lua plugin.

👉 **[ADMIN_CLI_NEOVIM.md](ADMIN_CLI_NEOVIM.md)** — *Full operator reference.*

---

## ⚡ Quickstart & Commands
```bash
# Initialize and Install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && pip install -e .
./scripts/start_opa.sh

# Run Substrate Audit
tt audit status
```

*   `/help`: View the command manifest.
*   `/catalog`: View the Exploitation Catalog.
*   `/airlock`: Manage the patch staging area.
*   `/sentinel`: Trigger a threat sweep.
*   `/report`: Generate a substrate health report.

---

## 📚 Documentation Index
*   📖 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Core Daemon and Guardian Triad.
*   🎯 **[THREAT_MODEL.md](docs/THREAT_MODEL.md)**: Foundational Live Threat Model.
*   🗺️ **[ROADMAP.md](docs/ROADMAP.md)**: Phased evolution roadmap.
*   🔑 **[KEYS.md](docs/KEYS.md)**: Hybrid PQC key taxonomy.
*   📻 **[SYNC_LOG.md](SYNC_LOG.md)**: Inverse-chronological record of all agentic breakthroughs.
