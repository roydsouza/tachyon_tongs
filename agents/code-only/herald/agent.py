from typing import Dict, Any, List
from agents._core.base import BaseAgentPlugin
from agents._core.registry import AgentRegistry
from .collectors.engine import FileLogCollector, AirlockCollector, TaskCollector
from .dispatchers.engine import ConsoleDispatcher
from .healer import Healer

@AgentRegistry.register("herald")
class HeraldPlugin(BaseAgentPlugin):
    """
    Herald Plugin: High-Assurance Unified Aggregator with Autonomic Self-Healing.
    """
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, "Herald", config)
        self.healer = Healer()
        self.collectors = [
            FileLogCollector("ALERT.md", r"## \[(.*?)\] (.*?)\n"),
            FileLogCollector("logs/EVOLUTION.md", r"## \[(.*?)\] (.*?)\n"),
            AirlockCollector(),
            TaskCollector("TASKS.md")
        ]
        self.dispatchers = [ConsoleDispatcher()]
        # Future: Add Slack/Signal dispatchers from config

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "aggregate_summary":
            all_events = self._collect_all()
            return {
                "status": "SUCCESS",
                "event_count": len(all_events),
                "summary": all_events
            }
        
        if action == "relay_new_events":
            new_events = self._get_new_events()
            for event in new_events:
                # Autonomic Healing Check
                event_type = event.get("type", "")
                if "Failure" in event_type or "FAILURE" in event_type:
                    resolution = self.healer.attempt_repair(event.get("summary", ""))
                    if resolution:
                        event["remediation_status"] = "RESOLVED"
                        event["resolution"] = resolution
                        # Log the successful repair back to evolution
                        from tachyon.core.state import StateManager
                        StateManager().log_evolution("SOMATIC_REPAIR", f"Herald resolved failure: {resolution}")
                
                for dispatcher in self.dispatchers:
                    # Mark as relayed FIRST to avoid double-processing during repairs
                    from tachyon.core.state import StateManager
                    StateManager().mark_event_relayed(dispatcher.dispatcher_id, event["id"])
                    dispatcher.dispatch(event)
            return {"status": "SUCCESS", "relayed_count": len(new_events)}

        return {"status": "ERROR", "message": f"Unknown action: {action}"}

    def _collect_all(self) -> List[Dict[str, Any]]:
        all_events = []
        for collector in self.collectors:
            all_events.extend(collector.collect())
        return all_events

    def _get_new_events(self) -> List[Dict[str, Any]]:
        from tachyon.core.state import StateManager
        state = StateManager()
        all_events = self._collect_all()
        new_events = []
        for event in all_events:
            # Check if ANY dispatcher hasn't seen this yet
            # (Simplification: if console hasn't seen it, it's 'new')
            if not state.is_event_relayed("console", event["id"]):
                new_events.append(event)
        return new_events
