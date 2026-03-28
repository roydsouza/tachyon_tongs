# ADR-0081: Reliability: EventBus Loop Guard (Circuit Breaker)

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: As agents interact autonomously via the `TachyonEventBus` (e.g., in the Debate Arena), the risk of cascading argumentation loops increases. Adverrsarial or misbehaving agents can saturate the bus with identical event payloads, exhausting memory, disk (SQLite-WAL), and processing overhead.

---

## 🧭 Decision

We implement a mandatory **Loop Guard (Circuit Breaker)** in the substrate's event broker (`tachyon/core/bus.py`).

### 1. Sliding-Window Event Tracking
- **Topic Fingerprinting**: Track event frequency by hashing the combination of `topic` and `payload_json`.
- **Temporal Window**: Maintain a memory-pinned cache of event timestamps over a sliding 300-second window.

### 2. Consensus Ceiling & Suppression
- **Threshold**: Define a hard "Consensus Ceiling" (Default: 3 identical events).
- **Circuit Breaker**: If the threshold is reached within the temporal window, subsequent emissions are suppressed (returning `-1`) and a `SECURITY_ALERT_LOOP` is emitted via the `StateManager`.

---

## 🧬 Consequences

### ✅ Positive
- **Reliability Sovereignty**: Protects the substrate's communication backbone from resource-draining loops.
- **Fail-Loud Fault Detection**: Automatically identifies and flags misbehaving agents to the administration tier.

### ⚠️ Negative
- **Memory Pressure**: The in-memory cache of event hashes adds minor memory overhead (mitigated by automated stale-event purging).
- **Suppression Edge-Cases**: Low-frequency repetitive tasks (e.g., heartbeats with 0.1Hz frequency) must ensure their interval is outside the suppression logic window.

---

## 🛠️ Performance Mandate
- Stale events MUST be purged from the cache on every `emit_event` call for that fingerprint.
- Hash computation MUST be constant-time where possible.
