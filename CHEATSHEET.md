# Tachyon Tongs Operator Cheatsheet

Quick-reference CLI commands for managing the Tachyon Substrate.

## 🛰️ Event-Horizon Command Bridge (`tt`)

| Action | Command |
| :--- | :--- |
| **Boot Ritual** | `tt ritual` |
| **Status Dashboard** | `tt dash` |
| **Integrity Check** | `tt status` |
| **Airlock Queue** | `tt airlock` |
| **Agent Management** | `tt agent list\|run\|stop` |
| **Herald Summary** | `bin/tt_herald summary` |
| **Herald Tail (-F)** | `bin/tt_herald tail` |

## 🧬 Legacy Controllers (Substrate v0.9)

| Role | Action | Command |
| :--- | :--- | :--- |
| **Guardian** | Verify Substrate | `python3 -m tachyon.main --role guardian --action verify_substrate` |
| **Canary** | Threat Scout | `python3 -m tachyon.main --role canary --action scout` |
| **Sentinel** | NVD Sweep | `python3 -m tachyon.main --role sentinel --action run_sweep` |
| **Engineer** | Apply Patch | `python3 -m tachyon.main --role engineer --action apply_and_test --params '{"cve_id": "CVE-X", "patch_files": []}'` |
| **Airlock** | List Proposals | `python3 scripts/airlock_cli.py list` |

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
