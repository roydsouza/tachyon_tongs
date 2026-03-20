import asyncio
import os
import sys

# Ensure the substrate is in path
sys.path.append(os.getcwd())

from tachyon.sandbox.wasm_runner import WasmRunner

def test_wasm_isolation():
    print("--- TIER 1 WASM ISOLATION TEST ---")
    runner = WasmRunner()
    wasm_path = "tachyon/sandbox/tools/safe_math.wasm"
    
    try:
        # Test the 'add' function: 10 + 20
        result = runner.run_tool(wasm_path, "add", 10, 20)
        print(f"RESULT (10 + 20): {result}")
        
        if result == 30:
            print("SUCCESS: WASM tool executed correctly.")
        else:
            print(f"FAIL: Unexpected result: {result}")
            
    except Exception as e:
        print(f"FAIL: Execution error: {e}")

if __name__ == "__main__":
    test_wasm_isolation()
