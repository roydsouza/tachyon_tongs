# ADR-0084: The Watcher Agent (Capability Verification)

## Context
As the collective grows, ensuring that agents stay within their delegated capability bounds is critical. Manual policy checks are insufficient for autonomous multi-hop reasoning chains. We need a dedicated security agent that audits all actions against cryptographic delegation certificates in real-time.

## Decision
We implement **The Watcher**, an autonomous security plugin that:
1.  Subscribes to all `ACTION_COMPLETED` events.
2.  Extracts the agent's delegation certificate from the event envelope.
3.  Verifies the PQC signature of the record against the certificate.
4.  Compares the `action` taken against the `allowed_actions` list in the certificate.
5.  Emits a `WATCHER_CAPABILITY_VIOLATION` alert with high severity if a breach is detected.

## Consequences
-   **Security**: Provides runtime enforcement of the principle of least privilege.
-   **Observability**: Creates a high-fidelity audit trail for capability utilization.
-   **Performance**: Adds minimal latency to the background event processing loop.

## Status
Approved (Phase 4)
