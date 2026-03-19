"""
Tachyon Tongs: Skeptic Agent (Adversarial Critic)
Pillar 4 of the Scalable Oversight Triad+.
"""
from typing import Dict, Any

class SkepticAgent:
    """
    The Skeptic is a rationally contrarian agent.
    Its goal is to find 'logic bombs', sycophantic reasoning, or hidden side-effects
    in the Analyst's proposed mitigations.
    """

    def critique(self, analysis: Dict[str, Any], patch_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyzes the Analyst's reasoning and the Engineer's patch to find flaws.
        Focuses on 'Structural Drifts' and 'Trojan Patches'.
        """
        if not patch_files:
            return {
                "is_skeptical": True,
                "banter": "Nothing to critique. It's too quiet. I suspect the Engineer is napping—or worse, plotting something 'useful'.",
                "risk_score": 0.0,
                "verdict": "pass"
            }

        cve_id = analysis.get("id", "UNKNOWN")
        
        critique_result = {
            "is_skeptical": True,
            "concerns": [],
            "risk_score": 0.0,
            "verdict": "pass",
            "detected_anomalies": [],
            "banter": "Oh look, another 'patch'. I've seen more secure code in a 'Hello World' tutorial. Are we trying to secure a substrate or or host a 'Bug Bounty for Dummies'?"
        }

        # Simulated Adversarial Analysis
        for filename, content in patch_files.items():
            # Check for suspicious patterns that might indicate a backdoor
            if "os.system" in content or "subprocess" in content:
                critique_result["concerns"].append(f"Suspicious execution pattern in {filename}")
                critique_result["risk_score"] += 0.4
                critique_result["detected_anomalies"].append("potential_rce_injection")

            if "eval(" in content:
                critique_result["concerns"].append(f"Unsafe usage of eval() in {filename}")
                critique_result["risk_score"] += 0.5
                critique_result["detected_anomalies"].append("unsafe_eval_pattern")

        if critique_result["risk_score"] > 0.5:
            critique_result["verdict"] = "fail"
        
        return critique_result

def skeptic_reasoning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node for the ADK State Graph. 
    Receives the 'analysis' and 'patch_files' and produces a critique.
    """
    skeptic = SkepticAgent()
    
    analysis = state.get("analysis")
    patch_files = state.get("patch_files")
    
    # Fallback to cve_context if patch_files is missing in state
    if not patch_files and "cve_context" in state:
        patch_files = state["cve_context"].get("patch_files", {})
    
    if analysis:
        state["critique"] = skeptic.critique(analysis, patch_files)
        
    return state
