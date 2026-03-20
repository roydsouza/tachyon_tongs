"""
Tachyon Tongs: State Bridge

High-assurance mapping between the SQLite StateManager and Pydantic API schemas.
"""

import sqlite3
import json
from datetime import datetime
from typing import List
from tachyon.core.state_manager import StateManager
from tachyon.api.schema import SubstrateHealth, SubstrateStatus, AgentDetail, AgentStatus, PatchProposal, PatchStatus

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
        agents = []
        # Hardcoded list of core roles for now
        roles = ["sentinel", "engineer", "guardian", "canary"]
        
        for role in roles:
            agents.append(AgentDetail(
                name=role,
                role=role.capitalize(),
                status=AgentStatus.RUNNING, # Ideally check PIDs or heartbeats
                last_action="Idle",
                skill_path=f"tachyon/agents/{role}/SKILL.md"
            ))
        return agents

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

    def register_patch(self, patch_id: str, summary: str, status: str = "pending_review"):
        """Registers a new patch proposal in the state layer."""
        with self.state._lock:
            with sqlite3.connect(self.state.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO patches (id, cve_id, summary, status, timestamp, additions, deletions, debate_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"patch-{patch_id}", 
                    patch_id, 
                    summary, 
                    status, 
                    datetime.now().isoformat(), 
                    0, 0, "active"
                ))
                conn.commit()
