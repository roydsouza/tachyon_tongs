# ADR-0003: Standardize Directory Structure

## Status
Accepted

## Context
The root directory was cluttered with logs, scripts, and temporary markdown files, making it difficult for both humans and agents to find relevant context.

## Decision
Implement a layered directory structure:
- `.agent/`: Governance (Mission, Soul, Identity).
- `agents/`: Consolidated agent modules.
- `intelligence/`: Threat catalogs and databases.
- `memory/`: Episodic logs and historical decision-tree data.
- `docs/adr/`: Architectural constraints.

## Consequences
- **Positive**: Improved "Progressive Disclosure" for agent context windows.
- **Positive**: Clean root directory for human maintenance.
- **Positive**: Explicit separation of Substrate (src) from Memory (memory).
