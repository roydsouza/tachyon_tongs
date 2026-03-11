import pytest
import os
import sqlite3
import threading
from src.state_manager import StateManager

@pytest.fixture
def state_manager():
    db_path = "/tmp/test_tachyon_state.db"
    log_file = "/tmp/test_run_log.md"
    cat_file = "/tmp/test_catalog.md"
    
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(cat_file):
        os.remove(cat_file)
        
    manager = StateManager(db_path=db_path)
    yield manager, log_file, cat_file
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(cat_file):
        os.remove(cat_file)
        
    StateManager._instance = None # Reset singleton for tests

def test_state_manager_run_log(state_manager):
    manager, log_file, _ = state_manager
    run_data = {
        "agent_id": "TestAgent1",
        "trigger_type": "CLI",
        "files_modified": {},
        "verbose_level": 2
    }
    
    manager.log_run(run_data, duration=1.5, limit=5, log_file=log_file)
    
    with open(log_file, "r") as f:
        content = f.read()
    assert "TestAgent1" in content
    assert "CLI" in content

def test_state_manager_exploitation_catalog(state_manager):
    manager, _, cat_file = state_manager
    threats = [
        {"id": "CVE-9999-001", "summary": "Prompt Injection", "source": "Test", "timestamp": "2026-01-01T00:00:00"},
        {"cve_id": "GHSA-1234", "description": "Agent Hijack", "source": "GitHub", "timestamp": "2026-01-02T00:00:00"}
    ]
    
    manager.log_exploitation(threats, catalog_file=cat_file)
    
    with open(cat_file, "r") as f:
        content = f.read()
    assert "CVE-9999-001" in content
    assert "Prompt Injection" in content
    assert "GHSA-1234" in content
    assert "Agent Hijack" in content

def test_state_manager_concurrency(state_manager):
    """Test that concurrent writes from threads do not corrupt the database (WAL mode test)."""
    manager, _, cat_file = state_manager
    
    def worker(i):
        threats = [{"id": f"CVE-2026-THREAD-{i}", "summary": "Test", "source": "Thread"}]
        manager.log_exploitation(threats, catalog_file=cat_file)
        
    threads = []
    for i in range(20): # simulate 20 rapid agents
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    with sqlite3.connect(manager.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM exploitation_catalog")
        count = cursor.fetchone()[0]
        
    assert count == 20

def test_state_manager_inject_tasks(state_manager):
    manager, _, _ = state_manager
    tasks_file = "/tmp/test_TASKS.md"
    
    # Create mock tasks file
    with open(tasks_file, "w") as f:
        f.write("# Project Backlog\n\n## Security Task Progression\n- [x] Old task\n")
        
    threats = [
        {"id": "CVE-2026-TEST", "source": "Mock API"}
    ]
    
    manager.inject_tasks(threats, tasks_file=tasks_file)
    
    with open(tasks_file, "r") as f:
        content = f.read()
        
    assert "## Security Task Progression" in content
    assert "### 🚨 [URGENT] Autonomous Discoveries" in content
    assert "CVE-2026-TEST" in content
    assert "Mock API" in content
    
    # Cleanup
    if os.path.exists(tasks_file):
        os.remove(tasks_file)

def test_state_manager_log_evolution(state_manager):
    manager, _, _ = state_manager
    evo_file = "/tmp/test_EVOLUTION.md"
    
    manager.log_evolution("Code Patch", "Mitigated Substrate zero-day via Rego constraint.", evolution_file=evo_file)
    manager.log_evolution("Perimeter Expansion", "Added https://new-hacker-blog.com to SITES.md", evolution_file=evo_file)
    
    with open(evo_file, "r") as f:
        content = f.read()
        
    assert "The Evolutionary Ledger" in content
    assert "Code Patch" in content
    assert "Mitigated Substrate" in content
    assert "Perimeter Expansion" in content
    assert "https://new-hacker-blog.com" in content
    
    # Verify chronological prepending (Perimeter Expansion should appear before Code Patch in the file beneath the header)
    idx_expansion = content.find("Perimeter Expansion")
    idx_patch = content.find("Code Patch")
    assert idx_expansion < idx_patch
    
    if os.path.exists(evo_file):
        os.remove(evo_file)

def test_state_manager_integrity_violation(state_manager):
    """Test that tampering with signed documents raises RuntimeError."""
    manager, _, _ = state_manager
    test_file = "/tmp/integrity_test.md"
    with open(test_file, "w") as f:
        f.write("# Original Content")
    
    # Sign it
    manager._sign_document(test_file)
    
    # Verify (should pass)
    manager._verify_catalog_integrity(catalog_file=test_file)
    
    # Tamper
    with open(test_file, "a") as f:
        f.write("\nMalicious injection")
    
    # Verify (should fail)
    with pytest.raises(RuntimeError) as excinfo:
        manager._verify_catalog_integrity(catalog_file=test_file)
    assert "INTEGRITY COMPROMISED" in str(excinfo.value)
    
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(f"{test_file}.sig"):
        os.remove(f"{test_file}.sig")

def test_state_manager_missing_signature(state_manager, capsys):
    """Test that missing signatures warn but don't halt (default behavior)."""
    manager, _, _ = state_manager
    test_file = "/tmp/missing_sig.md"
    with open(test_file, "w") as f:
        f.write("No signature here")
    
    manager._verify_catalog_integrity(catalog_file=test_file)
    captured = capsys.readouterr()
    assert "CRITICAL: No detached signature found" in captured.out
    
    if os.path.exists(test_file):
        os.remove(test_file)

