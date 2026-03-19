# ADR-0004: Cryptographic State Integrity & Alerting Hub

## Status
Accepted

## Context
Tachyon Tongs operates under a high-assurance model where the autonomous Sentinel agent identifies and catalogs threats. However, for the tool-using agent, the local state (specifically `EXPLOITATION_CATALOG.md` and the SQLite database) was vulnerable to "state malleability"—out-of-band modifications that could poison the agent's knowledge without detection. Additionally, there was a risk of "Catastrophic Design Flaws" if the agent autonomously modified its own source code without human oversight.

## Decision
We have implemented a two-fold security hardening layer:
1. **Cryptographic State Integrity**: All critical state changes (specifically the Exploitation Catalog) are now signed with HMAC-SHA256. The `StateManager` enforces mandatory signature verification during initialization, halting the substrate immediately if a mismatch is detected.
2. **High-Visibility Alerting (ALERT.md)**: A top-level high-visibility hub was created to capture critical substrate failures. This file uses reverse-chronological (LIFO) ordering to ensure the most recent security events are immediately visible to the operator.
3. **Airlock Enforcement**: Autonomous code mutations are now gated behind a mandatory "Airlock" (/tmp/tachyon_airlock/), requiring human-in-the-loop (HITL) review via the `airlock_cli.py` tool. This is a core component of the project's current **HITL Experimentation Phase**.

## Consequences
- **Positive**: Prevents state poisoning and unauthorized autonomous code mutations. Provides a centralized, robust notification system for security compromises.
- **Negative**: Increases operational friction by requiring manual approval of security patches and re-signing of state for recovery. Requires management of the `TACHYON_SECRET_KEY` environment variable for production environments.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0004",
  "hash": "sha256:ba36316597144847b30a19db5121f8b93f16654c9d45b6040b8b6c7654657f78",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
