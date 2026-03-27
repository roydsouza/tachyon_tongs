"""
Tachyon Tongs: Substrate API Contract & Type Definitions

This module defines the JSON schemas and Pydantic models used for communication
between the Substrate Daemon and the Command Bridge (CLI/TUI/NeoVIM).
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class SubstrateStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    COMPROMISED = "compromised"
    MAINTENANCE = "maintenance"

class AgentStatus(str, Enum):
    RUNNING = "running"
    IDLE = "idle"
    STOPPED = "stopped"
    CRASHED = "crashed"

class SubstrateHealth(BaseModel):
    status: SubstrateStatus
    uptime_seconds: int
    mode: str = "HITL"
    integrity_verified: bool
    merkle_root: str
    last_audit: datetime

class AgentDetail(BaseModel):
    name: str
    role: str
    status: AgentStatus
    pid: Optional[int] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    last_action: Optional[str] = None
    skill_path: str

class PatchStatus(str, Enum):
    PENDING = "pending"
    TESTING = "testing"
    APPROVED = "approved"
    DENIED = "denied"
    DEPLOYED = "deployed"

class PatchProposal(BaseModel):
    id: str
    cve: str
    timestamp: datetime
    status: PatchStatus
    additions: int
    deletions: int
    debate_status: str  # "in_progress", "complete"
    summary: str

class LogEntry(BaseModel):
    timestamp: datetime
    source: str  # "evolution", "alert", "canary", "run"
    level: str   # "INFO", "WARNING", "ERROR", "CRITICAL"
    agent: Optional[str] = None
    message: str

class ForensicAlert(BaseModel):
    id: int
    agent_id: str
    topic: str
    details: str
    timestamp: datetime

class ToolRequest(BaseModel):
    agent_id: str
    tool: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
