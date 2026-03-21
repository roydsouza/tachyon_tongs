# 🤖 The Tachyon Tongs Agent Collective

This document serves as the central directory for all specialized agents operating within the Tachyon Tongs substrate. Each agent is a discrete "immune cell" designed for a specific defensive or offensive role.

## 🗂️ Agent Directory (Alphabetical)

- [**Auditor**](AGENT_AUDITOR.md): The Compliance Sentinel. Maps telemetry to security frameworks and generates signed attestations.
- **[Canary (The Sacrificial Scout)](AGENT_CANARY.md)**: Honeypot for high-risk payload validation and forensic capture.
- **[Engineer (The Automated Remediator)](AGENT_ENGINEER.md)**: Autonomous patch synthesis and recursive policy evolution.
- [**Forge**](AGENT_FORGE.md): The Adversarial Architect. Generates synthetic zero-day mutations for proactive stress-testing.
- **[Guardian (The Substrate Sentry)](AGENT_GUARDIAN.md)**: Substrate integrity verification via Merkle-trees and syscall monitoring.
- **[Horizon Scout (The Competitive Intel)](AGENT_SCOUT.md)**: Continuous web-scouring for external threat research and competitive moats.
- **[Pathogen (The Adversarial Adversary)](AGENT_PATHOGEN.md)**: Red-team mutation engine for stress-testing substrate resistance.
- **[Sentinel (The Immune System)](AGENT_SENTINEL.md)**: Proactive reconnaissance and autonomous vulnerability aggregation.
- **[Synthesizer (The Policy Architect)](AGENT_SYNTHESIZER.md)**: Translates analyzed threats into signed OPA-Rego or Cedar policies.

---

## 🏗️ Architectural Pattern
All agents in this collective follow the **Logical Separation** pattern established in ADR-0024:
1. **Skill (`SKILL.md`)**: Declarative intent and capability manifest.
2. **Role (`*_role.py`)**: Substrate-integrated execution layer (forensics, sanitization).
3. **Engine (`*_engine.py`)**: Core logic and specialized tools.

For a deeper dive into how these agents interact, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.
