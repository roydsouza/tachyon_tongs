"""
Tachyon Tongs: The Sentinel ADK Supervisor Orchestration
Provides the Multi-Agent architecture for the Guardian Triad.
"""
from src.google_adk_mock import StateGraph
from src.agents.scout_agent import scout_network_node
from src.agents.analyst_agent import analyst_reasoning_node
from src.agents.engineer_agent import engineer_action_node

def create_supervisor_graph() -> StateGraph:
    """
    Creates the Supervisor Action Broker.
    Architectural layout for the Guardian Triad Split:
    Scout (Network Egress) -> Analyst (Air-Gapped Evaluation) -> Engineer (Logger / State Writing)
    """
    graph = StateGraph()
    
    # 1. Define the isolated nodes
    graph.add_node("Scout", scout_network_node)
    graph.add_node("Analyst", analyst_reasoning_node)
    graph.add_node("Engineer", engineer_action_node)
    
    # 2. Wire the Action Broker data-flow strictly (Physical Air Gap)
    graph.add_edge("Scout", "Analyst")
    graph.add_edge("Analyst", "Engineer")
    
    # 3. Set entry point
    graph.set_entry_point("Scout")
    
    return graph

def run_supervisor(url: str, logger=None, run_scraper=False) -> dict:
    """Executes the Guardian Triad Action Broker."""
    app = create_supervisor_graph().compile()
    
    if logger and url:
        logger.add_site_polled(url)
        
    initial_state = {
        "target_url": url,
        "run_scraper": run_scraper,
        "logger": logger
    }
    
    # Let the Triad negotiate the workflow
    final_state = app.invoke(initial_state)
    return final_state
