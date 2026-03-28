import pytest
import os
import json
import tempfile
import time
from datetime import datetime
from tachyon.core.state import StateManager
from tachyon.core.bus import TachyonEventBus
from tachyon.core.keys.certificates import DelegationCertificateAuthority
from tachyon.core.signing import IntegrityManager
from tachyon.api.pep import PEPLayer, ToolRequest
from agents.watcher.agent import WatcherPlugin

# Bypass identity check and stabilize crypto
os.environ["TACHYON_TEST_MODE"] = "1"
os.environ["TACHYON_STRICT_MODE"] = "0"
os.environ["TACHYON_SECRET_KEY"] = "forensic_test_secret_2026"

@pytest.fixture
def test_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_phase4.db")
        bus_db = os.path.join(tmpdir, "bus.db")
        sm = StateManager(db_path=db_path)
        im = IntegrityManager(use_hardware=False)
        ca = DelegationCertificateAuthority(im)
        bus = TachyonEventBus(db_path=bus_db, integrity_manager=im)
        
        # S-07/S-08: Pre-register sensors in trust table to allow PEP execution
        for agent in ["auditor-001", "skeptic-001", "admin-001", "researcher-001", "worker-001"]:
            sm.register_sensor(agent, "ed25519:testkey|mldsa65:testkey", status="ACTIVE")
            
        yield sm, im, ca, bus

@pytest.mark.asyncio
async def test_watcher_acv_violation(test_env):
    """[S-07] Verify the Watcher detects unauthorized actions."""
    sm, im, ca, bus = test_env
    
    # 1. Issue certificate with restricted actions
    agent_sk, cert = ca.derive_and_issue("researcher", allowed_actions=["SEARCH"])
    
    # 2. Start Watcher
    watcher = WatcherPlugin("watcher-001", {"event_bus": bus, "integrity_manager": im})
    
    # 3. Simulate an unauthorized action completion
    unauthorized_record = {
        "agent_id": "researcher-001",
        "action": "FILE_DELETE", # NOT in allowed_actions
        "parameters": {"path": "/etc/shadow"},
        "status": "SUCCESS",
        "timestamp": datetime.now().isoformat()
    }
    
    # S-07: Pass cert context in payload for the simulation helper
    unauthorized_record["certificate_context"] = cert

    # S-07: Sign the event content using the researcher's specific sub-key
    from tachyon.core.keys.hybrid import HybridSigner
    agent_signer = HybridSigner(ed25519_sk=agent_sk)
    event_content = f"ACTION_COMPLETED:{json.dumps(unauthorized_record, sort_keys=True, separators=(',', ':'))}:{unauthorized_record['timestamp']}"
    signature = agent_signer.sign(event_content.encode('utf-8'))

    bus.emit_event(
        topic="ACTION_COMPLETED",
        agent_id="researcher-001",
        payload=unauthorized_record,
        certificate=cert,
        signature=signature,
        timestamp=unauthorized_record['timestamp']
    )
    
    # 4. Wait for Watcher (Polling for up to 5 seconds)
    alert_path = os.path.join(os.path.dirname(sm.db_path), "admin", "ALERT.md")
    
    found = False
    for _ in range(10):
        if os.path.exists(alert_path):
            with open(alert_path, "r") as f:
                content = f.read()
                if "WATCHER_CAPABILITY_VIOLATION" in content:
                    found = True
                    break
        time.sleep(0.5)
    
    if not found:
        print(f"\n[DEBUG] ALERT.md path: {alert_path}")
        if os.path.exists(alert_path):
            with open(alert_path, "r") as f:
                print(f"[DEBUG] ALERT.md content:\n{f.read()}")
        else:
            print("[DEBUG] ALERT.md DOES NOT EXIST")
            
    # S-07 CLEANUP: Stop background thread to prevent leak to next tests
    watcher.stop_backplane_loop()
    assert found, f"WATCHER_CAPABILITY_VIOLATION alert not found in {alert_path}"

