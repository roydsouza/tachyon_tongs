"""
Tachyon Tongs: Behavioral Monitor (S-09)
Tracks statistical baselines for agent actions to detect model drift.
"""
import json
import math
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional
from tachyon.core.state import StateManager

class BehavioralMonitor:
    """
    Monitors agent execution metrics for anomalies.
    """
    def __init__(self):
        self.state = StateManager()

    def record_metrics(self, agent_id: str, action: str, latency_ms: float, tokens: int = 0):
        """
        Updates the statistical baseline for an agent/action pair.
        Flags anomalies if metrics deviate significantly from the baseline.
        """
        with self.state._lock:
            with self.state.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM behavioral_fingerprints WHERE agent_id = ? AND action = ?",
                    (agent_id, action)
                )
                row = cursor.fetchone()
                
                if not row:
                    # Initialize baseline
                    conn.execute('''
                        INSERT INTO behavioral_fingerprints (agent_id, action, avg_latency_ms, avg_tokens, samples)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (agent_id, action, latency_ms, tokens, 1))
                else:
                    avg_latency = row['avg_latency_ms']
                    avg_tokens = row['avg_tokens'] or 0
                    samples = row['samples']
                    
                    # 1. Simple Anomaly Detection (Threshold: > 300% of average)
                    # In production, use standard deviation from a moving window
                    if samples > 5:
                        if latency_ms > (avg_latency * 3.0):
                            self.state.emit_alert("MODEL_DRIFT_LATENCY", 
                                f"Agent {agent_id} action '{action}' latency anomaly: {latency_ms:.2f}ms (Avg: {avg_latency:.2f}ms)")
                        
                        if tokens > 0 and avg_tokens > 0 and tokens > (avg_tokens * 3.0):
                             self.state.emit_alert("MODEL_DRIFT_VERBOSITY", 
                                f"Agent {agent_id} action '{action}' verbosity anomaly: {tokens} tokens (Avg: {avg_tokens})")

                    # 2. Update Baseline (Cumulative Moving Average)
                    new_avg_latency = ((avg_latency * samples) + latency_ms) / (samples + 1)
                    new_tokens = tokens if tokens > 0 else avg_tokens
                    new_avg_tokens = ((avg_tokens * samples) + new_tokens) / (samples + 1)
                    
                    conn.execute('''
                        UPDATE behavioral_fingerprints 
                        SET avg_latency_ms = ?, avg_tokens = ?, samples = ?
                        WHERE agent_id = ? AND action = ?
                    ''', (new_avg_latency, int(new_avg_tokens), samples + 1, agent_id, action))
                
                conn.commit()
