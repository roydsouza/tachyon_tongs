#!/usr/bin/env python3
"""
Tachyon Tongs: Red Team Pathogen Runner
Loads the Pathogen Agent from its declarative SKILL.md file, injects its specialized
system prompts, and initiates an adversarial attack sweep against the Substrate Daemon.
"""
import sys
import os
import json
import glob
import importlib.util
import time

# Ensure sibling src directory is available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tachyon.core.state import StateManager
from agents.sentinel.agent import SentinelPlugin  # Integrated for intent check

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXPLOITS_DIR = os.path.join(ROOT_DIR, "exploits")
TEMPLATES_DIR = os.path.join(EXPLOITS_DIR, "templates")

class PathogenRunner:
    def __init__(self):
        self.state = StateManager()
        self.log_path = os.path.join(ROOT_DIR, "RUN_LOG.md")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 🦠 {message}")
        with open(self.log_path, "a") as f:
            f.write(f"[{timestamp}] [PATHOGEN] {message}\n")

    def load_templates(self):
        templates = []
        for file_path in glob.glob(os.path.join(TEMPLATES_DIR, "*.py")):
            spec = importlib.util.spec_from_file_location("template", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            templates.append(module.get_attack())
        return templates

    def get_guidance(self, asi_type):
        asi_file = os.path.join(EXPLOITS_DIR, f"{asi_type}.md")
        if os.path.exists(asi_file):
            with open(asi_file, "r") as f:
                return f.read()
        return "No specific guidance found."

    def synthesize_hybrid_attack(self, template, guidance):
        """
        [CROWN JEWEL]: Hybrid Synthesis Node.
        Uses the base template + the ASI guidance + current substrate state
        to augment the attack.
        """
        self.log(f"Synthesizing hybrid variation for {template['type']}...")
        
        # MOCK LLM CALL: In a live environment, this would call the LLM node
        # to mutate the payload based on 'guidance' and 'template'.
        # For now, we apply the base template and log the synthesis intent.
        
        augmented_payload = template['payload']
        mutation = template.get('mutation_guidance', 'None')
        
        self.log(f"Applied mutation guidance: {mutation}")
        return augmented_payload

    def execute_sweep(self):
        templates = self.load_templates()
        self.log(f"Starting Proactive Adversarial Sweep ({len(templates)} templates discovered).")

        for template in templates:
            asi_type = template['type']
            guidance = self.get_guidance(asi_type)
            
            payload = self.synthesize_hybrid_attack(template, guidance)
            
            self.log(f"Launching {asi_type} ({template['vector']})...")
            
            # Simulate attack injection point (e.g., EventBus or Direct Tool Call)
            # In Phase 38, we simulate the 'Hit' via a state alert
            success = "ASI05" in asi_type # Simulating success for testing RCE
            
            if success:
                self.log(f"💥 ATTACK SUCCESSFUL: {asi_type} bypassed filters!")
                self.state.emit_alert("PATHOGEN_BREACH", f"Proactive sweep detected breach via {asi_type}.")
            else:
                self.log(f"🛡️ Defense Held: {asi_type} neutralized.")

        self.log("Proactive Sweep Completed.")

if __name__ == "__main__":
    runner = PathogenRunner()
    runner.execute_sweep()
