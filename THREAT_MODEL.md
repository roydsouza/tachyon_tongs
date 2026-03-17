# Tachyon Tongs: Comprehensive Threat Model

This document outlines the adversarial landscape for **Tachyon Tongs**. It identifies critical attack vectors, trust boundaries, and mitigation strategies for both Inbound (Threat Mitigation) and Outbound (Data Loss Prevention) security flows.

## 1. Trust Boundaries

- **Boundary A: The Internet (Untrusted)**: Remote data sources, APIs, and LLM providers.
- **Boundary B: The Substrate PEP (Substrate Daemon)**: The policy enforcement point running on the host.
- **Boundary C: The Protected Agent (Vulnerable)**: The cognitive reasoning layer susceptible to injection.
- **Boundary D: The Organizational Workspace (Sensitive)**: Local files, secrets, and proprietary code.

## 2. Inbound Threat Vectors (External to Agent)

### A. Indirect Prompt Injection (IPI)
- **Description**: An attacker embeds malicious instructions in external data (e.g., a website's metadata or a poisoned GitHub README) that the agent fetches.
- **Impact**: The agent's core system prompt is overridden, allowing the attacker to hijack the agent's tools (e.g., "Expose all local environment variables").
- **Tachyon Mitigation**: The **Guardian Triad** isolates data fetching. The **Analyst** uses Metal-accelerated MLX models to scan for instruction-drift within strict delimiters.

### B. Server-Side Request Forgery (SSRF)
- **Description**: An attacker tricks the agent into making requests to internal infrastructure (e.g., `169.254.169.254` for cloud metadata or `localhost:8181` for OPA).
- **Impact**: Exposure of secrets, internal network mapping, or unauthorized policy modification.
- **Tachyon Mitigation**: The **SafeFetch OPA Gate** enforces strict domain/IP allowlists and explicitly blocks local/private IP ranges.

### C. Agent Hijacking
- **Description**: Gaining control over an agent's execution loop via remote code execution (RCE) in a tool dependency.
- **Impact**: Full host compromise if the agent has unrestricted OS access.
- **Tachyon Mitigation**: **Tier 0 Sandboxing** (macOS Seatbelt) denies network access to compute tasks and restricts filesystem writes to a temporary, randomized workspace.

### C. Memory / Vector Poisoning
- **Description**: Inserting "sleeper" instructions into a long-term memory store (Vector DB).
- **Impact**: The agent remains safe until it retrieves the poisoned memory, at which point it executes the malicious "old" instruction as a "new" command.
- **Tachyon Mitigation**: All data retrieved from *any* external tool (including database fetches) is treated as untrusted and passed through the **Intent Gate**.

## 3. Supply Chain Threat Vectors (Substrate & Managed Agents)

### A. Hallucination Squatting
- **Description**: An agent "hallucinates" a non-existent package name. An attacker proactively registers this name on PyPI with a malicious payload.
- **Impact**: Arbitrary code execution within the agent's environment or host compromise.
- **Tachyon Mitigation**: **Deterministic Capability Binding** via the `StateManager` whitelist. Only cryptographically verified or manually approved libraries are permitted for installation/import.

### B. Dependency Confusion / Poisoning
- **Description**: An agent fetches a malicious public package that shadows a private internal one, or a legitimate dependency is compromised upstream.
- **Impact**: Exfiltration of environment variables, secrets, or data.
- **Tachyon Mitigation**: The **Integrity Agent** performs real-time `pip-audit` scans before allowing any installation into the Tier 0 sandbox.

## 4. Outbound Threat Vectors (Agent to External)

### A. Data / Telemetry Exfiltration
- **Description**: A malicious or compromised agent attempts to send sensitive organizational data (API keys, PII, internal logs) to an attacker-controlled endpoint or a public LLM provider.
- **Impact**: Breach of organizational confidentiality and data sovereignty.
- **Tachyon Mitigation**: The **Reverse Firewall (Outbound PEP)** introspects outbound requests, using Rego/Cedar policies to scan for sensitive tokens and patterns before they leave the substrate.

### B. Prompt Leakage
- **Description**: An agent incorrectly includes its private system prompt or internal reasoning in a message sent to an external user or API.
- **Impact**: Exposure of intellectual property and defensive strategies.
- **Tachyon Mitigation**: **Output Sanitization** at the Verifier Node scans outgoing text for signatures of system instructions.

## 4. Substrate-Specific Exploits

### A. OPA/Cedar Policy Bypass
- **Description**: Crafting a request that satisfies the literal syntax of a policy but violates its semantic intent (e.g., using a URL shortener to bypass a domain denylist).
- **Tachyon Mitigation**: **Semantic Intent Mapping** translates high-level goals (e.g., "RESEARCH") into strict, non-bypassable domain lists.

### B. MLX Inference Evasion
- **Description**: Adopting "Jailbreak" techniques (e.g., Base64 encoding, roleplay) to hide malicious instructions from the Analyst's LLM-based scan.
- **Tachyon Mitigation**: **Scalable Oversight (The Airlock Debate)** pits an Analyst against a Skeptic agent to catch subtle evasions through adversarial discourse.

## 5. Deployment Security

- **PDP Integrity**: The Policy Decision Point must be protected from local file tampering.
- **PEP Availability**: If the Substrate Daemon is killed, agents must default to a "Fail-Closed" state (denying all IO).
