# Tachyon Tongs: Multi-Agent Security Substrate

Tachyon Tongs is a high-performance, Apple Silicon-optimized security substrate and AI firewall designed to protect autonomous agent architectures. By enforcing strict isolation, semantic intent gating, and active threat intelligence aggregation, Tachyon Tongs ensures that autonomous execution pipelines remain resilient against adversarial manipulation.

## 1. Problem Statement

Autonomous AI agents introduce critical new attack surfaces to organizational infrastructure:
*   **Prompt Injection & Agent Hijacking:** Untrusted external inputs (e.g., scraped websites, API payloads) can contain hidden steganographic or indirect instructions that override the agent's core system prompt.
*   **Memory Poisoning:** Adversarial payloads can lie dormant in vector databases, executing as a delayed trojan horse upon future retrieval.
*   **Zero-Day Threat Velocity:** The rapid publication of new offensive ML techniques makes static, hardcoded defensive measures obsolete almost instantly.

## 2. The Tachyon Tongs Solution

Tachyon Tongs addresses these vulnerabilities by acting as a mandatory proxy daemon (`substrate_daemon.py`) for all agent actions. Rather than relying on agent self-regulation, Tachyon Tongs implements a defense-in-depth pipeline:

*   **Semantic Intent Gating (OPA):** All outbound network and system tool requests are routed through a local Open Policy Agent (OPA). Requests are evaluated against declarative `.rego` policies that enforce strict capability boundaries.
*   **Tiered Workload Isolation:** High-risk actions are isolated execution environments. "Tier 0" workloads run under dynamically generated macOS `sandbox-exec` (Seatbelt) profiles, allowing native computation speeds with microsecond overhead, while preventing unauthorized network or filesystem access.
*   **The Guardian Triad:** Untrusted web payloads are processed by an air-gapped Triad architecture:
    1.  **Scout:** Fetches raw data within constrained routing rules.
    2.  **Analyst/Sanitizer:** Strips zero-width steganography and executes local, Metal-accelerated MLX inference models (e.g., Llama 3.2 4-bit) to detect injection vectors.
    3.  **Engineer:** Finalizes the sanitized, cryptographically bounded output for safe consumption by the requesting agent.

## 3. Evolutionary Architecture: Sentinel & Pathogen

Tachyon Tongs is not a static defense system; it is an evolutionary loop driven by two built-in, autonomous agents:

*   **The Sentinel (Blue Team):** A continuously running threat intelligence aggregator. It polls the National Vulnerability Database (NVD API v2), GitHub Advisories GraphQL, and the arXiv Research Pulsar to discover novel AI exploits. Validated threats are atomically committed to a SQLite-backed `StateManager`, which automatically generates the `EXPLOITATION_CATALOG.md`—the global master ledger of adversarial tactics.
*   **The Pathogen (Red Team):** Triggered asynchronously via macOS `launchd`, the Pathogen agent reads the `EXPLOITATION_CATALOG.md` synthesized by the Sentinel. Using declarative capabilities defined in its `SKILL.md` manifest, the Pathogen acts as an automated adversary, synthesizing mutated injection payloads and firing them against the Tachyon Substrate to ensure regressions do not occur and that semantic boundaries hold firm.

## 4. Protection Deployment Models

Tachyon Tongs supports multiple topologies for securing agent workloads:

### A. In-Band Agents (Managed)
Agents that are natively managed by the Tachyon Tongs Substrate. They are defined purely by a declarative `SKILL.md` manifest (e.g., Pathogen). The Substrate dynamically provisions their sandbox, injects their allowed tools, and monitors their execution lifecycle using the internal Python abstractions and SQLite `StateManager`.

### B. Out-of-Band Agents (Proxied)
Independent agents and applications (e.g., multi-repo agents like `entropy_dashboard` or `shors_reaper`) running in their own binaries or environments local to the machine. These agents utilize the `tachyon_client` to route their operations through the Substrate Proxy Daemon, benefiting from the Triad Pipeline and OPA Gating without having their core logic modified.

### C. Off-Machine Fleet (Planned phase)
Future iterations will transition the local daemon to a cloud-native architecture.
*   **Matchlock (Planned):** Will provide cryptographic workload identity and secrets management for agents.
*   **Tailscale (Planned):** Will establish an encrypted RPC mesh, allowing disparate "Out-of-Band" agents across physical machines to safely utilize a centralized cloud Tachyon Substrate.

## 5. Architectural Justifications

*   **Apple Silicon Native vs. Docker/Lima:** By leveraging macOS `sandbox-exec` profiles and `mlx_lm` bindings, Tachyon Tongs achieves bare-metal GPU/NPU acceleration and millisecond startup latency, avoiding the resource overhead and cold-starts associated with virtualizing Linux under Lima or Docker.
*   **OPA over Python Logic:** Decoupling security logic into declarative Rego modules allows security engineers to audit payload scopes without parsing application code.
*   **SQLite WAL over Markdown:** Transitioning from direct markdown file appends to a SQLite Write-Ahead Log (WAL) ensures atomic, non-corruptible writes during high-concurrency multi-agent traffic spikes.

## 6. Quickstart Guide (macOS Apple Silicon)

### Installation
Ensure Python 3.10+ and a local checkout of the repository.

```bash
# Initialize the Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies (includes OPA, Pytest, and MLX frameworks)
pip install -r requirements.txt
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
from src.tachyon_client import safe_fetch

# The Substrate Daemon evaluates the request against the OPA gateway
response = safe_fetch("https://untrusted-api.com/data", agent_id="MyExternalAgent")
print(response.get("content"))
```

*Suggestion:* Out-of-Band protection is ideal for any independent agent, from Financial Modeling assistants that scrape the open web to Bioinformatics processors parsing high-throughput, third-party datasets.

## 7. Further Reading

*   **[CONTENTS.md](CONTENTS.md):** The comprehensive index of all documentation, configurations, and core scripts.
*   **[ARCHITECTURE.md](docs/ARCHITECTURE.md):** Deep technical dive into the Guardian Triad, OPA Rego policies, Apple Sandbox profiles, and MLX inference loops.
*   **[DEPLOYMENT.md](docs/DEPLOYMENT.md):** The Builder's Guide for constructing In-Band and Out-of-Band agents, with template structures and capability whitelisting rules.
