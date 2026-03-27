import pytest
from unittest.mock import MagicMock, patch
from agents.herald.agent import HeraldPlugin

class MockCollector:
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail
    def collect(self):
        if self.should_fail:
            raise RuntimeError(f"Collector {self.name} failure")
        return [{"id": f"event-{self.name}", "type": "TEST", "summary": f"Data from {self.name}"}]

def test_herald_collector_resiliency_success():
    """TDAD: Verifies that Herald now survives single collector failures."""
    mock_bus = MagicMock()
    mock_bus.certificate = "HERALD-CERT"
    config = {}
    herald = HeraldPlugin(agent_id="herald-test", config=config)
    herald.certificate = "HERALD-CERT"
    herald.bus = mock_bus
    
    # Inject mock collectors
    good_collector = MockCollector("good")
    bad_collector = MockCollector("bad", should_fail=True)
    herald.collectors = [bad_collector, good_collector]
    
    # Trigger aggregation
    result = herald.execute_action("aggregate_summary", {})
    
    assert result["status"] == "SUCCESS"
    assert result["event_count"] == 1 # Data from 'good' collector
    assert result["summary"][0]["id"] == "event-good"
    
    # Verify error emission
    errors = [call for call in mock_bus.emit_event.call_args_list if call.kwargs.get('topic') == "HERALD_COLLECTOR_ERROR"]
    assert len(errors) == 1
    assert errors[0].kwargs['payload']['collector'] == "MockCollector"
    assert errors[0].kwargs['certificate'] == "HERALD-CERT"
