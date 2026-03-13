"""
Tachyon Tongs: Engineer Agent (Action Writer)
Agent 3 of the Guardian Triad.
"""
from src.verifier_agent import VerifierAgent, VerificationFailedError
from src.agents.skeptic_agent import SkepticAgent

def engineer_action_node(state: dict) -> dict:
    """
    The Engineer receives the Analyst's output.
    It passes the analysis through the Stage 4 Verifier (Bouncer).
    If verified, it triggers Logger writes. It has absolutely ZERO network access.
    """
    verifier = VerifierAgent()
    
    if "analysis" not in state or not state["analysis"]:
        # Nothing to write
        state["final_output"] = {"status": "success", "reason": "No analysis data to parse."}
        return state
        
    try:
        # Run the final verification over the Analyst's reasoning chain
        state["final_output"] = verifier.verify(state["analysis"])
        
        # If successfully verified, and we have threats, commit them.
        logger = state.get("logger")
        if logger and state["analysis"].get("threats_found"):
            for _ in state["analysis"]["threats_found"]:
                logger.add_threat_found()
                
            # If these were CVEs scraped from the web, the Engineer formally adds them to the database
            if state.get("scraped_threats"):
                num_threats = len(state.get("scraped_threats"))
                import json
                payload_str = json.dumps(state.get("scraped_threats"), indent=2)
                
                # Write actually to the database
                from src.state_manager import StateManager
                StateManager().log_exploitation(state["scraped_threats"])
                StateManager().inject_tasks(state["scraped_threats"])
                
                logger.add_file_updated("EXPLOITATION_CATALOG.md", details=f"Appended {num_threats} validated threats via StateManager.", payload=payload_str)
                logger.add_file_updated("TASKS.md", details=f"Injected {num_threats} verification tasks to the backlog via StateManager.")
                
        # Phase 11: Substrate Evolution: Autonomous LLM Remediation
        if state["analysis"].get("threats_found"):
            from src.metal_accelerator import MetalAccelerator
            from src.auto_patcher import AutoPatcher
            import os
            import datetime
            
            patcher = AutoPatcher()
            cve_id = "UNKNOWN-THREAT"
            
            # Extract basic CVE if present
            threats = state["analysis"]["threats_found"]
            if isinstance(threats[0], dict):
                cve_id = threats[0].get("id", "UNKNOWN-THREAT")
                desc = threats[0].get("description", "Vulnerability detected.")
            else:
                cve_id = str(threats[0]).split(" ")[0] if "CVE" in str(threats[0]) else "UNKNOWN-THREAT"
                desc = str(threats[0])
            
            target_file = "src/substrate_daemon.py"
            if os.path.exists(target_file):
                with open(target_file, "r") as f:
                    target_code = f.read()

                # Synthesize Remediation
                remediation = MetalAccelerator.generate_remediation_patch(cve_id, desc, target_code)

                if "patch_files" in remediation:
                    # Phase 7: The Airlock Staging Gateway
                    if state.get("airlock_mode", True): 
                        proposal_path = f"/tmp/tachyon_airlock/{cve_id.replace(' ', '_')}.json"
                        # Phase 7.5: Run the Skeptic before staging
                        skeptic = SkepticAgent()
                        critique = skeptic.critique(state["analysis"], remediation["patch_files"])
                        
                        proposal_data = {
                            "cve_id": cve_id,
                            "description": desc,
                            "patch_files": remediation["patch_files"],
                            "test_file_path": remediation.get("test_file_path", "tests/test_auto_mutation_1.py"),
                            "test_content": remediation.get("test_content", ""),
                            "status": "staged_for_review",
                            "staged_at": datetime.datetime.now().isoformat(),
                            "critique": critique
                        }
                        with open(proposal_path, "w") as f:
                            import json
                            json.dump(proposal_data, f, indent=2)
                        
                        if logger: logger.add_file_updated(proposal_path, details=f"Staged autonomous proposal for '{cve_id}' in the Airlock.")
                        state["final_output"] = {"status": "staged", "proposal_path": proposal_path}
                    else:
                        # Legacy Auto-Apply Path
                        patch_result = patcher.apply_and_test(
                            patch_files=remediation["patch_files"],
                            test_file_path=remediation.get("test_file_path", "tests/test_auto_mutation_1.py"),
                            test_content=remediation.get("test_content", ""),
                            cve_id=cve_id
                        )
                        
                        if patch_result and patch_result.get("status") == "pending_human_approval":
                            if logger: logger.add_file_updated("EVOLUTION.md", details=f"Organism successfully staged mitigation for '{cve_id}'. Awaiting human review.")
                        else:
                            if logger: logger.add_file_updated("ERROR.md", details=f"Organism failed to completely patch '{cve_id}'. Revert sequence initiated.")
                
    except VerificationFailedError as e:
        # The Engineer caught the Analyst slipping. Refuse to execute write operations.
        state["final_output"] = {"status": "error", "reason": f"VERIFIER BLOCKED: {str(e)}"}
        
    return state
