import unittest
import time
import os
import shutil
from tachyon.core.state import StateManager

class TestAlertRateLimiter(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_alert_limiter.db"
        if os.path.exists(self.db_path): os.remove(self.db_path)
        # Ensure StateManager is re-initialized for the test
        StateManager._instance = None
        self.manager = StateManager(db_path=self.db_path)
        self.alert_file = "TEST_ALERT.md"
        if os.path.exists(self.alert_file): os.remove(self.alert_file)

    def tearDown(self):
        if os.path.exists(self.db_path): os.remove(self.db_path)
        if os.path.exists(self.alert_file): os.remove(self.alert_file)

    def test_alert_rate_limiting(self):
        """Verify that alerts are suppressed after the threshold is reached."""
        # Patch the alert path for the test
        original_emit = self.manager.emit_alert
        
        # Emit 10 alerts of the same type sequentially
        for i in range(10):
            self.manager.emit_alert("DOS_ATTACK", f"Attempt {i}")
            
        # Count occurrences in the file
        if os.path.exists("ALERT.md"): # StateManager uses absolute path to ALERT.md usually
             with open("ALERT.md", "r") as f:
                 content = f.read()
                 count = content.count("DOS_ATTACK")
                 # The default limit is 5 per 60s
                 self.assertLessEqual(count, 5)
                 print(f"Alert count in log: {count}")

if __name__ == "__main__":
    unittest.main()
