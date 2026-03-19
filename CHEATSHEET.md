# Tachyon Tongs Operator Cheatsheet

Quick-reference CLI commands for managing the Tachyon Substrate.

## 🛡️ Core Controller (main.py)

| Role | Action | Command |
| :--- | :--- | :--- |
| **Guardian** | Verify Substrate | `python3 -m tachyon.main --role guardian --action verify_substrate` |
| **Canary** | Threat Scout | `python3 -m tachyon.main --role canary --action scout` |
| **Sentinel** | NVD Sweep | `python3 -m tachyon.main --role sentinel --action run_sweep` |
| **Engineer** | Apply Patch | `python3 -m tachyon.main --role engineer --action apply_and_test --params '{"cve_id": "CVE-X", "patch_files": []}'` |

## 🧬 Immune System & Evolution

| Tool | Action | Command |
| :--- | :--- | :--- |
| **ImmuneManager** | Trigger Evolution | `python3 -m tachyon.core.immune_manager` |
| **Airlock** | List Proposals | `python3 scripts/airlock_cli.py list` |
| **Airlock** | Approve Patch | `python3 scripts/airlock_cli.py approve <PROPOSAL_ID>` |
| **Airlock** | Deny Patch | `python3 scripts/airlock_cli.py deny <PROPOSAL_ID>` |

## 🧪 Testing & Verification

| Target | Command |
| :--- | :--- |
| **Full Suite** | `pytest` |
| **Airlock Suite** | `pytest tests/test_airlock_oversight.py` |
| **Immune Suite** | `python3 tests/test_immune_evolution.py` |

## 🧹 Maintenance

| Action | Command |
| :--- | :--- |
| **Forensic Re-sign** | `python3 scripts/forensic_resign.py` |
| **Clear Sandbox** | `rm -rf /tmp/tachyon_canary_sandbox` |
| **Restart Daemon** | `launchctl unload ~/Library/LaunchAgents/com.tachyon.canary.plist && launchctl load ~/Library/LaunchAgents/com.tachyon.canary.plist` |
