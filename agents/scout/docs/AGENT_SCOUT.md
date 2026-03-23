# 📡 Agent: Horizon Scout (The Competitive Intel)

## Overview
The Horizon Scout is the external-facing intelligence arm of the Tachyon Tongs project. Its primary mission is to continuously scour the open web for competitive intelligence (e.g., new LLM guardrails, agentic firewall research) and feed structured analysis back into the core documentation.

## Operational Mechanics

### 1. Triggers
The Horizon Scout is typically triggered by:
- **Scheduled Intel Runs**: Daily sweeps of high-value research feeds (arXiv, OWASP).
- **Manual Discovery**: Triggered via the `/sentinel-threat-intel` workflow.
- **Strategic Pivots**: When a new architectural phase is planned, the Scout is deployed to research existing solutions.

### 2. Configuration
The Scout operates primarily through `tachyon/agents/scout.py`:
- **Source Registry**: Maintains a list of prioritized feeds (arXiv CS.CR, CS.AI, OWASP).
- **Substrate Gateway**: All web requests are routed through the `SafeFetch` substrate to prevent honeypot ingestion.

### 3. Capabilities
- `scour_web()`: Executes multi-threaded pulls of research content via the Guardian Triad.
- `analyze_and_persist(raw_intel)`: Uses the `MetalAccelerator` to distill raw text into structured entries for the `COMPETITIVE_ANALYSIS.md` registry.

## Integration
- **Upstream**: Fetches raw data from the open research community and security advisories.
- **Downstream**: Synchronizes its findings with `docs/COMPETITIVE_ANALYSIS.md` and drafts entries for the `PENDING_STRATEGY_MERGE.md` roadmap.
