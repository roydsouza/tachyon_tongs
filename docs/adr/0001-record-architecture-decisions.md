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

## Integrity Attestation

```json
{
  "adr_id": "ADR-0001",
  "hash": "sha256:7571164c85dc409028706fc7d21a32b6f2548418e125d2ec4a7fbeecc1419da9",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
