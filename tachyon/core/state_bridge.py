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
        """Retrieves pending patches from the exploitation catalog/Airlock."""
        patches = []
        with sqlite3.connect(self.state.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # This logic will evolve as we add a 'patches' table, 
            # for now we scan the catalog for recent entries.
            cursor = conn.execute("SELECT * FROM exploitation_catalog ORDER BY id DESC LIMIT 10")
            for row in cursor:
                patches.append(PatchProposal(
                    id=f"patch-{row['id']}",
                    cve=row['cve_id'],
                    timestamp=datetime.fromisoformat(row['date_added']) if row['date_added'] else datetime.now(),
                    status=PatchStatus.PENDING,
                    additions=0,
                    deletions=0,
                    debate_status="complete",
                    summary=row['description'][:100]
                ))
        return patches
