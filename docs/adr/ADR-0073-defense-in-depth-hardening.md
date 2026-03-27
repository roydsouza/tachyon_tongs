# ADR-0073: Substrate Defense-in-Depth Hardening (H-01 to H-07)

## Status
Proposed (2026-03-27)

## Context
The Tachyon Tongs substrate audit identified 7 "High Severity" vulnerabilities that could lead to resource exhaustion (H-01), policy bypass via synonyms (H-03), data exfiltration (H-04, H-05), and identity confusion (H-07). While the core `CRITICAL` issues (C-01 to C-03) have been remediated, these secondary layers are essential for real-world adversarial resilience.

## Decision
We will implement a multi-layered defense strategy addressing each high-severity finding:

### 1. PEP Throttling (H-01)
- Deploy `AdaptiveRateLimiter` at the entry point of `PEPLayer.execute`.
- Prevent agent-driven DoS attacks or infinite tool-call loops.

### 2. Transactional Integrity (H-02)
- Enforce database transactions (`BEGIN IMMEDIATE`) during whitelist checks to prevent TOCTOU races between policy evaluation and substrate mutation.

### 3. Conceptual Alignment (H-03)
- Enhance `AlignmentPDP` using a **Conceptual Vectorizer**. 
- Map synonyms to shared semantic dimensions to prevent bypasses via semantic reframing (e.g. "fetch" vs "retrieve").

### 4. Recursive PII/Entropy Detection (H-04)
- Hardened `PIIScanner` with recursive Base64/Hex decoding and Shannon Entropy analysis.
- Detect high-randomness payloads (>4.5 bits) that suggest encrypted or encoded exfiltration.

### 5. SafeFetch Redirect Gating (H-05)
- Implement strict subdomain matching and parameter-based redirect detection.
- Block "Open Redirect" chains (e.g. `trusted.com/q=malicious.com`).

### 6. Signature Integrity Enforcement (H-06)
- Enforce structured JSON signatures (ML-DSA-65) in `HybridSigner`. Reject stripped or malformed signatures.

### 7. Process-Identity Binding (H-07)
- Bind cryptographic identities to specific process command lines.
- Prevent a lower-privileged agent (e.g., `Scout`) from assuming the keys of an elevated agent (e.g., `Engineer`) at runtime.

## Consequences
- **Security**: Significantly reduces the attack surface for advanced adversaries.
- **Performance**: Negligible overhead for rate-limiting and entropy checks.
- **Complexity**: Marginal increase in the signing layer to support process binding.

## Signature
- **Signed By**: AntiGravity (Gemini Flash)
- **Identity**: `tt-agent-antigravity-001`
- **Method**: Hybrid PQC (ML-DSA-65)
