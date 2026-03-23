# ADR-0034: The Mutant Lock Pattern (Signal Purification)

## Status
Proposed

## Context
The **Guardian IDS** monitors the substrate for unauthorized filesystem mutations. However, legitimate effector agents (e.g., the **Engineer** applying a patch) also modify the filesystem. Currently, this creates a race condition where the Guardian triggers a false positive (`STATE_COMPROMISED`) before the effector agent can signal its legitimacy.

This "Signal Noise" degrades the reliability of the substrate and causes unnecessary alert fatigue.

## Decision
We will implement the **Mutant Lock** pattern:

1.  **Lock Acquisition**: Any agent needing to mutate the substrate must first request a `MutantLock` from the `StateManager`.
2.  **Signed Token**: The `StateManager` issues a time-bound, cryptographically signed token (using the substrate's PQC keys).
3.  **Guardian Awareness**: The `Guardian` (and its verification plugins) must check for an active, valid `MutantLock` before raising an integrity alert.
4.  **Auto-Expiry**: Locks expire automatically after a predefined window (default: 5 minutes) to ensure that the substrate doesn't remain "unprotected" if an agent crashes during mutation.
5.  **Forensic Recording**: Every lock acquisition and release is recorded in the `EVOLUTION.md` ledger.

## Consequences
- **Positive**: Eliminates false positives during legitimate patching/maintenance.
- **Positive**: Provides a clear forensic trail of *who* intended to change the state.
- **Risk**: A compromised agent holding a `MutantLock` could hide its malicious mutations for the duration of the lock.
- **Mitigation**: Locks are strictly time-bound and associated with specific agent identities.
