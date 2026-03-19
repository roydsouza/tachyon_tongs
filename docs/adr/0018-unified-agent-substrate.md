# ADR-0018: Unified Agent Substrate (Phase 21.5)

## Status
Accepted

## Context
Tachyon Tongs has evolved into a "zoo" of independent agent scripts (Sentinel, Engineer, Guardian IDS). This fragmentation increases architectural surface area, leads to redundant security logic, and complicates forensic auditability. 

## Decision
We will consolidate all agents into a single, modular **Unified Agent Substrate**.
1.  **Core Base Class**: All agents will inherit from a refactored `BaseTachyonAgent` in `tachyon/agents/base.py`.
2.  **Role-Based Plugins**: Specialized logic (e.g., CVE harvesting, patch synthesis) will be implemented as modular "Roles" rather than monolithic scripts.
3.  **Unified Entry Point**: A single CLI controller (`tachyon/main.py`) will manage instantiation and role-switching.
4.  **Forensic Parity**: All roles will utilize the core `IntegrityManager` and `InputSanitizer` provided by the base class.

## Consequences
- **Positive**: Simplified security audits; 100% consistent forensic signing; reduced code duplication.
- **Negative**: Initial refactoring overhead; potential for "fat base class" anti-pattern if not carefully modularized.
- **Verification**: All existing agent tests must pass using the new `Role` abstractions.

## Integrity Attestation
```json
{
  "adr_id": "ADR-0018",
  "hash": "sha256:6c3c1b6413c2249d88d3484f2feb5e3c947a3327b41461e3ba8bf3fbf66e0218",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
