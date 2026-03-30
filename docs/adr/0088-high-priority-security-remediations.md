# ADR-0088: High Priority Security Remediations (AST & Identity Hardening)

## Status
Accepted

## Context
The Security Audit Report of 2026-03-29 flagged four high-priority logic bypasses occurring at critical trust boundaries (VX-04 through VX-07). Specifically:
* The Immunologist bypassed Orchestrator invocation because of a missing decorator.
* The test-mode identity heuristic persistently saved derived developer certificates to disk, yielding privilege-escalation vectors.
* The Pathogen's static analysis relied on string-based heuristics easily defeated via indirect imports.
* The SBOM verification fell back to a hardcoded local developer path instead of environment-based resolution.

## Decision
We enforce the following architectural rules:
1. **Dynamic Sandboxing via AST**: Substring heuristics for security sandboxing (M-06) are officially deprecated. All code evaluations now utilize the Python `ast` module, crawling trees to detect forbidden identifiers irrespective of string obfuscation. 
2. **Strict Test Environment Declarations**: `TACHYON_TEST_MODE=1` will actively invoke a `RuntimeError` (`SECURITY_VIOLATION`) if `TACHYON_ENV == "production"` is present, ensuring test identity scaffolding cannot bleed into deployed environments. Test identities are constrained specifically to `save_to_disk=False` to preserve ephemeral integrity.
3. **Registry Decorators**: Orchestrator visibility is required globally.
4. **Environment-driven SBOM**: The SBOM path resolution strictly checks `TACHYON_SBOM_PATH` utilizing fail-closed (`RegistrationError`) architecture during validation misses.

## Consequences
- **Positive**: Eradicates tool-call obfuscation bypasses during variant synthesis and secures node identity generation from exploitation.
- **Negative**: AST parsing invokes minor computational and edge-case syntax overhead compared to string scans, but the tradeoff is essential for secure-grade static analysis.
