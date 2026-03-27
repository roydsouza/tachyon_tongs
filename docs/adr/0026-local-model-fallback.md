# ADR-0026: Local Model Fallback & Routing

## Status
Proposed (Pending Review)

## Context
The Tachyon Tongs substrate currently relies on external LLM APIs (e.g., Google Gemini, OpenAI, Anthropic) via the `ModelRouter`. While effective, this creates a dependency on external connectivity and poses a risk to "High-Assurance" operations if the internet is compromised or if sensitive data cannot leave the local M5 sandbox.

To achieve true autonomy and resilience, the substrate must have a "Local Reasoning Substrate" (LRS) capable of performing tool-routing and safety-checks completely offline.

## Decision
We will implement the **Local Reasoning Substrate (LRS)** using `mlx_lm` optimized for Apple Silicon M5.

1.  **Local Model Provider**:
    - A new `LocalModelProvider` class will be added to the `ModelRouter`.
    - It will wrap the `mlx_lm` process to perform inference on MLX converted models.
    - Default model: **Llama-3.1-8B-Lexi-GGUF (Q5_K_M)** for optimal size/performance on 24GB RAM.

2.  **Fallback Strategy**:
    - The `ModelRouter` will be extended with an `execution_mode` parameter.
    - `MODE_HYBRID`: Try cloud, fallback to local on failure (default).
    - `MODE_LOCAL_ONLY`: Force local reasoning for AIRP (Phase 22) or other high-assurance tasks.
    - `MODE_CLOUDS_ONLY`: Standard cloud-only execution.

3.  **Hardware Acceleration**:
    - inference MUST use `GGML_METAL=ON` to leverage the M5 GPU via the `-ngl 99` flag.

## Technical Requirements
- Models must be stored in `/Users/rds/antigravity/wormhole/mlx_lm/models/`.
- The `LocalModelProvider` must handle token streaming and JSON-mode forcing where possible (via GBNF grammars).

## Consequences
- **Positive**: Complete offline capability for core substrate features.
- **Positive**: Zero-latency for simple reasoning tasks.
- **Negative**: Increased local resource consumption (CPU/GPU/RAM) during inference.
- **Negative**: 8B models may have slightly lower reasoning accuracy than cloud frontier models (Gemini 1.5 Pro).

---
*Signed by: Sentinel Agent*
*Date: 2026-03-20*


## Integrity Attestation

```json
{
  "adr_id": "ADR-0026",
  "hash": "sha256:4254b854dc3ea5ade72cb57b9b70f01bb851e8855b5e5e22a01cd47462841bf8",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
