# 🧬 Agent Onboarding Governance (ADR-0033)

**Objective**: Ensure that every new agent recruited into the Tachyon Tongs immune collective is professionally implemented, cryptographically anchored, and substrate-integrated.

---

### 🧪 The 5-Step Agent Onboarding Ritual

Every new agent project MUST complete the following steps before being marked as "Graduated" or "Operational" in the substrate roadmap.

#### 1. Implementation Layer
- **Standard Layout**: Every agent directory MUST include:
  - `agent.py`: Core logic inheriting from `BaseAgentPlugin`.
  - `config.yaml`: Standardized metadata (AgentID, PluginName).
- **Security Check**: Agent logic MUST utilize `BaseAgentPlugin` hooks for signed event emission.

#### 2. Verification Layer
- **Regression Suite**: Every agent MUST have a dedicated test file in `tests/` (e.g., `tests/test_immunologist.py`).
- **Pass Policy**: All agent-specific tests MUST pass with 100% fidelity before documentation occurs.

#### 3. Forensic Documentation Layer
- **Deep-Dive Guide**: Every agent MUST have a dedicated markdown guide in its `docs/` subdirectory (e.g., `agents/immunologist/docs/AGENT_IMMUNOLOGIST.md`).
- **Content Requirements**: The guide MUST detail:
  - **Overview**: Core purpose and threat mapping.
  - **Mechanics**: Triggers, EventBus subscriptions, and internal logic.
  - **Forensics**: Alert types and telemetry signatures.

#### 4. Topological Synchronization Layer
- **Primary README**: Add the agent to the "Agent Collective" section of the root [README.md](file:///Users/rds/antigravity/tachyon_tongs/README.md).
- **Master Directory**: Add the agent to the alphabetical directory in [docs/AGENTS.md](file:///Users/rds/antigravity/tachyon_tongs/docs/AGENTS.md).

#### 5. Forensic Ledger Update
- **SYNC_LOG Contribution**: Add a formal entry to [tasks/SYNC_LOG.md](file:///Users/rds/antigravity/tachyon_tongs/tasks/SYNC_LOG.md) documenting:
  - The objective of the recruitment.
  - The status [COMPLETE].
  - Detailed verification results (pytest summary).

---

> [!CAUTION]
> **Audit Failure**: Failure to complete the Onboarding Ritual for a new agent will be logged as a `GOVERNANCE_VIOLATION` in the substrate's high-priority alert hub.
