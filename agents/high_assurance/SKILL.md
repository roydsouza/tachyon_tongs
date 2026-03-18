---
name: high-assurance
description: Mandatory protocols for extending the Tachyon Tongs substrate with 100% test coverage and documentation sync.
---

# 🛡️ High-Assurance Development Protocol

This skill defines the mandatory "Entry" and "Exit" rituals for every feature addition or modification in the Tachyon Tongs substrate.

## 📥 Entry Ritual: Alignment
1.  **Grooming**: Read [TASKS.md](file:///Users/rds/antigravity/tachyon_tongs/TASKS.md) to identify the current active phase.
2.  **Architectural Intent**: Create or update a corresponding Architecture Decision Record (ADR) in `docs/adr/`.
3.  **Planning**: Create/Update an `implementation_plan.md` artifact and request user review.

## 🛠️ Execution: Implementation
1.  **Modular First**: Implement logic in the appropriate `tachyon/` submodule.
2.  **Traceability**: Tag all new code with the corresponding Phase ID (e.g., `# Phase 17`).

## 📤 Exit Ritual: Verification & Sync
1.  **Exhaustive Regression**: 
    - Create a new test file in `tests/` specifically for the feature.
    - Run the *entire* regression suite: `export PYTHONPATH=$PYTHONPATH:. && python3 -m unittest discover tests/`.
2.  **Documentation Sync**:
    - Update [TASKS.md](file:///Users/rds/antigravity/tachyon_tongs/TASKS.md) with `[COMPLETED]` and specific sub-task checkmarks.
    - Update [ARCHITECTURE.md](file:///Users/rds/antigravity/tachyon_tongs/ARCHITECTURE.md) if the data flow changed.
    - Update [SYNC_LOG.md](file:///Users/rds/antigravity/tachyon_tongs/SYNC_LOG.md) with session highlights.
3.  **Walkthrough**: Generate a `walkthrough.md` artifact as proof of work.
4.  **GitHub Push**: Run the `/push` workflow to synchronize all changes.

> [!IMPORTANT]
> Failure to run the full regression suite or update `TASKS.md` before completion is a violation of the high-assurance mandate.
