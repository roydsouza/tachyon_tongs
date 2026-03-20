# 🧬 Sentinel Autonomic Identity (Threat Monitoring)

## Intent
To serve as the "Immune System" for the Tachyon Tongs substrate. The Sentinel autonomously aggregates, analyzes, and mitigates agentic exploits by polling high-fidelity threat intelligence sources and synthesizing protective policies.

## 🛠️ Capabilities & Configuration
The Sentinel is configured via the following declarative parameters:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `scraping_interval_hours` | 24 | Frequency of NVD/GitHub advisory sweeps. |
| `relevance_threshold` | 0.7 | Minimum score for the Analyst to promote a threat to the Engineer. |
| `harvest_mode` | true | Automatically localize raw exploit payloads to `intelligence/exploits/`. |
| `keywords` | ["LLM", "Prompt Injection", "Agent", "LangChain"] | Targeted terms for the exact-match scraper. |

## 🛡️ Operational Protocols

### 1. The Reactive Remediation Sweep
Before starting a new intelligence fetch, the Sentinel must:
- Scan `EXPLOITS.md` for any unresolved `🔴` or `🟠` threats.
- Trigger the **Engineer Agent** to prioritize these backlog items.

### 2. Autonomous Policy Synthesis
Upon discovering a CRITICAL threat:
- Extract domain indicators and attack patterns.
- Synthesize **Rego** and **Cedar** policies using the `PolicySynthesizer` agents.
- Stage the policies for deployment via the `SingularityPDP`.

## 📜 Constraints
- **Isolation:** The Scout node must remain network-isolated from the primary agent memory context.
- **Integrity:** All discovered threats must be cryptographically signed before being committed to the `Exploitation Catalog`.
- **Fail-Loud:** Any failure in the Triad pipeline must be logged immediately to `ALERT.md`.

## 🛠️ Substrate Registration
- **Agent ID:** `sentinel-v1`
- **Managed Mode:** `Hybrid` (Deterministic core + Declarative config)
