# 👁️ Agent: Sentinel (The Immune System)

## Overview
The Sentinel Agent is the proactive reconnaissance arm of the Tachyon Tongs substrate. Its primary mission is to autonomously aggregate, analyze, and catalog new AI exploits and vulnerabilities from global intelligence feeds (e.g., GitHub Advisories, NVD).

## Operational Mechanics

### 1. Triggers
The Sentinel is typically triggered by:
- **Scheduled Sweeps**: Periodic background tasks to ingest new CVE/GHSA data.
- **Manual Discovery**: Triggered via the `/sentinel` or `/sentinel-threat-intel` workflows.
- **Substrate Alerts**: Anomaly detections that prompt a targeted intelligence sweep.

### 2. Configuration
The Sentinel operates primarily in the `tachyon/agents/sentinel/` directory:
- **Registry**: Interfaces with `EXPLOITATION_CATALOG.md` to avoid redundant analysis.
- **Intelligence Feeds**: Configured to scrape specific security advisory URLs and JSON feeds.

### 3. Capabilities
- `run_sweep(harvest_mode=True)`: Scours external feeds for new vulnerabilities. If `harvest_mode` is enabled, it localizes raw payloads for the `Canary` to process.
- **Autonomous Analysis**: Uses internal LLM loops to determine if a vulnerability is applicable to the current substrate environment.

## Integration
- **Upstream**: Scrapes global vulnerability databases and threat feeds.
- **Downstream**: Populates the `EXPLOITATION_CATALOG.md` and provides targets for the `Canary` (Scouting) and `Synthesizer` (Policy Generation).
