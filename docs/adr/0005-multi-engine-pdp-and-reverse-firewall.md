# ADR-0005: Multi-Engine PDP & Reverse Firewall (Outbound DLP)

## Status
Proposed (Phase 12.2)

## Context
As Tachyon Tongs evolves from a passive observer to an active security substrate, we need a robust mechanism to enforce policies bi-directionally. 
1. **Inbound**: Preventing agents from fetching malicious payloads or interacting with known exploit C&C servers.
2. **Outbound**: Preventing data leakage (PII, API Keys, Secrets) from the agentic workspace to external endpoints.

The existing Single-Engine OPA setup was insufficient for high-assurance environments requiring defense-in-depth and multi-vendor policy formats (e.g., AWS Cedar).

## Decision
We are implementing a **Multi-Engine Policy Decision Point (PDP)** architecture within the `Singularity` framework and a **Reverse Firewall** (Outbound DLP) in the Substrate Daemon.

1. **Singularity Multi-Engine Resolver**:
    - Federates evaluation across multiple engines (Rego/OPA and AWS Cedar).
    - Enforces an `ANY_DENY` consensus: If any engine denies an action, the substrate blocks it (Fail-Closed).
    - Logic is encapsulated in `tachyon/policy/singularity.py`.

2. **Reverse Firewall (Outbound DLP)**:
    - Injects an interception layer in the `ToolRouter` for outbound actions (`send_message`, `safe_fetch`).
    - Uses a `PIIScanner` (`tachyon/pipeline/pii_scanner.py`) to perform regex-based detection of sensitive tokens.
    - Policies for DLP are managed in `policies/rego/manual/dlp.rego`.

## Consequences
- **Positive**: Higher assurance through multi-engine consensus; reduced risk of secret exfiltration.
- **Negative**: Increased latency per tool call due to multi-engine evaluation (mitigated by asynchronous execution).
- **Maintenance**: Requires maintaining multiple policy sets (Rego and Cedar) for the same threat vectors.
