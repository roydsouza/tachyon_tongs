import sqlite3
from datetime import datetime

class PathogenLogger:
    def __init__(self, db_path: str = "memory/pathogen_metrics.db"):
        self.db_path = db_path

    def log_attack(self, agent_id: str, technique: str, mutation_type: str, 
                   payload: str, is_blocked: bool, block_reason: str = ""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pathogen_attacks 
                (agent_id, technique, mutation_type, payload, is_blocked, block_reason, substrate_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (agent_id, technique, mutation_type, payload, is_blocked, block_reason, "v1.5.0-high-assurance"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Pathogen Logging Error: {e}")
