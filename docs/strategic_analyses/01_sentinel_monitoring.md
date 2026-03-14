# 📊 Strategic Analysis 01: Sentinel Monitoring & Tuning

> **Purpose**: Prescriptive guide for monitoring and tuning the Sentinel agent's effectiveness at discovering and deduplicating relevant exploits.

---

## 1. Current State Assessment

### What Sentinel Does Today
The Sentinel (`scripts/sentinel.py`) is the **Blue Team** threat intelligence aggregator. It:
1. Invokes the Guardian Triad Supervisor Graph (`adk_sentinel.py`) which chains Scout→Analyst→Engineer.
2. Uses `VulnerabilityScraper` (`src/cve_scraper.py`) to poll the NVD API for CVEs matching hardcoded keywords.
3. Applies a `noise_denylist` (regex-level) to filter irrelevant results (printers, firmware, etc.)
4. Deduplicates by CVE ID using a Python dict comprehension: `{r['cve_id']: r for r in results}`.
5. Logs results via `StateManager.log_exploitation()` which uses `INSERT OR IGNORE` on `cve_id UNIQUE`.
6. Exports to `EXPLOITATION_CATALOG.md` and cryptographically signs it via HMAC.
7. Optionally "discovers" new intel sources via `_discover_new_sources()` (30% random trigger).

### Identified Gaps

| Gap | Severity | Description |
|-----|---------|-------------|
| **No relevance scoring** | HIGH | All CVEs that pass the noise denylist are treated equally. A "CRITICAL" printer-adjacent CVE that slips through is valued the same as a genuine agent hijacking zero-day. |
| **No dedup across runs** | MEDIUM | Dedup is per-run only (dict comprehension). Cross-run dedup relies solely on SQLite `UNIQUE` constraint on `cve_id`, which silently ignores duplicates without tracking "already seen" metrics. |
| **No effectiveness metrics** | HIGH | There is no dashboard or logging of: discovery rate, false positive rate, signal-to-noise ratio, or catalog growth velocity. |
| **Static keywords** | MEDIUM | The `search_keywords` list is hardcoded. There is no feedback loop from Pathogen results or human review to refine search terms. |
| **Single source dependency** | HIGH | Only NVD is polled live. GitHub Advisories and arXiv are mentioned in docs but not implemented in `cve_scraper.py`. |
| **No staleness detection** | MEDIUM | There is no mechanism to detect if Sentinel has been failing silently (e.g., NVD rate limiting all requests). |

---

## 2. Monitoring Framework

### 2.1 Key Metrics to Track

Implement a new `sentinel_metrics` table in the StateManager SQLite database:

```sql
CREATE TABLE IF NOT EXISTS sentinel_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER REFERENCES run_logs(id),
    timestamp TEXT,
    -- Discovery Metrics
    total_cves_fetched INTEGER,        -- Raw count before any filtering
    noise_filtered_count INTEGER,      -- Count removed by noise denylist
    dedup_filtered_count INTEGER,      -- Count removed by cross-run dedup
    net_new_discoveries INTEGER,       -- Genuinely novel threats added to catalog
    -- Source Metrics
    sources_polled INTEGER,
    sources_failed INTEGER,
    rate_limit_hits INTEGER,
    -- Quality Metrics
    avg_cvss_score REAL,               -- Average CVSS of discovered threats
    relevance_score REAL,              -- ML-derived relevance (future)
    -- Catalog State
    catalog_total_entries INTEGER,
    catalog_growth_rate REAL           -- Entries/week moving average
);
```

### 2.2 Dashboarding

Create a new script `scripts/sentinel_dashboard.py` that:

1. **Signal-to-Noise Ratio (SNR)**: `net_new_discoveries / total_cves_fetched`. A healthy SNR is >0.15. Below 0.05 means keywords need refinement.
2. **Source Health**: Percentage of sources returning `SUCCESS`. Below 80% triggers an alert.
3. **Discovery Velocity**: Rolling 7-day moving average of `net_new_discoveries`. A declining velocity means the keyword set is exhausted or sources are stale.
4. **Dedup Ratio**: `dedup_filtered_count / total_cves_fetched`. A ratio above 0.8 means Sentinel is mostly re-discovering known threats — increase polling interval or diversify sources.
5. **Staleness Alert**: If `net_new_discoveries == 0` for 3 consecutive runs, emit a `[STALE]` warning to `ERROR.md`.

