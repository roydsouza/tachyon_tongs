# ADR-0051: Pathogen Daemon Crash Visibility

## Status
Accepted

## Context
The `run_pathogen.py` script, which serves as the entry point for the adversarial red-team sweep, was identified in the Get-Well audit (Priority 2) as having an observability blindspot. Because this script often runs as a background process (macOS LaunchDaemon), any unhandled exceptions during the metamorphic sweep would cause the daemon to terminate silently, with the only record existing in the system logs. This makes it difficult for the substrate's forensic agents to automatically detect when a security scan has stalled.

## Decision
1. Implement a top-level exception handler in the `__main__` entry point of `run_pathogen.py`.
2. On any uncaught exception, the handler will write a detailed forensic entry to `ALERT.md`, including a full traceback.
3. The exception will be re-raised after logging to ensure existing LaunchD failure monitoring still functions correctly.

## Consequences
- **Positive**: Restores forensic visibility into background daemon failures.
- **Positive**: Enables automated "Dead Man's Switch" logic in future phases by monitoring `ALERT.md` for daemon crashes.
- **Negative**: Adds a direct dependency on the root `ALERT.md` file from the script.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0051",
  "hash": "sha256:e2b4e57bae99e4bd4057b927443cd0e7ad283bf2e1da7c44feff2258cb6b9889",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
