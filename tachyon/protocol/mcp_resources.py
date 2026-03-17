"""
Tachyon Tongs: MCP Resource Management
Ensures that external agents can only access whitelisted substrate assets.
"""

from typing import Dict, Any, List
import os

class MCPResourceManager:
    def __init__(self):
        # Whitelisted resources for the cumulative regression suite
        self.resources = {
            "tachyon://catalog": "# 📘 EXPLOITATION CATALOG\nMock catalog for testing.",
            "tachyon://audit/last": "RUN: 2026-03-17\nStatus: SUCCESS"
        }

    def list_resources(self) -> List[Dict[str, Any]]:
        """Lists available resources in Model Context Protocol format."""
        return [
            {
                "uri": "tachyon://intelligence/catalog",
                "name": "Exploitation Catalog",
                "mimeType": "text/markdown",
                "description": "Master list of identified threats."
            },
            {
                "uri": "tachyon://intelligence/sites",
                "name": "Audit Sites",
                "mimeType": "text/markdown",
                "description": "List of sites to be audited."
            }
        ]

    def read_resource(self, uri: str) -> str:
        """Reads a whitelisted resource by URI."""
        if uri == "tachyon://intelligence/catalog":
             path = "intelligence/catalog.md"
             if os.path.exists(path):
                 with open(path, "r") as f:
                     return f.read()
             return "# 📘 EXPLOITATION CATALOG\nMock catalog for testing."
        elif uri == "tachyon://intelligence/sites":
             return "https://example.com"
        raise ValueError(f"Resource '{uri}' not found.")

async def handle_mcp_resource_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Mock handler for MCP resource requests."""
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})
    
    manager = MCPResourceManager()
    
    try:
        if method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"resources": manager.list_resources()}
            }
        elif method == "resources/read":
            uri = params.get("uri")
            content = manager.read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [{"uri": uri, "mimeType": "text/markdown", "text": content}]
                }
            }
    except ValueError as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32602, "message": str(e)}
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32603, "message": str(e)}
        }
        
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not found."}
    }
