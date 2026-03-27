# ADR-0023: Formalizing Canary Agent Architecture

## Status
Proposed -> **Accepted** (2026-03-19)

## Context
The Canary Agent was initially implemented as a sub-component within the unified `roles.py` substrate. While functional, this "hidden" implementation made it difficult to audit, configure, and scale independently. High-assurance security engineering requires the "Honey-Pot" protocol to be explicit and first-class.

## Decision
We will formalize the Canary agent into a standalone, first-class component.
1.  **Dedicated Module**: Move core logic to `tachyon/agents/canary.py`.
2.  **Explicit Interface**: Define `scout` and `harvest` as top-level capabilities.
3.  **Isolation Reinforcement**: Ensure the Canary environment is strictly decoupled from the main `StateManager` for production runs.

## Consequences
- **Visibility**: The agent's code and its operational log (`CANARY_LOG.md`) are now clearly associated.
- **Modularity**: The Canary can now be updated and tested without risk to the main `Sentinel` or `Engineer` roles.
- **Consistency**: Legacy wrappers in `roles.py` maintain backward compatibility while delegating to the new module.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0023",
  "hash": "sha256:43716209243e7c3147f1e9d94da29323155ce4a93b52f9acb717320a39ea6ae6",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
