import pytest
import json
import os
import sys
from src.mcp_gateway import handle_mcp_request

@pytest.mark.asyncio
async def test_mcp_resources_list():
    """Verify that the MCP gateway returns the list of available resources."""
    request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "resources/list"
    }
    response = await handle_mcp_request(request)
    
    assert "result" in response
    assert "resources" in response["result"]
    resources = response["result"]["resources"]
    
    uris = [r["uri"] for r in resources]
    assert "tachyon://intelligence/catalog" in uris
    assert "tachyon://intelligence/sites" in uris

@pytest.mark.asyncio
async def test_mcp_resources_read_catalog():
    """Verify that the MCP gateway can read the catalog resource."""
    # Ensure the catalog exists for the test
    os.makedirs("intelligence", exist_ok=True)
    with open("intelligence/catalog.md", "w") as f:
        f.write("# Test Catalog\nCVE-TEST-999")
        
    request = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "resources/read",
        "params": {
            "uri": "tachyon://intelligence/catalog"
        }
    }
    response = await handle_mcp_request(request)
    
    assert "result" in response
    assert "contents" in response["result"]
    content = response["result"]["contents"][0]
    assert content["uri"] == "tachyon://intelligence/catalog"
    assert "# Test Catalog" in content["text"]

@pytest.mark.asyncio
async def test_mcp_resources_read_not_found():
    """Verify error handling for non-existent resource URIs."""
    request = {
        "jsonrpc": "2.0",
        "id": "3",
        "method": "resources/read",
        "params": {
            "uri": "tachyon://unreal/resource"
        }
    }
    response = await handle_mcp_request(request)
    
    assert "error" in response
    assert response["error"]["code"] == -32602
