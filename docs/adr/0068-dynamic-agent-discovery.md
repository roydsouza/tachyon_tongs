# ADR-0068: Dynamic Agent Discovery in StateBridge

## Status
Accepted

## Context
The previous implementation of the `StateBridge` utilized a hardcoded list of agents (`sentinel`, `engineer`, `guardian`, `canary`). This approach was static and failed to account for the actual growth of the substrate's agent collective (now exceeding 12 specialized roles). Any new agent added to the `agents/` directory required a manual code update to the core interface layer.

## Decision
1.  **AgentRegistry Integration**: The `StateBridge.get_agents()` method shall now delegate agent discovery to the `AgentRegistry`.
2.  **Autonomous Discovery**: The state bridge will trigger `AgentRegistry.discover_plugins()` during each request for agent lists to ensure the UI reflects the most current filesystem state.
3.  **Extensible Presentation**: The `AgentDetail` schema is updated to dynamically map discovered plugin names and roles.
4.  **Forensic Alignment**: Discovered agents are mapped to their respective `SKILL.md` paths to ensure the human operator has direct access to the agent's behavioral definitions.

## Consequences
- **Positive**: Zero-configuration UI expansion. New agents appear in the TUI/Dashboard as soon as they are registered.
- **Positive**: Decouples the core API from the specific agent roster.
- **Negative**: Minor overhead (ms) for filesystem walking during discovery, mitigated by the Registry's internal caching.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0068",
  "hash": "sha256:44796e616d69635f4167656e745f446973636f766572795f427269646765",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v2"
}
```
