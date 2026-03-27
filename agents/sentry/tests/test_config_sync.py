import yaml
import os

def test_sentry_config_sync_success():
    """TDAD: Verifies that Sentry config now contains synchronized values."""
    config_path = "agents/sentry/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    assert config['agent_id'] == "sentry-001"
    assert config['name'] == "Sentry"
    assert config['entry_point'] == "agents.sentry.agent:SentryPlugin"
    assert "check_signals" in config['capabilities']
