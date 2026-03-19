# ADR-0013: Airlock Debate Triad & Adversarial Oversight

## Status
Proposed

## Context
Tachyon Tongs currently relies on a single `EngineerAgent` to synthesize mitigations. While the `VerifierNode` provides heuristic safety checks, it lacks the cognitive depth to detect "Trojan Patches"—subtle backdoors or sycophantic reasoning that appears safe but violates semantic security. 

## Decision
We will implement the **Airlock Debate Triad**, a second-order oversight mechanism comprising three specialized agent personas:
1.  **EngineerAgent**: Proposes the patch/mitigation.
2.  **SkepticAgent**: An adversarial critic tasked with finding flaws, side-effects, or hidden risks in the proposal.
3.  **MetaCriticAgent**: A high-level arbiter that evaluates the debate between the Engineer and Skeptic to determine the final system verdict.

### Future Expansion: Diverse Models
To maximize the effectiveness of this debate, the triad will eventually utilize **disparate LLM architectures** (e.g., a Google-native Scout, a Meta-native Skeptic, and a Mistral-native Meta-Critic). This ensures the "intrinsically different viewpoints" necessary for robust adversarial synthesis.

## Consequences
- **Positive**: Significantly higher assurance for autonomous patches; reduction in "one-agent-to-rule-them-all" failure modes.
- **Negative**: Increased latency (multi-turn debate) and token consumption.
- **Verification**: Mandatory for all `HOTL/HOOTL` autonomous evolutions.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0013",
  "hash": "sha256:085d9c66d434e68c6b68e2e5b2eb1fcab87c294e2b972aa768802ecda7fb0048",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
