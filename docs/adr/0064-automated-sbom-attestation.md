# ADR-0064: Automated SBOM Attestation Mandate

## Status
Accepted

## Context
With the graduation of the Supply Chain Defense (DB-backed whitelisting), it is critical that the approved software inventory is exportable in a standard, machine-readable format. This allows third-party auditors and downstream security tools to verify the substrate's dependency health without direct database access.

## Decision
1.  **CycloneDX Standard**: The substrate MUST support the generation of a Software Bill of Materials (SBOM) in the **CycloneDX v1.5** (JSON) format.
2.  **Cryptographic Anchoring**: Every generated SBOM MUST be cryptographically signed using the substrate's PQC-ready `IntegrityManager` (ML-DSA-65/Ed25519 hybrid).
3.  **Source of Truth**: The SBOM components MUST be derived directly from the `package_whitelist` table in the `StateManager` database.
4.  **Forensic Path**: The signed SBOM shall be stored in `forensics/SBOM.json` (and `SBOM.json.sig`).

## Consequences
- **Positive**: Enables "Zero-Trust" dependency verification for external systems.
- **Positive**: Prevents "Ghost Dependency" injection by providing an immutable record of active whitelisted packages.
- **Negative**: Requires periodic re-generation to remain synchronized with whitelist updates (mitigated by automation).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0064",
  "hash": "sha256:a69448681410e96df429557bc704ae44792e54e527f1930dd5f63be93cda3275",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
