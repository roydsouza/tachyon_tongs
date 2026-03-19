# Tachyon Tongs: Multi-Agent Security Substrate

> [!WARNING]
> **Agent Firewall Experimentation Lab**: This project is currently in **HEAVY DEVELOPMENT** and is intended for **EXPERIMENTATION ONLY**. It is **NOT READY FOR PRODUCTION DEPLOYMENT**. 
> We are currently operating in **HITL (Human-In-The-Loop) Mode**, where all autonomous mutations and high-risk actions require manual operator authorization.

Tachyon Tongs is a high-performance, Apple Silicon-optimized security substrate and AI firewall designed to protect autonomous agent architectures. By enforcing strict isolation, semantic intent gating, and active threat intelligence aggregation, Tachyon Tongs ensures that autonomous execution pipelines remain resilient against adversarial manipulation.

## 0. Roadmap to Autonomy (Operational Modes)

Tachyon Tongs follows a tiered evolution path toward fully autonomous security governance:

1.  **HITL (Human-In-The-Loop) - [CURRENT]**: Every proposed substrate mutation or security patch is staged in the **Airlock** and requires explicit human approval via the `airlock_cli.py` or Dashboard. This mode prioritizes safety and "Ground Truth" collection over pure speed.
2.  **HOTL (Human-On-The-Loop) - [PLANNED]**: Transition to "experimental deployment" where the substrate autonomously applies low-risk patches with a mandatory reversibility window (e.g., 72 hours). Humans move to a supervisory role, monitoring for anomalous drift in the "Command Center."
3.  **HOOTL (Human-Out-Of-The-Loop) - [VISION]**: Broad deployment state. Full autonomous detection, synthesis, and remediation with provable security via formal verification and immutable Merkle-chain logging. Humans shift to periodic strategic policy governance.


## 1. Problem Statement

Autonomous AI agents introduce critical new attack surfaces to organizational infrastructure:
*   **Prompt Injection & Agent Hijacking:** Untrusted external inputs (e.g., scraped websites, API payloads) can contain hidden steganographic or indirect instructions that override the agent's core system prompt.
*   **Memory Poisoning:** Adversarial payloads can lie dormant in vector databases, executing as a delayed trojan horse upon future retrieval.
*   **Zero-Day Threat Velocity:** The rapid publication of new offensive ML techniques makes static, hardcoded defensive measures obsolete almost instantly.

## 2. Threat-Model-Driven Design

Tachyon Tongs is not merely a collection of security features; it is an implementation of a **Live Threat Model**. 

