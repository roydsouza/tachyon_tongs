# Task Synchronization Protocol (TSP)

## Status
Active

## Goal
Ensure that the agent's internal `task.md` (Artifact) and the project's permanent `TASKS.md` (Workspace) remain 100% synchronized at all times.

## Rules
1.  **Master Source of Truth**: The project's phased task files are the ultimate source of truth:
    - `TASKS_CLEANUP.md`: Active backlog and "Get-Well" plan.
    - `TASKS_BOOTSTRAP.md`: Historical forensic record.
    - `TASKS_ENHANCEMENTS.md`: Future strategic additions.
    The agent MUST periodically synchronize its internal state **from** these files.
2.  **Synchronize Before & After**: The agent MUST pull state from the master files before starting any task and MUST update them immediately after completion or status change.
3.  **Safer Targeted Edits**: Updates to master files MUST be performed using targeted edit tools (e.g., `multi_replace_file_content` or `replace_file_content`).
4.  **Prohibition of Overwrites**: The agent MUST NEVER use `write_to_file` on master task files. Overwriting the entire file is strictly prohibited to prevent data loss or accidental deletion.
5.  **PQC Anchoring & Provenance**: Every modification to a master task file, agent, or core component MUST be followed by the mandatory Forensic Ritual:
    - `python3 scripts/calibrate_sbom.py`: To update cryptographic provenance hashes.
    - `python3 scripts/forensics/resign_docs.py`: To re-anchor all task logs and audit trails.
6.  **Immediate & Granular Synchronization**: Any time an item is marked as `[x]`, `[/]`, or `[ ]` in the internal `task.md`, the corresponding change MUST be reflected in the master files immediately. This includes **every granular sub-item and Acceptance Test** defined within the task block. Partial updates are "Status Drift" violations.
7.  **Verification Before Closure**: A task MUST NOT be marked `[x]` in the master file until all its associated Acceptance Tests are also marked `[x]` and have been verified to PASS.
8.  **Assurance Mandate**: Every task fix/implementation MUST include exhaustive regression tests and a signed ADR.

## Automation Hook
In the future, a `/sync` workflow will invoke a script to parse both files and merge the states automatically.

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*
