import sqlite3
import os

def init_pathogen_db(db_path: str = "memory/pathogen_metrics.db"):
    """
    Initializes the Pathogen Metrics database.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
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

if __name__ == "__main__":
    init_pathogen_db()
    print("Pathogen Metrics Database Initialized.")
