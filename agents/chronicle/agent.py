import os
import time
import json
from typing import Dict, Any, List
from datetime import datetime
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from tachyon.core.state import StateManager

class ChronicleEngine:
    """Temporal Reasoning & Drift Analysis Engine."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = StateManager()
        self.velocity_threshold = 20 # events per 5 min window
        
    def analyze_trajectory(self, target_agent_id: str) -> Dict[str, Any]:
        """Analyze the recent trajectory of an agent for drift or velocity issues."""
        velocity = self.state.get_velocity(target_agent_id, window_minutes=5)
        history = self.state.get_agent_trajectories(target_agent_id, limit=20)
        
        anomalies = []
        if velocity > self.velocity_threshold:
            anomalies.append(f"VELOCITY_VIOLATION: {velocity} events in 5m window.")
            
        # Role Drift Logic (Simplified for Phase 1)
        # Check if a non-engineer agent is proposes patches
        if target_agent_id != "engineer":
            patch_plans = [h for h in history if "PATCH_PROPOSED" in h.get('topic', '')]
            if patch_plans:
                anomalies.append(f"ROLE_DRIFT: Non-engineer agent attempting patch proposals.")
                
        if anomalies:
            msg = f"Temporal Anomaly detected for Agent '{target_agent_id}': " + " | ".join(anomalies)
            self.state.emit_alert("TEMPORAL_ANOMALY", msg)
            return {"status": "ANOMALY_DETECTED", "details": anomalies}
            
        return {"status": "CLEAR", "velocity": velocity}

@AgentRegistry.register("chronicle")
class ChroniclePlugin(BaseAgentPlugin):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Chronicle", config)
        self.engine = ChronicleEngine(agent_id)
        
        # Subscribe to high-signal topics to build trajectories
        self.subscribe("COMMAND_EXECUTION", self._on_agent_activity)
        self.subscribe("PATCH_PROPOSED", self._on_agent_activity)
        self.subscribe("SENSITIVE_READ", self._on_agent_activity)
        self.subscribe("AGENT_ACTION_ERROR", self._on_agent_activity)

    def _on_agent_activity(self, payload: Dict[str, Any]):
        """Record and analyze agent activity as it hits the backplane."""
        actor = payload.get("agent_id", "UNKNOWN")
        topic = payload.get("topic", "UNKNOWN")
        details = json.dumps(payload.get("details", payload))
        
        # 1. Log to forensic ledger
        self.engine.state.log_forensic_event(actor, topic, details)
        
        # 2. Perform realtime drift analysis
        self.engine.analyze_trajectory(actor)

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> TachyonResult:
        from tachyon.core.results import TachyonResult, TachyonStatus
        if action == "analyze_drift":
            target = parameters.get("target_agent_id")
            if not target:
                return TachyonResult.failure("Missing 'target_agent_id'")
            res = self.engine.analyze_trajectory(target)
            return TachyonResult.success(res)
        return TachyonResult.failure(f"Unknown action: {action}", status=TachyonStatus.NOT_IMPLEMENTED)
