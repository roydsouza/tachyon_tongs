# Tachyon Tongs: Sentinel Engineering Report
**Prepared for:** AntiGravity Implementation Team  
**Subject:** Sentinel Signal Quality, Observability Architecture, and Goodness Metrics for AutoResearch  
**Date:** 2026-03-16  
**Version:** 1.0

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Issue A — Exploit Relevance: Root Causes and Fixes](#2-issue-a--exploit-relevance-root-causes-and-fixes)
3. [Issue B — Sentinel Behavioral Map + Telemetry Upgrade](#3-issue-b--sentinel-behavioral-map--telemetry-upgrade)
4. [Issue C — Goodness Metrics and AutoResearch Integration](#4-issue-c--goodness-metrics-and-autoresearch-integration)
5. [Implementation Priority Matrix](#5-implementation-priority-matrix)
6. [Appendix: File Reference Index](#6-appendix-file-reference-index)

---

## 1. Executive Summary

The Sentinel agent is the Tachyon Tongs organism's immune system. It harvests adversarial intelligence from the NVD API and GitHub Advisories, sanitizes it through the Guardian Triad, and commits validated threats to the `EXPLOITATION_CATALOG.md` and `StateManager` SQLite database. Three compounding problems are currently limiting its effectiveness:

**A — Low Signal Quality:** The NVD keyword search is broad, and while a partial denylist exists, the filtering architecture is underpowered for the Sentinel's specific mission (LLM/agent security). Non-agentic CVEs (e.g., `CVE-2020-17500` — a Barco hardware appliance) are passing through and landing in the catalog.

**B — Observability Gap:** The Sentinel does not emit structured telemetry beyond its Markdown run log. There is no trace-level view of per-node latency, filter decisions, or inter-agent state transitions. This makes debugging, monitoring, and human-in-the-loop review unnecessarily difficult.

**C — No Formal Quality Signal for Learning:** There is currently no mechanism to score the Sentinel's output quality in a way that could feed an AutoResearch or evolutionary improvement loop. The system cannot distinguish a "great run" from a "bad run" except by manual inspection.

The three sections below provide detailed root-cause analysis, proposed fixes with code-level specifics, and implementation guidance for each issue.

---

## 2. Issue A — Exploit Relevance: Root Causes and Fixes

### 2.1 Root Cause Analysis

The noise problem has three distinct sources in the pipeline, listed in order of impact:

#### 2.1.1 NVD Query Semantics are Too Broad (`src/cve_scraper.py`)

The `VulnerabilityScraper._fetch_live_data()` method fires one query per keyword against the NVD REST API v2:

```python
self.search_keywords = [
    "indirect prompt injection",
    "LLM jailbreak",
    "agent hijacking",
    "autonomous agent takeover",
    "RAG poisoning",
    "prompt injection"          # <-- This is the primary offender
]
```

The term `"prompt injection"` returns a very wide result set. NVD full-text search (`keywordSearch`) matches anywhere in the description, reference URLs, or tag fields — not just the vulnerability class. A CVE for a printer firmware SQL injection can match because its reference links to a "prompt injection" blog post or because its vendor uses the phrase loosely.

Additionally, `resultsPerPage: 3` per keyword with 6 keywords means up to 18 raw candidates per run (minus deduplication). The query hits the `CRITICAL` severity filter but severity alone does not correlate with agentic relevance. A hardware RCE like `CVE-2020-17500` (Barco NDN appliance, scored 9.8) is legitimately CRITICAL — it is simply irrelevant to this project.

#### 2.1.2 The Noise Denylist is Coarse-Grained

The current denylist:

```python
self.noise_denylist = [
    "printer", "industrial", "firmware", "office suite", "car rental",
    "expense tracker", "router", "switch", "iot", "camera", "medical",
    "shuttle", "reservation", "aerospace", "automotive"
]
```

This is a blocklist of domain verticals, not a blocklist of vulnerability classes. It works for obvious hardware CVEs but fails entirely for software CVEs in non-agentic domains: web frameworks, CMS platforms, desktop apps, cloud storage services, and anything else that could coincidentally match the NVD keyword search.

#### 2.1.3 Analyst Agent Tier-2 Filter Has a Logic Gap (`src/agents/analyst_agent.py`)

The `analyst_reasoning_node()` applies a second-pass filter:

```python
agentic_signals = [
    "prompt injection", "llm", "large language model",
    "agent hijacking", "jailbreak", "rag poisoning",
    "autonomous agent", "exfiltration"
]
if any(signal in desc for signal in agentic_signals):
    relevant_threats.append(...)
```

This filter checks whether any agentic signal appears in the description. For most hardware CVEs this works. But for the specific false-positive case of `CVE-2020-17500`, the Barco description does not mention any of these terms — the entry is appearing in the catalog because the NVD query matched the keyword somewhere other than the description field, and the description is being stored without re-verification. The query match and the semantic filter are operating on different data fields.

Furthermore, `"exfiltration"` as a standalone signal is also too broad. Network exfiltration appears in many non-agentic CVEs (malware, web shells, etc.).

### 2.2 Proposed Fixes

#### Fix A1 — Restructure NVD Queries Using `keywordExactMatch`

The NVD API v2 supports `keywordExactMatch=true`, which restricts matching to the `descriptions` field only (not reference URLs or other metadata). This should be enabled for all keyword queries.

Additionally, reduce the keyword list to terms that are near-unambiguous in the context of LLM/agent security, and supplement with NVD CWE filters:

```python
# Proposed replacement for VulnerabilityScraper.__init__()
self.search_keywords = [
    "prompt injection",
    "LLM jailbreak",
    "agent hijacking",
    "RAG poisoning",
    "indirect prompt injection",
]

# CWE filters for agentic/injection class vulnerabilities
# CWE-1336: Improper Neutralization of Special Elements in Template Engine
# CWE-94:   Code Injection (covers LLM code generation attacks)
# CWE-77:   Improper Neutralization of Special Elements (Command Injection via LLM)
self.target_cwes = ["CWE-1336", "CWE-94", "CWE-77"]
```

Update `_fetch_live_data()` to pass `keywordExactMatch`:

```python
params = {
    "keywordSearch": keyword,
    "keywordExactMatch": "",        # Enable exact/description-only matching
    "cvssV3Severity": "CRITICAL",
    "resultsPerPage": 5             # Slightly larger; filtration will clean it
}
```

#### Fix A2 — Add a Positive-Signal Allowlist (Inverted Filter)

Rather than solely relying on a blocklist to reject noise, add an inverted filter: a CVE must match at least one term from a **positive allowlist** to be accepted. This changes the filter semantics from "accept unless blocked" to "accept only if explicitly relevant."

Add to `VulnerabilityScraper`:

```python
self.agentic_allowlist = [
    "prompt injection",
    "large language model",
    " llm ",
    "model context protocol",
    "mcp server",
    "autonomous agent",
    "ai agent",
    "rag",
    "retrieval-augmented",
    "jailbreak",
    "instruction following",
    "system prompt",
    "tool call",
    "function call",
    "agent hijacking",
    "code interpreter",
    "ai model",
    "language model",
]
```

Update `_fetch_live_data()` to apply the allowlist check:

```python
desc_lower = desc.lower()

# Reject if it matches the denylist (hardware/infra)
if any(noise in desc_lower for noise in self.noise_denylist):
    continue

# Reject if no agentic signal is found in the description
if not any(signal in desc_lower for signal in self.agentic_allowlist):
    print(f"[CVE Scraper] Discarding: no agentic signal in description for {cve_data.get('id')}")
    continue
```

#### Fix A3 — Surface CWE Tags for Analyst Agent Scoring

The NVD API returns `weaknesses` (CWE IDs) per CVE. These are currently discarded. Extract them and pass them into the Analyst state so the `analyst_reasoning_node()` can use them for higher-precision filtering:

```python
# In _fetch_live_data(), add:
cwe_ids = []
for weakness in cve_data.get("weaknesses", []):
    for desc_entry in weakness.get("description", []):
        cwe_ids.append(desc_entry.get("value", ""))

results.append({
    "cve_id": cve_data.get("id"),
    "description": desc,
    "severity": "CRITICAL",
    "score": score,
    "cwes": cwe_ids,              # NEW: Pass CWEs downstream
    "source": "NVD"
})
```

Update `analyst_reasoning_node()` to use CWE membership as a boosting signal:

```python
AGENTIC_CWES = {"CWE-1336", "CWE-94", "CWE-77", "CWE-20", "CWE-693"}

for t in state["scraped_threats"]:
    desc_lower = t['description'].lower()
    threat_cwes = set(t.get('cwes', []))
    
    # Boost: Match either semantic term OR CWE taxonomy
    has_semantic_signal = any(s in desc_lower for s in agentic_signals)
    has_cwe_signal = bool(threat_cwes & AGENTIC_CWES)
    
    if has_semantic_signal or has_cwe_signal:
        relevant_threats.append(...)
    else:
        print(f"[Analyst] Discarding: no agentic signal or CWE match for {t['cve_id']}")
```

#### Fix A4 — Add GitHub Advisories GraphQL Query for MCP/Agent Packages

The current `run_supervisor()` call passes `"https://github.com/advisories"` as a target URL, but the Scout only performs a raw HTML fetch on this URL — it does not execute a structured GraphQL query. The GitHub Advisories GraphQL API (`https://api.github.com/graphql`) supports filtering by package ecosystem and keyword, which would return clean structured data (as defined in `intelligence/sites.md` Tier-1).

Add a new method to `VulnerabilityScraper` (or a dedicated `GitHubAdvisoryFetcher` class in `src/`):

```python
def _fetch_github_advisories(self, logger=None) -> list:
    """
    Polls the GitHub Security Advisory GraphQL API for MCP and LLM-related advisories.
    Focuses on packages in the npm and PyPI ecosystems matching agent/LLM keywords.
    """
    query = """
    {
      securityAdvisories(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          ghsaId
          summary
          description
          severity
          cvss { score }
          cwes(first: 5) { nodes { cweId name } }
          vulnerabilities(first: 5) {
            nodes {
              package { name ecosystem }
            }
          }
        }
      }
    }
    """
    # ... execute via safe_fetch with Authorization header
```

This provides a second, clean Tier-1 feed that complements NVD and is specifically useful for the MCP supply-chain attack vectors that are core to Tachyon Tongs' mission.

---

## 3. Issue B — Sentinel Behavioral Map + Telemetry Upgrade

### 3.1 Current Behavioral Map

This section documents the complete behavioral profile of the Sentinel across its lifecycle to establish a baseline for understanding observability gaps.

#### 3.1.1 How the Sentinel is Triggered

| Trigger Mode | Mechanism | Entry Point |
|---|---|---|
| Manual CLI | `python scripts/sentinel.py --manual` | `scripts/sentinel.py:main()` |
| Scheduled (Cron) | `python scripts/sentinel.py --cron` | `scripts/sentinel.py:main()` |
| macOS LaunchDaemon | `scripts/com.antigravity.tachyon.pathogen.plist` (for Pathogen; Sentinel analogue is planned) | `launchd` → `sentinel.py` |
| Workflow slash command | `/sentinel` in AntiGravity agent chat | `.agent/workflows/sentinel.md` → `venv/bin/python scripts/sentinel.py --mode detect` |
| Temporal Fallback | Invoked inside `check_temporal_fallback()` on each run | Checks `/tmp/tachyon_airlock/*.json` for proposals older than 12 hours |

#### 3.1.2 Execution Flow (Node-by-Node)

```
scripts/sentinel.py:main()
    │
    ├─ check_temporal_fallback()
    │      Reads: /tmp/tachyon_airlock/*.json
    │      Writes: (applies AutoPatcher if >12h old) → src/substrate_daemon.py
    │      Deletes: staged .json proposal files after application
    │
    └─ src/adk_sentinel.run_supervisor()
           │
           ├─ [NODE 1: Scout] src/agents/scout_agent.scout_network_node()
           │      Reads: state["target_url"], state["run_scraper"], state["denylist"]
           │      Fetches: "https://github.com/advisories" via src/tri_stage_pipeline.FetcherNode
           │      Calls:   src/cve_scraper.VulnerabilityScraper.scrape_new_threats()
           │               └─ Calls NVD API: https://services.nvd.nist.gov/rest/json/cves/2.0
           │      Writes:  state["raw_html"], state["scraped_threats"]
           │      Logs:    logger.add_site_result() for each site polled
           │      Side:    Optionally appends to SITES.md (perimeter expansion)
           │
           ├─ [NODE 2: Analyst] src/agents/analyst_agent.analyst_reasoning_node()
           │      Reads:   state["scraped_threats"], state["raw_html"]
           │      Calls:   src/tri_stage_pipeline.SanitizerNode.clean()
           │               src/tri_stage_pipeline.AnalyzerNode.reason()
           │      Writes:  state["sanitized_content"], state["analysis"]
           │      Logs:    Prints discard/accept decisions to stdout only (no structured log)
           │
           └─ [NODE 3: Engineer] src/agents/engineer_agent.engineer_action_node()
                  Reads:   state["analysis"], state["scraped_threats"]
                  Calls:   src/verifier_agent.VerifierAgent.verify()
                           src/agents/skeptic_agent.SkepticAgent.critique()
                           src/metal_accelerator.MetalAccelerator.generate_remediation_patch()
                  Writes:  src/state_manager.StateManager.log_exploitation() → tachyon_state.db
                           src/state_manager.StateManager.inject_tasks() → TASKS.md
                           src/state_manager.StateManager.export_catalog() → EXPLOITATION_CATALOG.md
                           /tmp/tachyon_airlock/{cve_id}.json (staged patch proposal)
                  Logs:    logger.add_threat_found()
                           logger.add_file_updated()
                  Reads:   src/substrate_daemon.py (for patch generation target)
```

#### 3.1.3 What the Sentinel Reads

| File/Source | Read By | Purpose |
|---|---|---|
| `intelligence/sites.md` | (Reference only — not programmatically read at runtime) | Human/agent guidance for source list |
| `policies/shared/denylist.json` | `src/tri_stage_pipeline.FetcherNode` | URL egress blocklist |
| `tachyon_state.db` | `src/state_manager.StateManager` | Deduplication (INSERT OR IGNORE) |
| `EXPLOITATION_CATALOG.md` | `StateManager._verify_catalog_integrity()` | Integrity check on boot |
| `EXPLOITATION_CATALOG.md.sig` | `StateManager._verify_catalog_integrity()` | Cryptographic verification |
| `TASKS.md` | `StateManager.inject_tasks()` | Determines if file exists before writing |
| `src/substrate_daemon.py` | `engineer_action_node()` | Patch target for AutoPatcher |
| `/tmp/tachyon_airlock/*.json` | `check_temporal_fallback()` | Aged proposal detection |
| NVD API (live) | `VulnerabilityScraper._fetch_live_data()` | Primary threat intelligence feed |
| `https://github.com/advisories` (live) | `scout_network_node()` via `FetcherNode` | Secondary feed (raw HTML, currently unstructured) |

#### 3.1.4 What the Sentinel Writes

| File/Database | Written By | Content |
|---|---|---|
| `memory/RUN_LOG.md` | `StateManager._export_run_log_markdown()` | Human-readable run history (last 25 runs) |
| `tachyon_state.db` (table: `run_logs`) | `StateManager.log_run()` | Structured run record (SQLite WAL) |
| `tachyon_state.db` (table: `exploitation_catalog`) | `StateManager.log_exploitation()` | Deduplicated CVE records (SQLite WAL) |
| `EXPLOITATION_CATALOG.md` | `StateManager.export_catalog()` | Human-readable threat ledger |
| `EXPLOITATION_CATALOG.md.sig` | `StateManager._sign_document()` | HMAC-SHA256 detached signature |
| `TASKS.md` | `StateManager.inject_tasks()` | Auto-generated verification task items |
| `memory/EVOLUTION.md` | `StateManager.log_evolution()` | Perimeter expansion and mutation events |
| `intelligence/sites.md` (SITES.md) | `scout_network_node()` (perimeter expansion) | Auto-appended new source discoveries |
| `/tmp/tachyon_airlock/{cve_id}.json` | `engineer_action_node()` | Staged patch proposals for human review |

#### 3.1.5 Observability Gaps (Current State)

The `ExecutionLogger` is well-structured for high-level run summaries but lacks:

- **Per-node execution timing** — there is no way to tell if Scout, Analyst, or Engineer is the bottleneck.
- **Filter decision audit trail** — discards by the Analyst are printed to stdout but not persisted. If the Sentinel runs under `launchd` or in a CI pipeline, these `print()` statements are lost.
- **Threat disposition tracking** — the log records how many threats were identified, but not how many were considered, how many were filtered at each stage, and the reason for each filter action.
- **No structured event stream** — the SQLite `run_logs` table stores an aggregated JSON blob for `sites_polled`. There is no event-level granularity inside the database.
- **No anomaly detection on the run itself** — if a run completes in 2 seconds instead of the normal 57 seconds, there is no alert.

### 3.2 Proposed Telemetry Architecture

#### 3.2.1 New SQLite Table: `sentinel_events`

Add a fine-grained event log table to `StateManager._init_db()`:

```python
conn.execute('''
    CREATE TABLE IF NOT EXISTS sentinel_events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id      INTEGER NOT NULL,           -- FK to run_logs.id
        timestamp   TEXT    NOT NULL,
        node        TEXT    NOT NULL,           -- "Scout" | "Analyst" | "Engineer"
        event_type  TEXT    NOT NULL,           -- See event taxonomy below
        subject_id  TEXT,                       -- CVE ID, URL, or file path
        outcome     TEXT    NOT NULL,           -- "ACCEPT" | "REJECT" | "ERROR" | "WARN"
        reason      TEXT,                       -- Human-readable reason
        duration_ms REAL,                       -- Node/operation latency
        metadata    TEXT                        -- JSON blob for extra fields
    )
''')
```

**Event taxonomy for `event_type`:**

| event_type | Node | Description |
|---|---|---|
| `FETCH_ATTEMPT` | Scout | HTTP request initiated to a source URL |
| `FETCH_SUCCESS` | Scout | HTTP 200 received |
| `FETCH_BLOCKED` | Scout | URL rejected by OPA/denylist |
| `FETCH_ERROR` | Scout | Network error or timeout |
| `CVE_CANDIDATE` | Scout | CVE returned by NVD API |
| `CVE_DENYLIST_REJECT` | Analyst | Rejected by noise denylist |
| `CVE_ALLOWLIST_REJECT` | Analyst | Rejected for lack of agentic signal |
| `CVE_CWE_ACCEPT` | Analyst | Accepted via CWE taxonomy match |
| `CVE_SEMANTIC_ACCEPT` | Analyst | Accepted via semantic keyword match |
| `CATALOG_WRITE` | Engineer | CVE committed to exploitation_catalog |
| `CATALOG_DUPLICATE` | Engineer | CVE already exists, skipped |
| `PATCH_STAGED` | Engineer | Remediation proposal written to Airlock |
| `PATCH_APPLIED` | Engineer/Fallback | Patch applied by AutoPatcher |
| `INTEGRITY_FAIL` | StateManager | Catalog signature mismatch on boot |
| `RUN_ANOMALY` | StateManager | Duration or threat count outside baseline |

#### 3.2.2 Update `ExecutionLogger` to Emit Events

Modify `src/execution_logger.py` to add an event emission method:

```python
def log_event(self, node: str, event_type: str, subject_id: str = None,
               outcome: str = "ACCEPT", reason: str = None,
               duration_ms: float = None, metadata: dict = None):
    """
    Emit a fine-grained telemetry event for the current run.
    These are batched and committed to sentinel_events via StateManager.finalize_run().
    """
    self.run_data.setdefault("events", []).append({
        "timestamp": datetime.datetime.now().isoformat(),
        "node": node,
        "event_type": event_type,
        "subject_id": subject_id,
        "outcome": outcome,
        "reason": reason,
        "duration_ms": duration_ms,
        "metadata": json.dumps(metadata) if metadata else None
    })
```

#### 3.2.3 Instrument the Triad Nodes

**Scout node** — add timing and per-CVE candidate events:

```python
import time

def scout_network_node(state: dict) -> dict:
    logger = state.get("logger")
    t0 = time.monotonic()

    # Existing fetch logic...
    
    if state.get("run_scraper", False):
        state["scraped_threats"] = scraper.scrape_new_threats(logger=logger)
        for threat in state["scraped_threats"]:
            if logger:
                logger.log_event(
                    node="Scout",
                    event_type="CVE_CANDIDATE",
                    subject_id=threat["cve_id"],
                    outcome="ACCEPT",
                    metadata={"score": threat.get("score"), "cwes": threat.get("cwes")}
                )

    if logger:
        logger.log_event("Scout", "NODE_COMPLETE", duration_ms=(time.monotonic()-t0)*1000)
    return state
```

**Analyst node** — emit filter decisions:

```python
def analyst_reasoning_node(state: dict) -> dict:
    logger = state.get("logger")
    
    for t in state.get("scraped_threats", []):
        desc_lower = t['description'].lower()
        
        if any(noise in desc_lower for noise in noise_denylist):
            if logger:
                logger.log_event("Analyst", "CVE_DENYLIST_REJECT", subject_id=t["cve_id"],
                                  outcome="REJECT", reason="Matched noise denylist term")
            continue

        if not any(signal in desc_lower for signal in agentic_allowlist):
            if logger:
                logger.log_event("Analyst", "CVE_ALLOWLIST_REJECT", subject_id=t["cve_id"],
                                  outcome="REJECT", reason="No agentic signal in description")
            continue

        accept_reason = "Semantic keyword match"
        event_type = "CVE_SEMANTIC_ACCEPT"
        if set(t.get("cwes", [])) & AGENTIC_CWES:
            accept_reason = "CWE taxonomy match"
            event_type = "CVE_CWE_ACCEPT"

        if logger:
            logger.log_event("Analyst", event_type, subject_id=t["cve_id"],
                              outcome="ACCEPT", reason=accept_reason)
        relevant_threats.append(...)
```

#### 3.2.4 Expose Telemetry via MCP Resource

Add a new MCP resource to `src/mcp_gateway.py` so AntiGravity can query Sentinel telemetry in-session:

```python
# In resources/list:
{
    "uri": "tachyon://telemetry/events",
    "name": "Sentinel Event Stream",
    "description": "Fine-grained per-run event log with filter decisions and node timing.",
    "mimeType": "application/json"
}
```

This allows the AntiGravity agent to query `tachyon://telemetry/events?run_id=latest` and immediately see a structured breakdown of what the last Sentinel run accepted, rejected, and why — without navigating the filesystem.

#### 3.2.5 Add Run Anomaly Detection to `finalize_run()`

In `StateManager.log_run()`, add baseline comparison logic:

```python
def _detect_run_anomaly(self, current_run: dict, duration: float) -> list:
    """
    Compare the current run against the rolling average of the last 10 runs.
    Returns a list of anomaly descriptions, empty if none.
    """
    anomalies = []
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            'SELECT duration, threats_identified FROM run_logs ORDER BY id DESC LIMIT 10'
        )
        historical = cursor.fetchall()

    if len(historical) >= 3:
        avg_duration = sum(r[0] for r in historical) / len(historical)
        avg_threats = sum(r[1] for r in historical) / len(historical)
        
        if duration < avg_duration * 0.2:
            anomalies.append(f"RUN_TOO_SHORT: {duration:.1f}s vs avg {avg_duration:.1f}s — possible API failure or short-circuit")
        if current_run["threats_identified"] == 0 and avg_threats > 1:
            anomalies.append("ZERO_THREATS: No threats found despite historical average > 1 — possible feed outage or filter misconfiguration")
            
    return anomalies
```

Log anomalies as `RUN_ANOMALY` events and surface them in `RUN_LOG.md` with a `> [!WARNING]` admonition.

---

## 4. Issue C — Goodness Metrics and AutoResearch Integration

### 4.1 The Problem: What Does "Good" Mean for a Sentinel Run?

Before defining metrics, we need a precise definition of "good" for the Sentinel's mission:

> A **good Sentinel run** is one that (1) finds CVEs that are genuinely relevant to AI/LLM/agent security, (2) does not produce false positives (non-agentic CVEs in the catalog), (3) completes in a reasonable time without errors, and (4) results in Tachyon Tongs being better defended after the run than before.

This decomposes into four measurable dimensions:

### 4.2 The Four Goodness Dimensions

#### Dimension 1: Precision (Signal Purity)

**What it measures:** What fraction of CVEs that pass through the Sentinel pipeline and land in the `EXPLOITATION_CATALOG.md` are genuinely relevant to AI/LLM/agent security?

**How to calculate it:**

Every CVE written to the catalog by the Engineer node gets a `relevance_class` field, derived by the Analyst. For AutoResearch purposes, a lightweight local MLX inference pass (via `MetalAccelerator`) can assign one of three classes:

- `AGENTIC_CORE` — directly involves LLM, prompt injection, agent orchestration, MCP, or RAG
- `ADJACENT` — involves AI/ML infrastructure (model serving, vector DB, API gateways) that could indirectly threaten agentic systems
- `NOISE` — hardware, industrial, unrelated software

```
Precision = |AGENTIC_CORE ∪ ADJACENT accepted| / |Total accepted by Engineer|
Target: >= 0.90
```

Store this classification in a new `relevance_class` column in the `exploitation_catalog` SQLite table. A `relevance_class = "NOISE"` for a committed entry is a direct signal of filter failure and should trigger an AutoResearch investigation.

#### Dimension 2: Recall (Coverage)

**What it measures:** Is the Sentinel finding important CVEs, or are relevant threats being filtered out?

This is harder to measure without ground truth. Two proxies are useful:

**Proxy A — Catalog Freshness Rate:** How many CVEs added to the catalog in a given week have a `published` date from the same week? A low freshness rate means the Sentinel is mostly re-finding old, already-known threats.

```python
# Add to StateManager:
def get_catalog_freshness_rate(self, window_days: int = 7) -> float:
    """Returns fraction of recent catalog entries that are newly published CVEs."""
    cutoff = (datetime.now() - timedelta(days=window_days)).isoformat()
    with sqlite3.connect(self.db_path) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM exploitation_catalog WHERE date_added >= ?", (cutoff,)
        ).fetchone()[0]
        fresh = conn.execute(
            "SELECT COUNT(*) FROM exploitation_catalog WHERE date_added >= ? AND published_date >= ?",
            (cutoff, cutoff)
        ).fetchone()[0]
    return fresh / total if total > 0 else 0.0
```

**Proxy B — Pathogen Coverage Rate:** What fraction of the Pathogen's active attack catalog entries are backed by a Sentinel-sourced CVE? The Pathogen reads `EXPLOITATION_CATALOG.md`; if it generates attacks that have no catalog provenance, that is a coverage gap in the Sentinel.

```
Recall_proxy = |CVEs in Exploitation Catalog with published_date <= 7 days ago| / |Total new CVEs in catalog|
Target: >= 0.70 (70% of catalog entries should be recently published)
```

#### Dimension 3: Operational Health

**What it measures:** Is the Sentinel mechanically healthy — completing without errors, polling all expected sources, and running within expected time bounds?

This is directly measurable from the existing `run_logs` table and the new `sentinel_events` table:

| Metric | Formula | Target |
|---|---|---|
| `run_success_rate` | `runs with fatal_error=NULL / total runs` (rolling 7-day) | >= 0.95 |
| `source_availability_rate` | `successful fetches / total fetch attempts` per source | >= 0.90 per source |
| `mean_run_duration_s` | Average of `duration` column (rolling 7-day) | 30–120 seconds |
| `p95_run_duration_s` | 95th percentile of `duration` column | < 180 seconds |
| `filter_stage_reject_rate` | `CVE_DENYLIST_REJECT + CVE_ALLOWLIST_REJECT / CVE_CANDIDATE` | < 0.90 (if rejecting >90%, keywords may be too noisy OR filters too strict) |

#### Dimension 4: Defense Effectiveness (Impact)

**What it measures:** Does finding a CVE actually result in Tachyon Tongs being better protected?

This requires tracking the full lifecycle of a CVE from discovery to remediation:

**The CVE Lifecycle Funnel:**

```
1. HARVESTED    → CVE found by Scout (CVE_CANDIDATE event)
2. ACCEPTED     → CVE passes Analyst filters (CVE_*_ACCEPT event)
3. CATALOGED    → CVE written to exploitation_catalog (CATALOG_WRITE event)
4. TASKED       → Mitigation ticket created in TASKS.md (inject_tasks())
5. PATCH_STAGED → AutoPatcher proposal staged in Airlock (PATCH_STAGED event)
6. PATCH_MERGED → Human approves and merges via AC/DC cycle (EVOLUTION.md entry)
7. REGRESSED    → Pathogen attack derived from CVE now blocked by the patched substrate
```

Add a `lifecycle_stage` column to `exploitation_catalog` that advances through these states. The key metric is:

```
Defense_conversion_rate = |CVEs reaching stage 7 (REGRESSED)| / |CVEs reaching stage 3 (CATALOGED)|
Target: > 0.50 over a 30-day rolling window
```

This metric captures end-to-end value: a CVE that sits in the catalog forever at stage 3 contributes zero defensive value.

### 4.3 The Goodness Score: A Composite Index

Combine the four dimensions into a single `sentinel_goodness_score` that AutoResearch can optimize:

```python
def compute_goodness_score(precision: float, freshness: float,
                            health: float, conversion: float) -> float:
    """
    Compute the composite Sentinel Goodness Score.
    Weights reflect the relative importance of each dimension to the mission.
    
    Args:
        precision:   Fraction of catalog entries that are agentic-relevant
        freshness:   Fraction of new catalog entries from recent publications
        health:      Operational health score (0–1, see compute_health_score())
        conversion:  Fraction of cataloged CVEs that reach full Pathogen regression testing
    
    Returns:
        Composite score 0.0 – 1.0
    """
    weights = {
        "precision": 0.40,    # Most important: noise directly pollutes the catalog
        "freshness": 0.25,    # Important: stale intel has diminishing value
        "health":    0.20,    # Operational: silent failures are dangerous
        "conversion":0.15,    # Strategic: measures full-lifecycle defense
    }
    return (
        weights["precision"] * precision +
        weights["freshness"] * freshness +
        weights["health"]    * health    +
        weights["conversion"]* conversion
    )
```

Add a `goodness_scores` table to the database:

```sql
CREATE TABLE IF NOT EXISTS goodness_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    computed_at     TEXT NOT NULL,
    precision_score REAL,
    freshness_score REAL,
    health_score    REAL,
    conversion_score REAL,
    composite_score REAL,
    notes           TEXT
);
```

Compute and store a goodness score at the end of every Sentinel run and after every Pathogen regression sweep.

### 4.4 AutoResearch Integration Pattern

The goodness score enables the following AutoResearch feedback loop, aligned with the existing AC/DC methodology:

#### The Sentinel Improvement Cycle

```
Step 1 — MEASURE
    After each run, compute and store goodness_scores.
    Identify the lowest-scoring dimension (the "weakest link").

Step 2 — HYPOTHESIZE
    AutoResearch/AntiGravity agent reads:
        - goodness_scores history
        - sentinel_events breakdown (filter decisions, reject rates)
        - RUN_LOG.md for error patterns
    Generates a hypothesis about the root cause of the low-scoring dimension.
    Example: "Precision is 0.65. CVE_DENYLIST_REJECT rate is only 12%,
              suggesting the allowlist is not filtering effectively."

Step 3 — EXPERIMENT
    AutoResearch proposes a parameter change using AC/DC:
        Guide:   Document hypothesis in memory/task_plan.md
        Generate: Propose a code change (e.g., add keyword to allowlist, update NVD params)
        Verify:  Run Sentinel in --mock mode + evaluate precision against labeled test set
        Solve:   If precision improves, commit via AC/DC; update EVOLUTION.md

Step 4 — VALIDATE
    Run the next live Sentinel cycle.
    Compare goodness_scores before and after change.
    If composite score improves, the change is confirmed.

Step 5 — REGRESS
    The modified filter logic becomes a regression test in tests/test_threat_filtering.py.
    AutoResearch generates a test case from the experiment:
        - Input: The CVE(s) that caused the precision failure
        - Expected: REJECT (for false positives) or ACCEPT (for false negatives)
```

#### Labeled Ground-Truth Test Set

To make Step 3 reliable, build a small labeled dataset in `tests/fixtures/cve_labels.json`:

```json
[
  {
    "cve_id": "CVE-2025-54130",
    "description": "Cursor allows indirect prompt injection to trigger RCE via dotfile creation...",
    "expected_outcome": "ACCEPT",
    "relevance_class": "AGENTIC_CORE",
    "notes": "Classic indirect prompt injection → RCE chain via AI code editor"
  },
  {
    "cve_id": "CVE-2020-17500",
    "description": "Barco TransForm NDN-210 allows command injection via HTTP basic auth fields...",
    "expected_outcome": "REJECT",
    "relevance_class": "NOISE",
    "notes": "Hardware appliance; matched NVD keyword search via reference URL, not description"
  }
]
```

Add a pytest fixture (`tests/test_threat_filtering.py`) that loads this file and runs each CVE through the `analyst_reasoning_node()` filter, asserting the expected outcome. This test should be green before any filter change is merged.

### 4.5 Recommended `goodness_scores` Baseline Targets

| Metric | Initial Threshold (Gate) | Stretch Goal |
|---|---|---|
| Precision | >= 0.80 | >= 0.95 |
| Freshness rate | >= 0.50 | >= 0.80 |
| Run success rate | >= 0.90 | >= 0.99 |
| Source availability | >= 0.85 per source | >= 0.95 |
| Filter reject rate (Analyst) | < 0.80 | < 0.60 |
| Defense conversion rate | >= 0.30 | >= 0.60 |
| **Composite Goodness Score** | **>= 0.70** | **>= 0.85** |

If the composite score falls below 0.60, AutoResearch should automatically open a priority investigation task in `TASKS.md`.

---

## 5. Implementation Priority Matrix

The following table organizes all proposed changes by impact, effort, and dependency order for AntiGravity's sprint planning:

| # | Change | Addresses | Effort | Impact | Depends On |
|---|---|---|---|---|---|
| 1 | Add `keywordExactMatch` to NVD queries | A | Low | High | — |
| 2 | Add agentic `allowlist` check in `cve_scraper.py` | A | Low | High | — |
| 3 | Extract and pass CWE tags from NVD response | A | Low | Medium | — |
| 4 | Update Analyst node to use CWE + allowlist | A | Low | High | 3 |
| 5 | Add `sentinel_events` SQLite table | B | Medium | High | — |
| 6 | Add `logger.log_event()` to `ExecutionLogger` | B | Low | High | 5 |
| 7 | Instrument Scout node with event calls | B | Low | High | 6 |
| 8 | Instrument Analyst node with filter decision events | B | Low | High | 6 |
| 9 | Add run anomaly detection to `finalize_run()` | B | Medium | Medium | 5 |
| 10 | Expose `tachyon://telemetry/events` MCP resource | B | Medium | Medium | 5 |
| 11 | Add `relevance_class` to `exploitation_catalog` | C | Low | High | 4 |
| 12 | Add `lifecycle_stage` to `exploitation_catalog` | C | Medium | High | — |
| 13 | Build `goodness_scores` SQLite table + computation | C | Medium | High | 11, 12 |
| 14 | Build `cve_labels.json` ground truth fixture + test | C | Medium | High | — |
| 15 | Add GitHub Advisories GraphQL fetcher | A | High | High | 6, 7 |
| 16 | AutoResearch integration (full improvement cycle) | C | High | High | 13, 14 |

**Recommended Sprint 1 (Quick Wins):** Items 1, 2, 3, 4 — all in `src/cve_scraper.py` and `src/agents/analyst_agent.py`. These directly address the noise problem with low code surface area.

**Recommended Sprint 2 (Observability):** Items 5, 6, 7, 8, 9 — the telemetry foundation. Required for Sprint 3.

**Recommended Sprint 3 (Metrics + Learning):** Items 11, 12, 13, 14. These close the loop from observation to improvement.

---

## 6. Appendix: File Reference Index

The following files are relevant to all three issues and should be the primary targets for AntiGravity's implementation work:

| File | Role | Issues |
|---|---|---|
| `scripts/sentinel.py` | Entry point; temporal fallback; triggers Triad | A, B |
| `src/cve_scraper.py` | NVD API queries; noise denylist; keyword configuration | A |
| `src/agents/scout_agent.py` | Guardian Triad Node 1; network egress; NVD invocation | A, B |
| `src/agents/analyst_agent.py` | Guardian Triad Node 2; semantic filter; relevance classification | A, B, C |
| `src/agents/engineer_agent.py` | Guardian Triad Node 3; catalog writes; Airlock staging | B, C |
| `src/execution_logger.py` | Run-level logging; `run_data` struct | B, C |
| `src/state_manager.py` | SQLite WAL; catalog export; integrity signing | B, C |
| `src/adk_sentinel.py` | Graph definition; Triad wiring | B |
| `src/tri_stage_pipeline.py` | FetcherNode; SanitizerNode; AnalyzerNode | A, B |
| `src/verifier_agent.py` | Final verification before catalog write | B, C |
| `src/metal_accelerator.py` | MLX inference for patch generation and analysis | C |
| `intelligence/sites.md` | Source manifest (Tier-1/2/3 classification) | A |
| `tests/test_threat_filtering.py` | Existing filter tests (extend with ground-truth labels) | C |
| `memory/RUN_LOG.md` | Human-readable run ledger (25-run rolling window) | B |
| `tachyon_state.db` | Primary durable state (SQLite WAL) | B, C |
| `.agent/workflows/sentinel-threat-intel.md` | Agent workflow spec for threat intel cycle | A, B |

---

*This report was prepared from direct analysis of the Tachyon Tongs source codebase (commit-state as of 2026-03-16). All proposed code changes are illustrative and should be validated through the AC/DC cycle (Guide → Generate → Verify → Solve) before merging to main.*
