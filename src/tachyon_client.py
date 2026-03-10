import requests
import os
from typing import Dict, Any, Optional

class TachyonClient:
    """
    Lightweight client for the Tachyon Tongs Substrate.
    Agents use this to request safe tool execution.
    """
    def __init__(self, agent_id: str, tenant_id: str = "default", base_url: str = "http://127.0.0.1:60461"):
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.base_url = base_url

    def safe_fetch(self, url: str) -> Dict[str, Any]:
        """
        Requests the substrate to fetch and sanitize a URL.
        """
        payload = {
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "action": "safe_fetch",
            "parameters": {"url": url}
        }
        try:
            response = requests.post(f"{self.base_url}/action", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def health_check(self) -> bool:
        """Verifies the Substrate Daemon is alive."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

# Convenience singleton instance
def get_client(agent_id: str) -> TachyonClient:
    return TachyonClient(agent_id=agent_id)

# Top-level procedural wrappers for easy import
def safe_fetch(url: str, agent_id: str = "AnonymousAgent", tenant_id: str = "default") -> Dict[str, Any]:
    """
    Convenience wrapper that dynamically spins up a TachyonClient to execute a fetch.
    Returns: {"status": "SUCCESS" | "BLOCKED" | "ERROR", ...}
    """
    client = TachyonClient(agent_id=agent_id, tenant_id=tenant_id)
    return client.safe_fetch(url)

def safe_execute(command: str, agent_id: str = "AnonymousAgent", tenant_id: str = "default") -> Dict[str, Any]:
    """
    Stub for the safe_execute action boundary (to be implemented in the Substrate).
    """
    client = TachyonClient(agent_id=agent_id, tenant_id=tenant_id)
    payload = {
        "agent_id": client.agent_id,
        "tenant_id": client.tenant_id,
        "action": "safe_execute",
        "parameters": {"command": command}
    }
    try:
        response = requests.post(f"{client.base_url}/action", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
