# 🔮 The Data-Driven Skills Architecture

Welcome to the **Tachyon Tongs** Extensibility Engine (Phase 6).

While the [Client Integration (Pub/Sub)](CLIENT_INTEGRATION.md) model allows *external* agents to mooch off the Sentinel's protective shadow, the **Skills Architecture** defines how we build and deploy highly secure agents *internally* within the Substrate itself.

## ⚠️ The Problem: Python-Bound Privilege Collapse

Historically, the Sentinel Agent was hardcoded into a python script (e.g., `engineer_agent.py` or `cve_scraper.py`). 

This approach creates friction:
1. **Opaque Logic:** To see what an agent is designed to do, a human has to read dense algorithmic Python code.
2. **Brittle Updates:** Tweaking an agent's capability (like adding `read_file` permission) requires a Developer to modify the daemon core, risking the introduction of bugs.
3. **No Marketplace:** You can't easily "share" an agent's structural configuration with a friend.

## 🛠️ The Solution: Orthogonal Extensibility

We are decoupling the **AI Generation Logic** from the **Security Enforcement Sandbox**. 

In the Skills Architecture, an "Agent" is no longer a python script. It is simply a declarative Markdown file containing structured data (YAML) and natural language directives. 

### Anatomy of a `SKILL.md`

Every agent deployed natively inside the Tachyon Substrate is defined by a markdown configuration. Here is an example of what `tachyon_sentinel/SKILL.md` looks like:

```yaml
---
name: SentinelAgent
author: roydsouza
version: 1.0.0
description: Autonomous threat intelligence scavenger.
network_policy:
  mode: strict_allowlist
  allowed_domains: ["nvd.nist.gov", "github.com", "cisa.gov"]
capabilities:
  - web_search
  - update_ledger:
      target_file: "EXPLOITATION_CATALOG.md"
intent_throttle: 0.9  # Extremely cautious threshold required before committing a write
---

# Directives

You are the Sentinel. You are paranoid, relentless, and focused solely on identifying zero-day threats targeting LLM architectures.
When investigating a threat, you must adhere strictly to the capability bounds provided. 
```

## ⚙️ How the Substrate Uses Skills

1. **Discovery:** On boot, the Tachyon `substrate_daemon.py` scans a `skills/` directory.
2. **Parsing:** It parses the YAML frontmatter to understand exactly what permissions (Tools) the agent is requesting.
3. **Instantiation:** The Substrate dynamically builds a `google-adk` graph. It mounts the LLM model, injects the *Directives* as the System Prompt, and wires up *only* the capability wrappers explicitly approved in the YAML.
4. **Execution:** The dynamically instantiated agent is now live and waiting for task instructions via the Daemon's routing API.

## ✅ Why This is Future-Proof

By distilling behavior into data:
- **Introspection:** The system (or another agent) can easily read a `SKILL.md` and immediately understand what bounds the agent operates under.
- **Cloning:** Want a more aggressive Sentinel? Just duplicate the `SKILL.md`, change the `intent_throttle` to `0.5`, and reload the daemon.
- **Auditing:** Security reviewers only need to approve the text boundaries, not the raw Python implementation of the tools themselves (which the Substrate handles safely in the backend).

This data-driven approach allows for an evolutionary, rapidly scalable swarm of agents that remain mathematically isolated and perfectly safe.
