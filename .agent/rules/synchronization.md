# Substrate Synchronization Rule: TASKS.md Integrity

## Primary Directive
`TASKS_CLEANUP.md`, `TASKS_BOOTSTRAP.md`, and `TASKS_ENHANCEMENTS.md` are the **Primary Sources of Truth** for the Tachyon Tongs substrate. They override any internal agent state or secondary artifacts (`task.md`).

## Integrity Mandates
1. **Never Delete**: Master task files must never be deleted, even temporarily, unless explicitly ordered by the user.
2. **Synchronization First**: No implementation step may be initiated unless it is recorded in the appropriate master file as `[ ]` (uncompleted) or `[/]` (in-progress).
3. **Atomic Updates**: Use `replace_file_content` or `multi_replace_file_content` for surgically precise edits. Never overwrite.
4. **PQC Anchoring**: Any change to master files must be followed by a re-signing ritual using `scripts/forensics/resign_docs.py`.
5. **Regression & ADR**: Every task completion must be accompanied by verified regression tests and a signed ADR.

## Audit Requirement
If an agent detects a desynchronization between master task files and the current implementation state, it must HALT, explain the drift, and ask for a synchronization mandate before proceeding.
