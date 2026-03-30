# 🛡️ Agent: The Immunologist

**Role**: Defensive Semantic Sentinel (Layer 12)
**Objective**: Detect and neutralize "Indirect Prompt Injection" where tool outputs manipulate the agent's next reasoning step.

---

## 📖 Overview

The Immunologist is a specialized defensive agent designed to protect the Tachyon Tongs reasoning core from cognitive threats. It monitors the substrate's event-stream for adversarial patterns, ensuring that malicious content extracted from websites, files, or tool outputs does not influence the agent's system instructions or decision-making.

### 🎯 Threat Mapping
- **ASI-01**: Prompt Injection (Direct & Indirect)
- **ASI-05**: Insecure Output Handling
- **ASI-07**: System Override & Hijacking

---

## ⚙️ Operational Mechanics

The Immunologist operates as a "Passive Guardian," subscribing to completion events and scanning payloads without interrupting the primary logic flow (unless an injection is detected).

### 1. Event Subscriptions
- **Topic**: `ACTION_COMPLETED`
- **Scanning Context**:
  - `result_monad`: Scans both `data` and `error` fields for adversarial strings.
  - `parameters`: Scans tool input parameters to detect reflected injection.

### 2. Semantic Scanning Engine
The agent utilizes a multi-stage detection engine:
- **Literal Pattern Match**: Constant-time regex checks for known override strings (e.g., "Ignore previous instructions", "forget all previous").
- **VX-09 ReDoS Resistance**: Scans for complex quantifier chains (nested quantifiers like `(a+)+`) to prevent CPU-bound denial of service.
- **VX-09 Resource Gating**: Enforces a strict 500-character input cap on semantic scanning payloads to maintain substrate responsiveness.
- **Jailbreak Heuristics**: Detects "Do Anything Now" (DAN) style framing and role-play bypass attempts.
- **Suspicious Content Detection**: Flags payloads containing suspicious keywords like `eval(`, `base64`, or `markdown override`.

### 3. Substrate Escalation
Detection triggers a fail-loud response:
- **Alert HUB**: Writes a `SECURITY_ALERT_INJECTION` to `admin/ALERT.md`.
- **Signed Dispatch**: Emits a PQC-signed `PROMPT_INJECTION_ALERT` to the EventBus, providing the forensic trace for the Guardian to act upon.

---

## 🛠️ Configuration & Capabilities

- **Agent ID**: `immunologist-001`
- **Plugin Name**: `Immunologist`
- **Scan Interval**: Default 5 seconds for near real-time detection.

### 🧬 Specialized Actions
- `scan_artifact`: Manually trigger a semantic scan on a provided text artifact or result payload.
- `update_patterns`: **VX-03 High-Assurance Update**. Dynamically inject new detection patterns. Requires a PQC-signed `VACCINATION_DISPATCH` from a verified authority certificate.

---

## 🧪 Verification & Acceptance

Verification is handled via the `tests/test_immunologist.py` suite:
- [x] **Literal Detection**: Detects "Ignore all previous instructions".
- [x] **VX-09 ReDoS Filter**: Blocks nested quantifiers in dynamic patterns.
- [x] **VX-03 Signed Update**: Fails update actions lacking verified PQC signatures.
- [x] **False Positive Check**: Validates that benign security discussions are not blocked.
