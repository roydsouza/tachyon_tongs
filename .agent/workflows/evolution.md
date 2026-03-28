---
description: Perform the 8-step Forensic Evolution Ritual (FER-001) for substrate enhancements.
---

# /evolution: The Forensic Evolution Ritual

Follow these steps to ensure every substrate enhancement is professionally documented and cryptographically anchored.

### 1. Task Synchronization (Pre-flight)
- [ ] Ensure the relevant task file (e.g., `tasks/TASKS_SECURITY.md`) is up-to-date.
- [ ] Identify and sync sub-tasks in that file.

### 2. Status Update
- [ ] Mark the task as `[/]` (In-Progress) in the relevant `TASKS_*.md` file.

### 3. Execution
- [ ] Implement the feature or fix according to the plan.
- [ ] Ensure all new files follow directory topology.

### 4. Verification (TDAD)
- [ ] Generate comprehensive regression tests in `tests/`.
// turbo
- [ ] Run `PYTHONPATH=. pytest -v tests/test_<new_feature>.py`.
- [ ] Ensure 100% pass rate.

### 5. Task Completion
- [ ] Update the `TASKS_*.md` file to reflect completion (`[x]`).

### 6. Architectural Anchoring (ADR)
- [ ] Create a new Architecture Decision Record in `docs/adr/00xx-*.md`.
// turbo
- [ ] Run `sha256sum docs/adr/00xx-*.md` and update `docs/adr/MANIFEST.json`.

### 7. Forensic Ledger (Pulse)
- [ ] Add a formal entry to [tasks/SYNC_LOG.md](file:///Users/rds/antigravity/tachyon_tongs/tasks/SYNC_LOG.md).
- [ ] Summarize the implementation, status [COMPLETE], and verification results.
// turbo
- [ ] Run `python3 scripts/forensics/resign_docs.py <MODIFIED_FILES>`.

### 8. Handoff
- [ ] Confirm completion to the user and wait for instructions.
