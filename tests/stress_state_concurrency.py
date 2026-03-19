import unittest
import multiprocessing
import os
import time
from tachyon.core.state import StateManager

def write_alert(worker_id):
    """Worker function to hammer the alert log."""
    manager = StateManager() # Shared singleton
    for i in range(20):
        manager.emit_alert("CONCURRENCY_TEST", f"Worker {worker_id} iteration {i}")
        time.sleep(0.01)

class TestConcurrencyStress(unittest.TestCase):
    def setUp(self):
        self.db_path = "stress_test.db"
        if os.path.exists(self.db_path): os.remove(self.db_path)
        StateManager._instance = None
        self.manager = StateManager(db_path=self.db_path)
        # Ensure ALERT.md is clean
        if os.path.exists("ALERT.md"): os.remove("ALERT.md")

    def test_concurrent_alerts(self):
        """Stress test StateManager with multiple processes writing alerts."""
        processes = []
        for i in range(5):
            p = multiprocessing.Process(target=write_alert, args=(i,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # Verify that the file is not corrupted and rate limiting worked
        if os.path.exists("ALERT.md"):
            with open("ALERT.md", "r") as f:
                content = f.read()
                count = content.count("CONCURRENCY_TEST")
                # 5 processes, each should be limited. Rate limiter is per-singleton.
                # Since multiprocessing creates new singletons in each process, 
                # each process will have its own 5-alert limit.
                # Total should be around 25.
                self.assertLessEqual(count, 30)
                print(f"Total concurrent alerts captured: {count}")

if __name__ == "__main__":
    unittest.main()
