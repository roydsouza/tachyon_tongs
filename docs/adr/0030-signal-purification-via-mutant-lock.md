# ADR-0030: Signal Purification via Mutant Lock

## Status
Proposed/Signed

## Context
As the **Engineer Agent** evolved to apply surgical patches autonomously, the **GuardianIDS** correctly signaled these as "Unauthorized Mutations." While technically accurate, this created high-frequency "Alarm Fatigue" for operators. We needed a way to cryptographically distinguish between a hostile tamper and a legitimate agentic evolution.

## Decision
We implement a **Mutant Lock** protocol:
1.  Before any mutation (patch application), the Engineer must create a `.mutant.lock` file containing the task metadata (CVE ID, Timestamp, Agent ID).
2.  The Engineer must sign this lock file using its delegated PQC certificate.
3.  The **GuardianIDS** is updated to recognize the `.mutant.lock`. If present and valid (signature matches the task), the Guardian downgrades the status from `CRITICAL_VIOLATION` to `MUTATING`.
4.  The lock is atomically removed upon task completion.

## Consequences
- **Positive:** Purifies the integrity signal; operators only receive critical alerts for truly unknown mutations.
- **Positive:** provides a clear cryptographic trace of "Who changed what and why" in the forensic ledger.
- **Neutral:** Adds a small I/O and cryptographic overhead to the patch cycle.

---
*Signed by: Hybrid Root Authority*
*Merkle Inclusion: Phase 27 Hardening*
