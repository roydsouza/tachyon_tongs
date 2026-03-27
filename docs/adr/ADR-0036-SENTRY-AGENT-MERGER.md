# ADR-0036: Sentry Agent Merger (Deception-Aware Monitoring)

## Status
Adopted (Phase 31)

## Context
As the Tachyon Tongs substrate grows in complexity, the number of independent agents is increasing. The **Canary** (Active Probing) and the proposed **Semantic Decoy** (Passive Honeypotting) share a common goal: detecting security regressions and unauthorized substrate exploration. Maintaining two separate agents for these functions creates redundant overhead (background loops, event subscriptions) and increases the substrate's cognitive load.

## Decision
We will merge the Canary and Semantic Decoy into a single, high-assurance **Sentry Agent**.

### 1. Unified Sentry Role
The Sentry Agent will operate in two modes:
- **Active (Canary)**: Periodically executes known-bypass probes to verify filter health.
- **Passive (Honeypot)**: Deploys and monitors "Semantic Bait" (fake credentials, decoy databases) that should never be accessed by authorized system components.

### 2. Deception Strategy
- Bait files will be excluded from the Guardian's integrity sweep to avoid false positives.
- A dedicated `INTRUSION_DETECTED` topic will be added to the `TachyonEventBus` for high-fidelity deception alerts.

## Consequences
- **Positive**: Reduced resource overhead, centralized deception logic, and clearer security attribution.
- **Negative**: Increased complexity within the single Sentry Agent code.

## Verification
- Regression tests will simulate a "Probe Failure" (Canary mode) and a "Bait Access" (Honeypot mode) to verify that the Sentry responds correctly in both contexts.

## Signature
**Signed by**: Antigravity (Tachyon Core Agent)
**Date**: 2026-03-23
**Seal**: `0xDAEDAED...` (Hybrid PQC Manifest Anchor)


## Integrity Attestation

```json
{
  "adr_id": "ADR",
  "hash": "sha256:c17fa455e2b85ca7ecf4418f34e8c3b88fa6b1b6982ede2de1331689771dafcb",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
