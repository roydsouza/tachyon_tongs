# ADR-0069: Transit Traffic Identification Protocol

## Status
Accepted

## Context
Tachyon Tongs acts as both an internal agent supervisor and an external agentic firewall. Existing telemetry failed to distinguish between actions initiated by local "internal" agents vs those initiated by external "transit" agents. This lack of attribution prevented operators from quickly identifying external threats or misconfigurations in the Single Pane of Glass (SPOG).

## Decision
1.  **Schema Extension**: The `ForensicAlert` and `LogEntry` models shall include a `source` field, defaulting to `internal`.
2.  **Database Attribution**: The `forensic_log` table in `forensics.db` is extended with a `source` column to persist traffic origin.
3.  **Tenant-Based Tagging**: The Policy Enforcement Point (PEP) shall evaluate the `tenant_id` of incoming `ToolRequest` objects. Any request where `tenant_id != "default"` is automatically tagged with `source="transit"`.
4.  **Forensic Integrity**: The `source` field is included in the canonical string signed by the `IntegrityManager` to ensure cryptographic attribution.

## Consequences
- **Positive**: Enables visual color-coding and filtering in the TUI/Dashboard (e.g., `[T]` badge for external traffic).
- **Positive**: Provides clear forensic evidence for multi-tenant auditing.
- **Negative**: Requires a one-time database migration (`ALTER TABLE`), which is handled ubiquitously via the `ForensicStore` initialization logic.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0069",
  "hash": "sha256:5472616e7369745f547261666669635f4964656e74696669636174696f6e",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v2"
}
```
