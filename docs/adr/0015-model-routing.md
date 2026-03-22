# ADR-0015: Substrate-Aware Model Routing (Quota Management)

- **Status**: Proposed
- **Date**: 2026-03-18
- **Author**: AntiGravity Agent
- **Tags**: #architecture #security #quota #routing

## Context

To prevent "Quota Blackouts" and ensure the long-term operational integrity of the Tachyon Tongs substrate, we require a mechanism to autonomously manage token consumption. High-reasoning models (Pro/Ultra) should be reserved for security-critical tasks, while routine operations should be routed to cost-effective alternatives.

## Decision

We will implement an autonomous **ModelRouter** integrated into the **SubstrateDaemon**.

1.  **Complexity-Based Routing**: Tasks will be classified into L1 (Reconnaissance), L2 (Verification), and L3 (Mutation/ADR) based on prompt analysis.
2.  **Model Matrix**: 
    - L1/L2 -> `gemini-3-flash` (or local `mlx_lm` instance).
    - L3 -> `gemini-3.1-pro` / `ultra`.
3.  **Low-Power Mode (LPM)**: A global threshold (15% quota) will trigger an automatic shift to the lowest-cost model for all tasks.
4.  **Fallback Mechanism**: The router will support prioritized fallbacks (e.g., Gemini Flash -> Local LLM) to ensure zero-latency execution even under provider failures.

## Consequences

- **Pros**: Significant token cost reduction, increased resilience to api failures, guaranteed availability for critical ADRs.
- **Cons**: Increased logic complexity in the daemon, potential performance hit if complexity detection is slow.

## Integrity Attestation

```json
{
  "adr_id": "ADR-0015",
  "hash": "sha256:7f9c3e8a2b5d4f1a6c..." ,
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
