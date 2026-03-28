# ADR-0078: Security: The Immunologist (Cognitive Injection Defense)

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: As agents perform autonomous tool-calling (e.g., web-scouring, file-scouring), the probability of encountering uncontrolled adversarial payloads increases. Prompt injection—specifically indirect injection via tool results—can manipulate the model's next reasoning step to override its system instructions or exfiltrate private data.

---

## 🧭 Decision

We recruit a specialized defensive agent, **The Immunologist**, to neutralize cognitive threats.

### 1. Event-First Backplane Monitoring
- **Topic Subscription**: The Immunologist subscribes to all `ACTION_COMPLETED` events on the `TachyonEventBus`.
- **Async Inspection**: It scans result payloads (`data`, `error`) and input parameters for adversarial patterns asynchronously, ensuring no latency impact on the primary reasoning chain.

### 2. Semantic Scanning Heuristics
- **Pattern Registry**: Implement regex-based literal matches for common override strings (e.g., "Ignore previous instructions").
- **Heuristic Scanning**: Identify suspicious markers in tool results (e.g., `DAN:`, `markdown override`, `new system prompt`).
- **Fail-Loud Alerting**: Every detection results in a substrate-level `SECURITY_ALERT_INJECTION` and a PQC-signed audit event.

---

## 🧬 Consequences

### ✅ Positive
- **Cognitive Resilience**: Hardens the substrate against the primary vector for agent hijacking (ASI-01).
- **Substrate Separation**: The defense logic is decoupled from the specific reasoning model, providing a resilient filter in front of the core LLM.

### ⚠️ Negative
- **Resource Overhead**: Requires a dedicated agent instance and minor EventBus traffic overhead.
- **Pattern Lag**: Signature-based regex scanning may lag behind novel, highly polymorphic prompt injection techniques (mitigated by future S-12/S-13 learning phases).

---

## 🛠️ Performance Mandate
- Scans MUST complete within 100ms per event to preventEventBus congestion.
- Pattern registry must be updatable via signed administrative dispatches.
