# ADR-0044: Autonomous Threat Model Propagation

## Status
Proposed

## Context
Currently, the `THREAT_MODEL.md` is a semi-static document updated by human or agent intervention during specific architectural cycles. However, `CATALOG.md` is updated in real-time by the Sentinel and Pathogen agents. There is a "Cognitive Gaps" risk where the formal threat model trails behind actual adversarial discoveries.

## Decision
1. **ThreatModelUpdater**: Implement a substrate-level service that periodically queries the `ForensicStore` (SQL Ledger) for high-signal adversarial discoveries (Pathogen-detected breaches).
2. **Automated Synthesis**: The service will map these discoveries to the existing `ASI01-ASI11` categories in `THREAT_MODEL.md`.
3. **Forensic Linkage**: Every update to the threat model will include a canonical URI pointing to the specific forensic database record (e.g., `forensic:5031`) that justified the risk adjustment.
4. **PQC Anchoring**: The updated `THREAT_MODEL.md` will be re-signed by the Root PQC identity to ensure the entire propagation trail is tamper-evident.

## Consequences
- **Security**: Ensures the threat model is always current and data-driven.
- **Traceability**: Provides a direct "Audit to Action" path from the forensic ledger to the architecture.
- **Risk**: Automated documentation updates must be fail-closed to prevent an adversary from "overwriting" the threat model (mitigated by mandatory PQC re-signing).
