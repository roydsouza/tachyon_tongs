# ADR-0046: Sentry Honeypot Alert Signing Refactor

## Status
Accepted

## Context
During the Get-Well audit (Priority 1), we discovered that the `SentryPlugin` was emitting critical security alerts (honeypot triggers) with a hardcoded `signature="CRITICAL"` string literal. As established in ADR-0043 (Hybrid PQC Mandate), the EventBus verifier rejects any event that does not carry a valid cryptographic signature or delegation certificate. Consequently, all intrusion alerts from the Sentry agent were being silently suppressed by the bus, creating a critical security blindspot.

## Decision
1. Remove the legacy `signature="CRITICAL"` parameter from all `emit_event` calls in `SentryPlugin`.
2. Replace it with `certificate=self.certificate`, passing the agent's PQC-signed delegation certificate.
3. This ensures that every intrusion alert is cryptographically anchored to the agent's identity and verifiable by the `IntegrityManager`.

## Consequences
- **Positive**: Restores visibility into substrate intrusions.
- **Positive**: Aligns Sentry alerts with the substrate's zero-trust architectural mandates.
- **Negative**: None identified.


## Integrity Attestation

```json
{
  "adr_id": "ADR-0046",
  "hash": "sha256:287e4bc2e52948e979ddf45b4362404338d78e1643c9a474e7d48e6a1cad7328",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
