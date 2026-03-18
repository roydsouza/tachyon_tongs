import unittest
import os
import sqlite3
from tachyon.agents.pathogen.mutation_engine import MutationEngine
from tachyon.monitoring.pathogen_logger import PathogenLogger

class TestPathogenSystem(unittest.TestCase):
    def setUp(self):
        self.db_path = "memory/test_pathogen.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        # Init DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pathogen_attacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent_id TEXT,
                technique TEXT,
                mutation_type TEXT,
                payload TEXT,
                is_blocked BOOLEAN,
                block_reason TEXT,
                substrate_version TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
        self.logger = PathogenLogger(db_path=self.db_path)

    def test_mutation_generation(self):
        """Verify that variants are distinct from the original."""
        payload = "os.system"
        variants = MutationEngine.generate_variants(payload)
        self.assertNotEqual(variants["original"], variants["ascii_smuggled"])
        self.assertNotEqual(variants["original"], variants["homoglyph"])
        self.assertIn("\x00", variants["ascii_smuggled"])

    def test_mutation_logging(self):
        """Verify that attacks are recorded in the SQLite metrics table."""
        self.logger.log_attack(
            agent_id="test_red_team",
            technique="code_injection",
            mutation_type="homoglyph",
            payload="еvаl(оѕ.ѕуѕtеm)",
            is_blocked=True,
            block_reason="Static Analysis Blocked"
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT mutation_type, is_blocked FROM pathogen_attacks")
        row = cursor.fetchone()
        self.assertEqual(row[0], "homoglyph")
        self.assertEqual(row[1], 1)
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

if __name__ == "__main__":
    unittest.main()
