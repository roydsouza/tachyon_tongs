"""
Tachyon Tongs: The Sentinel ADK Orchestration
Maps the tri-stage pipeline strictly to Google ADK state graphs.
"""
from src.google_adk_mock import StateGraph
from src.tri_stage_pipeline import FetcherNode, SanitizerNode, AnalyzerNode

def adk_fetch_node(state: dict) -> dict:
    fetcher = FetcherNode()
    state["raw_html"] = fetcher.get_raw_data(state["target_url"])
    return state

def adk_sanitize_node(state: dict) -> dict:
    sanitizer = SanitizerNode()
    state["sanitized_text"] = sanitizer.clean(state["raw_html"])
    return state
    
def adk_analyze_node(state: dict) -> dict:
    analyzer = AnalyzerNode()
    state["analysis"] = analyzer.reason(state["sanitized_text"])
    return state

def create_sentinel_graph() -> StateGraph:
    graph = StateGraph()
    
    # 1. Define nodes
    graph.add_node("Fetcher", adk_fetch_node)
    graph.add_node("Sanitizer", adk_sanitize_node)
    graph.add_node("Analyzer", adk_analyze_node)
    
    # 2. Wire the Tri-Stage pipeline edges securely
    graph.add_edge("Fetcher", "Sanitizer")
    graph.add_edge("Sanitizer", "Analyzer")
    
    # 3. Set entry
    graph.set_entry_point("Fetcher")
    
    return graph

def run_sentinel(url: str) -> dict:
    """Executes the Sentinel payload."""
    app = create_sentinel_graph().compile()
    
    initial_state = {
        "target_url": url,
        "raw_html": "",
        "sanitized_text": "",
        "analysis": {}
    }
    
    final_state = app.invoke(initial_state)
    return final_state
