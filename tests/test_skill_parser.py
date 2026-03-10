import unittest
import os
import tempfile
from src.skill_parser import load_skill, materialize_network_constraints, SkillParserError

class TestSkillParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary perfectly formed SKILL.md
        self.valid_skill = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".md")
        self.valid_skill.write("---\n")
        self.valid_skill.write("name: TestAgent\n")
        self.valid_skill.write("capabilities:\n  - web_search\n")
        self.valid_skill.write("network_policy:\n  mode: strict_allowlist\n  allowed_domains: ['github.com']\n")
        self.valid_skill.write("---\n")
        self.valid_skill.write("# Identity\nYou are a test agent.")
        self.valid_skill.flush()
        
        # Create a malformed one (missing YAML delimiters)
        self.invalid_skill = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".md")
        self.invalid_skill.write("name: BadAgent\ncapabilities: []\n# Identify\nI am broken.")
        self.invalid_skill.flush()

    def tearDown(self):
        os.unlink(self.valid_skill.name)
        os.unlink(self.invalid_skill.name)

    def test_load_valid_skill(self):
        metadata, prompt = load_skill(self.valid_skill.name)
        self.assertEqual(metadata["name"], "TestAgent")
        self.assertIn("web_search", metadata["capabilities"])
        self.assertEqual(prompt, "# Identity\nYou are a test agent.")

    def test_malformed_skill_raises_error(self):
        with self.assertRaises(SkillParserError):
            load_skill(self.invalid_skill.name)
            
    def test_materialize_network_constraints_strict(self):
        metadata, _ = load_skill(self.valid_skill.name)
        domains = materialize_network_constraints(metadata)
        self.assertEqual(domains, ['github.com'])
        
    def test_materialize_network_constraints_default(self):
        # If no policy is provided, it should default to filtering_only which returns None for domains
        metadata = {"name": "DefaultAgent"}
        domains = materialize_network_constraints(metadata)
        self.assertIsNone(domains)

if __name__ == '__main__':
    unittest.main()
