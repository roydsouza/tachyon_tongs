# ADR-0083: Privacy: Semantic Taint Tracking Policy

**Status**: [ACCEPTED]
**Date**: 2026-03-28
**Context**: Agents are autonomous and may handle sensitive data (e.g., API keys, PII) during their collective reasoning. If an agent is subtly compromised or falls victim to a prompt injection attack, it could attempt to exfiltrate this data via the `Herald` or other outbound channels.

---

## 🧭 Decision

We implement a **Semantic Taint Tracking & Redaction** mechanism in the substrate's enforcement tier (`tachyon/enforcement/taint.py`).

### 1. "Deep Secret" Pattern Registry
- **Sensitive Signatures**: Define regex-based patterns for common high-value secrets (OpenAI Keys, Google Cloud Keys, GitHub tokens, and Tachyon keys).
- **Extensibility**: The registry MUST allow for easy manual updates and autonomous discovery of new patterns.

### 2. Mandatory Taint Scanning (Taint-on-Relay)
- **Sanitization Layer**: The `HeraldPlugin` is updated to perform a "Taint Check" on every event summary before dispatching to external channels.
- **Auto-Redaction**: If a "Deep Secret" pattern is detected, it is immediately replaced with `[REDACTED_SECRET]`.
- **Fail-Loud Alerting**: Every detected exfiltration attempt triggers a `SECURITY_ALERT_TAINT` and is recorded in the Merkle-linked forensic ledger.

---

## 🧬 Consequences

### ✅ Positive
- **Exfiltration Resistance**: Neutralizes the primary goal of many prompt injection attacks (secret theft).
- **Data Leak Prevention**: Protects the substrate's high-value credentials from accidental exposure in logs or UI.

### ⚠️ Negative
- **Operational Blindness**: If an administrator needs to see a key for debugging, they must access the raw Database state directly (Redaction occurs ONLY on the relay/export path).
- **Pattern Maintenance**: Requires constant updates to the pattern registry as new API formats emerge.

---

## 🛠️ Performance Mandate
- Taint scanning MUST use pre-compiled regex for efficiency.
- Scanning MUST occur before any other sanitization (flattening, truncation) to prevent obfuscation.
