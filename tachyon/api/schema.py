"""
Tachyon Tongs: Substrate API Contract & Type Definitions

This module defines the JSON schemas and Pydantic models used for communication
between the Substrate Daemon and the Command Bridge (CLI/TUI/NeoVIM).
"""

from enum import Enum
from typing import List, Optional, Dict, Any
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

class AgentHealth(BaseModel):
    name: str
    status: AgentStatus
    last_heartbeat: Optional[datetime] = None
    last_action: Optional[str] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    total_events: int = 0

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
    source: str = "internal"
    level: str   # "INFO", "WARNING", "ERROR", "CRITICAL"
    agent: Optional[str] = None
    message: str

class ForensicAlert(BaseModel):
    id: int
    agent_id: str
    topic: str
    details: Dict[str, Any]
    source: str = "internal"
    timestamp: datetime



class ToolRequest(BaseModel):
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    tenant_id: Optional[str] = "default"
    prompt_context: Optional[str] = None

class ToolResponse(BaseModel):
    request_id: str
    status: str
    selected_model: str
    result: Optional[Any] = None
    error: Optional[str] = None

class AuthExchangeRequest(BaseModel):
    sensor_id: str
    public_key_b64: str
    attestation: Optional[str] = None

class TrafficSummary(BaseModel):
    total: int
    allow: int
    deny: int
    error: int
    internal: int
    transit: int

class SignedCommand(BaseModel):
    command_body: str  # JSON string of ToolRequest
    signature: str     # Hybrid signature (Ed25519 + ML-DSA)
    signer_id: str     # Agent ID of the remote sender
    nonce: int         # Monotonic counter for replay protection
    timestamp: datetime

