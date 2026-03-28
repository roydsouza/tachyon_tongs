---
description: Add and document a new agent to the Tachyon Tongs collective.
---

# /add-agent: The Agent Onboarding Ritual

Follow these steps to recruit and document a new agent in the Tachyon Tongs substrate.

### 1. Implementation
- [ ] Create `agents/<agent_name>/agent.py`.
- [ ] Create `agents/<agent_name>/config.yaml`.
- [ ] Implement `execute_action` and `subscribe` logic.

### 2. Verification (TDAD)
- [ ] Create `tests/test_<agent_name>.py`.
// turbo
- [ ] Run `PYTHONPATH=. pytest -v tests/test_<agent_name>.py`.
- [ ] Ensure 100% pass rate.

### 3. Forensic Documentation
- [ ] Create `agents/<agent_name>/docs/AGENT_<AGENT_NAME>.md`.
- [ ] Detail the agent's Overview, Mechanics, and Telemetry signatures.

### 4. Topological Synchronization
- [ ] Update §112 of [README.md](file:///Users/rds/antigravity/tachyon_tongs/README.md).
- [ ] Update the directory in [docs/AGENTS.md](file:///Users/rds/antigravity/tachyon_tongs/docs/AGENTS.md).

### 5. Forensic Ledger Contribution
- [ ] Add a formal entry to [tasks/SYNC_LOG.md](file:///Users/rds/antigravity/tachyon_tongs/tasks/SYNC_LOG.md).
- [ ] Summarize the implementation, status [COMPLETE], and test results.

### 6. Substrate Re-signing
// turbo
- [ ] Run `python3 scripts/forensics/resign_docs.py agents/<agent_name>/docs/AGENT_<AGENT_NAME>.md README.md docs/AGENTS.md tasks/SYNC_LOG.md`.
- [ ] Push all changes to GitHub.
