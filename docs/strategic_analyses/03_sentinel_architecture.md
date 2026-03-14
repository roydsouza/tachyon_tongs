# 🏗️ Strategic Analysis 03: Sentinel Architecture Trade-offs

> **Purpose**: Should Sentinel remain a bespoke Python script, or should it be refactored into a skills-based declarative agent like Pathogen? This document analyzes the trade-offs.

---

## 1. The Question

Sentinel (`scripts/sentinel.py`) is a **procedural Python script** that hardcodes its workflow:
```
sentinel.py → check_temporal_fallback() → run_supervisor() → VulnerabilityScraper → StateManager
```

Pathogen (`agents/pathogen/SKILL.md`) is a **declarative agent** loaded via `skill_parser.py` with:
- YAML frontmatter (name, capabilities, network policy, intent throttle)
- Markdown system prompt (identity, mission, execution loop, constraints)
- Runtime materialization of network constraints

**Should Sentinel follow Pathogen's pattern?**

---

## 2. Architecture Comparison

| Axis | Sentinel (Current) | Pathogen (Declarative) |
|------|-------------------|----------------------|
| **Definition** | Python script (`sentinel.py` → `cve_scraper.py` → `adk_sentinel.py`) | YAML+Markdown manifest (`SKILL.md`) |
| **Extensibility** | Requires modifying Python code | Modify YAML fields or swap markdown prompt |
| **Capability Control** | Hardcoded function calls | Declarative `capabilities:` list enforced at runtime |
| **Network Policy** | Implicit (whatever `cve_scraper.py` calls) | Explicit `network_policy:` in YAML |
| **Scheduling** | CLI flags (`--manual`, `--cron`) | External (`launchd` plist) |
| **Testability** | Requires mocking many internal functions | Can test manifest loading separately from execution |
| **LLM Integration** | Indirect (via Guardian Triad) | Direct (system prompt for LLM reasoning) |

---

## 3. Trade-off Analysis

### 3.1 Arguments FOR Converting Sentinel to Skills-Based

| Benefit | Description |
|---------|-------------|
| **Consistency** | One agent pattern for the entire codebase. New contributors learn one model. |
| **Hot-Swappable Prompts** | Change Sentinel's behavior by editing `SKILL.md` without touching Python. Enable A/B testing of system prompts. |
| **Pluggable Capabilities** | Add new capabilities (e.g., `read_arxiv`, `query_github_advisories`) by updating YAML, not code. |
| **Intent Throttling** | The `intent_throttle` field (Pathogen uses 0.1) could give Sentinel a configurable aggression level for production vs. testing. |
| **Multi-Sentinel Variants** | Create `sentinel_nvd.skill.md`, `sentinel_arxiv.skill.md`, `sentinel_github.skill.md` — each specialized for a different intel source, loaded by the same runner. |
| **OPA Integration** | Declarative capabilities map directly to OPA policy evaluation, enabling the PDP to govern what Sentinel is allowed to do at runtime. |

### 3.2 Arguments AGAINST Converting Sentinel to Skills-Based

| Risk | Description |
|------|-------------|
| **Complexity Overhead** | Sentinel's workflow is inherently procedural (fetch→filter→dedup→store). Forcing it into a declarative manifest adds indirection without clear benefit for simple pipelines. |
| **Performance** | Pathogen's SKILL.md is parsed at runtime by `skill_parser.py`. For a high-frequency cron job, this adds latency. |
| **LLM Dependency** | A skills-based Sentinel implies LLM reasoning in the loop. The current Sentinel is **deterministic** — it doesn't hallucinate, doesn't require inference, and is fully auditable. Converting it means introducing non-determinism. |
| **Debugging Difficulty** | When Sentinel fails, the Python traceback is clear. With a declarative manifest + LLM reasoning, failures become opaque ("why did the LLM skip this CVE?"). |
| **Existing Test Coverage** | 30 tests exist for the current architecture. A refactor means rewriting most of them. |

### 3.3 The Hybrid Approach (Recommended)

**Don't fully convert. Instead, adopt a "Declarative Envelope, Procedural Core" model:**

```
┌──────────────────────────────────────────┐
│ sentinel.skill.md                         │
│ (Declarative: identity, capabilities,     │
│  network_policy, scheduling, metrics)     │
├──────────────────────────────────────────┤
│ sentinel_runner.py                        │
│ (Procedural: deterministic code execution │
│  referencing the SKILL.md for config)     │
└──────────────────────────────────────────┘
```

#### What Goes in the SKILL.md
```yaml
---
name: SentinelAgent
version: 2.0.0
description: Blue Team threat intelligence aggregator.
network_policy:
  mode: egress_restricted
  allowed_domains:
    - services.nvd.nist.gov
    - api.github.com
    - arxiv.org
capabilities:
  - fetch_nvd_cves
  - fetch_github_advisories
  - fetch_arxiv_papers
  - write_catalog
  - inject_tasks
  - sign_catalog
scheduling:
  mode: cron
  interval: "0 */6 * * *"  # Every 6 hours
metrics:
  snr_threshold: 0.15
  staleness_alert_after: 3  # consecutive empty runs
  relevance_min_score: 0.3
---
# Identity
You are **Sentinel**, the Blue Team threat intelligence agent...
```

#### What Stays in Python
- `VulnerabilityScraper` (deterministic NVD/GitHub/arXiv polling)
- `StateManager` (SQLite WAL, HMAC signing)
- `RelevanceScorer` (deterministic scoring)
- Deduplication logic
- Metric collection

#### The Bridge: `sentinel_runner.py`
```python
def run_sentinel():
    metadata, prompt = load_skill("agents/sentinel/SKILL.md")
    
    # Extract configuration from declarative manifest
    config = {
        "allowed_domains": materialize_network_constraints(metadata),
        "capabilities": metadata.get("capabilities", []),
        "metrics_config": metadata.get("metrics", {}),
    }
    
    # Execute deterministic pipeline with config
    scraper = VulnerabilityScraper(config=config)
    threats = scraper.scrape_new_threats()
    # ...rest of deterministic pipeline...
```

---

## 4. Migration Path

| Phase | Action | Effort |
|-------|--------|--------|
| **Phase 1** | Create `agents/sentinel/SKILL.md` with identity, capabilities, network policy | Low |
| **Phase 2** | Externalize hardcoded config (keywords, thresholds) into SKILL.md YAML | Low |
| **Phase 3** | Create `sentinel_runner.py` that reads SKILL.md for config | Medium |
| **Phase 4** | Register Sentinel as a proper agent in the substrate registry | Medium |
| **Phase 5** (Optional) | Add LLM-assisted analysis as an optional capability | High |

---

## 5. Recommendation

> **Adopt the Hybrid Approach.** Create a `SKILL.md` for Sentinel that governs its identity, capabilities, and configuration. Keep the execution pipeline deterministic (Python). This gives you the benefits of declarative management (hot-swap config, OPA governance, multi-variant support) without sacrificing the auditability and determinism that makes Sentinel trustworthy as a security agent.

> **Do NOT introduce LLM reasoning into Sentinel's core pipeline.** The moment Sentinel can hallucinate, it becomes a liability rather than an asset. Reserve LLM integration for optional, non-critical analysis tasks (e.g., "summarize this CVE for the human operator").
