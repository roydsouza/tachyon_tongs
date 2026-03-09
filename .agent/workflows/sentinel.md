---
description: Trigger a manual execution run of the Tachyon Tongs Sentinel Agent.
---
# Trigger Sentinel

This workflow manually triggers the Sentinel Agent to scrape for the latest AI agent vulnerabilities (CVEs/Advisories), parse them through the Tri-Stage pipeline (Fetcher -> Sanitizer -> Analyzer -> Verifier), and log the execution results immutably to `RUN_LOG.md`.

// turbo-all
1. Navigate to the `tachyon_tongs` directory and invoke the Sentinel Python CLI manually.
```bash
cd /Users/rds/antigravity/tachyon_tongs
./scripts/start_opa.sh & sleep 2
python3 sentinel.py --manual
```
