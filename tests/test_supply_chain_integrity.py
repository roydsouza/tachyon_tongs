import pytest
import unittest.mock as mock
from src.agents.integrity_agent import IntegrityAgent

# Scaffolding for the Integrity Agent since we haven't implemented the logic yet
# This test will drive the implementation.

def test_hallucination_squatting_block():
    """Verify that the system blocks unknown/hallucinated packages."""
    agent = IntegrityAgent()
    
    # Simulating a hallucinated package name
    malicious_pkg = "hallucinated-agent-tool-9999"
    
    # Deterministic binding check
    with mock.patch("src.state_manager.StateManager.is_package_whitelisted", return_value=False):
        verdict = agent.audit_install_request(malicious_pkg)
        assert verdict["status"] == "REJECTED"
        assert "not in the trusted registry" in verdict["reason"]

def test_vulnerability_interception():
    """Verify that pip-audit style scanning blocks known vulnerable packages."""
    agent = IntegrityAgent()
    
    # Simulating a package with a known CVE (e.g., an old version of requests)
    vulnerable_pkg = "requests==2.20.0"
    
    # Mocking the vulnerability scanner result
    with mock.patch("src.agents.integrity_agent.IntegrityAgent._scan_package", return_value={"vulnerabilities": ["CVE-2018-18074"]}):
        verdict = agent.audit_install_request(vulnerable_pkg)
        assert verdict["status"] == "REJECTED"
        assert "CVE-2018-18074" in str(verdict["vulnerabilities"])
