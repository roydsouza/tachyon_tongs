"""
Tachyon Tongs: Analyst Agent (Air-Gapped Reasoner)
Agent 2 of the Guardian Triad.
"""
from src.tri_stage_pipeline import SanitizerNode, AnalyzerNode

def analyst_reasoning_node(state: dict) -> dict:
    """
    The Analyst receives the raw network output from the Scout.
    It has no network access itself. It sanitizes the payload and parses for threats.
    """
    sanitizer = SanitizerNode()
    analyzer = AnalyzerNode()
    
    # Process scraped CVEs if present
    if "scraped_threats" in state and state["scraped_threats"]:
        state["analysis"] = {
            "status": "success",
            "threats_found": [
                f"CVE ID: {t['cve_id']} - {t['description']}" for t in state["scraped_threats"]
            ]
        }
        return state

    # Process targeted Fetch Payload if present
    if "raw_html" in state and state["raw_html"]:
        state["sanitized_content"] = sanitizer.clean(state["raw_html"])
        state["analysis"] = analyzer.reason(state["sanitized_content"])
        
    return state
