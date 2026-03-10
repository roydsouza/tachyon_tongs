# Tachyon Tongs: Deployment & Integration Guide

This document serves as the Builder's Guide for integrating your autonomous agents into the **Tachyon Tongs** security substrate. 

Tachyon Tongs supports two distinct deployments paradigms: **In-Band** (managed internally via the Skills Engine) and **Out-of-Band** (independent agents proxying requests through the client library).

## 1. In-Band Deployment (The Skills Engine)

In-Band agents are defined declaratively via Markdown and managed entirely by the Tachyon Tongs infrastructure. This is ideal for lightweight, highly reliable internal agents (e.g., the built-in Pathogen Red Team).

### Directory Structure
We recommend deploying your In-Band agents inside the `agents/` directory using individual folders for isolation.

```text
tachyon_tongs/
├── agents/
│   ├── pathogen/
│   │   └── SKILL.md
│   ├── log_auditor/
│   │   └── SKILL.md
│   └── code_reviewer/
│       └── SKILL.md
```

### The `SKILL.md` Manifest Template

To construct a new In-Band agent, drop a `SKILL.md` file into its dedicated directory. The Substrate Daemon leverages the YAML frontmatter to construct the agent's OPA identity, allowed capabilities, and network constraints.

```yaml
---
name: CodeReviewer
version: 1.0.0
description: "An internal agent that analyzes pull requests for zero-days."
capabilities:
  - safe_fetch
  - safe_execute
constraints:
  allowed_domains:
    - github.com
    - api.github.com
---
# Instructions
1. Monitor the configured repository.
2. Formally generate review datasets for the workspace.
```

By defining the `allowed_domains`, the Substrate's OPA gateway dynamically whitelists only the specified targets. A capability request to `https://malicious-pastebin.com` will instinctively trip a `SecurityViolationError`.

## 2. Out-of-Band Deployment (Proxied Integration)

Out-of-Band agents are self-contained applications, distinct codebases, or distinct repositories entirely (e.g., `entropy_dashboard`, `financial_fragility_monitor`). This paradigm protects agents from prompt injection without hindering their native dependencies, execution loops, or language stacks.

### Proxy Integration (`tachyon_client.py`)

Out-of-Band agents communicate with the Tachyon Substrate Daemon natively using the Client API.

1. Ensure the Substrate Daemon is running on the host via `python3 src/substrate_daemon.py`.
2. Integrate the `tachyon_client` bindings into your autonomous loop.

```python
from src.tachyon_client import safe_fetch, safe_execute

AGENT_IDENTITY = "EntropyDashboard"
ALLOWED_SINKS = ["news.ycombinator.com", "arxiv.org"]

# The Substrate Daemon processes the fetch, subjecting it to the Guardian Triad pipeline.
# Air-gapped MLX acceleration will strip zero-width steganography and reject overrides natively.
response = safe_fetch(
    "https://news.ycombinator.com", 
    agent_id=AGENT_IDENTITY, 
    allowed_domains=ALLOWED_SINKS
)

if response.get("status") == "SUCCESS":
    print(f"Sanitized Data Acquired: {response.get('content')}")
else:
    print(f"Substrate Dropped Payload: {response.get('error')}")
```

### Recommended Out-of-Band Capabilities

When building an independent agent ecosystem via Tachyon Tongs, consider these architectural separations:
*   **Whitelisting:** Provide strict `allowed_domains` arrays for specific ingestion tasks.
*   **Blacklisting:** Rely on the Sentinel's `EXPLOITATION_CATALOG.md` (which the Substrate inherently respects) to act as an un-overrideable global blacklist blocking dynamic, adversarial endpoints across all Out-of-Band components.

## 3. Off-Machine Deployment (Planned Architecture)

Future releases of Tachyon Tongs will transition to fleet-level management.

*   **Matchlock Authentication:** In-Band and Out-of-Band agents will be required to fetch cryptographic workload identities via Matchlock tokens before the Substrate honors their `safe_fetch` requests.
*   **Tailscale Mesh RPC:** Out-of-Band agents deployed across disparate compute nodes (e.g., cloud workers) will route their Tachyon requests over an encrypted Tailscale overlay network, ensuring Substrate Daemon centralization without exposing the security port to the public internet.
