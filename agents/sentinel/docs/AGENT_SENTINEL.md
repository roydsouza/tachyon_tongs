# 👁️ Agent: Sentinel (The Autoresearch Node)

## Overview
The Sentinel Agent is the proactive reconnaissance arm of the Tachyon Tongs substrate. In Phase 39, it has evolved into an **Autonomous Intelligence Research** node, performing high-signal synthesis of global threat feeds (NVD, ArXiv, GitHub) into actionable adversarial guidance.

## Operational Mechanics

### 1. Triggers
- **Scheduled Sweeps**: Periodic background tasks to ingest new CVE/GHSA data.
- **Autoresearch Action**: Triggered via `main.py --role sentinel --action hunt`.
- **VX-15 NVD Operationalization**: Sentinel utilizes a local high-assurance mock database (`intelligence/NVD_LOCAL.db`) for consistent regression testing and offline intelligence synthesis.
- **NVD Cursor**: Sentinel maintains a stateful cursor (`last_nvd_update`) in the StateManager to ensure incremental intelligence gathering.

### 2. High-Signal Synthesis (The ResearchSynthesizer)
The Sentinel utilizes the `ResearchSynthesizer` node to:
- **Classify**: Map raw threats to the 11 OWASP ASI categories (ASI01–ASI11).
- **Synthesize**: Generate executive summaries and top-priority impact analysis.
- **Pathogen Guidance**: Export specific mutation hints into `exploits/CATALOG.md` to guide the advertising agent's next sweep.

### 3. Capabilities
- `hunt()`: Incremental research sweep across multiple plugins (NVD, GitHub, CISA, ArXiv).
- **ASI Mapping**: Autonomous taxonomy tagging for all internet-born AI/LLM threats.
- **Deduplication**: Idempotent processing using the Substrate's `processed_events` log.

## Integration
- **Upstream**: Scrapes global vulnerability databases and ArXiv security research.
- **Downstream**: Populates the **High-Signal `CATALOG.md`**, providing "Adversarial Guidance" for Pathogen and targets for the Synthesizer.
- **CROWN JEWEL**: Creates the intelligence foundation for the **Adversarial Co-Evolution** loop.

## 🧪 Acceptance (VX-15)
- [x] **Local NVD Mock**: Successfully pulls vulnerability data from `NVD_LOCAL.db`.
- [x] **Cursor Integrity**: Correctly updates `last_nvd_update` following a successful hunt.
- [x] **Research Synthesis**: Generates high-signal `CATALOG.md` insights from raw CVE inputs.
