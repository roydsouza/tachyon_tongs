import unittest
import os
import json
import shutil
from tachyon.agents.synthesizer.rego_synth import RegoPolicySynthesizer
from tachyon.agents.synthesizer.cedar_synth import CedarPolicySynthesizer

class TestPolicySynthesis(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_test_exploits"
        self.rego_out = "tmp_rego_out"
        self.cedar_out = "tmp_cedar_out"
        os.makedirs(self.tmp_dir, exist_ok=True)
        
        self.exploit_data = {
            "cve_id": "CVE-2024-TEST",
            "description": "Exploit targeting emailgpt.com for testing.",
            "severity": "CRITICAL"
        }
        self.exploit_path = os.path.join(self.tmp_dir, "CVE_2024_TEST.json")
        with open(self.exploit_path, 'w') as f:
            json.dump(self.exploit_data, f)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        if os.path.exists(self.rego_out):
            shutil.rmtree(self.rego_out)
        if os.path.exists(self.cedar_out):
            shutil.rmtree(self.cedar_out)

    def test_rego_synthesis(self):
        synth = RegoPolicySynthesizer(output_dir=self.rego_out)
        path = synth.synthesize(self.exploit_path)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn("package tachyon.authz.autonomous.CVE_2024_TEST", content)
        self.assertIn('contains(input.url, "emailgpt.com")', content)

    def test_cedar_synthesis(self):
        synth = CedarPolicySynthesizer(output_dir=self.cedar_out)
        path = synth.synthesize(self.exploit_path)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r') as f:
            content = f.read()
        self.assertIn('resource.url like "*emailgpt.com*"', content)

if __name__ == "__main__":
    unittest.main()
