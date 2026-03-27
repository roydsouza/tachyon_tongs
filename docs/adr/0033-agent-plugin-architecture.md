# ADR-0033: Agent Plugin Architecture

## Status
Proposed (2026-03-22)

## Context
Tachyon Tongs agents are currently fragmented across multiple directories (`tachyon/agents/`, `docs/`, `.agent/workflows/`), leading to discovery difficulty, redundant boilerplate, and documentation drift. Additionally, operational "noise" (e.g., repository bloat from debates) requires a more structured lifecycle management for agent artifacts.

## Decision
We will transition to a unified **Agent Plugin Architecture**. This involves:

1. **Modular Directory Structure**: All agents will be colocated in a top-level `agents/` directory. Each agent will have its own subdirectory containing implementation, documentation, skills, and tests.
2. **Plugin Registry**: A central `AgentRegistry` in `agents/_core/` will handle autonomous discovery and loading of plugins based on a standardized `config.yaml`.
3. **Colocated Testing (TDAD)**: As per the Test-Driven Agent Development (TDAD) workflow in the SDLC, tests for each agent will live within its plugin directory.

### Directory Layout
```
agents/
├── _core/                     # Shared base classes & registry
├── [agent-name]/              # Individual plugin
│   ├── README.md              # Documentation
│   ├── agent.py               # Code (if applicable)
│   ├── SKILL.md               # LLM Skill (if applicable)
│   ├── config.yaml            # Registration & Metadata
│   └── tests/                 # Plugin-specific tests
```

## Consequences
- **Improved Discoverability**: All agent capabilities are centralized.
- **Strict Isolation**: Agents are self-contained plugins.
- **Reduced Noise**: Lifecycle management (e.g., archival scripts) can be applied per-plugin.
- **Breaking Change**: Existing import paths from `tachyon/agents/` will be deprecated and eventually removed.

## Alternatives Considered
- **Maintaining current structure**: Rejected due to unsustainable fragmentation.
- **Using external package managers (e.g., Poetic/Nix)**: Rejected as overly complex for the current development scale.

---
**Signatures** (Signed via `scripts/sign_artifact.py`)
> [!NOTE]
> Signature pending execution of Phase 1.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0033",
  "hash": "sha256:33bdfe98e3053490c22b4f20e8aec43e99825c86ab4f50d3e534a34dceb1d5c7",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
