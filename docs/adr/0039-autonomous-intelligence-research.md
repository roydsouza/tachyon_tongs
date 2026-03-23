# ADR-0039: Autonomous Intelligence Research (Sentinel Autoresearch)

## Context
The Sentinel agent's cataloging of vulnerability intelligence was previously a raw aggregation of CVE and GHSA feeds. This resulted in "underewhelmed" low-signal output that required manual filtering for relevance.

## Decision
We are implementing **Autonomous Intelligence Research** (Karpathy-style) within the Sentinel agent.
- **ResearchSynthesizer**: A new core node that uses LLM synthesis to transform raw threat signals into high-signal intelligence.
- **ASI Taxonomy Mapping**: Sentinel autonomously classifies discovered threats into the 11 OWASP ASI categories.
- **Mutation Guidance**: Sentinel now produces "Pathogen Guidance" as part of its cataloging, providing the Pathogen agent with specific hints on how to mutate its next adversarial sweep.

## Consequences
- **Positive**: High-signal intelligence hub (`CATALOG.md`). Automated discovery-to-attack-synthesis pipeline.
- **Neutral**: Requires LLM tokens for synthesis during every hunt.
- **Negative**: Risk of misclassification if the synthesis heuristic/LLM fails to understand a complex exploit.

## Status
OPERATIONAL (2026-03-23)
