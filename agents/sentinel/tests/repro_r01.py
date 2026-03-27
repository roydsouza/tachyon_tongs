import os
import json
from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager
from agents.sentinel.agent import NVDClient

# 1. Setup minimal environment
os.environ["TACHYON_SECRET_KEY"] = "test_key"

def repro():
    print("[*] Starting R-01 reproduction...")
    
    # Mock IntegrityManager to return None certificate
    im = IntegrityManager(use_hardware=False)
    # Force None certificate
    cert = None
    print(f"[*] Forced certificate: {cert}")
    
    bus = TachyonEventBus(integrity_manager=im)
    client = NVDClient("sentinel-test", bus)
    client.certificate = cert
    
    print("[*] Triggering _call_mcp_tool failure...")
    try:
        # retries=1 to trigger the immediate failure path
        client._call_mcp_tool("test", {}, retries=1)
    except Exception as e:
        print(f"[!] Caught exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    repro()
