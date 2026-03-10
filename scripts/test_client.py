"""
Tachyon Tongs: Substrate Client Verification Script
Simulates an external "AshaAgent" and "SynthesisAgent" calling the Daemon via the SDK.
"""
import sys
import os

# Ensure the sibling src directory is reachable without pip install for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tachyon_client import safe_fetch

def test_substrate_routing():
    print("🚀 Simulating external Agent calls to the Substrate Daemon...\n")
    
    # 1. Asha attempts to read a safe resource.
    print("[AshaAgent] Attempting to fetch a safe Wikipedia article...")
    res1 = safe_fetch("https://en.wikipedia.org/wiki/Artificial_intelligence", agent_id="AshaAgent")
    print(f"Status: {res1.get('status')} | Response Preview: {str(res1.get('content'))[:50]}...\n")
    
    # 2. Synthesis explores an unknown but potentially safe site.
    print("[SynthesisAgent] Attempting to fetch a threat intel framework...")
    res2 = safe_fetch("https://github.com/promptfoo/promptfoo", agent_id="SynthesisAgent")
    print(f"Status: {res2.get('status')} | Response Preview: {str(res2.get('content'))[:50]}...\n")

if __name__ == "__main__":
    test_substrate_routing()
    print("✅ Completed. Please verify RUN_LOG.md shows isolated Agent IDs.")
