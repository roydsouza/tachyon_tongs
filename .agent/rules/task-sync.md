# Task Synchronization Protocol (TSP)

## Status
Active

## Goal
Ensure that the agent's internal `task.md` (Artifact) and the project's permanent `TASKS.md` (Workspace) remain 100% synchronized at all times.

## Rules
1.  **Dual-Update**: Any time an item is marked as `[x]`, `[/]`, or `[ ]` in the internal `task.md`, the corresponding change MUST be reflected in `TASKS.md` immediately.
2.  **Phase Matching**: Every phase mentioned in the internal `task.md` MUST exist in the workspace `TASKS.md` with an identical status label.
3.  **Completion Verification**: Before closing a phase as `[DONE]`, the agent MUST verify that all related ADRs, tests, and documentation are listed in `TASKS.md`.

## Automation Hook
In the future, a `/sync` workflow will invoke a script to parse both files and merge the states automatically.

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*
