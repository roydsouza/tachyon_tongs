#!/usr/bin/env python3
"""
Tachyon Tongs: MCP (Model Context Protocol) Gateway
Refactored to use the unified ToolRouter.
"""

import sys
import json
import asyncio
import os

from tachyon.enforcement import AppleSandbox, ToolRouter, safe_fetch
from tachyon.pipeline import SentinelOrchestrator
from tachyon.monitoring import syscall_monitor
from tachyon.policy import PolicyEngine

# Initialize shared components
sandbox = AppleSandbox(workspace_dir="/tmp/tachyon_mcp_tier0")
orchestrator = SentinelOrchestrator()
policy_engine = PolicyEngine()
router = ToolRouter(orchestrator, sandbox, policy_engine, None, syscall_monitor)

async def handle_mcp_request(request: dict) -> dict:
    method = request.get("method")
    req_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "tachyon-mcp-gateway", "version": "1.0.0"}
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "safe_fetch",
                        "description": "Fetch a URL safely through the Prophylactic Pipeline.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"url": {"type": "string"}},
                            "required": ["url"]
                        }
                    },
                    {
                        "name": "safe_execute",
                        "description": "Execute a shell command inside the Tier-0 Sandbox.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"command": {"type": "string"}},
                            "required": ["command"]
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        # Route through unified ToolRouter
        result = await router.route("mcp_external_agent", tool_name, args)
        
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}],
                "isError": result.get("status") != "SUCCESS"
            }
        }
        
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
