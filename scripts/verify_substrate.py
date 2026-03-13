from src.tachyon_client import TachyonClient
import time
import sys

def verify_substrate():
    print("🚀 [Verification] Initializing Mock Agent (AshaAgent)...")
    client = TachyonClient(agent_id="AshaAgent", tenant_id="alpha-tenant")
    
    if not client.health_check():
        print("❌ [Verification] Substrate Daemon is NOT running. Please start it with: ./venv/bin/python src/substrate_daemon.py")
        sys.exit(1)
    
    print("✅ [Verification] Substrate reached. Requesting safe_fetch for 'https://nvd.nist.gov'...")
    
    start_time = time.time()
    response = client.safe_fetch("https://nvd.nist.gov")
    duration = time.time() - start_time
    
    if response.get("status") == "SUCCESS":
        print(f"✅ [Verification] Action SUCCESS in {duration:.2f}s!")
        print(f"📄 [Verification] Content received (truncated): {response['result']['content'][:50]}...")
        print(f"🛡️ [Verification] Threats identified: {response['result']['threats']}")
    else:
        print(f"❌ [Verification] Action FAILED: {response.get('error')}")
        sys.exit(1)

    print("\n📜 [Verification] Checking RUN_LOG.md for multi-tenant isolation...")
    with open("RUN_LOG.md", "r") as f:
        log_content = f.read()
        if "Agent: AshaAgent" in log_content:
            print("✅ [Verification] Isolated log entry found for AshaAgent!")
        else:
            print("❌ [Verification] AshaAgent log entry missing!")
            sys.exit(1)

if __name__ == "__main__":
    verify_substrate()
