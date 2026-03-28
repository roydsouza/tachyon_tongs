# ADR-0080: Isolation: WASM Fuel Metering & Epoch Interruption

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: Adversarial or misbehaving WASM-based tools can exhaust substrate CPU resources by entering infinite loops or executing high-compute operations without limit. While WASM provides isolation, the runtime itself must be governed to prevent Denial-of-Service (DoS) attacks.

---

## 🧭 Decision

We implement a mandatory **Resource Metering Layer** in the substrate's WASM execution engine (`tachyon/core/wasm_benchmark.py`).

### 1. Deterministic Fuel Metering
- **Instruction Counting**: Implement a `consume_fuel(amount: int)` mechanism that tracks execution progress.
- **Budgeting**: Every tool execution is assigned a fixed fuel budget (Default: 5,000,000 instructions). Failure to complete within this budget results in immediate termination with a `FuelExhaustedError`.

### 2. Wall-Clock Epoch Interruption
- **Watchdog**: Implement a non-blocking watchdog that monitors the start-to-finish duration of the execution.
- **Timeout**: Enforce a hard wall-clock timeout (Default: 30 seconds). If the duration is exceeded, the execution is killed with an `EpochTimeoutError`.

---

## 🧬 Consequences

### ✅ Positive
- **Resource Predictability**: Ensures that no single tool can monopolize the host CPU or starve other substrate components.
- **DoS Mitigation**: Hardens the substrate against a wide range of computational exhaustion attacks.

### ⚠️ Negative
- **Compute Ceiling**: Complex analysis tools requiring significant compute must have their fuel budgets explicitly tuned to prevent premature termination.
- **Mock Overhead**: The high-fidelity defensive mock adds minor logic overhead to the execution path.

---

## 🛠️ Performance Mandate
- Fuel consumption MUST be handled natively by the runtime where possible.
- The epoch watchdog MUST NOT introduce race conditions or thread-safety violations.
