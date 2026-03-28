"""
Tachyon Tongs: State Bridge

High-assurance mapping between the SQLite StateManager and Pydantic API schemas.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List
from tachyon.core.state import StateManager
from tachyon.api.schema import (
    SubstrateHealth, SubstrateStatus, AgentDetail, AgentStatus, 
    PatchProposal, PatchStatus, ForensicAlert, AgentHealth, TrafficSummary
)

class StateBridge:
    def __init__(self):
        self.state = StateManager()

    def get_substrate_health(self) -> SubstrateHealth:
        """Retrieves real-time health metrics from the substrate."""
        # Calculate uptime (mocked for now, usually tracked in StateManager singleton)
        uptime = 123456 # Pre-scaffolded mock
        
        # Verify integrity of core files
        integrity_ok = True
        try:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.state.integrity.verify_integrity(os.path.join(root_dir, "EXPLOITATION_CATALOG.md"))
        except Exception:
            integrity_ok = False

        return SubstrateHealth(
            status=SubstrateStatus.OPERATIONAL if integrity_ok else SubstrateStatus.DEGRADED,
            uptime_seconds=uptime,
            integrity_verified=integrity_ok,
            merkle_root=self.state.integrity.get_merkle_root() if hasattr(self.state.integrity, "get_merkle_root") else "unknown",
            last_audit=datetime.now()
        )

    def get_agents(self) -> List[AgentDetail]:
        """Maps active agents from the registry and run logs."""
        from agents._core.registry import AgentRegistry
        
        # Discover plugins
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        agents_dir = os.path.join(root_dir, "agents")
        AgentRegistry.discover_plugins(agents_dir)
        
        roles = AgentRegistry.list_plugins()
        agents = []
        
        for role in roles:
            agents.append(AgentDetail(
                name=role,
                role=role.capitalize(),
                status=AgentStatus.RUNNING, # Ideally check PIDs or heartbeats
                last_action="Idle",
                skill_path=f"agents/{role}/SKILL.md"
            ))
        return agents

    def get_agent_health(self, name: str) -> AgentHealth:
        """Calculates granular health metrics for a specific agent from the ForensicStore."""
        # 1. Total events count for this agent
        # We need to use the forensics DB path, which might be different from state.db_path
        from tachyon.core.forensics import ForensicStore
        store = ForensicStore()
        db_path = store.db_path
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM forensic_log WHERE agent_id = ?", (name,))
                total_events = cursor.fetchone()[0]
        except Exception:
            total_events = 0
            
        # 2. Latest activity
        latest = store.query_latest(limit=1, agent_id=name)
        
        last_heartbeat = None
        last_action = "None"
        if latest:
            ts_str = latest[0]['timestamp']
            try:
                last_heartbeat = datetime.fromisoformat(ts_str)
            except Exception:
                pass
            last_action = latest[0]['action']
            
        return AgentHealth(
            name=name,
            status=AgentStatus.RUNNING if total_events > 0 else AgentStatus.IDLE,
            last_heartbeat=last_heartbeat,
            last_action=last_action,
            cpu_percent=0.0,
            memory_mb=0.0,
            total_events=total_events
        )

    def get_traffic_summary(self) -> TrafficSummary:
        """Aggregates traffic distribution metrics (ALLOW/DENY/ERROR and Internal/Transit)."""
        from tachyon.core.forensics import ForensicStore
        store = ForensicStore()
        
        summary = {
            "total": 0, "allow": 0, "deny": 0, "error": 0,
            "internal": 0, "transit": 0
        }
        
        try:
            with sqlite3.connect(store.db_path) as conn:
                conn.row_factory = sqlite3.Row
                # Simplified total query for now; can be expanded with time filtering
                cursor = conn.execute("""
                    SELECT status, source, COUNT(*) as count 
                    FROM forensic_log 
                    GROUP BY status, source
                """)
                for row in cursor:
                    count = row['count']
                    status = row['status'].upper()
                    source = row['source'].lower()
                    
                    summary["total"] += count
                    if "ALLOW" in status or "SUCCESS" in status:
                        summary["allow"] += count
                    elif "DENY" in status or "BLOCKED" in status:
                        summary["deny"] += count
                    elif "ERROR" in status or "FAIL" in status:
                        summary["error"] += count
                    
                    if source == "transit":
                        summary["transit"] += count
                    else:
                        summary["internal"] += count
        except Exception:
            pass
            
        return TrafficSummary(**summary)

    def get_patches(self) -> List[PatchProposal]:
        """Retrieves pending patches from the Airlock."""
        patches = []
        with sqlite3.connect(self.state.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM patches ORDER BY timestamp DESC LIMIT 50")
            for row in cursor:
                patches.append(PatchProposal(
                    id=row['id'],
                    cve=row['cve_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else datetime.now(),
                    status=row['status'],
                    additions=row['additions'] or 0,
                    deletions=row['deletions'] or 0,
                    debate_status=row['debate_status'] or "pending",
                    summary=row['summary'] or "No summary provided."
                ))
        return patches

    def get_forensic_alerts(self, limit: int = 10) -> List[ForensicAlert]:
        """Retrieves recent forensic events for the dashboard."""
        alerts = []
        with sqlite3.connect(self.state.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM forensic_events ORDER BY id DESC LIMIT ?", (limit,))
            for row in cursor:
                ts_str = row['timestamp']
                try:
                    # Handle both ISO and space-separated formats
                    if "T" in ts_str:
                        ts = datetime.fromisoformat(ts_str)
                    else:
                        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    ts = datetime.now()
                    
                alerts.append(ForensicAlert(
                    id=row['id'],
                    agent_id=row['agent_id'],
                    topic=row['topic'],
                    details=row['details'],
                    timestamp=ts
                ))
        return alerts

    def register_patch(self, patch_id: str, summary: str, status: str = "pending_review"):
        """Registers a new patch proposal in the state layer."""
        with self.state._lock:
            with sqlite3.connect(self.state.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO patches (id, cve_id, summary, status, timestamp, additions, deletions, debate_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patch_id, 
                    patch_id, 
                    summary, 
                    status, 
                    datetime.now().isoformat(), 
                    0, 0, "active"
                ))
                conn.commit()
