"""
Tachyon Tongs: Scout Agent (Isolated Network Capabilities)
Agent 1 of the Guardian Triad.
"""
from src.tri_stage_pipeline import FetcherNode
from src.cve_scraper import VulnerabilityScraper

def scout_network_node(state: dict) -> dict:
    """
    The sole node in the Sentinel architecture with network egress.
    Controlled securely by the SafeFetch OPA intent gate.
    """
    fetcher = FetcherNode(
        allowed_domains=state.get("allowed_domains"),
        denylist=state.get("denylist")
    )
    scraper = VulnerabilityScraper()

    # The Scout can do two things based on state: 
    # 1. Fetch a specific URL
    # 2. Scrape the NVD API
    
    if state.get("target_url"):
        site = state["target_url"].split("//")[-1].split("/")[0] # Extract domain
        try:
            raw_data = fetcher.get_raw_data(state["target_url"])
            state["raw_html"] = raw_data
            if state.get("logger"):
                state["logger"].add_site_result(site, status="SUCCESS", signals=1)
        except Exception as e:
            if state.get("logger"):
                state["logger"].add_site_result(site, status="FAIL", error=str(e))
            raise e
        
    if state.get("run_scraper", False):
        state["scraped_threats"] = scraper.scrape_new_threats(logger=state.get("logger"))
        
    # Autonomous Perimeter Expansion (Self-Evolution)
    if state.get("new_discovery_sites"):
        from src.state_manager import StateManager
        with open("SITES.md", "a") as f:
            for new_site in state["new_discovery_sites"]:
                # Basic formatting for the append
                f.write(f"\n- **[{new_site.get('name', 'Autodiscovered')}]({new_site.get('url')}):** {new_site.get('reason', 'Autodiscovered by Sentinel during routine threat scrape.')}\n")
                
                # Formally log the organistic mutation
                StateManager().log_evolution(
                    event_type="Perimeter Expansion (SITES.md)",
                    details=f"The Guardian Triad autonomously discovered a high-signal security node at `{new_site.get('url')}` and mutated `SITES.md` to include it in future telemetry sweeps."
                )
                
                if state.get("logger"):
                    state["logger"].add_file_updated("SITES.md", details=f"Appended autonomous discovery: {new_site.get('url')}")
                    state["logger"].add_file_updated("EVOLUTION.md", details=f"Logged perimeter expansion for {new_site.get('url')}")
        
    return state
