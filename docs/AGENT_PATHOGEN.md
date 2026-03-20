# 🦠 Agent: Pathogen (The Adversarial Adversary)

## Overview
The Pathogen Agent is the "Red Team" component of the Tachyon Tongs substrate. Its primary mission is to autonomously mutate known exploit payloads into novel variants, stress-testing the substrate's detection and remediation capabilities.

## Operational Mechanics

### 1. Triggers
The Pathogen is typically triggered by:
- **Sandbox Stress Tests**: When the `Canary` is scouting, the Pathogen provides mutated payloads to find bypasses.
- **Immune Validation**: Testing if a newly applied policy (from the `Engineer`) can be bypassed by slight variations of the original exploit.
- **Autonomous Evolution**: Long-running background tasks to "fuzz" the substrate's policy boundaries.

### 2. Configuration
The Pathogen operates in the `tachyon/agents/pathogen/` directory:
- **Mutation Engine**: Uses semantic and structural mutation techniques (via `mutation_engine.py`) to alter exploit code without breaking its functional malicious intent.
- **Context Awareness**: Tailors mutations based on the target substrate's known policy set (e.g., OPA or Cedar).

### 3. Capabilities
- `mutate_payload(payload, context)`: Applies a series of adversarial transformations (e.g., encoding, obfuscation, logic splitting) to a raw exploit.
- **Exploit DNA Mapping**: Tracks which mutation techniques successfully bypass current substrate protections.

## Integration
- **Upstream**: Fed by the `ExploitationCatalog` or `Sentinel` harvested payloads.
- **Downstream**: Feeds mutated variants to the `Canary` for scouting and the `Engineer` for iterative remediation.
