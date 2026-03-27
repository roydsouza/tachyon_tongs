# ADR-0038: Proactive Adversarial Substrate (Pathogen v2)

## Context
The original Pathogen implementation was primarily reactive, triggered by specific discovery events or manual fuzzer runs. To achieve "Crown Jewel" status, the substrate requires a continuous, proactive validation loop that identifies and tests potential bypasses before they are exploited in the wild.

## Decision
We are evolving the Pathogen agent into a **Proactive Adversarial Substrate**.
- **Template-Driven Hybrid Engine**: Pathogen now utilizes pre-defined exploit templates (`exploits/templates/*.py`) which are dynamically augmented and mutated using LLM guidance extracted from the 11 OWASP ASI Playbooks.
- **Autonomous Scheduling**: Implement a macOS LaunchAgent (`com.tachyon.pathogen.plist`) to trigger a full adversarial sweep every 24 hours.
- **ASI Mapping**: Every attack synthesized by Pathogen must be mapped to an ASI category (ASI01-ASI11) to ensure full-spectrum coverage of the OWASP Agentic Top 10.

## Consequences
- **Positive**: Continuous validation of the substrate's security posture. High-signal feedback loop for the Engineer agent.
- **Neutral**: Increased computational overhead for daily sweeps.
- **Negative**: Potential for false positives if the mutation engine generates non-functional "hallucinated" attacks.

## Status
OPERATIONAL (2026-03-23)


## Integrity Attestation

```json
{
  "adr_id": "ADR-0038",
  "hash": "sha256:674cf778d6d5766322ce75bf62a81f56c8ca787a7586a836c6551fb80d61a371",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
