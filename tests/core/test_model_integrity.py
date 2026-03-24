import unittest
import os
import shutil
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.warden import ModelIntegrityWarden

class TestModelIntegrity(unittest.TestCase):
    def setUp(self):
        self.model_dir = "tests/core/mock_model"
        os.makedirs(self.model_dir, exist_ok=True)
        self.weight_file = os.path.join(self.model_dir, "adapter_model.bin")
        with open(self.weight_file, "wb") as f:
            f.write(b"REAL_WEIGHTS_DATA_001")
        self.warden = ModelIntegrityWarden(model_root=self.model_dir)

    def tearDown(self):
        if os.path.exists(self.model_dir):
            shutil.rmtree(self.model_dir)

    def test_weight_protection(self):
        # 1. Generate Manifest
        self.warden.generate_manifest()
        
        # 2. Initial Verification
        self.assertTrue(self.warden.verify_weights())
        
        # 3. Simulate Poisoning
        with open(self.weight_file, "wb") as f:
            f.write(b"MALICIOUS_WEIGHTS_DATA_666")
            
        # 4. Detect Poisoning
        self.assertFalse(self.warden.verify_weights())

if __name__ == "__main__":
    unittest.main()
