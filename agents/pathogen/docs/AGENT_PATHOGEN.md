# 🦠 Agent: Pathogen (The Proactive Adversary)

## Overview
The Pathogen Agent is the "Red Team" component of the Tachyon Tongs substrate. In Phase 38, it has evolved into a **Proactive Adversarial Substrate**, executing periodic, template-driven sweeps to hunt for emergent substrate bypasses.

## Operational Mechanics

### 1. Triggers
- **24-Hour Sweep**: Triggered autonomously via LaunchAgent (`com.tachyon.pathogen.plist`).
- **Hybrid Synthesis**: Triggered manually via `scripts/run_pathogen.py`.
- **Adversarial Co-Evolution**: Triggered when **Sentinel** discovers a new threat with specific "Guidance" metadata.

### 2. Hybrid Attack Synthesis
Pathogen utilizes a **Template Engine** (`exploits/templates/`) to synthesize attacks:
- **Seed Templates**: Baseline Python exploit payloads for specific ASI categories.
- **Mutation guidance**: Ingests "Adversarial Guides" from the 11 OWASP ASI Playbooks (`exploits/ASI*.md`).
- **LLM Mutation**: Hallucinates metamorphic variations of the payload to bypass current filters.

### 3. Capabilities
- `execute_sweep()`: Traverses the ASI taxonomy to test full-spectrum resistance.
- **Metamorphic Payload Generation**: Mutates code/prompt structures while maintaining malicious semantics.
- **Bypass Validation**: Directly injects synthesized attacks into the Substrate's Event Horizon to verify defensive resilience.

## Integration
- **Upstream**: Fed by **Sentinel's** high-signal guidance in `CATALOG.md` and the **ASI Playbooks**.
- **Downstream**: Log results to the `StateManager`, providing "Adversarial Feedback" for the **Engineer** to generate new patches.
- **CROWN JEWEL**: Serves as the continuous "Fitness Function" for the substrate's immunity.
