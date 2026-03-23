# 🦠 Agent: Pathogen (The Proactive Adversary)

## Overview
The Pathogen Agent is the "Red Team" component of the Tachyon Tongs substrate. In Phase 38, it has evolved into a **Proactive Adversarial Substrate**, executing periodic, template-driven sweeps to hunt for emergent substrate bypasses.

## Operational Mechanics

### 1. Triggers
- **24-Hour Sweep**: Triggered autonomously via LaunchAgent (`com.tachyon.pathogen.plist`).
- **Hybrid Synthesis**: Triggered manually via `scripts/run_pathogen.py`.
- **Adversarial Co-Evolution**: Triggered when **Sentinel** discovers a new threat with specific "Guidance" metadata.

### 2. Metamorphic Reflection (Phase 40)
The Pathogen utilizes a **Reflector Node** (`tachyon/core/reflector.py`) to move beyond static templates:
- **Knowledge Ingestion**: Reads ADRs and ARCHITECTURE.md to "scout" the substrate's defenses from the inside.
- **Goal Aliasing**: Mutates payloads to masquerade as benign system traffic (Semantic Drift).
- **Internal Critique**: Uses an LLM loop to predict failure points and self-correct attacks before launching.

### 3. Capabilities
- `execute_sweep()`: Traverses the ASI taxonomy using metamorphic logic.
- **Metamorphic Reflection**: Autonomously critiques and improves attack vectors based on substrate state.
- **Herald Orchestration**: Emits high-signal events (`PATHOGEN_REFLECTION_STARTED`, `PATHOGEN_GOAL_MUTATED`) to provide operator visibility into the cognitive attack chain.

## Integration
- **Upstream**: Fed by **Sentinel's** high-signal guidance and the substrate's own architectural blueprints.
- **Downstream**: Log results to the `StateManager`, providing "Adversarial Feedback" for the **Engineer**.
- **CROWN JEWEL**: Serves as the self-thinking "Fitness Function" that ensures the substrate never settles for a shallow defensive equilibrium.
