# Substrate Synchronization Rule: TASKS.md Integrity

## Primary Directive
`TASKS.md` is the **Primary Source of Truth** for the Tachyon Tongs substrate. It overrides any internal agent state or secondary artifacts (`task.md`).

## Integrity Mandates
1. **Never Delete**: The `TASKS.md` file must never be deleted, even temporarily, unless explicitly ordered by the user.
2. **Synchronization First**: No implementation step (Phase X.Y) may be initiated unless it is physically recorded in `TASKS.md` as `[ ]` (uncompleted) or `[/]` (in-progress).
3. **Atomic Updates**: When updating phase status, use `replace_file_content` or `multi_replace_file_content` to perform surgically precise edits. Avoid `write_to_file` with `Overwrite=true` on this file to prevent data loss.
4. **PQC Anchoring**: Any change to `TASKS.md` must be followed by a re-signing ritual using `scripts/forensics/resign_docs.py`.

## Audit Requirement
If an agent detects a desynchronization between `TASKS.md` and the current implementation state, it must HALT, explain the drift, and ask for a synchronization mandate before proceeding.
