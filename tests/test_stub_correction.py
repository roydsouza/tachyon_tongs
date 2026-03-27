import pytest
from agents.synthesizer.agent import SynthesizerPlugin
from agents.scout.agent import ScoutPlugin

def test_stubs_return_not_implemented():
    """TDAD: Verifies that stubs now return NOT_IMPLEMENTED."""
    synth = SynthesizerPlugin(agent_id="test-synth", config={})
    scout = ScoutPlugin(agent_id="test-scout", config={})
    
    # After fix, these should return NOT_IMPLEMENTED
    r1 = synth.execute_action("synthesize_cedar", {"intent": "test"})
    r2 = synth.execute_action("synthesize_rego", {"intent": "test"})
    r3 = scout.execute_action("scout_network", {"target": "localhost"})
    
    assert r1["status"] == "NOT_IMPLEMENTED"
    assert r2["status"] == "NOT_IMPLEMENTED"
    assert r3["status"] == "NOT_IMPLEMENTED"
