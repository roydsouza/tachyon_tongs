# ADR-0079: Governance: Agent Onboarding Ritual

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: As the Tachyon Tongs agent collective expands, the risk of documentation drift and architectural fragmentation increases. New agents must be recruited with high-assurance standards to maintain the project's forensic integrity and topological consistency.

---

## 🧭 Decision

We formally expand the **Agent Plugin Architecture (ADR-0033)** to include a mandatory **5-step Agent Onboarding Ritual**.

### 1. The 5-Step Process
1. **Implementation**: Mandatory `agent.py` (logic) and `config.yaml` (metadata).
2. **Verification**: Dedicated `pytest` regression suite with 100% pass rate.
3. **Forensic Documentation**: A deep-dive guide in the agent's `docs/` directory (`AGENT_*.md`).
4. **Topological Sync**: Registration in the root `README.md` and `docs/AGENTS.md`.
5. **Forensic Ledger Contribution**: A formal SYNC_LOG entry with verification results.

### 2. Governance Rule
- Codify this ritual as a substrate rule in `.agent/rules/AGENT_GOVERNANCE.md`.
- Implement a `/add-agent` workflow in `.agent/workflows/` to automate template generation and re-signing.

---

## 🧬 Consequences

### ✅ Positive
- **Auditable Collective**: 100% of agents are professionally documented and topologically integrated.
- **Onboarding Speed**: Standards-based recruitment reduces the time to operationalize new defensive or offensive agents.

### ⚠️ Negative
- **Onboarding Overhead**: Increases the initial labor required to recruit a new agent by ~20%.
- **Rigidity**: Highly experimental agents must still fulfill the documentation mandate before substrate graduation.

---

## 🛠️ Performance Mandate
- The `/add-agent` workflow MUST be discoverable and slash-commandable.
- All documents generated in the ritual MUST be PQC-signed via `resign_docs.py`.
