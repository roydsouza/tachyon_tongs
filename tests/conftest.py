import os
import pytest
import tempfile
import shutil
import json
import time
from tachyon.core.signing import IntegrityManager
from tachyon.core.bus import TachyonEventBus
from tachyon.core.state import StateManager

@pytest.fixture
def substrate_env():
    """Create a real, mock-free substrate environment for integration testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Environment Hijack & Backup (Phase 44 Stabilization)
        # We backup EVERYTHING we're about to touch
        old_env = {
            k: os.environ.get(k) 
            for k in ["TACHYON_ROOT_KEY_PATH", "TACHYON_TEST_MODE", "TACHYON_STRICT_MODE", 
                     "TACHYON_DB_PATH", "TACHYON_LOG_DIR", "TACHYON_SECRET_KEY"]
        }
        
        # EXPLICITLY UNSET strict mode for the process to avoid poisoning unrelated tests
        if "TACHYON_STRICT_MODE" in os.environ: 
            del os.environ["TACHYON_STRICT_MODE"]
        
        os.environ["TACHYON_DB_PATH"] = os.path.join(tmp_dir, "state.db")
        os.environ["TACHYON_LOG_DIR"] = os.path.join(tmp_dir, "logs")
        os.environ["TACHYON_SECRET_KEY"] = "integration-test-secret"
        
        root_key_path = os.path.join(tmp_dir, "root_sk.bin")
        from cryptography.hazmat.primitives.asymmetric import ed25519
        root_sk = ed25519.Ed25519PrivateKey.generate()
        with open(root_key_path, "wb") as f:
            f.write(root_sk.private_bytes_raw())
            
        os.environ["TACHYON_ROOT_KEY_PATH"] = root_key_path
        os.environ["TACHYON_TEST_MODE"] = "1"
        
        os.makedirs(os.environ["TACHYON_LOG_DIR"], exist_ok=True)
        
        # 2. Initialize Substrate Hardware Proxy
        StateManager._instance = None # Purge any pre-leakage singleton
        im = IntegrityManager(use_hardware=False)
        bus = TachyonEventBus(integrity_manager=im)
        state = StateManager()
        
        yield {
            "tmp_dir": tmp_dir,
            "im": im,
            "bus": bus,
            "state": state
        }
        
        # 3. Environment Restoration & Singleton Purge (Critical for Process Isolation)
        for k in ["TACHYON_ROOT_KEY_PATH", "TACHYON_TEST_MODE", "TACHYON_STRICT_MODE", 
                  "TACHYON_DB_PATH", "TACHYON_LOG_DIR", "TACHYON_SECRET_KEY"]:
            v = old_env.get(k)
            if v is None:
                if k in os.environ: del os.environ[k]
            else:
                os.environ[k] = v
            
        # Purge singleton state so subsequent tests re-initialize with fresh env
        StateManager._instance = None
