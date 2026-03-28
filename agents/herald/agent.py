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
        from .collectors.engine import FileLogCollector, AirlockCollector, TaskCollector, ForensicCollector
        self.collectors = [
            ForensicCollector(), # High-Assurance SQL Ledger
            FileLogCollector("ALERT.md", r"## \[(.*?)\] (.*?)\n"),
            FileLogCollector("logs/EVOLUTION.md", r"## \[(.*?)\] (.*?)\n"),
            AirlockCollector(),
            TaskCollector("tasks/TASKS_CLEANUP.md")
        ]
        self.dispatchers = [ConsoleDispatcher()]
        # Future: Add Slack/Signal dispatchers from config

    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        from tachyon.core.results import TachyonResult, TachyonStatus
        if action == "aggregate_summary":
            all_events = self._collect_all()
            return TachyonResult.success({
                "event_count": len(all_events),
                "summary": all_events
            })
        
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
                    # M-09: Sanitize before dispatching to external channels
                    sanitized_event = self._sanitize_event(event)
                    dispatcher.dispatch(sanitized_event)
            return TachyonResult.success({"relayed_count": len(new_events)})

        return TachyonResult.failure(f"Unknown action: {action}", status=TachyonStatus.NOT_IMPLEMENTED)

    def _sanitize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Signal Purification: Strips newlines and truncates URLs (M-09)."""
        import re
        clean_event = event.copy()
        summary = str(clean_event.get("summary", ""))
        
        # 1. Flatten newlines to prevent multi-line injection in Signal/Slack
        summary = summary.replace("\n", " | ").replace("\r", "")
        
        # 2. Truncate long URLs to prevent buffer overflow/obfuscation (limit to 256 chars)
        def _truncate_url(match):
            url = match.group(0)
            return url[:253] + "..." if len(url) > 256 else url
            
        summary = re.sub(r'https?://[^\s<>"]+|www\.[^\s<>"]+', _truncate_url, summary)
        
        # 3. Overall length limit
        if len(summary) > 2000:
             summary = summary[:1997] + "..."
             
        clean_event["summary"] = summary
        return clean_event

    def _collect_all(self) -> List[Dict[str, Any]]:
        all_events = []
        for collector in self.collectors:
            try:
                all_events.extend(collector.collect())
            except Exception as e:
                print(f"[{self.agent_id}] Collector {collector.__class__.__name__} failed: {e}")
                self.bus.emit_event(
                    topic="HERALD_COLLECTOR_ERROR",
                    agent_id=self.agent_id,
                    payload={"collector": collector.__class__.__name__, "error": str(e)},
                    certificate=self.certificate
                )
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
