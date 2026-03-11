import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.behavior_monitor import SyscallBehaviorMonitor, BehaviorAnomalyError
from src.behavior_monitor import SyscallBehaviorMonitor, BehaviorAnomalyError

def test_stable_behavior_flow():
    monitor = SyscallBehaviorMonitor(drift_threshold=3.0)
    agent = "test_agent_stable"
    
    # 5 fetches, 5 executes -> ratio 1:1, perfectly within < 3.0 threshold
    for _ in range(5):
        monitor.log_and_evaluate(agent, "safe_fetch")
        monitor.log_and_evaluate(agent, "safe_execute")
        
    stats = monitor.baselines[agent]
    assert stats["network"] == 6 # 5 + 1 starting smooth
    assert stats["execute"] == 6

def test_anomalous_drift_halting():
    monitor = SyscallBehaviorMonitor(drift_threshold=3.0)
    agent = "test_agent_hijacked"
    
    # Baseline establishment (4 of each)
    for _ in range(4):
        monitor.log_and_evaluate(agent, "safe_fetch")
        monitor.log_and_evaluate(agent, "safe_execute")
        
    # Attack begins: massive looping of execute without fetches
    with pytest.raises(BehaviorAnomalyError) as exc_info:
        for _ in range(15):
            monitor.log_and_evaluate(agent, "safe_execute")
            
    assert "Statistical syscall drift" in str(exc_info.value)
    
    # Ensure ERROR.md was touched
    error_file = os.path.join(os.path.dirname(__file__), '..', 'ERROR.md')
    assert os.path.exists(error_file)
    with open(error_file, 'r') as f:
        content = f.read()
        assert "test_agent_hijacked" in content
