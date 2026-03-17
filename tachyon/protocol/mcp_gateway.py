#!/usr/bin/env python3
"""
Tachyon Tongs: MCP (Model Context Protocol) Gateway
Refactored to use the unified ToolRouter.
"""

import sys
import json
import asyncio
import os

from tachyon.enforcement.apple_sandbox import AppleSandbox
from tachyon.enforcement.router import ToolRouter
from tachyon.enforcement.safe_fetch import safe_fetch

def safe_execute(*args, **kwargs):
    # Shim for mocking
    pass

from tachyon.pipeline.orchestrator import SentinelOrchestrator
from tachyon.monitoring import syscall_monitor
from tachyon.policy.singularity import SingularityPDP as PolicyEngine

class MCPGateway:
    def __init__(self):
        self.sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_mcp_tier0")
        self.orchestrator = SentinelOrchestrator()
        self.policy_engine = PolicyEngine()
        self.router = ToolRouter(self.orchestrator, self.sandbox, self.policy_engine, None, syscall_monitor)

    async def handle_request(self, request: dict) -> dict:
        return await handle_mcp_request(request, self.router)

MCPHandler = MCPGateway

async def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Mock handler for MCP requests."""
    method = request.get("method")
    req_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "TachyonServer", "version": "1.0"}
            }
        }
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {"name": "tachyon_safe_fetch", "description": "Fetch content safely"},
                    {"name": "tachyon_safe_execute", "description": "Execute command safely"}
                ]
            }
        }
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        # Strip 'tachyon_' prefix for internal routing if present
        internal_name = tool_name.replace("tachyon_", "")
        
        # Route through unified ToolRouter
        result = await router.route("mcp_external_agent", internal_name, args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "isError": result.get("status") != "SUCCESS"
            }
        }
        
    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        if tool_name not in ["tachyon_safe_fetch", "tachyon_safe_execute"]:
             raise ValueError(f"Tool '{tool_name}' not found")

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

async def run_stdio_server():
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line: break
        try:
            request = json.loads(line.decode('utf-8'))
            response = await handle_mcp_request(request)
            if response:
                sys.stdout.write(json.dumps(response) + '\n')
                sys.stdout.flush()
        except: pass

if __name__ == "__main__":
    asyncio.run(run_stdio_server())
