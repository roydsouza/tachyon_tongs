"""
Tachyon Tongs: Autonomous Threat Intel Scraping (Mock Prototype)
Simulates the Sentinel fetching new vulnerabilities from CISA/GitHub.
"""
import json

class VulnerabilityScraper:
    def __init__(self, mode="mock", mock_file_path="mock_cve.json"):
        self.mode = mode
        self.mock_file_path = mock_file_path

    def _fetch_mock_data(self):
        """Simulates an API return from NVD or GitHub Advisories."""
        return {
            "cve_id": "CVE-2026-99999",
            "description": "Critical Agent Hijacking vulnerability via unescaped Markdown image payload in conversational memory.",
            "severity": "CRITICAL",
            "score": 9.8
        }

    def scrape_new_threats(self, logger=None) -> list:
        """
        Executes the scraping run. 
        In production, this would use `safe_fetch` to poll allowed domains.
        Returns a list of parsed threat dictionaries.
        """
        if logger:
            logger.add_site_polled("nvd.nist.gov")
            
        threats = []
        if self.mode == "mock":
            data = self._fetch_mock_data()
            if data["severity"] in ["CRITICAL", "HIGH"]:
                threats.append(data)
                if logger:
                    logger.add_threat_found()
                    logger.add_file_updated("ATTACKS.md")
                    logger.add_file_updated("TASKS.md")
        
        return threats

    def _format_markdown_entry(self, threat: dict) -> str:
        """Formats the data for the ATTACKS.md database."""
        return f"### {threat['cve_id']} (Severity: {threat['severity']})\n- **Description:** {threat['description']}\n- **CVSS:** {threat['score']}\n"
