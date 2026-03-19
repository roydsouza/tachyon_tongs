# ADR-0022: Whitelisted Supply Chain Defense

## Status
Proposed -> **Accepted** (2026-03-19)

## Context
The `StateManager.is_package_whitelisted()` method was a stub that always returned `True`, effectively disabling the substrate's supply chain defense against hallucination squatting and dependency confusion.

## Decision
We will implement an active whitelist lookup mechanism.
1.  **Catalog Lookup**: The `is_package_whitelisted` method now queries the `exploitation_catalog` table.
2.  **Explicit Approval**: Packages are only considered whitelisted if they exist in the catalog with a `relevance_class` of `APPROVED`.
3.  **Fail-Closed**: If the package is unknown or has any other classification, it is blocked by default.

## Consequences
- **Security**: Preemptively blocks installation of non-vetted or malicious packages.
- **Control**: Operators can manually "approve" packages by adding them to the exploitation catalog with the `APPROVED` tag.
- **Friction**: New dependencies require an entry in the catalog before the agent can install them.
