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
          [Updates to SITES, EXPLOITATION_CATALOG, TASKS]
```

## 🛡️ The Prophylactic Layer (Defensive Infrastructure)

The Prophylactic layer assumes the Sentinel will inevitably ingest malicious prompts (IPI) and attempts to constrain the *execution environment* rather than the *model's reasoning*.

*Note: The "Hot Reload" happens whenever the Sentinel finds something scary. It's like a vaccine that propagates across your entire workspace in milliseconds.*

---
*Anecdote: We once tried to let the Scout and Analyst share a single memory buffer. Within five minutes, the Analyst was trying to convince the Scout to 'run a quick shell script' from a random CVE description. We don't do that anymore. Boundaries are friends.*
xfiltrate data.

## 🔄 Evolutionary Architecture

As the Sentinel discovers new attack vectors in the wild, it updates the `EXPLOITATION_CATALOG.md` (our single source of truth for internet-born terror) and generates actionable tickets in `TASKS.md`. The AntiGravity team (and authorized LLMs with enough caffeine) then implement these defensive upgrades in the Prophylactic Layer, closing the self-improving security loop.

---
*Status: Initial Architecture Definition - v1.0*
