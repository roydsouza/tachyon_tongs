# 🧠 ADR Governance Skill

## Description
This skill ensures that Tachyon Tongs' architecture remains stable and well-documented by mandating the use of Architecture Decision Records (ADRs) for all significant technical mutations.

## Core Rules
1. **Mandatory Documentation**: BEFORE implementing any change that modifies directory structures, security core components (`tachyon/core/`), or cross-agent communication protocols, an ADR MUST be proposed.
2. **Consistency check**: All ADRs must reside in `docs/adr/` and follow the `NNNN-slug.md` naming convention.
3. **Sequential Integrity**: Never skip a number in the ADR sequence.
4. **Trigger Workflow**: Use the `/adr` workflow to generate new records.

## Significant Changes Definition
A change is "significant" if it:
- Introduces a new top-level directory.
- Modifies the `StateManager` schema or integrity logic.
- Adds/Removes a member of the Guardian Triad.
- Changes the primary telemetry or logging format.
- Impacts "Apple Silicon Native" performance guarantees.
