---
description: Implement UX changes with forensic consistency and architectural alignment.
---

# /ux-interface Workflow (The Design Ritual)

Follow these steps for any task involving TUI, CLI, Dashboard, or Operator UX:

1. **Context Sync**: Read `docs/INTERFACES.md` to ensure architectural and design principle alignment.
2. **Current Audit**: Perform an audit of existing interface components (`main.py`, `app.py`, `daemon.py`, etc.).
3. **Master Record Sync**:
    - **Check**: Is the task already defined in `TASKS_INTERFACES.md`?
    - **Action**: If not, create a new task entry in `TASKS_INTERFACES.md`.
4. **Execution Loop (TDAD)**:
    - **Implement**: Write the code in a modular fashion.
    - **Test**: Add or update tests in `tests/integration/test_interfaces.py`.
    - **ADR**: If architectural changes were made, add a signed ADR to `docs/adr/`.
5. **State Alignment**:
    - **Update**: Reflect the new component state in `docs/INTERFACES.md`.
    - **Mark**: Mark the task as complete `[x]` in `TASKS_INTERFACES.md`.
6. **Forensic Checkpoint**:
    - **Re-sign**: Run `python3 scripts/forensics/resign_docs.py`.
    - **Sync**: Update `SYNC_LOG.md` and push to GitHub.

---
> [!NOTE]
> This workflow is a mandatory "Guardrail" to prevent documentation drift in the interface layer.
