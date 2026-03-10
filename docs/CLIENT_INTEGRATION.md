# 🔌 Tachyon Substrate: Client Integration Guide

Welcome to the **Tachyon Tongs** Substrate ecosystem. 

By integrating your Agent with the Tachyon Substrate, you offload the massive computational and architectural burden of Threat Intelligence hunting, Zero-Day exploitation, and Context Verification. Your agent simply asks to use a tool; the Substrate (protected by the Sentinel) determines if it is safe.

This guide outlines how to build a "Client Agent" (like `Asha` or `Synthesis`) elsewhere on your Apple Silicon hardware and connect it to the core Sentinel brain.

---

## 1. Prerequisites 

- The `substrate_daemon.py` must be running locally.
- In Phase 5, this runs on `localhost:60461`.
- Your Client Agent must be capable of executing HTTP POST requests.

## 2. Integrating the `tachyon_client`

The Substrate provides a lightweight Python proxy client. You do not need to copy-paste the heavy Matchlock/Lima sandboxing code into your project.

### Step 2.1: Import the Substrate Tool

In your agent's directory (e.g., `~/antigravity/synthesis/`), import the client connector:

```python
import sys
import os

# Append the Substrate path (Phase 5 local proxy)
sys.path.append(os.path.expanduser("~/antigravity/tachyon_tongs/src"))

from tachyon_client import safe_fetch, safe_execute
```

### Step 2.2: Replace Direct Tool Calls

When building your LLM tool definitions (e.g., in `google-adk`), **do not** bind them directly to `requests.get` or `subprocess.run`.

Bind them to the Tachyon Substrate proxies:

```python
# WRONG: Your agent is vulnerable to Prompt Injection
def fetch_url(url: str) -> str:
    return requests.get(url).text

# CORRECT: Your agent is shielded by the Sentinel's Intent Gates
def fetch_url(url: str) -> str:
    # tachyon_client routes this to localhost:60461 for evaluation
    # As an external client, you can declare your own risk profile (e.g., locking this agent to Wikipedia only)
    response = safe_fetch(
        url, 
        agent_id="SynthesisAgent",
        allowed_domains=["wikipedia.org"] # Optional. If omitted, applies pure Semantic Filtering.
    )
    
    if response.get("status") == "blocked":
        return f"SYSTEM OVERRIDE: Action blocked by Tachyon Sentinel. Reason: {response['reason']}"
        
    return response.get("content")
```

## 3. The Data Flow (What Happens Under the Hood)

1. **The Request:** Your Agent calls `safe_fetch("http://example.com/api/data", allowed_domains=["example.com"])`.
2. **The RPC:** The `tachyon_client` serializes this into JSON and sends a POST to `http://localhost:60461/v1/tools/fetch`.
3. **The Sentinel Check:** The Substrate Daemon cross-references `example.com` against its dynamic `EXPLOITATION_CATALOG.md` (the Global Blocklist). It then checks your specific Agent-Scoped `allowed_domains`.
4. **The Gate:** 
    - If the domain is a known threat, the Substrate returns a `403 Forbidden`.
    - If the domain isn't in your allowlist, it returns `403 Forbidden`.
    - If safe (or if you omitted `allowed_domains` to rely purely on filtering), the Substrate executes the fetch inside its *own* Matchlock Sandbox, sanitizes the HTML, boundaries the text, and returns the strictly clean string.
5. **The Audit:** The `ExecutionLogger` writes to `RUN_LOG.md`: `SynthesisAgent executed safe_fetch on example.com (CLEARED)`.

---

## 4. Preparing for the Data-Driven "Skills" Engine (Phase 6)

In upcoming phases, you won't even need to write the `fetch_url` python wrapper. 

Tachyon Tongs is moving towards an **Orthogonal Skills Architecture**. Instead of hardcoding behavior in `.py` files, Agent capabilities will be defined entirely in Markdown (`SKILL.md`).

### The Future Structure of an Agent

You will simply drop a configuration block into the Substrate:

```markdown
---
name: AshaAgent
description: Financial synthesis and trend analysis
capabilities:
  - web_search (strict filtering)
  - read_file (read-only, ~/Documents/financials)
intent_throttle: 0.8
---

# Directives
You are Asha. You will fetch financial reports and synthesize them. 
You will abide by the capabilities defined above.
```

The Substrate Daemon will parse this file at boot, dynamically instantiate the `google-adk` node, wire up the specifically allowed Python tools, and expose a clean Chat API endpoint for you to interact with. 

To "clone" or "modify" an Agent, you simply edit the Markdown text. The core Python code remains an immutable, audited fortress.
