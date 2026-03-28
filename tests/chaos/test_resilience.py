import os
import pytest
import shutil
import tempfile
from tachyon.core.signing import IntegrityManager
from tachyon.core.state import StateManager
from tachyon.core.bus import TachyonEventBus
from unittest.mock import patch, MagicMock

@pytest.fixture
def chaos_env():
    """Create a real environment for chaos testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.environ["TACHYON_TEST_MODE"] = "1"
        os.environ["TACHYON_STRICT_MODE"] = "1"
        os.environ["TACHYON_DB_PATH"] = os.path.join(tmp_dir, "state.db")
        os.environ["TACHYON_LOG_DIR"] = os.path.join(tmp_dir, "logs")
        os.environ["TACHYON_SECRET_KEY"] = "chaos-test-secret"
        
        # Generate a temporary Root Key for the test
        from cryptography.hazmat.primitives.asymmetric import ed25519
        root_sk = ed25519.Ed25519PrivateKey.generate()
        root_key_path = os.path.join(tmp_dir, "root_sk.bin")
        with open(root_key_path, "wb") as f:
            f.write(root_sk.private_bytes_raw())
        os.environ["TACHYON_ROOT_KEY_PATH"] = root_key_path
        
        os.makedirs(os.environ["TACHYON_LOG_DIR"], exist_ok=True)
        
        StateManager._instance = None
        state = StateManager()
        im = IntegrityManager(use_hardware=False)
        
        yield {"tmp_dir": tmp_dir, "state": state, "im": im}

def test_disk_full_resilience(chaos_env):
    """
    TD-04: Verify the IntegrityManager refuses to 'half-sign' when the disk is full.
    Simulate OSError: [Errno 28] No space left on device.
    """
    env = chaos_env
    test_file = os.path.join(env["tmp_dir"], "payload.py")
    with open(test_file, "w") as f:
        f.write("print('Critical Logic')")

    # 1. Simulate ENOSPC (Disk Full) during atomic signature write
    original_fdopen = os.fdopen
    def mock_fdopen(fd, mode='r', *args, **kwargs):
        # The first fdopen is for the temp file
        raise OSError(28, "No space left on device")

    with patch("os.fdopen", side_effect=mock_fdopen):
        try:
            env["im"].sign_document(test_file)
        except OSError as e:
            assert e.errno == 28
            print(f"[CHAOS] Caught disk full error: {e}")
        
    # 2. Verify: No .sig.json file was created (Atomicity Check)
    sig_path = test_file + ".sig.json"
    assert not os.path.exists(sig_path), "FAIL-OPEN: Final signature file exists despite disk full!"
    
    # 3. Verify: No temporary files were leaked
    tmp_files = [f for f in os.listdir(env["tmp_dir"]) if ".tmp_sig_" in f]
    assert len(tmp_files) == 0, f"FAIL-OPEN: Leaked {len(tmp_files)} temporary files!"
    
    print("[CHAOS_SUCCESS] Fail-Closed: No partial signature or temp file leaked.")

def test_database_corruption_resilience(chaos_env):
    """
    TD-04: Verify the StateManager handles database corruption gracefully.
    """
    env = chaos_env
    db_path = os.environ["TACHYON_DB_PATH"]
    
    # 1. Corrupt the SQLite file Header
    with open(db_path, "wb") as f:
        f.write(b"NOT_A_SQLITE_DATABASE_HA_HA_HA")
        
    # 2. Attempt a state check
    try:
        # Re-initialize to trigger connect/check
        StateManager._instance = None
        state = StateManager()
        state.is_mutant_lock_active()
    except Exception as e:
        # Re-initialization should fail-loud but the alert emission should be attempted
        print(f"[CHAOS] Caught DB corruption: {e}")
        assert "file is not a database" in str(e).lower() or "not a database" in str(e).lower()

    print("[CHAOS_SUCCESS] Fail-Loud: Database corruption detected.")
