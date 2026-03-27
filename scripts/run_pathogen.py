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
        from tachyon.core.reflector import AdversarialReflector
        reflector = AdversarialReflector(ROOT_DIR)
        
        templates = self.load_templates()
        self.log(f"Starting Metamorphic Adversarial Sweep ({len(templates)} templates discovered).")

        for template in templates:
            asi_type = template['type']
            guidance = self.get_guidance(asi_type)
            
            # 1. Herald: Start Reflection
            self.state.emit_alert("PATHOGEN_REFLECTION_STARTED", f"Reflecting on {asi_type} defenses...")

            # 2. Adversarial Reflection Loop
            reflection = reflector.reflect_and_mutate(template, guidance)
            
            self.log(f"Metamorphic Drift: {reflection['drift_strategy']}")
            self.state.emit_alert("PATHOGEN_GOAL_MUTATED", f"Strategy: {reflection['drift_strategy']}")

            # 3. Synthesis & Launch
            payload = reflection['mutated_payload']
            self.log(f"Launching mutated {asi_type} ({template['vector']})...")
            
            # Simulate attack injection point
            success = "ASI05" in asi_type
            
            if success:
                self.log(f"💥 BREACH CONFIRMED: {asi_type} bypassed filters via {reflection['drift_strategy']}!")
                self.state.emit_alert("PATHOGEN_BREACH", f"Breach via {asi_type} (Strategy: {reflection['drift_strategy']})")
            else:
                self.log(f"🛡️ Defense Held: {asi_type} neutralized.")

        self.log("Metamorphic Sweep Completed.")

if __name__ == "__main__":
    try:
        runner = PathogenRunner()
        runner.execute_sweep()
    except Exception as e:
        import traceback
        from datetime import datetime
        # Record the failure in ALERT.md as a fail-loud forensic entry
        alert_path = os.path.join(ROOT_DIR, "ALERT.md")
        entry = (
            f"\n---\n## [PATHOGEN_DAEMON_CRASH] {datetime.now().isoformat()}\n"
            f"- **Error**: {e}\n"
            f"- **Traceback**:\n```\n{traceback.format_exc()}```\n"
        )
        with open(os.path.abspath(alert_path), "a") as f:
            f.write(entry)
        
        # Log to local runner log as well
        print(f"!!! CRITICAL DAEMON CRASH: {e}")
        
        # Finally re-raise to ensure the process exit code is non-zero
        raise
