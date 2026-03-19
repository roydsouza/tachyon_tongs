import pytest
import asyncio
from typing import Dict, Any
from tachyon.enforcement.router import ImmutableToolRequest, recursive_freeze
from types import MappingProxyType

def test_recursive_freeze_dict():
    data = {"a": 1, "b": {"c": 2}}
    frozen = recursive_freeze(data)
    assert isinstance(frozen, MappingProxyType)
    assert isinstance(frozen["b"], MappingProxyType)
    assert frozen["a"] == 1
    assert frozen["b"]["c"] == 2
    
    with pytest.raises(TypeError):
        frozen["a"] = 2
    with pytest.raises(TypeError):
        frozen["b"]["c"] = 3

def test_recursive_freeze_list():
    data = {"a": [1, 2, {"b": 3}]}
    frozen = recursive_freeze(data)
    assert isinstance(frozen["a"], tuple)
    assert isinstance(frozen["a"][2], MappingProxyType)
    assert frozen["a"][2]["b"] == 3

def test_immutable_tool_request_toctou():
    params = {"target": "original"}
    request = ImmutableToolRequest(agent_id="test-agent", action="test-action", params=params)
    
    # Attempt mutation of the original dictionary
    params["target"] = "mutated"
    
    # Verify the request remains original
    assert request.params["target"] == "original"
    
    # Attempt mutation of the request params directly
    with pytest.raises(TypeError):
        request.params["target"] = "mutated"
