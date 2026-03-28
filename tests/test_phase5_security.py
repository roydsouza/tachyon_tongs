import unittest
import os
import json
import hashlib
from agents._core.registry import AgentRegistry, RegistrationError
from agents.herald.agent import HeraldPlugin
from tachyon.enforcement.entropy import EntropyAnalyzer

class TestPhase5Defenses(unittest.TestCase):
    def setUp(self):
        self.agents_dir = os.path.join(os.getcwd(), "agents")
        # Enable TEST_MODE to bypass identity check for Herald tests
        os.environ["TACHYON_TEST_MODE"] = "1"
        # Reset Registry
        AgentRegistry._plugins = {}
        if "TACHYON_STRICT_MODE" in os.environ:
            del os.environ["TACHYON_STRICT_MODE"]

    def tearDown(self):
        if "TACHYON_TEST_MODE" in os.environ:
            del os.environ["TACHYON_TEST_MODE"]
        # Clear specific agent modules from sys.modules to allow re-importing
        import sys
        to_delete = [m for m in sys.modules if m.startswith("agents.") or m == "malicious_agent"]
        for m in to_delete:
            del sys.modules[m]

    def test_s10_provenance_success(self):
        """Verify that a legitimate agent with a matching hash loads successfully."""
        # This assumes the current SBOM is correct for the current agents
        # Let's test discovery
        AgentRegistry._plugins = {} # Clear for test
        AgentRegistry.discover_plugins(self.agents_dir)
        self.assertIn("herald", AgentRegistry.list_plugins())

    def test_s10_provenance_violation_strict(self):
        """Verify that a hash mismatch blocks agent load in STRICT mode."""
        os.environ["TACHYON_STRICT_MODE"] = "1"
        
        # Create a dummy agent
        dummy_dir = os.path.join(self.agents_dir, "malicious_agent")
        os.makedirs(dummy_dir, exist_ok=True)
        with open(os.path.join(dummy_dir, "config.yaml"), "w") as f:
            f.write("agent_id: malicious\nclass: MaliciousPlugin")
        with open(os.path.join(dummy_dir, "agent.py"), "w") as f:
            f.write("from agents._core.base import BaseAgentPlugin\nfrom agents._core.registry import AgentRegistry\n@AgentRegistry.register('malicious')\nclass MaliciousPlugin(BaseAgentPlugin):\n    pass")
            
        try:
            with self.assertRaises(RegistrationError) as cm:
                AgentRegistry.discover_plugins(self.agents_dir)
            self.assertIn("Provenance Failure", str(cm.exception))
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(dummy_dir)
            del os.environ["TACHYON_STRICT_MODE"]

    def test_s11_entropy_calculation(self):
        """Verify Shannon entropy calculation accuracy."""
        # Low entropy: repeated string
        low_entropy = "AAAA" * 64 # 256 'A's
        self.assertEqual(EntropyAnalyzer.calculate(low_entropy), 0.0)
        
        # High entropy: 128 bytes of random data (bits/byte should be > 5.8)
        import base64
        # Increasing length ensures bit density is high enough for the threshold
        high_entropy = base64.b64encode(os.urandom(256)).decode()
        self.assertGreater(EntropyAnalyzer.calculate(high_entropy), 5.8)

    def test_s11_herald_flagging(self):
        """Verify that Herald flags high-entropy summaries."""
        config = {"agent_id": "herald-test"}
        # Mock bus to avoid real network/event emission errors
        class MockBus:
            def emit_event(self, *args, **kwargs): pass
            
        herald = HeraldPlugin("herald-test", config)
        herald.bus = MockBus()
        herald.certificate = {}
        
        # Base64 of 512 random bytes (Guaranteed high entropy > 5.9)
        import base64
        suspicious_payload = base64.b64encode(os.urandom(512)).decode()
        
        event = {
            "id": "evt-001",
            "topic": "RESEARCH_DATA",
            "summary": suspicious_payload
        }
        
        sanitized = herald._sanitize_event(event)
        self.assertTrue(sanitized.get("is_suspicious"))
        self.assertGreater(sanitized.get("entropy_bits", 0), 5.8)

if __name__ == "__main__":
    unittest.main()
