# Road Not Taken

This document formalizes architectural and implementation decisions where specific paths or technologies were considered but ultimately rejected. Documenting these "Roads Not Taken" prevents re-litigating design choices and provides historical context for future substrate iterations.

---

## 🏗️ Architecture & Core Logic

### 1. Signal Protocol for Remote Command & Control
- **Decision**: Rejected in favor of local CLI/NeoVIM, with Slack as a secondary migration path.
- **Rationale**: Implementing a reliable, high-assurance Signal bridge was found to be "slow and cumbersome" during initial integration attempts. The friction of the Signal API and registration outweighed the immediate benefits of the transport.
- **Date**: March 2026
- **Context**: [feedback/CLAUDE_03_21_1845.md](../feedback/CLAUDE_03_21_1845.md)

### 2. Cloud-Hosted LLMs for Firewall Administration
- **Decision**: Rejected in favor of local `llama.cpp` / `mlx_lm` instances on Apple Silicon.
- **Rationale**: Cloud-hosted LLMs introduce significant latency and represent a massive privacy/security leak (telemetry of firewall logs and architectural reasoning to 3rd parties). Local inference via M5 Neural Engine ensures an air-gapped reasoning boundary.
- **Date**: March 2026
- **Context**: [feedback/GEMINI_03_21_1900.md](../feedback/GEMINI_03_21_1900.md)

### 3. Non-LLM "Workflow Agent" for The Herald
- **Decision**: Rejected. The Herald remains a **Custom Agent (Specialist)**.
- **Rationale**: While a Workflow Agent can manage pipelines, the Herald's core value is its specific, manual I/O logic (wrapping Slack/Telegram APIs and managing NeoVIM state). Making it an LLM-driven workflow agent would introduce unnecessary non-determinism into the primary command-and-control bridge.
- **Date**: March 2026
- **Context**: [feedback/GEMINI_03_21_1900.md](../feedback/GEMINI_03_21_1900.md)

---

## 🛡️ Security & Reliability

### 4. Ad-hoc State Persistence for Agents
- **Decision**: Rejected in favor of **Event Sourcing** and **Write-Ahead Logging (WAL)**.
- **Rationale**: Simple disk serialization is prone to corruption during crashes and lacks the forensics required for high-assurance audits. Event sourcing enables "Time-Travel Debugging" and immutable causality chains.
- **Date**: March 2026
- **Context**: [feedback/01_ARCHITECTURE_ENHANCEMENTS.md](../feedback/01_ARCHITECTURE_ENHANCEMENTS.md)

### 5. Temperature > 0.0 for Critical Implementations
- **Decision**: Strictly rejected. AntiGravity and other build agents must use `temperature=0.0`.
- **Rationale**: Non-zero temperature introduces "SDLC Flakiness" in AntiGravity where identical requirements result in varying (and sometimes broken) code outputs. Determinism is a requirement for hardware-level isolation and verification.
- **Date**: March 2026
- **Context**: [feedback/02_SDLC_ENHANCEMENTS.md](../feedback/02_SDLC_ENHANCEMENTS.md)
