# ADR-0041: Alignment PDP (Policy Decision Point)

## Status
Proposed (Phase 41)

## Context
The current semantic alignment mechanism (`AlignmentChecker`) utilizes a keyword-based frequency vectorizer and cosine similarity to detect "Semantic Drift" between an agent's declared intent and its technical parameters. Security audits (Grok/Gemini 2026-03-23) have identified this as a high-severity bypass surface:
1.  **Probabilistic Fragility**: Simple word overlaps can be spoofed by "Reframing" (e.g., reframing `rm -rf /` as `cleanup temporary files`).
2.  **Intent Omission**: The current `ToolRouter` skips the check if the `intent` field is missing, effectively allowing a "Legacy Bypass."
3.  **Blind Single-Pass**: The check is performed as a static computation without the benefit of the substrate's cognitive reasoning capabilities.

## Decision
We will extract the alignment logic from the `ToolRouter` and formalize it as a standalone, pluggable **Alignment PDP** engine integrated directly into the **Singularity Meta-PDP** framework.

### 1. Singularity-Native Engine
The `AlignmentPDP` will reside in `tachyon/policy/checkers/alignment_pdp.py`, implementing the `PolicyEngine` interface. It will be registered as the `ALIGNMENT` engine type within `SingularityPDP`. This allows it to participate in the central `ANY_DENY` consensus loop alongside `REGO` and `CEDAR`.

### 2. Multi-Turn Adversarial Refinement
For high-stakes tool calls (e.g., `safe_execute`), the PDP will not rely on static scoring. Instead, it will trigger a "Reflection Loop":
*   The **Analyst Node** compares the `intent` vs. `params` using a local LLM (`mlx_lm`).
*   The **Reflector Node** (Phase 40) is invoked to attempt to "Bypass" the stated intent.
*   The action is only allowed if the alignment is semantically verified through cognitive reasoning.

### 3. Mandatory Intent Gating
The PDP will enforce a "Fail-Closed" policy for high-risk actions. If an `intent` field is missing for a sensitive tool, the request will be automatically denied.

### 4. Metal-Accelerated Embeddings
Transition from TF-IDF frequency vectors to dense vector embeddings using a local, Metal-accelerated model (e.g., `all-MiniLM-L6-v2` via MLX). This provides semantic understanding beyond keyword matching.

## Consequences
*   **Performance**: Semantic embedding and LLM refinement add latency (mitigated by Metal NRT acceleration).
*   **Reliability**: Significant reduction in "Semantic Drift" bypasses.
*   **Auditability**: Reasoning traces for alignment decisions will be stored in the `ActionRecord` for forensic review.
