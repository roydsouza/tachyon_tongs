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
        relevant_threats = []
        for t in state["scraped_threats"]:
            desc = t['description'].lower()
            # Tier 2: Expert heuristic refinement.
            # We want specific combinations or high-fidelity agentic terms. 
            # 'Injection' alone is too noisy (SQLi), so we look for 'Prompt Injection'.
            agentic_signals = [
                "prompt injection", "llm", "large language model", 
                "agent hijacking", "jailbreak", "rag poisoning",
                "autonomous agent", "exfiltration"
            ]
            if any(signal in desc for signal in agentic_signals):
                relevant_threats.append(f"CVE ID: {t['cve_id']} - {t['description']}")
            else:
                # Log but do not promote to action
                print(f"[Analyst] Discarding irrelevant semantic noise: {t['cve_id']}")
        
        if relevant_threats:
            state["analysis"] = {
                "status": "success",
                "threats_found": relevant_threats
            }
        else:
            state["analysis"] = {"status": "success", "reason": "All discovered signals were filtered as out-of-scope noise."}
            
        return state

    # Process targeted Fetch Payload if present
    if "raw_html" in state and state["raw_html"]:
        state["sanitized_content"] = sanitizer.clean(state["raw_html"])
        state["analysis"] = analyzer.reason(state["sanitized_content"])
        
    return state
