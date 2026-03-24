import unittest
import os
import subprocess
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tachyon.core.signing import IntegrityManager

class TestPQCMandate(unittest.TestCase):
    def setUp(self):
        self.test_file = "tests/core/strip_test.txt"
        with open(self.test_file, "w") as f:
            f.write("Sensitive Substrate Configuration")
        self.im = IntegrityManager()

    def tearDown(self):
        if os.path.exists(self.test_file): os.remove(self.test_file)
        sig_path = self.test_file + ".sig"
        if os.path.exists(sig_path): os.remove(sig_path)

    def test_strip_attack_detection(self):
        # 1. Sign normally
        self.im.sign_document(self.test_file)
        
        # 2. Simulate Strip Attack: Remove the mldsa65 layer
        sig_path = self.test_file + ".sig"
        with open(sig_path, "r") as f:
            original_sig = f.read()
        
        stripped_sig = original_sig.split("|")[0]
        with open(sig_path, "w") as f:
            f.write(stripped_sig)
            
        # 3. Verify in STRICT mode via subprocess to ensure clean environment
        env = os.environ.copy()
        env["TACHYON_PQC_STRICT"] = "1"
        env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env["TACHYON_SECRET_KEY"] = "placeholder" # for the signing manager
        
        verify_code = f"from tachyon.core.signing import IntegrityManager; IntegrityManager().verify_integrity('{self.test_file}', enforce=True)"
        
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.check_output(["python3", "-c", verify_code], env=env, stderr=subprocess.STDOUT)
            
        output = cm.exception.output.decode()
        self.assertIn("Strip Attack Detected in STRICT MODE", output)

if __name__ == "__main__":
    unittest.main()
