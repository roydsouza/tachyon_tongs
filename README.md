# Tachyon Tongs: Multi-Agent Security Substrate

> [!IMPORTANT]
> **Development Status**: Tachyon Tongs is under heavy active development and operates as an **Agent Firewall Experimentation Lab** in **HITL (Human-In-The-Loop)** mode. It is **not yet production-ready**. All autonomous mutations require explicit human approval via the Airlock.

Tachyon Tongs is a high-performance, Apple Silicon-native security substrate and AI firewall. It is designed to protect autonomous agent architectures by enforcing strict isolation, semantic intent gating, and active threat intelligence aggregation.

## 1. Problem Statement

Autonomous AI agents introduce critical new attack surfaces to organizational infrastructure:
*   **Prompt Injection & Agent Hijacking**: Untrusted external inputs (scraped websites, API payloads) can contain steganographic instructions that override the agent's core system prompt.
*   **Capability Over-Reach**: Agents with broad tool access (filesystem, network, shell) lack a centralized "Least Privilege" enforcement point, allowing minor prompts to escalate into major infrastructure breaches.
*   **Zero-Day Threat Velocity**: The rapid evolution of offensive ML techniques makes static, hardcoded defensive measures obsolete almost instantly.

## 2. Threat-Model-Driven Design

Tachyon Tongs is an implementation of a **Live Threat Model**. Every architectural decision is mapped directly to a specific vector in the [THREAT_MODEL.md](file:///Users/rds/antigravity/tachyon_tongs/THREAT_MODEL.md).

*   **Semantic Intent Gating (PDP/PEP)**: All tool requests are routed through a Policy Enforcement Point and evaluated by the **Singularity Meta-PDP** against declarative OPA (Rego) and Cedar policies.
*   **Tiered Workload Isolation**: High-risk actions run in dynamically generated macOS `sandbox-exec` (Seatbelt) profiles, providing bare-metal speed with microsecond overhead and strict resource lockdown.
*   **Forensic Integrity Gating**: Every substrate mutation is cryptographically signed using high-assurance HMAC-SHA256 sidecars and anchored to a cumulative Merkle root in the `MANIFEST.json`.

## 3. Evolutionary Architecture

Tachyon Tongs is not a static defense system; it is an autonomic immune system driven by five modular roles:

*   **The Sentinel (Blue Team)**: Continuously polls the NVD, GitHub Advisories, and arXiv to discover and sign novel AI exploits into the [EXPLOITATION_CATALOG.md](file:///Users/rds/antigravity/tachyon_tongs/EXPLOITATION_CATALOG.md).
*   **The Pathogen (Red Team)**: Synthesizes mutated injection payloads to stress-test the substrate and ensure zero regressions against the cataloged threat landscape.
*   **The Canary (Honeypot)**: Proactively scouts malicious endpoints in a secure sandbox, logging intelligence to [CANARY_LOG.md](file:///Users/rds/antigravity/tachyon_tongs/CANARY_LOG.md).
*   **The Engineer (Autopatcher)**: Self-synthesizes infrastructure patches and policy mutations to neutralize detected threats in response to the Canary's intelligence.
*   **The Guardian (Auditor)**: Performs periodic forensic audits of the architectural substrate, ensuring HMAC signatures and Merkle roots remain untampered.

## 🤖 The Agent Collective

Tachyon Tongs is powered by a diverse set of specialized agents, each following the **Logical Separation** pattern. For a detailed breakdown of every agent's capabilities, operational mechanics, and integration points, see:

👉 **[AGENTS.md](docs/AGENTS.md)** — *The central directory for the Tachyon Tongs immune system.*

## 4. Deployment Models

*   **In-Band (Managed)**: Agents declared purely via `SKILL.md` manifests, running within substrate-provisioned sandboxes.
*   **Out-of-Band (Proxied)**: Independent local applications using the `tachyon_client` to route tool requests through the secure proxy.
*   **Standard Protocol (MCP)**: Implements the **Model Context Protocol**. Standards-compliant agents (Claude, IDEs) can discover and use Tachyon tools via `stdio`.

## 5. Forensic Debate Monitoring

Tachyon Tongs employs **Scalable Oversight** via the **Airlock Debate Triad**. Every autonomous patch proposed by the Engineer is debated by a **Skeptic** and a **Meta-Critic** before reaching the operator.
- **Visibility**: Monitor real-time adversarial discourse in the `memory/operational/debates/` directory.
- **Humorous Oversight**: Debates are recorded in high-fidelity markdown, making security audits both informative and engaging.

## 6. Architectural Justifications

*   **Apple Silicon Native**: Leveraging macOS `sandbox-exec` and Metal-accelerated reasoning (`mlx_lm`) avoids the resource overhead and latency of virtualization (Docker/Lima).
*   **Declarative Policy (OPA/Rego)**: Decoupling security logic from application code allows for transparent third-party auditing without parsing Python.
*   **SQLite WAL over Filesystem**: Using a Write-Ahead Log for state management ensures atomic, non-corruptible writes during multi-agent concurrency.

## 7. Roadmap to Autonomy (Operational Modes)

Tachyon Tongs follows a tiered evolution path toward fully autonomous security governance:

1.  **HITL (Human-In-The-Loop) - [CURRENT]**: Every mutation requires explicit human approval in the **Airlock** via `airlock-approve` or the Dashboard.
2.  **HOTL (Human-On-The-Loop) - [PHASE 22]**: The substrate autonomously applies low-risk patches with a mandatory reversibility window. Humans move to a supervisory monitoring role.
3.  **HOOTL (Human-Out-Of-The-Loop) - [VISION]**: Full autonomous detection, synthesis, and remediation with formal verification. Humans shift to strategic policy governance.

## 8. Quickstart Guide

```bash
# Initialize and Install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -e .  # Register substrate
./scripts/start_opa.sh

# Run the Substrate Controller
python3 -m tachyon.main --role guardian --action verify_substrate
```

## 🧬 Phase 22: Autonomic Immune Response [ACTIVE]
The **Evolutionary Substrate** is live. Phase 22 introduces the **ImmuneManager**, an autonomic immune system that detects defensive gaps via the **Canary** and self-synthesizes high-assurance policy updates. The substrate is now self-healing — proposed patches are staged in the **Airlock** for HITL oversight before deployment.

## ⚡ Slash Commands
- `/help`: View the command manifest.
- `/catalog`: View the Exploitation Catalog.
- `/airlock`: Manage the patch staging area.
- `/sentinel`: Trigger a threat sweep.
- `/report`: Generate a substrate health report.