> [!IMPORTANT]
> **The Threat Model is Primary**: All architectural decisions, autonomous patches, and operator interventions are driven by the [THREAT_MODEL.md](file:///Users/rds/antigravity/tachyon_tongs/THREAT_MODEL.md). It serves as the project's single source of security truth, ensuring that the implementation remains in lock-step with the adversarial landscape.

Every mitigation in this substrate—from ADR-signed forensic baselines to the Guardian Triad—mapped directly to a specific vector in the Threat Model. Our governance follows the **ACDC-Loop (Agent-Centric Development Cycle)**, where every code change begins with an update to the threat landscape.

*   **Semantic Intent Gating (PDP/PEP):** All outbound network and system tool requests are routed through a Policy Enforcement Point ([event_horizon](file:///Users/rds/antigravity/event_horizon)). Requests are evaluated against declarative `.rego` policies by the Policy Decision Point ([singularity](file:///Users/rds/antigravity/singularity)) that enforce strict capability boundaries.
*   **Tiered Workload Isolation:** High-risk actions are isolated execution environments. "Tier 0" workloads run under dynamically generated macOS `sandbox-exec` (Seatbelt) profiles, allowing native computation speeds with microsecond overhead, while preventing unauthorized network or filesystem access.
*   **Inbound Protection (Threat Mitigation)**: A three-stage pipeline (Scout, Analyst, Engineer) that harvests, analyzes, and mitigates agentic exploits.
*   **Bi-Directional Capability Firewall**: Zero-Trust tool access via OPA (Rego) and Cedar policy federation.
- **Substrate-Aware Model Routing**: Autonomous token management routing between Flash/Local and Pro substrates based on intent complexity.
- **Pathogen Adversarial Tuning**: Generational mutation engine for continuous defense validation.
*   **Sentinel Harvest Mode**: Autonomous localization of raw exploit payloads to a local "data lake" for amortized discovery and policy synthesis.
*   **Pluggable Governance (PDP/PEP)**: Separation of Policy Decision Points (supporting Rego and Cedar) from Policy Enforcement Points at the edges.
*   **Security Evolution Ledger (Guardian IDS)**: A cryptographically signed hybrid signature chain (Internal JSON + External .sig) that tracks substrate mutations. 
*   **Merkle Anchoring**: A cumulative Merkle Root in `docs/adr/MANIFEST.json` ensuring the entire architectural substrate is tamper-proof against repository-level compromises.
*   **Apple Silicon Native**: Optimized for Metal-accelerated reasoning and Seatbelt sandboxing.
*   **Supply Chain Integrity Gating (Phase 11):** Tachyon Tongs implements a multi-layered defense against library-based attacks:
    *   **Hallucination Squatting Defense**: Blocks agents from installing/using "imagined" malicious packages via **Deterministic Capability Binding**.
    *   **Real-Time Auditing**: The **Integrity Agent** performs on-the-fly `pip-audit` scans of all proposed library intents.
    *   **Cryptographic Provenance**: All trusted libraries are validated against a local state registry.
    *   Detailed documentation: [SUPPLY_CHAIN_SECURITY.md](docs/SUPPLY_CHAIN_SECURITY.md).

## 3. Evolutionary Architecture: Sentinel & Pathogen

Tachyon Tongs is not a static defense system; it is an evolutionary loop driven by two built-in, autonomous agents:

*   **The Sentinel (Blue Team):** A continuously running threat intelligence aggregator. It polls the National Vulnerability Database (NVD API v2), GitHub Advisories GraphQL, and the arXiv Research Pulsar to discover novel AI exploits. Validated threats are cryptographically signed to prevent offline tampering and atomically committed to a SQLite-backed `StateManager`, which automatically generates the `EXPLOITATION_CATALOG.md`—the global master ledger of adversarial tactics.
*   **The Pathogen (Red Team):** Triggered asynchronously via macOS `launchd`, the Pathogen agent reads the `EXPLOITATION_CATALOG.md` synthesized by the Sentinel. Using declarative capabilities defined in its `SKILL.md` manifest, the Pathogen acts as an automated adversary, synthesizing mutated injection payloads and firing them against the Tachyon Substrate to ensure regressions do not occur and that semantic boundaries hold firm.
*   **The Zero-Day Simulator:** Powered by `scripts/zero_day_drill.py`, this continuous fuzzer harnesses the Pathogen agent to generate novel, entirely un-cataloged prompt attacks. It fires them against the local daemon, validating the abstract resilience of the architecture and exporting metrics to `docs/zero_day_drills.md`.

## 4. Protection Deployment Models

Tachyon Tongs supports multiple topologies for securing agent workloads:

### A. In-Band Agents (Managed)
Agents that are natively managed by the Tachyon Tongs Substrate. They are defined purely by a declarative `SKILL.md` manifest (e.g., Pathogen). The Substrate dynamically provisions their sandbox, injects their allowed tools, and monitors their execution lifecycle using the internal Python abstractions and SQLite `StateManager`.

### B. Out-of-Band Agents (Proxied)
Independent agents and applications (e.g., multi-repo agents like `entropy_dashboard` or `shors_reaper`) running in their own binaries or environments local to the machine. These agents utilize the `tachyon_client` to route their operations through the Substrate Proxy Daemon, benefiting from the Triad Pipeline and OPA Gating without having their core logic modified.

### C. Standard Protocol Agents (MCP)
Tachyon Tongs implements the **Model Context Protocol (MCP)**. External agents (e.g., Claude Desktop, IDE extensions) can connect directly to `tachyon/protocol/mcp.py` via `stdio`. This allows standard agents to discover and execute `tachyon_safe_fetch` and `tachyon_safe_execute` as native tools, with all substrate security logic applied transparently. All proposed modifications are subject to the **Scalable Oversight (Airlock Debate)** protocol.

### D. Off-Machine Fleet (Planned phase)
Future iterations will transition the local daemon to a cloud-native architecture.
*   **Matchlock (Planned):** Will provide cryptographic workload identity and secrets management for agents.
*   **Tailscale (Planned):** Will establish an encrypted RPC mesh, allowing disparate "Out-of-Band" agents across physical machines to safely utilize a centralized cloud Tachyon Substrate.

- **HOOTL (Human-Out-Of-The-Loop)**: *Target*. Full autonomous self-healing substrate with high-fidelity immutable logging.

## 7. Forensic Debate Monitoring

Tachyon Tongs provides a unique "Adversarial Audit" capability. Use the `debates/` directory to monitor the real-time discourse between the **Engineer**, **Skeptic**, and **Meta-Critic**. 

- **Visibility**: Every autonomous patch is debated by specialized agents before reaching the Airlock.
- **Humorous Oversight**: These debates are recorded in witty, high-fidelity markdown, making security audits both informative and engaging. 
- **The Heartbeat**: Even when idle, the Triad provides "Heartbeat Banter" to confirm oversight availability.

## 7. Architectural Justifications

*   **Apple Silicon Native vs. Docker/Lima:** By leveraging macOS `sandbox-exec` profiles and `mlx_lm` bindings, Tachyon Tongs achieves bare-metal GPU/NPU acceleration and millisecond startup latency, avoiding the resource overhead and cold-starts associated with virtualizing Linux under Lima or Docker.
*   **OPA over Python Logic:** Decoupling security logic into declarative Rego modules allows security engineers to audit payload scopes without parsing application code.
*   **SQLite WAL over Markdown:** Transitioning from direct markdown file appends to a SQLite Write-Ahead Log (WAL) ensures atomic, non-corruptible writes during high-concurrency multi-agent traffic spikes.

## 8. Quickstart Guide (macOS Apple Silicon)

### Installation
Ensure Python 3.10+ and a local checkout of the repository.

```bash
# Initialize the Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies (includes OPA, Pytest, and MLX frameworks)
pip install -r requirements.txt
pip install -e . --break-system-packages # Register the tachyon package
./scripts/start_opa.sh
```

### Running an In-Band Agent
In-Band agents are declared in the `agents/` directory. You can trigger the Pathogen Red Team via the CLI:

```bash
python3 scripts/run_pathogen.py
```

*Suggestion:* Consider building complementary In-Band agents for log auditing, automated code-review, or internal CI/CD sanitation by dropping a new folder and `SKILL.md` into `agents/`.

### Integrating an Out-of-Band Agent
For independent applications, import the Tachyon Client to proxy unsafe fetches and command executions through the protective daemon.

```python
from tachyon.enforcement import safe_fetch

# The Substrate Daemon evaluates the request against the OPA gateway
response = safe_fetch("https://untrusted-api.com/data", agent_id="MyExternalAgent")
print(response.get("content"))
```

*Suggestion:* Out-of-Band protection is ideal for any independent agent, from Financial Modeling assistants that scrape the open web to Bioinformatics processors parsing high-throughput, third-party datasets.

## 7. Further Reading

*   **[CONTENTS.md](CONTENTS.md):** The comprehensive index of all documentation, configurations, and core scripts.
*   **[ARCHITECTURE.md](docs/ARCHITECTURE.md):** Deep technical dive into the Guardian Triad, OPA Rego policies, Apple Sandbox profiles, and MLX inference loops.
*   **[DEPLOYMENT.md](docs/DEPLOYMENT.md):** The Builder's Guide for constructing In-Band and Out-of-Band agents, with template structures and capability whitelisting rules.
*   **[THREAT_MODEL.md](THREAT_MODEL.md):** Comprehensive analysis of Inbound (Hijacking/Injection) and Outbound (DLP) threat vectors and mitigations.
*   **[PHASE_10_STATUS.md](docs/PHASE_10_STATUS.md):** Current progress on Automated Competitive Intelligence.
## ⚡ Slash Commands (The Operator Interface)
Tachyon Tongs supports explicit control via standardized slash commands, allowing you to bypass manual file lookups:
- `/help`: View the command manifest.
- `/catalog`: View the Exploitation Catalog.
- `/sentinel`: Trigger a threat sweep.
- `/report`: Generate a substrate health report.
- `/acdc-loop`: Start a high-assurance development cycle.
