# Task Synchronization Protocol (TSP)

## Status
Active

## Goal
Ensure that the agent's internal `task.md` (Artifact) and the project's permanent `TASKS.md` (Workspace) remain 100% synchronized at all times.

## Rules
1.  **Master Source of Truth**: The workspace `TASKS.md` file is the ultimate source of truth for the project state. The agent MUST periodically synchronize its internal state **from** `TASKS.md`.
2.  **Safer Targeted Edits**: Updates to `TASKS.md` MUST be performed using targeted edit tools (e.g., `multi_replace_file_content` or `replace_file_content`).
3.  **Prohibition of Overwrites**: The agent MUST NEVER use `write_to_file` on `TASKS.md`. Overwriting the entire file is strictly prohibited to prevent data loss or accidental deletion.
4.  **Immediate Synchronization**: Any time an item is marked as `[x]`, `[/]`, or `[ ]` in the internal `task.md`, the corresponding change MUST be reflected in `TASKS.md` immediately using a targeted edit.
5.  **Completion Verification**: Before closing a phase as `[DONE]`, the agent MUST verify that all related ADRs, tests, and documentation are listed in `TASKS.md`.

## Automation Hook
In the future, a `/sync` workflow will invoke a script to parse both files and merge the states automatically.

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*
