# ADR-0059: High-Assurance Environment Synchronization

## Status
Accepted

## Context
The Tachyon Tongs substrate previously used redundant dependency manifests (`requirements.txt` and `pyproject.toml`) which led to inconsistencies. Furthermore, the search for macOS-specific PQC and Keychain headers caused noisy `UserWarning` failures in headless or test environments (such as CI/CD or specialized agent execution contexts), masking legitimate cryptographic errors.

## Decision
1.  **Unify Manifests**: Consolidate all core and development dependencies into a single, premium `pyproject.toml`.
2.  **Native Security Integration**: Add `pyobjc-framework-Security` as a conditional dependency for macOS (`sys_platform == 'darwin'`) to ensure native Keychain access is always available in the primary target environment.
3.  **Headless Resilience**: Hardened `KeychainProvider` to recognize `TACHYON_HEADLESS=1` or `TACHYON_TEST_MODE=1`. In these modes, noisy hardware-loading warnings are suppressed unless `TACHYON_STRICT_MODE=1` is explicitly set.
4.  **Purge Redundancy**: Delete `requirements.txt` to ensure `pip install -e .` is the sole source of truth for the substrate environment.

## Consequences
- **Positive**: Provides a single, clean entry point for substrate installation and development.
- **Positive**: Enables "Silent but Strong" testing where environmental warnings don't clutter high-signal forensic logs.
- **Positive**: Ensures that production environments (where `STRICT_MODE` is active) still fail-loudly if keys are missing.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0059",
  "hash": "sha256:9d6f9717ea4498803d7d372bfc8e73ec082d4a1bf9254517500523ea200e8bd5",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
