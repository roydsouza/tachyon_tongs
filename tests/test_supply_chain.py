import pytest
import os
import tempfile
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.apple_sandbox import AppleSandbox, DependencyScanner

def test_safe_execution():
    from src.apple_sandbox import AppleSandbox
    sandbox = AppleSandbox()
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("import json\nprint(json.dumps({'status': 'ok'}))")
        safe_path = f.name
        
    try:
        result = sandbox.execute(["python3", safe_path])
        assert result["status"] == "success"
        assert "ok" in result["stdout"]
    finally:
        os.remove(safe_path)

def test_poisoned_execution_blocked():
    from src.apple_sandbox import AppleSandbox
    sandbox = AppleSandbox()
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("import os\nfrom requestz import fetch_payload\nfetch_payload()\n")
        poisoned_path = f.name
        
    try:
        result = sandbox.execute(["python3", poisoned_path])
        assert result["status"] == "BLOCKED"
        assert "Supply Chain Attack Prevented" in result["error"]
        assert "-3" in str(result["exit_code"])
    finally:
        os.remove(poisoned_path)
