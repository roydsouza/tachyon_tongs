import os
import sys
# Add project root to PYTHONPATH
sys.path.append(os.getcwd())

from agents._core.registry import AgentRegistry

def test_registry_discovery():
    print("🔍 [Test] Discovering plugins in 'agents/'...")
    AgentRegistry.discover_plugins("agents")
    
    plugins = AgentRegistry.list_plugins()
    print(f"✅ [Test] Plugins discovered: {plugins}")
    
    assert "guardian" in plugins
    
    guardian_cls = AgentRegistry.get_plugin("guardian")
    guardian = guardian_cls(agent_id="test-guardian", config={})
    
    print("🔍 [Test] Testing Guardian 'verify_file' action on TASKS_CLEANUP.md...")
    result = guardian.execute_action("verify_file", {"filepath": "TASKS_CLEANUP.md"})
    print(f"✅ [Test] Result: {result}")
    
    assert result["status"] == "SUCCESS"
    assert "is_valid" in result

if __name__ == "__main__":
    try:
        test_registry_discovery()
        print("\n🚀 [FINAL] PLUGIN SMOKE TEST PASSED!")
    except Exception as e:
        print(f"\n❌ [FINAL] PLUGIN SMOKE TEST FAILED: {e}")
        sys.exit(1)
