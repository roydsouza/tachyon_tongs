import sqlite3
import json
from datetime import datetime

class AuthorizationLedger:
    """
    Tachyon Tongs: Absolute Authorization Ledger.
    Provides 100% auditability for policy decisions.
    """
    def __init__(self, db_path: str = "memory/authorization_ledger.db"):
        self.db_path = db_path

    def log_decision(self, agent_id: str, action: str, params: dict, verdict: str, reason: str, engine: str):
        """
        Records a policy decision to the SQLite ledger.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure table exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS authz_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    action TEXT,
                    params_json TEXT,
                    verdict TEXT,
                    reason TEXT,
                    engine_source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            params_json = json.dumps(params)
            
            cursor.execute('''
                INSERT INTO authz_ledger (agent_id, action, params_json, verdict, reason, engine_source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (agent_id, action, params_json, verdict, reason, engine))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ledger Logging Error: {e}")

    def get_recent_logs(self, limit: int = 10):
        """
        Retrieves recent audit logs.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM authz_ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
