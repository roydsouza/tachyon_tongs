
def analyst_reasoning_node(state: dict) -> dict:
    """
    The Analyst receives the raw network output from the Scout.
    It has no network access itself. It sanitizes the payload and parses for threats.
    """
    from tachyon.pipeline.tri_stage_pipeline import SanitizerNode, AnalyzerNode
    sanitizer = SanitizerNode()
    analyzer = AnalyzerNode()
    
    # Process scraped CVEs if present
    if "scraped_threats" in state and state["scraped_threats"]:
        relevant_threats = []
        
        # Proposed agentic signals (Fix A2/A3)
        AGENTIC_ALLOWLIST = [
            "prompt injection", "large language model", " llm ",
            "model context protocol", "mcp server", "autonomous agent",
            "ai agent", "rag", "retrieval-augmented", "jailbreak",
            "instruction following", "system prompt", "tool call",
            "function call", "agent hijacking", "code interpreter",
            "ai model", "language model"
        ]
        
        # AGENTIC CWEs (Fix A3)
        # CWE-1336: Improper Neutralization of Special Elements in Template Engine
        # CWE-94: Code Injection (covers LLM code generation attacks)
        # CWE-77: Improper Neutralization of Special Elements (Command Injection via LLM)
        AGENTIC_CWES = {"CWE-1336", "CWE-94", "CWE-77", "CWE-20", "CWE-693"}

        for t in state["scraped_threats"]:
            desc_lower = t['description'].lower()
            threat_cwes = set(t.get('cwes', []))
            
            # Boost: Match either semantic term OR CWE taxonomy
            has_semantic_signal = any(s in desc_lower for s in AGENTIC_ALLOWLIST)
            has_cwe_signal = bool(threat_cwes & AGENTIC_CWES)
            
            if has_semantic_signal or has_cwe_signal:
                accept_reason = "CWE match" if has_cwe_signal else "Semantic match"
                print(f"[Analyst] Accepting {t['cve_id']} via {accept_reason}")
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

    # Process targeted CVE investigation if present
    if "cve_context" in state and state["cve_context"]:
        cve = state["cve_context"]
        print(f"[Analyst] [INVESTIGATION] Focusing on targeted threat: {cve['id']}")
        state["analysis"] = {
            "status": "success",
            "threats_found": [f"CVE ID: {cve['id']} - {cve['description']}"]
        }
        return state

    # Process targeted Fetch Payload if present
    if "raw_html" in state and state["raw_html"]:
        state["sanitized_content"] = sanitizer.clean(state["raw_html"])
        state["analysis"] = analyzer.reason(state["sanitized_content"])
        
    return state
