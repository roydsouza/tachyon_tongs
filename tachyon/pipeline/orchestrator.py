"""
Tachyon Tongs: The Sentinel ADK Supervisor Orchestration
Provides the Multi-Agent architecture for the Guardian Triad.
"""
from tachyon.core.google_adk_mock import StateGraph
from tachyon.agents.legacy.scout_agent import scout_network_node
from tachyon.agents.legacy.analyst_agent import analyst_reasoning_node
from tachyon.agents.legacy.engineer_agent import engineer_action_node
from tachyon.agents.legacy.skeptic_agent import skeptic_reasoning_node
from tachyon.agents.legacy.metacritic_agent import metacritic_arbitration_node

class SentinelOrchestrator:
    """Convenience class for the Guardian Triad."""
    def run(self, url: str, logger=None, run_scraper=False):
        return run_supervisor(url, logger=logger, run_scraper=run_scraper)

    def fetch_and_sanitize(self, url: str, agent_id: str):
        # Stub for router compatibility
        return run_supervisor(url, run_scraper=True)

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
    graph.add_node("Skeptic", skeptic_reasoning_node)
    graph.add_node("MetaCritic", metacritic_arbitration_node)
    
    # 2. Wire the Action Broker data-flow strictly (Physical Air Gap)
    graph.add_edge("Scout", "Analyst")
    graph.add_edge("Analyst", "Engineer")
    graph.add_edge("Engineer", "Skeptic")
    graph.add_edge("Skeptic", "MetaCritic")
    
    # 3. Set entry point
    graph.set_entry_point("Scout")
    
    return graph

def run_supervisor(url: str, logger=None, run_scraper=False, allowed_domains=None, denylist=None, cve_context=None, harvest_mode=False) -> dict:
    """Executes the Guardian Triad Action Broker."""
    app = create_supervisor_graph().compile()
    
    if logger and url:
        logger.add_site_polled(url)
        
    initial_state = {
        "target_url": url,
        "run_scraper": run_scraper,
        "logger": logger,
        "allowed_domains": allowed_domains,
        "denylist": denylist,
        "cve_context": cve_context,
        "harvest_mode": harvest_mode
    }
    
    # Let the Triad negotiate the workflow
    final_state = app.invoke(initial_state)
    return final_state
