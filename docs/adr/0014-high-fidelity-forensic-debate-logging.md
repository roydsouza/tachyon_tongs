# ADR-0014: High-Fidelity Forensic Debate Logging & Humor-Injected Personas

## Status
Proposed

## Context
The Airlock Debate Triad (ADR-0013) generates critical forensic data. However, this data is currently ephemeral (state-only) or stored in opaque SQLite ledgers. To make the architecture more transparent, auditable, and engaging for human operators, we need a high-fidelity record of the adversarial discourse.

## Decision
1.  **Debate Marketplace**: We will create a `debates/` directory to store timestamped markdown files (`DEBATE_YYYYMMDD_HHMMSS_<CVE_ID>.md`).
2.  **Adversarial Banter**: We will inject "Humorous Contention" into the agent personas. The `Skeptic` will be prompted to use incisive, witty insults toward the `Engineer's` "naive" implementations, and the `Meta-Critic` will adopt a dry, judgmental tone.
3.  **Forensic Value**: While humorous, the documents will maintain a strict technical structure (Proposal -> Critique -> Arbitration) to serve as a legal/forensic "Ground Truth" for substrate mutations.

## Consequences
- **Positive**: High engagement for human reviewers; simplified forensic audits; visible "Agent Reasoning" chains.
- **Negative**: Increased filesystem clutter (requires periodic archival); slightly higher token count for persona-building.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0014",
  "hash": "sha256:7463eddf19b8828cb05d24202dbfcf9b30412f24a999a96ffe1fa8d06b25850f",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
