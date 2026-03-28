import os
import sys
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.core.state import StateManager

def test_rate_limiting():
    print("--- [Security] Starting Alert Rate-Limiting Test ---")
    
    # 1. Purge ALERT.md if it exists
    if os.path.exists("ALERT.md"):
        os.remove("ALERT.md")
    
    state = StateManager()
    alert_type = "FLOOD_TEST"
    
    print("[Test] Emitting 10 alerts in rapid succession (Limit is 5 per 60s)...")
    for i in range(10):
        state.emit_alert(alert_type, f"Flood message {i}")
    
    # 2. Check ALERT.md line count
    with open("ALERT.md", "r") as f:
        content = f.read()
        alert_count = content.count(f"## [{alert_type}]")
    
    print(f"[Test] Alerts found in ALERT.md: {alert_count}")
    
    if alert_count == 5:
        print("[SUCCESS] Rate-Limiter suppressed 5/10 alerts!")
    elif alert_count > 5:
        print(f"[FAILURE] Rate-Limiter let too many alerts through: {alert_count}")
        sys.exit(1)
    else:
        print(f"[FAILURE] Alerts missing? Found: {alert_count}")
        sys.exit(1)

if __name__ == "__main__":
    test_rate_limiting()
