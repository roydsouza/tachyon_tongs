#!/usr/bin/env python3
"""
Tachyon Tongs: MCP (Model Context Protocol) Gateway
Creates an MCP-compliant Server over stdio that exposes the Tachyon Tongs Substrate
capabilities (Guardian Triad + Tier-0 Sandboxing) to any external agent framework.
"""

import sys
import json
import asyncio
import os

# Ensure sibling src directory is available
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.tachyon_client import safe_fetch, safe_execute

async def handle_mcp_request(request: dict) -> dict:
    """Process an incoming JSON-RPC 2.0 request from an MCP client."""
    method = request.get("method")
    req_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05", # Standard MCP version
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "tachyon-mcp-gateway",
                    "version": "1.0.0"
                }
            }
        }
        
    elif method == "notifications/initialized":
        return None # No response expected for notifications

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "tachyon_safe_fetch",
                        "description": "Fetch a URL but force it through the Tachyon Guardian Triad (Sanitizer/Analyzer/Verifier) to prevent prompt injection.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The URL to fetch safely."
                                }
                            },
                            "required": ["url"]
                        }
                    },
                    {
                        "name": "tachyon_safe_execute",
                        "description": "Execute a shell command inside the Tier-0 Apple Sandbox.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The bash command to run in the isolated environment."
                                }
                            },
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
        
        try:
            if tool_name == "tachyon_safe_fetch":
                url = args.get("url")
                # Route through the Substrate Daemon
                result = safe_fetch(url=url, agent_id="mcp_external_agent")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ],
                        "isError": result.get("status") == "ERROR" or result.get("status") == "BLOCKED"
                    }
                }
                
            elif tool_name == "tachyon_safe_execute":
                cmd = args.get("command")
                result = safe_execute(command=cmd, agent_id="mcp_external_agent")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ],
                        "isError": result.get("status") == "ERROR" or result.get("status") == "BLOCKED"
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)}
            }
            
    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {
                        "uri": "tachyon://intelligence/catalog",
                        "name": "Exploitation Catalog",
                        "description": "The master ledger of adversarial tactics and active CVEs discovered by the Sentinel.",
                        "mimeType": "text/markdown"
                    },
                    {
                        "uri": "tachyon://intelligence/sites",
                        "name": "Intelligence Sites",
                        "description": "Vetted intelligence destinations for threat scraping.",
                        "mimeType": "text/markdown"
                    }
                ]
            }
        }

    elif method == "resources/read":
        params = request.get("params", {})
        uri = params.get("uri")
        file_path = None
        
        if uri == "tachyon://intelligence/catalog":
            file_path = "intelligence/catalog.md"
        elif uri == "tachyon://intelligence/sites":
            file_path = "intelligence/sites.md"
            
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/markdown",
                            "text": content
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Resource '{uri}' not found."}
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not implemented."}
        }

async def run_stdio_server():
    """Reads JSON-RPC messages from stdin and writes to stdout."""
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8').strip()
            if not line_str:
                continue
                
            try:
                request = json.loads(line_str)
                response = await handle_mcp_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()
            except json.JSONDecodeError:
                sys.stderr.write(f"Invalid JSON received: {line_str}\n")
                sys.stderr.flush()
                
        except Exception as e:
            sys.stderr.write(f"MCP Server error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    try:
        asyncio.run(run_stdio_server())
    except KeyboardInterrupt:
        pass
