# ADR-0057: Mutant Lock Service Integration

## Status
Accepted

## Context
During the Get-Well substrate remediation phase, it was observed that the **Guardian** agent generated false-positive `STATE_COMPROMISED` alerts when the **Engineer** agent applied authorized patches. This happened because the files were mutated on disk before they were re-signed, causing a temporary integrity mismatch.

## Decision
1.  Implement a **Mutant Lock Service** (via `MutantLockManager` and `StateManager`) to facilitate "authorized mutation windows".
2.  The **Engineer** agent must acquire a time-bound, signed mutant lock token before performing any substrate modifications.
3.  The **Guardian** agent (`verify_file` and `verify_substrate` actions) must check the status of the Mutant Lock before emitting high-priority security alerts.
4.  If a lock is active, integrity violations are downgraded to `WARNING` status and the `STATE_COMPROMISED` alert is suppressed.
5.  All lock acquisitions and releases are recorded in the `EVOLUTION.md` ledger for forensic auditability.

## Consequences
- **Positive**: Eliminates signal noise and false positives in the security alert hub during maintenance.
- **Positive**: Maintains high-fidelity forensic logs even during authorized modifications.
- **Negative**: Adds a dependency on the lock service status during verification sweeps.
- **Negative**: Risk of lock contention if an agent fails to release a lock (mitigated by mandatory TTL).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0057",
  "hash": "sha256:243d66ff873959efe10df61149385d2a3cbff195972fb4839fabcfa76b1f068c",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
