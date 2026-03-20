# ADR-0024: Agent Infrastructure Consolidation

## Status
Proposed (2026-03-19)

## Context
Tachyon Tongs currently maintains two separate agent directories:
1.  `agents/`: Declarative "Skills", experimental modules, and GUI-focused residents.
2.  `tachyon/agents/`: Substrate-integrated Roles and core Python implementations.

This dual-structure has led to discovery confusion, duplication of "Sentinel" concepts, and a fragmented development experience.

## Decision
We will consolidate all agent-related files into a single unified directory: **`tachyon/agents/`**.

### Unified Sub-directory Pattern
Each agent will reside in its own sub-directory within `tachyon/agents/`, following this "Logical Separation" of files:

| File Pattern | Category | Purpose |
| :--- | :--- | :--- |
| `SKILL.md` | **Intent (Declarative)** | High-level goal, capabilities, and configuration schema. |
| `[name]_role.py` | **Role (Execution)** | Substrate-integrated class (e.g., `SentinelRole`) that maps to a `BaseTachyonAgent`. |
| `[name]_engine.py` | **Core Logic** | The actual performant logic (e.g., scraping, patching) used by the Role. |
| `tests/` | **Verification** | Agent-specific unit and integration tests. |

## Consequences
- **Positive**: Single source of truth for every agent. Easier discovery for both humans and AI agents.
- **Positive**: Simplified `PYTHONPATH` and module imports.
- **Neutral**: Requires updating all local imports and `git` paths.
- **Critical**: The "Logical Separation" is maintained by the file naming/types, not by physical directory distance.
