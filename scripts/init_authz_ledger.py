import sqlite3
import os

def init_ledger_db(db_path: str = "memory/authorization_ledger.db"):
    """
    Initializes the Authorization Ledger database.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authz_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_id TEXT,
            action TEXT,
            params_json TEXT,
            verdict TEXT,
            reason TEXT,
            engine_source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_ledger_db()
    print("Authorization Ledger Database Initialized.")
