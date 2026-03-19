import pytest
import os
import json
import subprocess
import shutil

AIRLOCK_DIR = "/tmp/test_airlock"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture
def airlock_setup():
    if os.path.exists(AIRLOCK_DIR):
        shutil.rmtree(AIRLOCK_DIR)
    os.makedirs(AIRLOCK_DIR)
    yield AIRLOCK_DIR
    if os.path.exists(AIRLOCK_DIR):
        shutil.rmtree(AIRLOCK_DIR)

def test_airlock_cli_inspect_dict_format(airlock_setup):
    # Create patch in DICT format (which caused the crash before)
    patch_id = "test_dict_patch"
    patch_path = os.path.join(AIRLOCK_DIR, f"{patch_id}.json")
    patch_data = {
        "cve_id": "CVE-DICT",
        "description": "Test dict format",
        "patch_files": {
            "dummy.py": "print('fixed')"
        }
    }
    with open(patch_path, "w") as f:
        json.dump(patch_data, f)
    
    # Run the inspect command
    env = os.environ.copy()
    env["AIRLOCK_DIR"] = AIRLOCK_DIR # Need to update script to read from env or pass as arg
    # Wait, the script currently hardcodes /tmp/tachyon_airlock. 
    # I should update it to be more testable.
    
    # For now, I'll just check if the logic I added to the script handles it in-process
    from scripts.airlock_cli import inspect_patch
    import scripts.airlock_cli
    scripts.airlock_cli.AIRLOCK_DIR = AIRLOCK_DIR
    
    # Capture stdout
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        inspect_patch(patch_id)
    
    output = f.getvalue()
    assert "Target File: dummy.py" in output
    assert "print('fixed')" in output
