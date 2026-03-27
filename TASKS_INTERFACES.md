# 🖥️ Phase: Interfaces & Remote Access [ ] IN-PROGRESS

> [!IMPORTANT]
> **MASTER TASK RECORD**: This file is the primary source of truth for the project's interface engineering state.
> - **Pre-Work**: Always synchronize internal agent state from this file before starting work.
> - **Post-Work**: Always update this file immediately upon task completion. Mark `[x]` for done, `[/]` for in-progress.
> - **Integrity**: Every modification requires a re-signing ritual (`scripts/forensics/resign_docs.py`).
> - **Assurance**: Every UI/Interface change MUST include exhaustive regression tests (using `browser_subagent` where applicable) and a signed ADR.
> - **Commits**: One fix per commit. Format: `feat(interface): <one-line summary> [INT-<N>]`
> - **Workflow**: Follow the TDAD workflow (`.agent/workflows/tdad.md`): write the failing test first, then fix, then verify.

---

## 📋 Ground Rules for the Implementing Agent

1. All interface logic must be verified against the core `TachyonEventBus` for event integrity.
2. Every UI component **MUST** handle signed events and display their cryptographic status (e.g., "PQC VERIFIED").
3. Follow the TDAD workflow: **write the failing test first**, then implement the interface/logic, then verify.
4. All remote access implementations must use post-quantum encrypted tunnels or signed request-response loops.
5. Update this file immediately when starting (`[/]`) and completing (`[x]`) each task.
6. Update `SYNC_LOG.md` after completing each task with the detail level specified in the Handoff section.
7. **AUTO-COMMIT**: Every completed task must be followed by a git push to origin main.

---

## 🔳 Active & Priority: Dashboard & TUI Evolution

### [INT-00] Architecture: docs/INTERFACES.md & Component Audit [ ]
- **Goal**: Establish the definitive architectural guide for human-substrate interaction.
- **Requirements**:
  - Document CLI/TUI/Bridge topology.
  - Audit all interface-related files (`main.py`, `app.py`, `daemon.py`).
  - List all user-facing forensic records (`ALERT.md`, `SYNC_LOG.md`, `forensics.db`).
- **Acceptance Criteria**:
  - [ ] `docs/INTERFACES.md` created and PQC-signed.
  - [ ] Integration test verifies existence and accessibility of all components.

### [INT-01] Textual TUI: Real-Time Event Stream Visualizer [ ]
- **Goal**: Create a high-fidelity terminal dashboard for the `TachyonEventBus`.
- **Requirements**:
  - Filter by topic/severity.
  - Interactive "View Certificate" details for PQC signatures.
  - Auto-refresh with non-blocking async bus subscription.
- **Acceptance Criteria**:
  - [ ] Test script that emits 10 events and asserts they appear in the TUI state.

### [INT-02] Remote Access: Signed Command Relay [ ]
- **Goal**: Enable secure remote triggering of agent actions via signed JSON bundles.
- **Requirements**:
  - Replay attack protection (monotonically increasing nonces).
  - PQC signature validation before execution.
- **Acceptance Criteria**:
  - [ ] Integration test demonstrating a signed remote command being executed by a local agent.

---

## 📺 Operational Transparency (CLI/TUI)

- [ ] **[TUI] Health Score Dashboard**: Dashboard for PQC Coverage, Pathogen Block Rate, and Alignment Drift.
- [ ] **[CLI] tt bus explore**: JSONL-paginated view of signed EventBus events.
- [ ] **[UI] Web Dashboard**: React-based dashboard for long-term telemetry analysis (Future).

---

## 🧪 Verification & Hardening

- [ ] **[VERIFY] UI Stress Test**: Saturate the EventBus with 1000 events/sec and ensure TUI stability.
- [ ] **[VERIFY] Remote Auth**: Negative tests for expired/forged certificates in remote relay.

---

## ✅ Final Verification Checklist

After all Interface tasks are resolved, run the following sequence:

```bash
# 1. Core integration tests
pytest -v tests/integration/test_interfaces.py

# 2. Forensic re-signing
python scripts/forensics/resign_docs.py TASKS_INTERFACES.md

# 3. Final Push
PAGER=cat MANPAGER=cat git add .
PAGER=cat MANPAGER=cat git commit -m "feat: interface stabilization phase complete"
PAGER=cat MANPAGER=cat git push origin main
```

---

## 📝 SYNC_LOG Handoff Protocol for Agentic Models

> [!IMPORTANT]
> When updating `SYNC_LOG.md`, use the following structure for **each task completed**.

### Required Detail Level per SYNC_LOG Entry:
```markdown
### YYYY-MM-DD: Task INT-XX Completion
- **Objective**: One-line summary of the interface enhancement.
- **Status**: [COMPLETE]
- **Tasks Completed**:
  - **[INT-XX] Title**: Summary of the implementation.
    - **Files Modified**: List all source and test files.
    - **Test Added**: Exact test file path and test function name.
    - **Test Result**: `PASS` or `FAIL`.
- **Regression Status**: `pytest` summary line.
- **ADR Created**: ADR number and title.
```
