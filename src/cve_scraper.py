"""
Tachyon Tongs: Autonomous Threat Intel Scraping 
Polls the National Vulnerability Database (NVD) for critical AI and LLM threats.
"""
import requests
import time
import json

class VulnerabilityScraper:
    def __init__(self, mode="live"):
        self.mode = mode
        self.api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # We search specifically for AI related hijackings, injections, etc.
        # This prevents the Sentinel from panicking over an ancient Windows XP Print Spooler bug.
        self.search_keywords = ["large language model", "LLM", "prompt injection", "agent hijacking", "autonomous agent"]

    def _fetch_live_data(self, logger=None):
        """Polls the NVD API for recent CVEs matching our keywords."""
        if logger:
            logger.add_site_polled("nvd.nist.gov")
            
        results = []
        for keyword in self.search_keywords:
            try:
                # The NVD API without a key limits to 5 requests per rolling 30 seconds
                # We do a tiny sleep to be polite.
                time.sleep(2)
                
                params = {
                    "keywordSearch": keyword,
                    "cvssV3Severity": "CRITICAL",  # Only wake me up for the scary stuff
                    "resultsPerPage": 3
                }
                
                response = requests.get(self.api_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    for v in vulnerabilities:
                        cve_data = v.get("cve", {})
                        
                        # Extract the english description
                        desc = next((d.get("value") for d in cve_data.get("descriptions", []) if d.get("lang") == "en"), "No description available.")
                        
                        # Extract CVSS
                        metrics = cve_data.get("metrics", {})
                        cvss_data = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
                        score = cvss_data.get("baseScore", 0.0)
                        
                        results.append({
                            "cve_id": cve_data.get("id"),
                            "description": desc,
                            "severity": "CRITICAL",
                            "score": score
                        })
                        
                elif response.status_code == 403:
                    # NVD API rate limits aggressively
                    print(f"[CVE Scraper] Rate limited by NVD for keyword '{keyword}'.")
            except Exception as e:
                print(f"[CVE Scraper] Failed to fetch NVD intel for '{keyword}': {str(e)}")
                
        # Deduplicate results
        unique_results = {r['cve_id']: r for r in results}.values()
        return list(unique_results)

    def scrape_new_threats(self, logger=None) -> list:
        """
        Executes the scraping run against the NVD REST API. 
        Returns a list of parsed threat dictionaries.
        """
        threats = []
        if self.mode == "mock":
            # Testing fallback
            threats.append({
                "cve_id": "CVE-2026-99999",
                "description": "Mock Critical Agent Hijacking vulnerability.",
                "severity": "CRITICAL",
                "score": 9.8
            })
        else:
            threats = self._fetch_live_data(logger=logger)
            
        if threats and logger:
            for t in threats:
                logger.add_threat_found()
            if self.mode != "mock":
                logger.add_file_updated("EXPLOITATION_CATALOG.md")
                logger.add_file_updated("TASKS.md")
                
        return threats

    def _format_markdown_entry(self, threat: dict) -> str:
        """Formats the data for the EXPLOITATION_CATALOG.md database."""
        return f"### {threat['cve_id']} (Severity: {threat['severity']})\n- **Description:** {threat['description']}\n- **CVSS:** {threat['score']}\n"
