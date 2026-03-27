# ADR-0062: Graduated Supply Chain Defense

## Status
Accepted

## Context
Initial implementations of the "Supply Chain Defense" (the package/domain whitelist) used hardcoded mocks or optional fallbacks. As the substrate evolves into an autonomous state-aware system, it is necessary to graduate this defense to a mandatory, database-backed verification mechanism that is cryptographically anchored to the substrate's manifest.

## Decision
1.  **Mandatory Whitelisting**: All agentic network operations performed via `SafeFetch` MUST pass an `is_package_whitelisted` check against the `package_whitelist` table in the `StateManager` database.
2.  **Fail-Loud Enforcement**: Any attempt to access a domain not present in the authorized whitelist is treated as a `SUPPLY_CHAIN_VIOLATION` and MUST be escalated to the central `ALERT.md` hub with full forensic context (agent_id, targeted domain).
3.  **Removal of Mocks**: The `rego_mock` fallback is disabled by default in all production and high-assurance contexts, ensuring that if the database is inaccessible, network operations fail-closed.
4.  **Cryptographic Anchoring**: The whitelist is synchronized with the substrate's Merkle tree-signed MANIFEST.json, ensuring that an attacker cannot spoof the whitelist by modifying the SQLite database without triggering an integrity alarm.

## Consequences
- **Positive**: Prevents "Supply Chain Squatting" and "Hallucination-Born Exfiltration" by restricting agents to a verified set of domains.
- **Positive**: Provides permanent forensic evidence of unauthorized tool use.
- **Negative**: Adds a small performance overhead for DB-lookup on each fetch request (mitigated by SQLite WAL mode and indices).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0062",
  "hash": "sha256:0c7c2ebbc9a237b4b5a057bdcd643b7a736e77a7eb526b2dd0cba567b8c6402b",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
