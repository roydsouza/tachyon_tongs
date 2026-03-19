# 📋 Tachyon Tongs: Substrate Cheatsheet

Quick-access guide for the Mission Control dashboard and substrate operations.

## 🔗 Operational URLs

| Component | URL | Description |
| :--- | :--- | :--- |
| **Airlock Console** | [http://127.0.0.1:3030](http://127.0.0.1:3030) | "Deep Space" visual dashboard & mandatory **HITL Experimentation** gate. |
| **Substrate Health** | [http://127.0.0.1:60461/health](http://127.0.0.1:60461/health) | API health-check for the core enforcement daemon. |
| **Airlock API** | [ws://127.0.0.1:60462/ws/telemetry](ws://127.0.0.1:60462/ws/telemetry) | WebSocket endpoint for real-time telemetry. |

---

## 🛠️ Common Commands

### Start Services (Manual)
If the background processes halt, use these commands to restore the substrate:

```bash
# Start Substrate Daemon & Airlock API
python3 -m uvicorn tachyon.enforcement.daemon:app --host 127.0.0.1 --port 60461 &
python3 -m uvicorn tachyon.enforcement.daemon:airlock_app --host 127.0.0.1 --port 60462 &

# Start Web Dashboard
cd dashboard && npm run dev
```

### Trigger a Pulse
Force a telemetry update to verify the dashboard is receiving WebSocket data:
```bash
python3 scripts/test_client.py
```

```bash
pytest
```

---

## 🛡️ Forensic Integrity (IDS)

Manual verification of the substrate's architectural integrity:

| Action | Command |
| :--- | :--- |
| **Full IDS Audit** | `python3 tachyon/agents/guardian_ids.py` |
| **Verify ADRs** | `shasum -a 256 docs/adr/*.md` (Manual check vs .sig) |
| **Check Manifest** | `cat docs/adr/MANIFEST.json` |

---

## 🛡️ Port Registry
For the full station-wide allocation, see **[~/antigravity/PORTS.md](file:///Users/rds/antigravity/PORTS.md)**.
