from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import uuid
import json
import threading
from datetime import datetime
from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager

class BaseAgentPlugin(ABC):
    """
    Standardized interface for all Tachyon Tongs agent plugins.
    Ensures consistent lifecycle management and registration.
    """
    def __init__(self, agent_id: str, plugin_name: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.plugin_name = plugin_name
        self.config = config
        self.quarantine_mode = config.get("quarantine_mode", False)
        self.graduated = config.get("graduated", not self.quarantine_mode)
        
        # Phase 33: Core Infrastructure Integration
        self.im = IntegrityManager()
        self.bus = TachyonEventBus(integrity_manager=self.im)
        
        # Phase 25.2: Recruitment of Delegated Identity
        self.certificate = self.im.load_agent_identity(self.plugin_name.lower())
        if self.certificate:
             print(f"[{self.agent_id}] Operating with Delegated Identity (Role: {self.plugin_name})")
        else:
             print(f"[{self.agent_id}] Falling back to Root Identity (Unauthorized/Direct)")
        
        # Subscriptions & Backplane Loop
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._stop_event = threading.Event()
        self._loop_thread: Optional[threading.Thread] = None
        self._last_event_id = 0
        
        # Lifecycle: Notify the collective of agent presence
        self.bus.emit_event(
            topic="AGENT_BOOT",
            agent_id=self.agent_id,
            payload={
                "plugin_name": self.plugin_name,
                "status": "INITIALIZING",
                "graduated": self.graduated
            },
            certificate=self.certificate
        )

    def run_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public entry point for executing agent actions.
        Wraps execute_action with auditing, telemetry, and signing.
        """
        action_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # 1. Telemetry: Action Start
        self.bus.emit_event(
            topic="ACTION_START",
            agent_id=self.agent_id,
            payload={
                "action": action,
                "action_id": action_id,
                "parameters": parameters
            },
            certificate=self.certificate
        )
        
        try:
            # 2. Execution
            result = self.execute_action(action, parameters)
            status = result.get("status", "SUCCESS")
        except Exception as e:
            result = {"status": "ERROR", "message": str(e)}
            status = "ERROR"
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 3. Phase 33.2: Formal ActionRecord Generation
        record = {
            "version": "1.0",
            "action_id": action_id,
            "agent_id": self.agent_id,
            "action": action,
            "parameters": parameters,
            "result": result,
            "status": status,
            "duration_sec": duration,
            "timestamp": end_time.isoformat()
        }
        
        # 4. PQC Signing (ActionRecord Integrity)
        record_json = json.dumps(record, sort_keys=True)
        signature = self.im.signer.sign(record_json.encode('utf-8'))
        
        # 5. Telemetry: Action Completed (Auditable Record)
        self.bus.emit_event(
            topic="ACTION_COMPLETED",
            agent_id=self.agent_id,
            payload=record,
            signature=signature,
            certificate=self.certificate
        )
        
        return result

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to a specific topic on the EventBus."""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)
        print(f"[{self.agent_id}] Subscribed to topic: {topic}")

    def start_backplane_loop(self, interval_sec: int = 5):
        """Start the background thread listening for EventBus signals."""
        if self._loop_thread and self._loop_thread.is_alive():
            return
            
        self._stop_event.clear()
        self._loop_thread = threading.Thread(
            target=self._backplane_loop, 
            args=(interval_sec,),
            daemon=True,
            name=f"BackplaneLoop-{self.agent_id}"
        )
        self._loop_thread.start()
        print(f"[{self.agent_id}] Backplane signal loop started.")

    def stop_backplane_loop(self):
        """Stop the backplane listener."""
        self._stop_event.set()
        if self._loop_thread:
            self._loop_thread.join(timeout=2)
        print(f"[{self.agent_id}] Backplane signal loop stopped.")

    def _backplane_loop(self, interval_sec: int):
        """Internal loop to fetch and route events."""
        while not self._stop_event.is_set():
            try:
                # Fetch new events for all subscribed topics
                for topic in self._subscriptions.keys():
                    events = self.bus.fetch_events(topic=topic, after_id=self._last_event_id)
                    for event in events:
                        # Update high-water mark
                        self._last_event_id = max(self._last_event_id, event['id'])
                        
                        # Phase 33: Automatic Event Verification
                        # verify_event checks the PQC signature and delegation chain
                        is_valid = self.bus.verify_event(event['id'])
                        
                        payload = json.loads(event['payload_json'])
                        
                        if is_valid:
                            # Route to callbacks
                            for callback in self._subscriptions.get(topic, []):
                                callback(payload)
                        else:
                            print(f"[SECURITY] Suppressing UNSIGNED or INVALID event {event['id']} on topic {topic}")
            except Exception as e:
                print(f"[{self.agent_id}] Backplane Loop Error: {e}")
                
            self._stop_event.wait(interval_sec)

    @abstractmethod
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic for the plugin (to be implemented by subclasses)."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata for registration."""
        return {
            "agent_id": self.agent_id,
            "plugin_name": self.plugin_name,
            "config": self.config
        }
