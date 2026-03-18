# ADR-0012: State Layer Hardening & Integrity Gating

## Status
Proposed

## Context
The `StateManager` handles persistent execution logs and the `EXPLOITATION_CATALOG.md`. While detached signatures existed, enforcement was inconsistent across different runtime modes. Additionally, sensitive data in logs (e.g., scraped payloads) was stored in plain text, posing a risk of telemetry leakage.

## Decision
Harden the state management layer with strict runtime integrity gating and field-level encryption hooks.

1. **Strict Integrity Gating**: Introduce `TACHYON_STRICT_MODE`. When enabled, any integrity failure (wrong signature or missing signature) in the catalog will cause a hard runtime halt rather than just an alert.
2. **Field-Level Encryption**: Implement `_encrypt_field` and `_decrypt_field` hooks in `StateManager`. Use `TACHYON_ENCRYPT_LOGS` to toggle encryption for sensitive payloads at rest.
3. **Engine Abstraction**: Refactor `SingularityPDP` to use a class-level `_registry`, moving away from hardcoded engine lists to support pluggable policy engines.

## Consequences
- **Resilience**: Prevents the substrate from operating on a compromised knowledge base in strict environments.
- **Privacy**: Protects harvested threat intelligence from unauthorized local access.
- **Extensibility**: Simplifies the addition of new policy engines (e.g., Cedar, OPA variants).
