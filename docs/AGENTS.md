# 🤖 The Tachyon Tongs Agent Collective

This document serves as the central directory for all specialized agents operating within the Tachyon Tongs substrate. Each agent is a discrete "immune cell" designed for a specific defensive or offensive role.

## 🗂️ Agent Directory (Alphabetical)

- [**Administrator (The Firewall Admin)**](../agents/code-only/administrator/docs/AGENT_ADMINISTRATOR.md): The Thinker. Always-on LLM agent that reasons over traffic logs and governs substrate capabilities.
- [**Auditor**](../agents/code-only/guardian/docs/AGENT_AUDITOR.md): The Compliance Sentinel. Maps telemetry to security frameworks and generates signed attestations.
- **[Canary (The Sacrificial Scout)](../agents/code-only/canary/docs/AGENT_CANARY.md)**: Honeypot for high-risk payload validation and forensic capture.
- **[Engineer (The Automated Remediator)](../agents/code-only/engineer/docs/AGENT_ENGINEER.md)**: Autonomous patch synthesis and recursive policy evolution.
- [**Forge**](../agents/code-only/engineer/docs/AGENT_FORGE.md): The Adversarial Architect. Generates synthetic zero-day mutations for proactive stress-testing.
- **[Guardian (The Substrate Sentry)](../agents/code-only/guardian/docs/AGENT_GUARDIAN.md)**: Substrate integrity verification via Merkle-trees and syscall monitoring.
- **[Herald (The Command Conduit)](../agents/code-only/herald/docs/AGENT_HERALD.md)**: The Mouth & Ear. Custom agent that aggregates notifications and manages NeoVIM/CLI state.
- **[Horizon Scout (The Competitive Intel)](../agents/code-only/scout/docs/AGENT_SCOUT.md)**: Continuous web-scouring for external threat research and competitive moats.
- **[Pathogen (The Adversarial Adversary)](../agents/code-only/pathogen/docs/AGENT_PATHOGEN.md)**: Red-team mutation engine for stress-testing substrate resistance.
- **[Sentinel (The Immune System)](../agents/hybrid/sentinel/docs/AGENT_SENTINEL.md)**: Proactive reconnaissance and autonomous vulnerability aggregation.
- **[Synthesizer (The Policy Architect)](../agents/code-only/synthesizer/docs/AGENT_SYNTHESIZER.md)**: Translates analyzed threats into signed OPA-Rego or Cedar policies.

---

## 🏗️ Architectural Pattern
All agents in this collective follow the **Logical Separation** pattern established in ADR-0024:
1. **Skill (`SKILL.md`)**: Declarative intent and capability manifest.
2. **Role (`*_role.py`)**: Substrate-integrated execution layer (forensics, sanitization).
3. **Engine (`*_engine.py`)**: Core logic and specialized tools.

For a deeper dive into how these agents interact, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.
