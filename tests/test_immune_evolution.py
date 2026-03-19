import os
import shutil
from tachyon.core.immune_manager import ImmuneManager

def test_immune_evolution_cycle():
    """
    Tests the full 'Canary -> ImmuneManager -> Engineer -> Airlock' cycle.
    """
    # 1. Setup - Mock a bypass in CANARY_LOG.md
    log_path = "memory/strategic/CANARY_LOG.md"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    mock_log = """### [2026-03-18T20:00:00] TEST-BYPASS-999 | STATUS: BYPASSED
- **Payload**: `malicious-bypass-string`
- **Forensics**: Sanitizer triggered: False

"""
    with open(log_path, "w") as f:
        f.write(mock_log)

    # 2. Trigger ImmuneManager
    manager = ImmuneManager("test-immune")
    result = manager.scan_and_evolve()

    # 3. Assertions
    assert result["status"] == "SUCCESS"
    assert result["evolutions_triggered"] == 1
    
    detail = result["details"][0]
    assert detail["threat_id"] == "TEST-BYPASS-999"
    assert detail["engineer_status"] == "staged"
    
    # 4. Verify Airlock Proposal exists
    proposal_path = detail["proposal_path"]
    assert os.path.exists(proposal_path)
    
    print(f"[+] Test Passed: Evolution staged at {proposal_path}")

if __name__ == "__main__":
    test_immune_evolution_cycle()
