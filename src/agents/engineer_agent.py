"""
Tachyon Tongs: Engineer Agent (Action Writer)
Agent 3 of the Guardian Triad.
"""
from src.verifier_agent import VerifierAgent, VerificationFailedError

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
                
        # Substrate Evolution: Auto-Patching if explicitly given structural mitigations
        if state["analysis"].get("proposed_patch_files") and state["analysis"].get("proposed_regression_test"):
            from src.auto_patcher import AutoPatcher
            patcher = AutoPatcher()
            
            cve_id = state["analysis"].get("threats_found", [{}])[0].get("id", "UNKNOWN-THREAT")
            
            patch_result = patcher.apply_and_test(
                patch_files=state["analysis"]["proposed_patch_files"],
                test_file_path=state["analysis"]["proposed_regression_test"].get("path", "tests/test_auto_mutation_1.py"),
                test_content=state["analysis"]["proposed_regression_test"].get("content", ""),
                cve_id=cve_id
            )
            
            if patch_result and patch_result.get("status") == "success":
                logger.add_file_updated("EVOLUTION.md", details=f"Organism successfully patched '{cve_id}' without human intervention.")
            else:
                logger.add_file_updated("ERROR.md", details=f"Organism failed to patch '{cve_id}'. Revert sequence initiated.")
                
    except VerificationFailedError as e:
        # The Engineer caught the Analyst slipping. Refuse to execute write operations.
        state["final_output"] = {"status": "error", "reason": f"VERIFIER BLOCKED: {str(e)}"}
        
    return state
