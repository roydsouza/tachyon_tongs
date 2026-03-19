# ADR-0006: Sentinel Hybrid Migration (Skill-Based Architecture)

## Status
Accepted (Phase 13)

## Context
The original Sentinel implementation was a standalone monolithic script (`scripts/sentinel.py`) with hardcoded configurations (keywords, thresholds, harvest modes). This approach was difficult to manage as the substrate evolved into a multi-agent environment and lacked a formal identity within the Tachyon Tongs lifecycle.

## Decision
We are migrating the Sentinel into a **Hybrid Agent** model:
1. **Skill-Based Identity**: A formal `agents/sentinel/SKILL.md` defines the Sentinel's intent, protocols, and constraints.
2. **Declarative Configuration**: All operational parameters (e.g., `harvest_mode`, `keywords`) are moved from code to the `SKILL.md` or a structured configuration layer.
3. **Managed Runner**: A new `tachyon/agents/sentinel/runner.py` acts as the execution bridge, loading the skill manifest and orchestrating the deterministic core.
4. **Substrate Registration**: The Sentinel is now formally registered in the substrate node registry (`/tmp/tachyon/nodes.json`), allowing it to be managed by the central daemon.

## Consequences
- **Positive**: Improved modularity; configuration can be updated without code changes; better alignment with the "Substrate as a Platform" vision.
- **Negative**: Slight overhead in the execution lifecycle due to configuration parsing and dynamic imports.
- **Maintenance**: Requires keeping the `SKILL.md` manifest in sync with the underlying core logic.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0006",
  "hash": "sha256:e2fc5283c174333cd56ebf6092cb0c641054602566a437bee2bac74c6a9519f7",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
