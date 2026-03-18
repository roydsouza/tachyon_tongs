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
