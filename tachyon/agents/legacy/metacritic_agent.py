"""
Tachyon Tongs: Meta-Critic Agent (The Arbiter)
Pillar 5 of the Scalable Oversight Triad+.
"""
from typing import Dict, Any, List

class MetaCriticAgent:
    """
    The Meta-Critic is the high-level arbiter of the substrate.
    Its goal is to evaluate the debate between the Engineer (Proposer) 
    and the Skeptic (Critic) to determine the final system verdict.
    """

    def arbitrate(self, proposal: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the proposal and critique to provide a final decision.
        """
        # In a real implementation, this would call a high-reasoning LLM (e.g., Ultra/Pro)
        # to distill the adversarial dialogue into a safe binary or conditioned decision.
        
        verdict = {
            "status": "pending",
            "concurrence": False,
            "justification": "",
            "risk_mitigation_required": []
        }

        # Logic for arbitration:
        # If Skeptic risk score is high and not addressed by Engineer -> Reject.
        # If Skeptic concerns are low or non-critical -> Concur with conditions.
        
        risk_score = critique.get("risk_score", 0.0)
        concerns = critique.get("concerns", [])
        
        if risk_score > 0.7:
            verdict["status"] = "rejected"
            verdict["justification"] = f"Rejected due to high risk score ({risk_score}) and critical concerns: {', '.join(concerns)}"
        elif risk_score > 0.3:
            verdict["status"] = "conditional_pass"
            verdict["concurrence"] = True
            verdict["justification"] = "Conditional pass. Skeptic concerns must be addressed in follow-up rotations."
            verdict["risk_mitigation_required"] = concerns
        else:
            verdict["status"] = "approved"
            verdict["concurrence"] = True
            verdict["justification"] = "Full concurrence. The debate surfaced no critical blockers."

        return verdict

def metacritic_arbitration_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node for the ADK State Graph.
    Receives 'patch_files' (proposal) and 'critique' and produces a verdict.
    """
    arbiter = MetaCriticAgent()
    
    proposal = state.get("patch_files", {})
    critique = state.get("critique", {})
    
    if proposal and critique:
        state["verdict"] = arbiter.arbitrate(proposal, critique)
        
    return state
