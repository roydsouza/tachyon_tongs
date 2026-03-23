from typing import Dict, Any

class BaseDispatcher:
    def __init__(self, dispatcher_id: str):
        self.dispatcher_id = dispatcher_id

    def dispatch(self, event: Dict[str, Any]):
        raise NotImplementedError

class ConsoleDispatcher(BaseDispatcher):
    def __init__(self):
        super().__init__("console")

    def dispatch(self, event: Dict[str, Any]):
        e_type = event.get("type", "EVENT")
        source = event.get("source", "Unknown")
        summary = event.get("summary") or event.get("id")
        
        status_prefix = "📣"
        if event.get("remediation_status") == "RESOLVED":
            status_prefix = "✅ [RESOLVED]"
            
        print(f"{status_prefix} [{e_type}] from {source}: {summary}")
        if "resolution" in event:
            print(f"    └─ Recovery: {event['resolution']}")

class WebhookDispatcher(BaseDispatcher):
    def __init__(self, dispatcher_id: str, url: str):
        super().__init__(dispatcher_id)
        self.url = url

    def dispatch(self, event: Dict[str, Any]):
        # Mocking webhook dispatch
        # In production: requests.post(self.url, json=event)
        pass
