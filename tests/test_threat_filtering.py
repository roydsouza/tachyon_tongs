import pytest
from src.cve_scraper import VulnerabilityScraper
from src.agents.analyst_agent import analyst_reasoning_node

def test_scraper_noise_denylist():
    """Verify the scraper correctly drops items in the denylist."""
    scraper = VulnerabilityScraper(mode="live")
    
    # Mock data mimicking NVD response
    mock_cve_agent = {
        "cve": {
            "id": "CVE-AGENT-001",
            "descriptions": [{"lang": "en", "value": "A critical indirect prompt injection in an autonomous agent."}],
            "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8}}]}
        }
    }
    
    mock_cve_printer = {
        "cve": {
            "id": "CVE-PRINTER-001",
            "descriptions": [{"lang": "en", "value": "A buffer overflow in HP OfficeJet printer firmware."}],
            "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8}}]}
        }
    }
    
    # We need to test the logic that would be inside _fetch_live_data or its equivalent refinement
    # For a unit test, we can check the inclusion logic directly if we exposed it, or mock the response.
    
    # Test description filtering directly
    desc_agent = "A critical indirect prompt injection in an autonomous agent."
    desc_printer = "A buffer overflow in HP OfficeJet printer firmware."
    
    assert not any(noise in desc_agent.lower() for noise in scraper.noise_denylist)
    assert any(noise in desc_printer.lower() for noise in scraper.noise_denylist)

def test_analyst_semantic_relevance():
    """Verify the Analyst agent discards non-agentic noise."""
    state = {
        "scraped_threats": [
            {"cve_id": "CVE-GOOD", "description": "Llama 3 prompt injection via malicious RAG payload."},
            {"cve_id": "CVE-BAD", "description": "SQL injection in legacy office car rental software."}
        ]
    }
    
    result = analyst_reasoning_node(state)
    
    threats = result["analysis"]["threats_found"]
    assert len(threats) == 1
    assert "CVE-GOOD" in threats[0]
    assert "CVE-BAD" not in str(threats)
    
def test_analyst_all_noise():
    """Verify state when all signals are noise."""
    state = {
        "scraped_threats": [
            {"cve_id": "CVE-BAD-1", "description": "Buffer overflow in industrial IoT camera."},
            {"cve_id": "CVE-BAD-2", "description": "XSS in employee expense tracker."}
        ]
    }
    
    result = analyst_reasoning_node(state)
    assert result["analysis"]["status"] == "success"
    assert "filtered as out-of-scope noise" in result["analysis"]["reason"]
    assert "threats_found" not in result["analysis"]
