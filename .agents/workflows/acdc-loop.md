---
description: Agent Centric Development Cycle (AC/DC) for high-assurance security engineering.
---

# 🌀 AC/DC: Agent Centric Development Cycle

Follow this loop for every feature or mitigation:

## 1. 🧭 GUIDE (Planning)
- **Identify Intent**: Define the goal in `memory/task_plan.md`.
- **Constraint Check**: Review `.agent/rules/MISSION.md` and `SOUL.md`.
- **Architectural Alignment**: Create an ADR in `docs/adr/` for significant changes.

## 2. 🧪 GENERATE (Implementation)
- **Agentic TDD**: Write a failing test in `tests/` that demonstrates the lack of the feature or the presence of the bug.
- **Minimal Code**: Write the minimal code in `src/` to make the test pass.
- **Refactor**: Clean up the code while staying within OPA and Sandbox boundaries.

## 3. 🛡️ VERIFY (Validation)
- **Deterministic Check**: Run `pytest` and any substrate-specific verification scripts (e.g., `verify_substrate.py`).
- **Policy Audit**: Ensure no new tool calls bypass `policies/tool_access.rego`.

## 4. 🧠 SOLVE (Finalization)
- **Memory Update**: Append the result to `memory/evolution.md`.
- **Task Pruning**: Update `TASKS.md` and move completed items to `memory/accomplishments.md`.
- **Walkthrough**: Generate a post-implementation walkthrough artifact.
