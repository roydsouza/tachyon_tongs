# ADR-0040: Metamorphic Adversarial Reasoning

## Context
Pathogen v2 established a proactive, template-driven sweep. However, static templates are susceptible to signature-based detection and do not account for the substrate's specific defensive evolution (recorded in ADRs and ARCHITECTURE.md). To maintain an offensive edge, the Pathogen requires a cognitive layer that can reason about defenses.

## Decision
We are implementing **Metamorphic Adversarial Reasoning** via a dedicated **Reflector Node**.
- **Reflector Node (`tachyon/core/reflector.py`)**: A specialized LLM-driven reasoning engine that ingests substrate metadata (ADRs, docs, state) to identify "blind spots."
- **Adversarial Reflection Loop**: The Pathogen now follows a "Think-Criticize-Attack" cycle:
    1.  **Analyze**: Review ARCHITECTURE.md for defensive primitives.
    2.  **Critique**: Predict why a baseline template will fail.
    3.  **Mutate**: Synthesize a "Goal-Aliased" payload that bypasses predicted filters.
- **Herald Orchestration**: All cognitive stages (Reflection, Mutation, Synthesis) are broadcast as high-signal events for remote observability.

## Consequences
- **Positive**: Substrate defenses are tested against human-like adversarial intent. Identification of complex "semantic drift" vulnerabilities.
- **Neutral**: Increased token usage and execution time per sweep.
- **Negative**: Risk of "reasoning loops" if the LLM enters a recursive self-critique without a termination boundary.

## Status
IMPLEMENTING (2026-03-23)


## Integrity Attestation

```json
{
  "adr_id": "ADR-0040",
  "hash": "sha256:1642893657feb759600902cbf09a5e2c01f2e95d03a78a5addc544f0a2d7e9f5",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
