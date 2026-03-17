import pytest
from tachyon.agents.sentinel.scraper import VulnerabilityScraper
from tachyon.agents.legacy.analyst_agent import analyst_reasoning_node

def test_scraper_mock_data_cwe_extraction():
    """Verify that the scraper correctly includes CWEs in mock mode."""
    scraper = VulnerabilityScraper(mode="mock")
    threats = scraper.scrape_new_threats()
    
    assert len(threats) > 0
    assert "cwes" in threats[0]
    assert "CWE-1336" in threats[0]["cwes"]

def test_analyst_filtering_precision():
    """Verify that the analyst correctly accepts/rejects based on semantic and CWE signals."""
    # Test case 1: Relevant (Prompt Injection)
    state_relevant = {
        "scraped_threats": [
            {
                "cve_id": "CVE-2025-0001",
                "description": "Critical prompt injection in agent framework.",
                "cwes": []
            }
        ]
    }
    processed_relevant = analyst_reasoning_node(state_relevant)
    assert "threats_found" in processed_relevant["analysis"]
    assert len(processed_relevant["analysis"]["threats_found"]) == 1

    # Test case 2: Irrelevant (Generic SQLi)
    state_irrelevant = {
        "scraped_threats": [
            {
                "cve_id": "CVE-2025-0002",
                "description": "Standard SQL injection in web portal.",
                "cwes": ["CWE-89"]
            }
        ]
    }
    processed_irrelevant = analyst_reasoning_node(state_irrelevant)
    assert "threats_found" not in processed_irrelevant["analysis"]
    assert "filtered as out-of-scope noise" in processed_irrelevant["analysis"]["reason"]

    # Test case 3: CWE Boost (Generic description but agentic CWE)
    state_cwe_boost = {
        "scraped_threats": [
            {
                "cve_id": "CVE-2025-0003",
                "description": "Insecure element handling in engine.",
                "cwes": ["CWE-1336"]
            }
        ]
    }
    processed_cwe = analyst_reasoning_node(state_cwe_boost)
    assert "threats_found" in processed_cwe["analysis"]

def test_scraper_keyword_exact_match():
    """Smoke test for keywordExactMatch parameter in scraper."""
    scraper = VulnerabilityScraper()
    # We won't trigger a live API call here, but verify the internal attribute exists or params are built
    # Since _fetch_live_data is internal, we check the allowlist presence
    assert hasattr(scraper, "agentic_allowlist")
    assert "prompt injection" in scraper.agentic_allowlist
