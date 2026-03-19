# ADR-0007: Adaptive Rate-Limiting for Substrate Tools

## Status
Proposed (Phase 15)

## Context
As Tachyon Tongs manages multiple autonomous agents, there is a high risk of "Agentic Loops" (infinite tool-calling recursion) or intentional abuse (DoS attacks against the substrate or external APIs). We need a deterministic layer to throttle requests before they consume significant compute or network resources.

## Decision
We are implementing an **Adaptive Rate-Limiting** middleware within the `ToolRouter`.

1. **Window-Based Throttling**: Each agent/tool combination will have a sliding window counter (requests per minute).
2. **Pluggable Middleware**: The `RateLimiter` will be a standalone class in `tachyon/enforcement/rate_limiter.py`, injected into the `ToolRouter`.
3. **Fail-Fast**: Requests exceeding the threshold will be dropped immediately with a `status: BLOCKED` and a specific rate-limit error message.
4. **Adaptive Readiness**: While initial thresholds are static, the structure will support dynamic adjustments based on system load or quota status (Phase 20).

## Consequences
- **Positive**: Prevents cascading failures from looping agents; protects external API quotas; improves substrate stability.
- **Negative**: Adds a small lookup overhead to every tool call; may require fine-tuning to avoid blocking legitimate high-burst workloads (e.g., parallel data processing).

## Integrity Attestation

```json
{
  "adr_id": "ADR-0007",
  "hash": "sha256:8f0ae177f7b4e61e1f5b4e8978457aa75a3a31d0d20caeadfd81bf87380eb95d",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
