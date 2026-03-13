# ADR-0001: Record Architecture Decisions

## Status
Accepted

## Context
Tachyon Tongs was suffering from "vibe-coding" debt where architectural decisions were transient and often undocumented, leading to inconsistency in security enforcement and directory structure.

## Decision
We will use Architecture Decision Records (ADRs) to document all significant technical decisions. ADRs will be stored in `docs/adr/` as sequential markdown files.

## Consequences
- **Positive**: Clear audit trail of "why" decisions were made.
- **Positive**: Prevents AI agents from accidentally undoing security constraints during optimization.
- **Negative**: Adds slight overhead to the planning phase.