### 2.3 Relevance Scoring (Phase 2)

Enhance the `VulnerabilityScraper` with a lightweight relevance classifier:

```python
class RelevanceScorer:
    """Scores CVE descriptions for agentic relevance using keyword proximity."""
    
    HIGH_VALUE_TERMS = [
        "agent", "autonomous", "LLM", "prompt injection", "RAG",
        "tool use", "function calling", "MCP", "plugin", "memory poisoning"
    ]
    
    LOW_VALUE_TERMS = [
        "buffer overflow", "XSS", "CSRF", "SQL injection",  # Traditional web
        "denial of service", "integer overflow",              # OS-level
    ]
    
    @classmethod
    def score(cls, description: str) -> float:
        desc_lower = description.lower()
        high_hits = sum(1 for t in cls.HIGH_VALUE_TERMS if t in desc_lower)
        low_hits = sum(1 for t in cls.LOW_VALUE_TERMS if t in desc_lower)
        
        # Normalize: high_hits boost, low_hits penalty
        raw_score = (high_hits * 2.0 - low_hits * 1.0) / max(len(cls.HIGH_VALUE_TERMS), 1)
        return max(0.0, min(1.0, raw_score))
```

Store the `relevance_score` per CVE in the `exploitation_catalog` table and filter out entries below a configurable threshold (default: 0.3).

---

## 3. Tuning Procedures

### 3.1 Keyword Tuning Loop

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Sentinel Run     │───▶│ Metrics Collected │───▶│ Human/Agent Review   │
│ (NVD + Sources)  │     │ (SNR, Velocity)  │     │ (Keyword Refinement) │
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                            │
                                                            ▼
                                                  ┌─────────────────────┐
                                                  │ Updated Keywords    │
                                                  │ (search_keywords[]) │
                                                  └─────────────────────┘
```

**Procedure:**
1. After every 10 runs, review `sentinel_metrics` for SNR trends.
2. If SNR < 0.05 for 3+ consecutive runs, the Sentinel should auto-suggest new keywords by analyzing the most recent successful catalog entries.
3. Store keywords in a `sentinel_config.json` rather than hardcoded in `cve_scraper.py`.

### 3.2 Source Diversification

**Current**: Only NVD is polled live. `_discover_new_sources()` is simulated.

**Target**: Implement real polling for:
- **GitHub Advisory Database** (GraphQL API): `gh api graphql -f query='{securityAdvisories(first:10, orderBy:{field:PUBLISHED_AT, direction:DESC})...}'`
- **arXiv cs.CR**: RSS feed polling for papers mentioning "prompt injection" or "agent hijacking".
- **OWASP Agentic Top 10**: Periodic scrape of the latest mitigations page.

Each source should have its own adapter class implementing a common `ThreatSource` interface:

```python
class ThreatSource(ABC):
    @abstractmethod
    def fetch_threats(self, logger=None) -> list[dict]: ...
    
    @abstractmethod
    def source_name(self) -> str: ...
```

### 3.3 Deduplication Enhancement

**Current**: `INSERT OR IGNORE` on `cve_id UNIQUE` — silent, no metrics.

**Target**:
1. Before insert, `SELECT COUNT(*) FROM exploitation_catalog WHERE cve_id = ?`.
2. If exists, increment a `dedup_filtered_count` metric.
3. Also track "near-duplicates" — CVEs with >80% description similarity (using Jaccard or cosine on TF-IDF vectors) that have different IDs.

---

## 4. Implementation Priority

| Task | Effort | Impact | Priority |
|------|--------|--------|----------|
| Add `sentinel_metrics` table | Low | High | P0 |
| Externalize keywords to `sentinel_config.json` | Low | Medium | P0 |
| Implement `RelevanceScorer` | Medium | High | P1 |
| Create `sentinel_dashboard.py` | Medium | High | P1 |
| Implement GitHub Advisory source adapter | Medium | High | P1 |
| Implement arXiv source adapter | Medium | Medium | P2 |
| Near-duplicate detection | High | Medium | P2 |
| Auto-keyword suggestion from catalog analysis | High | Medium | P3 |

---

## 5. Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Signal-to-Noise Ratio | Unknown (no tracking) | >0.20 |
| Source Diversity | 1 (NVD only) | ≥3 |
| Discovery Velocity | Unknown | >2 net-new/week |
| Dedup Visibility | Silent | Full metrics |
| Staleness Detection | None | Automated alerts |