@pytest.mark.asyncio
async def test_consensus_airlock_gating(test_env):
    """[S-08] Verify that Airlock patches require 3 signatures."""
    sm, im, ca, bus = test_env
    pep = PEPLayer()
    
    patch_id = "P-999"
    # Stage patch
    with sm.get_db_connection() as conn:
        conn.execute("INSERT INTO patches (id, summary, status) VALUES (?, ?, ?)", (patch_id, "Test", "PENDING"))
        conn.commit()
    
    # 1. First approval (auditor)
    req1 = ToolRequest(agent_id="auditor-001", action="APPROVE_PATCH", parameters={"patch_id": patch_id, "signature": "sig1"})
    await pep.execute(req1)
    
    # 2. Check status (Should still be PENDING)
    with sm.get_db_connection() as conn:
        cursor = conn.execute("SELECT status FROM patches WHERE id = ?", (patch_id,))
        status = cursor.fetchone()[0]
        print(f"[DEBUG] Status after 1st vote: {status}")
        assert status == "PENDING"
    
    # 3. Second approval (skeptic)
    req2 = ToolRequest(agent_id="skeptic-001", action="APPROVE_PATCH", parameters={"patch_id": patch_id, "signature": "sig2"})
    await pep.execute(req2)
    
    # 4. Third approval (Threshold reached)
    req3 = ToolRequest(agent_id="admin-001", action="APPROVE_PATCH", parameters={"patch_id": patch_id, "signature": "sig3"})
    res3 = await pep.execute(req3)
    print(f"[DEBUG] 3rd vote response: {res3.status} - {res3.result}")
    
    # 5. Check status (Should be APPROVED)
    with sm.get_db_connection() as conn:
        cursor = conn.execute("SELECT status FROM patches WHERE id = ?", (patch_id,))
        final_status = cursor.fetchone()[0]
        print(f"[DEBUG] Final status: {final_status}")
        
        # Debug consensus_votes table correctly
        cursor_votes = conn.execute("SELECT signer_id FROM consensus_votes WHERE action_id = ?", (patch_id,))
        votes = [r[0] for r in cursor_votes.fetchall()]
        print(f"[DEBUG] Votes recorded: {votes}")
        
        from tachyon.core.state import StateManager
        print(f"[DEBUG] Test StateManager DB: {sm.db_path}")
        print(f"[DEBUG] Global StateManager DB: {StateManager().db_path}")

        assert final_status == "APPROVED"

@pytest.mark.asyncio
async def test_behavioral_monitor_drift(test_env):
    """[S-09] Verify that significant latency drift triggers alerts."""
    sm, im, ca, bus = test_env
    pep = PEPLayer()
    
    agent_id = "worker-001"
    action = "safe_math"
    
    # 1. Establish baseline (Small latencies)
    for _ in range(6):
        req = ToolRequest(agent_id=agent_id, action=action, parameters={"val1": 1, "val2": 2})
        await pep.execute(req)
        
    # 2. Simulate Drift (Latency Spike)
    from tachyon.monitoring.behavioral import BehavioralMonitor
    monitor = BehavioralMonitor()
    monitor.record_metrics(agent_id, action, latency_ms=1000.0) 
    
    # 3. Verify Alert
    alert_path = os.path.join(os.path.dirname(sm.db_path), "admin", "ALERT.md")
    
    found = False
    for _ in range(5):
        if os.path.exists(alert_path):
            with open(alert_path, "r") as f:
                content = f.read()
                if "MODEL_DRIFT_LATENCY" in content:
                    found = True
                    break
        time.sleep(0.5)
        
    if not found:
        print(f"\n[DEBUG] ALERT.md path: {alert_path}")
        if os.path.exists(alert_path):
            with open(alert_path, "r") as f:
                print(f"[DEBUG] ALERT.md content:\n{f.read()}")
    
    assert found, f"MODEL_DRIFT_LATENCY alert not found in {alert_path}"
