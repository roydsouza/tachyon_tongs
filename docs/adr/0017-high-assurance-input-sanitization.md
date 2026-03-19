# ADR-0017: High-Assurance Input Sanitization & Redaction

## Status
Accepted

## Context
Prompt injection and PII leakage are primary threats to agentic security substrates. Initial implementations relied on model-level instructions, which are susceptible to bypass.

## Decision
We will implement a mandatory, pre-policy **Input Sanitization Layer** (`tachyon/core/sanitizer.py`) for all agents.
1.  **Normalization**: Mandatory NFKC normalization to collapse homographs and control characters.
2.  **PII Redaction**: Regex-based scrubbing of emails and sensitive identifiers.
3.  **XSS Protection**: Stripping of `<script>` tags and HTML elements.
4.  **Injection Gating**: Blocking or neutralizing known adversarial prefixes (e.g., "Ignore previous instructions").

## Consequences
- **Positive**: Hard defense against common prompt injection; significant reduction in accidental PII exfiltration.
- **Negative**: May interfere with legitimate reasoning tasks that involve discussing "instructions" or "policy."
- **Verification**: Mandatory integration in `BaseTachyonAgent`. Checked via `tests/core/test_sanitizer.py`.

## Integrity Attestation
```json
{
  "adr_id": "ADR-0017",
  "hash": "sha256:7030f30f352790fcd7c8ee9daee65dfebd4ab6f544ae33e7d582bc0edfe42202",
  "status": "SIGNED",
  "signer": "tachyon-substrate-v1"
}
```
