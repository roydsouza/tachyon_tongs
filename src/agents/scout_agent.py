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
    fetcher = FetcherNode()
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
        
    return state
