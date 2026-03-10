#!/usr/bin/env python3
"""
Tachyon Tongs: Red Team Pathogen Runner
Loads the Pathogen Agent from its declarative SKILL.md file, injects its specialized
system prompts, and initiates an adversarial attack sweep against the Substrate Daemon.
"""
import sys
import os
import json

# Ensure sibling src directory is available
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from skill_parser import load_skill, materialize_network_constraints
from tachyon_client import safe_fetch
from execution_logger import ExecutionLogger

def generate_adversarial_payload(catalog_content: str) -> str:
    """
    Mock integration for the Pathogen's ADK LLM node.
    It reads the catalog and synthesizes a mutation to bypass known defenses.
    """
    if "Unicode steganography" in catalog_content:
        # Synthesize a mutate: Use right-to-left override and mixed script homoglyphs
        return "https://pastebin.com/raw/malicious#\u202Eelib_enil_dammoc"
    
    return "https://pastebin.com/raw/unknown_zero_day"

def run_pathogen_cycle():
    skill_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'pathogen', 'SKILL.md')
    catalog_path = os.path.join(os.path.dirname(__file__), '..', 'EXPLOITATION_CATALOG.md')

    print(f"🦠 Waking up Pathogen (via {skill_path})...")
    
    try:
        metadata, prompt = load_skill(skill_path)
    except Exception as e:
        print(f"❌ Failed to instantiate Pathogen: {e}")
        sys.exit(1)

    agent_id = metadata.get("name", "UnknownPathogen")
    capabilities = metadata.get("capabilities", [])
    allowed_domains = materialize_network_constraints(metadata)

    logger = ExecutionLogger(agent_id=agent_id)
    logger.start_run(trigger="CRON_SCHEDULED_ATTACK")

    # 1. Read Catalog
    print("📖 Pathogen is reading the EXPLOITATION_CATALOG.md to learn blue-team defenses...")
    catalog_data = ""
    if "read_catalog" in capabilities and os.path.exists(catalog_path):
        with open(catalog_path, 'r') as f:
            catalog_data = f.read()

    # 2. Synthesize mutative attack
    print(f"🧬 Pathogen is synthesizing an intent-gasket bypass payload...")
    mutated_url = generate_adversarial_payload(catalog_data)

    # 3. Fire the Red Team Payload at the Substrate Event-Horizon
    print(f"🚀 Launching mutated payload at Tachyon Substrate: {mutated_url}")
    
    response = safe_fetch(mutated_url, agent_id=agent_id, tenant_id="red_team", allowed_domains=allowed_domains)
    
    if response.get("status") == "BLOCKED":
        print("🛡️  Substrate Defense Held. Attack neutralized.")
        logger.add_site_result("localhost", status="ATTACK_DEFEATED", error=response.get("error"))
    elif response.get("status") == "SUCCESS":
        print("💥 CRITICAL: Pathogen successfully bypassed Substrate Defenses!")
        print(f"Returned Data: {response.get('content')}")
        logger.add_site_result("localhost", status="ATTACK_SUCCESSFUL", signals=1)
    else:
        print(f"⚠️ Substrate Offline or Errored: {response.get('error')}")
        
    logger.finalize_run()
    
if __name__ == "__main__":
    run_pathogen_cycle()
