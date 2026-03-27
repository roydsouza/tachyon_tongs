# ADR-0066: Supply-Chain Oracle and Quarantine Auditor (v2)

## Context
The Tachyon Tongs substrate requires high-assurance infrastructure to defend against supply-chain injection and insecure artifact propagation. While the EventBus and PQC signatures provide runtime integrity, the "Point of Import" (Claw/pip) and "Staging" (Airlock) areas were previously under-monitored.

## Decision
We implement a dual-layer defense graduation for Phase 25:

1.  **Supply-Chain Oracle (Phase 25.1)**:
    - Enforces **SLSA Level 3** (or equivalent) provenance verification for all substrate imports.
    - Requires a signed attestation (JSON-LD) for every non-standard library package.
    - Persists attestations in the `package_attestations` vault within `StateManager`.

2.  **Quarantine Auditor (v2) (Phase 25.2)**:
    - A specialized agent plugin that performs live static and dynamic analysis on sandboxed payloads.
    - Audits the `quarantine/` directory for unsigned or tampered artifacts using the `IntegrityManager`.
    - Audits the `package_attestations` vault for cryptographic consistency against the Root of Trust.

## Status
**ACCEPTED**

## Consequences
- Every new package import must be accompanied by an attestation signature.
- The `tt status` dashboard now provides a "Supply Chain" metric (Verified vs. Whitelisted).
- The `Auditor` agent must possess a valid delegated identity (Anchored) to emit trusted alerts.

---
**Signed**: Hybrid Root (Ed25519 + ML-DSA-65)
