# 🧬 Forensic Evolution Ritual (FER-001)

**Objective**: Ensure that every modification, enhancement, or fix to the Tachyon Tongs substrate is professionally documented, cryptographically anchored, and substrate-integrated.

---

### 🛡️ The 8-Step Evolution Ritual

For every enhancement or security fix, the following ritual MUST be performed atomically. Failure to complete any step is a `FORENSIC_VIOLATION`.

#### 1. Task Synchronization (Pre-flight)
- **Sync**: Ensure the relevant task file (e.g., `tasks/TASKS_SECURITY.md`) is current.
- **Mark**: Identify the specific sub-tasks in the file.

#### 2. Status Update
- **In-Progress**: Mark the task as `[/]` (In-Progress) in the relevant `TASKS_*.md` file.

#### 3. Execution
- **Implement**: Create/modify files according to the implementation plan.
- **Rules Compliance**: Ensure all code follows the "Modular First" and "Apple Silicon Native" mandates.

#### 4. Verification (TDAD)
- **Regressions**: Generate comprehensive regression tests in `tests/`.
- **Pass Policy**: All tests MUST pass with 100% fidelity before documentation occurs.

#### 5. Task Completion
- **Mark Complete**: Update the `TASKS_*.md` file to reflect completion (`[x]`).

#### 6. Architectural Anchoring (ADR)
- **Author ADR**: Create a new Architecture Decision Record in `docs/adr/`.
- **Anchor**: Update `docs/adr/MANIFEST.json` with the new record's hash.

#### 7. Forensic Ledger (Pulse)
- **Update SYNC_LOG**: Add an entry to `tasks/SYNC_LOG.md` detailing the objective, tasks completed, and verification results.
- **Sign**: Re-sign all updated documentation via `resign_docs.py`.

#### 8. Handoff
- **Circle Back**: Confirm completion to the user and wait for instructions.

---

> [!CAUTION]
> **Audit Failure**: Any Turn that results in a "feat" or "fix" commit without a corresponding ADR and SYNC_LOG entry is an invalid architectural state.
