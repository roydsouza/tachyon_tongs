import os
import sys
import shutil
import tempfile

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.core.state import StateManager

def test_db_path_robustness():
    print("--- [Regression] Testing Database Path Robustness Across CWD Changes ---")
    
    # 1. Initialize StateManager in the default location
    # (The refactor should use an absolute path to intelligence/tachyon_state.db)
    state = StateManager()
    db_path = state.db_path
    print(f"[Test] StateManager initialized with: {db_path}")
    
    if not os.path.isabs(db_path):
        print(f"[FAILURE] StateManager.db_path is NOT absolute: {db_path}")
        sys.exit(1)
        
    # 2. Perform a write
    state.log_evolution("PATH_TEST", "Initial write before CWD change")
    
    # 3. CHANGE DIRECTORY to /tmp (or a temp dir)
    new_dir = tempfile.mkdtemp()
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        print(f"[Test] Changed CWD to: {new_dir}")
        
        # 4. Attempt a read/write in the new directory
        # This will fail with the old relative-path bug
        try:
            state.log_evolution("PATH_TEST", "Secondary write after CWD change")
            print("[SUCCESS] StateManager survived the CWD change!")
        except Exception as e:
            print(f"[FAILURE] StateManager failed after CWD change: {e}")
            sys.exit(1)
            
    finally:
        os.chdir(old_dir)
        shutil.rmtree(new_dir)

if __name__ == "__main__":
    test_db_path_robustness()
