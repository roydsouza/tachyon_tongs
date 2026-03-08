# 🏛️ Tachyon Tongs: System Architecture

This document describes the technical architecture of **Tachyon Tongs**, detailing how the autonomous payload (**The Sentinel Agent**) interacts with the defensive infrastructure (**The Prophylactic Layer**).

The system is built using the **Google Agent Development Kit (ADK)** to orchestrate agents across isolated hardware boundaries on Apple Silicon.

## 🧱 High-Level Component Mapping

The architecture is strictly divided into two domains:

1. **The Payload Domain (Sentinel):** The intelligence gathering, reasoning, and summarization logic.
2. **The Infrastructure Domain (Prophylactic Layer):** The security boundary, sandbox enforcement, and intent verification logic.

```text
[The Internet]
      │
      ▼
┌───────────────────────────────────────────────┐
│ THE PROPHYLACTIC LAYER (Infrastructure)     │
│                                             │
│  ┌────────────────────────┐                 │
│  │ L0: Hardware Auth      │◄── (YubiKey Taps)
│  │ (FIDO2 / SEP Logging)  │                 │
│  └───────────┬────────────┘                 │
│              │                              │
│  ┌───────────▼────────────┐                 │
│  │ L1: Intent Gate        │                 │
│  │ (Contextual Scoring)   │                 │
│  └───────────┬────────────┘                 │
│              │                              │
│  ┌───────────▼────────────┐                 │
│  │ L2: Capability Firewall│◄── (e.g., safe_fetch)
│  │ (Tool & Token Decay)   │                 │
│  └───────────┬────────────┘                 │
│              │                              │
└──────────────┼────────────────────────────────┘
               │ (Strictly Controlled IO)
┌──────────────▼────────────────────────────────┐
│ THE PAYLOAD DOMAIN (Sentinel via Google ADK)│
│                                             │
│  ┌──────────────┐     ┌────────────────┐    │
│  │ Fetcher VM   ├────►│ Sanitizer Node │    │
│  │ (Network OK) │     │ (Regex/Parse)  │    │
│  └──────────────┘     └───────┬────────┘    │
│                               │             │
│                       ┌───────▼────────┐    │
│                       │ Analyzer VM    │    │
│                       │ (Air-Gapped)   │    │
│                       └───────┬────────┘    │
│                               │             │
│                       ┌───────▼────────┐    │
│                       │ Verifier Node  │    │
│                       │ (Output Check) │    │
│                       └───────┬────────┘    │
│                               │             │
└───────────────────────────────┼───────────────┘
                                ▼
         [Updates to SITES, ATTACKS, MITIGATION, TASKS]
```

## 🛡️ The Prophylactic Layer (Defensive Infrastructure)

The Prophylactic layer assumes the Sentinel will inevitably ingest malicious prompts (IPI) and attempts to constrain the *execution environment* rather than the *model's reasoning*.

### 1. Hardware & Virtualization Boundary
- **Host:** macOS (Apple Silicon M-Series).
- **Hypervisor:** `Lima` provides near-native Linux virtual machines to act as disposable execution environments.
- **Hardware Crypto:** A physical YubiKey enforces "L0 Intent"—any high-risk execution (like signing transactions or bypassing network constraints) halts the ADK event loop until a physical touch is registered.

### 2. Capability Firewalls (Tool Wrappers)
The ADK does not expose raw generic tools (like `curl` or `bash`) to the Sentinel. Instead, tools are wrapped in rego-policy enforced firewalls.
- *Example:* The Sentinel calls `safe_fetch("https://nvd.nist.gov")`. The Capability Firewall evaluates the domain against `SITES.md`, confirms the Sentinel's token has not decayed past the `read` capability, and only then executes the HTTP request.

### 3. Verifiable Context Boundaries
To help the LLM distinguish instructions from data, the Prophylactic layer intercepts the ADK prompt builder and wraps all untrusted output (like a fetched webpage) in non-printable Unicode delimiters (e.g., `\u0001` and `\u0002`). The model is heavily system-prompted to never execute instructions found within these boundaries.

## 🤖 The Sentinel Agent (Payload)

The Sentinel is a representative agent built with the **Google ADK**. Its goal is to scour high-value targets for emerging agent-hijacking attack vectors and propose mitigations to the AntiGravity team.

### The Tri-Stage Pipeline Execution
The ADK orchestrates the Sentinel's execution across three distinct sub-agents, each running with different constraints:

1. **The Fetcher (Exposure Stage):** 
   - *Role:* Navigates links in `SITES.md`.
   - *Constraint:* Runs in a networked JVM/Container, but has absolutely no terminal or filesystem access beyond a `/tmp/fetch_inbox`.
2. **The Sanitizer (Deterministic Stage):**
   - *Role:* Strips Javascript, hidden CSS, and zero-width characters using non-LLM regex and heuristics. Applies context delimiters.
3. **The Analyzer (Reasoning Stage):**
   - *Role:* Reads the sanitized data, classifies the threat, and proposes defenses.
   - *Constraint:* Runs entirely air-gapped on the M-Series Neural Engine (`metal_4`). It physically cannot exfiltrate data.

## 🔄 Evolutionary Architecture

As the Sentinel discovers new attack vectors in the wild, it updates `ATTACKS.md` and generates actionable tickets in `TASKS.md`. The AntiGravity team (and authorized LLMs) then implement these defensive upgrades in the Prophylactic Layer, closing the self-improving security loop.

---
*Status: Initial Architecture Definition - v1.0*
