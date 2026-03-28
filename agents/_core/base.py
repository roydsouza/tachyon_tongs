import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Union
import uuid
import json
import threading
from datetime import datetime
from tachyon.core.bus import TachyonEventBus
from tachyon.core.signing import IntegrityManager
from tachyon.core.state import StateManager
from tachyon.core.results import TachyonResult, TachyonStatus

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
        
        # Phase 33: Core Infrastructure Integration (w/ Dependency Injection)
        # Allows tests to pass their own mocks/proxies in config
        self.im = config.get("integrity_manager")
        if not self.im:
            # Phase 44: Standardize test mode hardware usage
            use_hardware = os.environ.get("TACHYON_TEST_MODE") != "1"
            self.im = IntegrityManager(use_hardware=use_hardware)
        
        self.bus = config.get("event_bus")
        if not self.bus:
            self.bus = TachyonEventBus(integrity_manager=self.im)
        
        # Phase 25.2: Recruitment of Delegated Identity
        # load_agent_identity updates self.im.signer internally and returns the certificate
        self.certificate = self.im.load_agent_identity(self.plugin_name.lower())
        if self.certificate:
             print(f"[{self.agent_id}] Operating with Delegated Identity (Role: {self.plugin_name})")
        else:
             print(f"[{self.agent_id}] Falling back to Root Identity (Unauthorized/Direct)")
             
        # Phase 44: Self-Heal Identity for Tests
        if not self.certificate and os.environ.get("TACHYON_TEST_MODE") == "1":
             print(f"[{self.agent_id}] TEST_MODE: Deriving missing identity for {self.plugin_name}...")
             self.im.derive_agent_key(self.plugin_name.lower(), save_to_disk=True)
             # Retry load
             self.certificate = self.im.load_agent_identity(self.plugin_name.lower())
        
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
            
            # Auto-wrap legacy dicts for backward compatibility during transition
            if isinstance(result, dict):
                result = TachyonResult(**result)
            
            status = result.status
        except Exception as e:
            result = TachyonResult.failure(str(e))
            status = TachyonStatus.ERROR
            
        # Phase 46: Fail-Loud Escalation (ADR-0061)
        if status in [TachyonStatus.ERROR, TachyonStatus.FATAL]:
            msg = f"Agent {self.agent_id} ({self.plugin_name}) failed action '{action}': {result.error or result.data}"
            StateManager().emit_alert("AGENT_ACTION_ERROR", msg)
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 3. Phase 33.2: Formal ActionRecord Generation
        record = {
            "version": "1.1", # Updated for Monadic Results
            "action_id": action_id,
            "agent_id": self.agent_id,
            "action": action,
            "parameters": parameters,
            "result_monad": result.model_dump(),
            "status": status.value,
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
            certificate=self.certificate
        )
        
    def emit_signed_event(self, topic: str, payload: Dict[str, Any]):
        """
        Emits a PQC-signed event to the EventBus.
        Automatically handles content construction and signing using the agent's identity.
        """
        timestamp = datetime.now().isoformat()
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # Pattern: topic + payload_json + timestamp (matches EventBus.verify_event)
        content = f"{topic}:{payload_json}:{timestamp}"
        signature = self.im.signer.sign(content.encode('utf-8'))
        
        self.bus.emit_event(
            topic=topic,
            agent_id=self.agent_id,
            payload=payload,
            signature=signature,
            certificate=self.certificate,
            timestamp=timestamp
        )

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to a specific topic on the EventBus."""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)

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

    def stop_backplane_loop(self):
        """Stop the backplane listener."""
        self._stop_event.set()
        if self._loop_thread:
            self._loop_thread.join(timeout=2)

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
            except Exception as e:
                # Phase 46: Fail-Loud Escalation (ADR-0061)
                msg = f"Agent {self.agent_id} ({self.plugin_name}) backplane loop CRASHED: {e}"
                StateManager().emit_alert("AGENT_BACKPLANE_CRASH", msg)
                
                try:
                    self.bus.emit_event(
                        topic="AGENT_CALLBACK_ERROR",
                        agent_id=self.agent_id,
                        payload={"error": str(e), "error_type": type(e).__name__},
                        certificate=self.certificate
                    )
                except Exception:
                    pass # Bus itself may be broken; don't recurse
                
            self._stop_event.wait(interval_sec)

    @abstractmethod
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Union[TachyonResult, Dict[str, Any]]:
        """Core execution logic for the plugin (to be implemented by subclasses)."""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata for registration."""
        return {
            "agent_id": self.agent_id,
            "plugin_name": self.plugin_name,
            "config": self.config
        }
