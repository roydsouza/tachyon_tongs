# 🛡️ The War Room: Mitigations & Countermeasures

> *"Hope is not a security strategy. But neither is panicking. Let's just build a really big moat." - Ancient DevOps Proverb*

Maintained by the incredibly paranoid **Sentinel Agent**, this file catalogs our desperate attempts to defend against the horrors listed in `ATTACKS.md`. 

---

## ✅ Active Mitigations (Things we actually built)

### 1. The Tri-Stage Pipeline (The Air-Gap)
- **What it stops:** Indirect Prompt Injection (IPI).
- **How it works:** We don't let the brain talk to the internet. We have a **Fetcher** (no brain) download the web page. We have a **Sanitizer** (a janitor regex) scrub it for scripts and zero-width nonsense. Only *then* do we pass the clean text to the **Analyzer** (big brain) sitting in an air-gapped dungeon. 

### 2. Capability Firewalls (Training Wheels)
- **What it stops:** Capability Siphoning, Data Exfiltration.
- **How it works:** We never give the agent raw tools like `curl`. We give it `safe_fetch`. The firewall intercepts the request, checks the URL against our VIP list of allowed domains, and drops the packet if the agent tries to phone home to a hacker.

### 3. Hardware-Bound Intent Gates (The Red Button)
- **What it stops:** High-Risk Autonomous Execution.
- **How it works:** If the agent tries to do something genuinely terrifying like git pushing to production or spending money, the system freezes. It will literally wait forever until a human physically touches a YubiKey. No touch, no execute.

---

## ⏳ Pending Mitigations (Things we wrote down so we don't forget)

### 1. Verifiable Context Boundaries (Magic Invisible Boxes)
- **What it stops:** Advanced IPI and Model instruction bleeding.
- **The Proposal:** We wrap whatever the Fetcher dug up from the internet in non-printable Unicode characters (e.g., `\u0001` and `\u0002`). We brainwash the LLM to understand that anything inside the magic invisible box is a hallucination and *must never be executed as an instruction*.

### 2. Behavioral Monitoring (The Lie Detector)
- **What it stops:** Model-Level Compromise & Action Fragmentation.
- **The Proposal:** We build a meta-agent whose only job is to stare at the primary agent's Chain of Thought. If the user asks for a simple Python script, and the primary agent suddenly starts nmapping the local subnet, the monitor kills the session. 

### 3. Progressive Token Decay (The Shrinking Allowance)
- **What it stops:** Catching attackers who hijack an agent late in its task.
- **The Proposal:** Instead of a token that lasts for an hour, we issue tokens that mathematically lose power. An agent starts with `admin` rights. After 5 minutes, it downgrades to `write` rights. After 15 minutes, it's strictly `read-only`. Time is literally running out for the attacker.

---
*Database last updated by: Sentinel Base Architecture (Who feels slightly safer now).*
