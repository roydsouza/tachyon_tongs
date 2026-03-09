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
                logger.add_file_updated("EXPLOITATION_CATALOG.md", details=f"Appended {num_threats} validated threats.", payload=payload_str)
                logger.add_file_updated("TASKS.md", details=f"Injected {num_threats} verification tasks to the backlog.")
                
    except VerificationFailedError as e:
        # The Engineer caught the Analyst slipping. Refuse to execute write operations.
        state["final_output"] = {"status": "error", "reason": f"VERIFIER BLOCKED: {str(e)}"}
        
    return state
