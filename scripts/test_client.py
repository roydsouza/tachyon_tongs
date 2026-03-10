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
    
    # 1. Asha fetches Wikipedia WITH a strict whitelist
    print("[AshaAgent] Fetching Wikipedia with allowed_domains=['en.wikipedia.org']...")
    res1 = safe_fetch("https://en.wikipedia.org/wiki/Artificial_intelligence", agent_id="AshaAgent", allowed_domains=["en.wikipedia.org"])
    print(f"Status: {res1.get('status')} | Expected: SUCCESS\n")
    
    # 2. Asha attempts to fetch GitHub WITH a strict whitelist for Wikipedia
    print("[AshaAgent] Fetching GitHub with allowed_domains=['en.wikipedia.org']...")
    res2 = safe_fetch("https://github.com/promptfoo/promptfoo", agent_id="AshaAgent", allowed_domains=["en.wikipedia.org"])
    print(f"Status: {res2.get('status')} | Expected: BLOCKED\n")

    # 3. Synthesis fetches GitHub relying PURELY on Semantic Filtering
    print("[SynthesisAgent] Fetching GitHub with Pure Semantic Filtering...")
    res3 = safe_fetch("https://github.com/promptfoo/promptfoo", agent_id="SynthesisAgent")
    print(f"Status: {res3.get('status')} | Expected: SUCCESS\n")
    
    # 4. Synthesis fetches Pastebin (Global Denylist) relying on Semantic Filtering
    print("[SynthesisAgent] Fetching Pastebin (Global Deny) with Pure Semantic Filtering...")
    res4 = safe_fetch("https://pastebin.com/raw/malicious", agent_id="SynthesisAgent")
    print(f"Status: {res4.get('status')} | Expected: BLOCKED\n")

if __name__ == "__main__":
    test_substrate_routing()
    print("✅ Completed. Please verify RUN_LOG.md shows isolated Agent IDs.")
