# 🛸 tachyon_tongs
### High-Assurance Prophylactic for Agentic Systems

**tachyon_tongs** is a defense-in-depth framework for autonomous AI agents running on Apple Silicon. It is designed to proactively defend against **Agent Hijacking**, **Indirect Prompt Injection**, and **Memory Poisoning** by enforcing a "Zero-Trust Tool Bus" and verifiable execution boundaries.

## 🎯 Intent

Autonomous systems that execute tools (terminal, browser, API calls) on your behalf represent an unprecedented security risk in 2026. If an agent is compromised by malicious instructions hidden in a webpage or email, it can be steered to exfiltrate private keys, delete repositories, or sign transactions. 

The intent of **tachyon_tongs** is to shift the defensive paradigm from *Content Filtering* to **Action Governance**. We assume the model will be compromised, and instead focus on geometrically restricting the "blast radius" of its actions.

## 🛡️ Approach

The architecture is built upon four foundational pillars:

1. **The Tri-Stage Pipeline:** Agents are physically isolated by function. The agent fetching untrusted internet data (Fetcher) is not the agent reasoning over it (Analyzer). 
2. **Capability Firewalls:** Agents never receive raw shell tools like `curl`. Instead, they receive constrained policy-wrapped tools like `safe_fetch` that strictly limit destinations.
3. **Intent Gates & Hardware Handshakes:** High-risk execution (like modifying system files or making crypto transactions) is suspended until physical authorization is provided via a **YubiKey** or equivalent FIDO2 device.
4. **Hardware-Virtualized Sandboxing:** Agents run inside restricted Linux instances managed by **Lima** and **Matchlock**, completely separated from the host macOS kernel.

## 🚀 Current Status

### Phase 1: The Core Pipeline (Implemented)

We have laid the groundwork and implemented the foundation of the Tri-Stage architecture:

- [ROADMAP.md](./ROADMAP.md) — The evolutionary path of the project.
- [TASKS.md](./TASKS.md) — The living checklist of security tasks for the autonomous **Sentinel Agent**.
- **Capability Firewalls:** Basic `safe_fetch` firewall wrapper implemented and governed by Open Policy Agent (`tool_access.rego`).
- **Tri-Stage Objects:** Fetcher, Sanitizer, and Analyzer objects implemented and passing steganographic parsing tests.

### Phase 2 & ADK Orchestration (In Progress)

Currently implementing Google ADK state graphs to route the Tri-Stage pipeline and constructing the Contextual Intent Scoring engine to enforce token decay.

---

### Getting Involved

(Documentation on `init_bus.sh`, Sentinel deployment, and Rego policies is forthcoming).
