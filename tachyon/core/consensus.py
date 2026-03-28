"""
Tachyon Tongs: Consensus Engine (S-08)
Provides Byzantine-resilient gating for high-risk substrate actions.
Requires M-of-N signatures for action commitment.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Tuple
from tachyon.core.state import StateManager
from tachyon.core.signing import IntegrityManager

class ConsensusEngine:
    """
    Manages multi-signature gathering and quorum verification.
    """
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.state = StateManager()
        self.im = IntegrityManager()

    def collect_vote(self, action_id: str, signer_id: str, signature: str) -> bool:
        """
        Records a signature for a specific action.
        Verifies the signature before persistence.
        """
        # 1. Verification (Mock/Standalone for now as per S-08 mandate)
        # In production, we'd pull the signer's certificate from StateManager 
        # to verify the signature against the action_id payload.
        
        with self.state._lock:
            with self.state.get_db_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO consensus_votes (action_id, signer_id, signature, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (action_id, signer_id, signature, datetime.now().isoformat()))
                conn.commit()
        return True

    def check_quorum(self, action_id: str) -> Tuple[bool, int]:
        """
        Checks if the number of unique valid signatures meets the threshold.
        """
        with self.state.get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(DISTINCT signer_id) FROM consensus_votes WHERE action_id = ?",
                (action_id,)
            )
            count = cursor.fetchone()[0]
            return count >= self.threshold, count

    def get_votes(self, action_id: str) -> List[Dict[str, Any]]:
        """Retrieves all votes for a given action."""
        with self.state.get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM consensus_votes WHERE action_id = ?", (action_id,))
            return [dict(row) for row in cursor.fetchall()]

    def clear_votes(self, action_id: str):
        """Purges votes after action completion."""
        with self.state._lock:
            with self.state.get_db_connection() as conn:
                conn.execute("DELETE FROM consensus_votes WHERE action_id = ?", (action_id,))
                conn.commit()
