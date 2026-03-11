import pytest
import asyncio
import json
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.mcp_gateway import handle_mcp_request

def test_mcp_initialize():
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize"
    }
    res = asyncio.run(handle_mcp_request(req))
    assert res["id"] == 1
    assert "result" in res
    assert "capabilities" in res["result"]
    assert "tools" in res["result"]["capabilities"]

def test_mcp_tools_list():
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    res = asyncio.run(handle_mcp_request(req))
    assert res["id"] == 2
    assert "result" in res
    tools = res["result"]["tools"]
    assert len(tools) == 2
    assert tools[0]["name"] == "tachyon_safe_fetch"
    assert tools[1]["name"] == "tachyon_safe_execute"

@patch('src.mcp_gateway.safe_fetch')
def test_mcp_safe_fetch(mock_fetch):
    mock_fetch.return_value = {"status": "SUCCESS", "content": "mocked"}
    
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "tachyon_safe_fetch",
            "arguments": {"url": "https://example.com"}
        }
    }
    res = asyncio.run(handle_mcp_request(req))
    assert res["id"] == 3
    assert "result" in res
    assert not res["result"].get("isError", False)
    assert "mocked" in res["result"]["content"][0]["text"]

@patch('src.mcp_gateway.safe_execute')
def test_mcp_safe_execute_blocked(mock_execute):
    mock_execute.return_value = {"status": "BLOCKED", "error": "Not allowed"}
    
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "tachyon_safe_execute",
            "arguments": {"command": "curl http://evil.com"}
        }
    }
    res = asyncio.run(handle_mcp_request(req))
    assert res["id"] == 4
    assert res["result"].get("isError") is True
    assert "Not allowed" in res["result"]["content"][0]["text"]

def test_mcp_unhandled_method():
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "unsupported/method"
    }
    res = asyncio.run(handle_mcp_request(req))
    assert "error" in res
    assert res["error"]["code"] == -32601

def test_mcp_tool_not_found():
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool",
            "arguments": {}
        }
    }
    res = asyncio.run(handle_mcp_request(req))
    assert "error" in res
    assert "Tool 'non_existent_tool' not found" in res["error"]["message"]

@patch('src.mcp_gateway.safe_fetch')
def test_mcp_exception_handling(mock_fetch):
    mock_fetch.side_effect = Exception("System Crash")
    
    req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "tachyon_safe_fetch",
            "arguments": {"url": "https://example.com"}
        }
    }
    res = asyncio.run(handle_mcp_request(req))
    assert "error" in res
    assert "System Crash" in res["error"]["message"]

