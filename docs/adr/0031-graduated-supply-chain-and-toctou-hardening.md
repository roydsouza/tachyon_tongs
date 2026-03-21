# ADR-0031: Graduated Supply Chain & TOCTOU Hardening

## Status
Proposed/Signed

## Context
Phase 26.2 relied on "stub" logic for some critical security gates (e.g., `is_package_whitelisted` returning `True`). Additionally, tool requests were vulnerable to "Double Fetch" or TOCTOU attacks where an agent could modify parameters after policy evaluation but before execution.

## Decision
1.  **Supply Chain Defense:** Graduate the `is_package_whitelist` stub to a real SQLite check against the `package_whitelist` table. This table is synced directly from the **Signed Merkle Manifest**.
2.  **TOCTOU Hardening:** enforce deep immutability in `ImmutableToolRequest`. We use `recursive_freeze` with `MappingProxyType` and `tuple` to ensure that even nested JSON dictionaries cannot be mutated post-acceptance.
3.  **Log Archival:** Implement automated pruning of `RUN_LOG.md` at the 100KB threshold to prevent "Log Fog" and ensure performant indexing by the **Auditor Agent**.

## Consequences
- **Positive:** Eliminates high-priority security gaps identified in the Claude/Grok/Gemini audit.
- **Positive:** increases substrate resilience against advanced memory-munging and bypass techniques.
- **Neutral:** increases strictness of the supply chain; new packages must be formally added to the MANIFEST.

---
*Signed by: Hybrid Root Authority*
*Merkle Inclusion: Phase 27 Hardening*
