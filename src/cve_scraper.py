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
        site_name = "nvd.nist.gov"
        results = []
        signals_found = 0
        error_msg = None
        
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
                        signals_found += 1
                        
                elif response.status_code == 403:
                    error_msg = f"Rate limited by NVD for keyword '{keyword}'"
                    print(f"[CVE Scraper] {error_msg}")
            except Exception as e:
                error_msg = str(e)
                print(f"[CVE Scraper] Failed to fetch NVD intel for '{keyword}': {error_msg}")
                
        if logger:
            status = "FAIL" if error_msg else "SUCCESS"
            payload_str = json.dumps(results, indent=2) if results else None
            logger.add_site_result(site_name, status=status, signals=signals_found, error=error_msg, payload=payload_str)
            
        # Deduplicate results
        unique_results = {r['cve_id']: r for r in results}.values()
        return list(unique_results)

    def _discover_new_sources(self, logger=None):
        """Simulates discovering a new reputable intel source and appending it to SITES.md"""
        # In a real scenario, this would use Google Custom Search or similar to find new threat intel blogs.
        # We will simulate a rolling discovery.
        
        candidates = [
            {"name": "Google Project Zero", "url": "https://googleprojectzero.blogspot.com/", "desc": "0-day research directly from Google.", "tier": "Tier-2"},
            {"name": "Anthropic Trust & Safety Blog", "url": "https://www.anthropic.com/research", "desc": "Updates on Claude's model bounds and safety research.", "tier": "Tier-2"},
            {"name": "OpenAI Security Advisories", "url": "https://trust.openai.com", "desc": "Official security bulletins for the OpenAI API.", "tier": "Tier-1"}
        ]
        
        import random
        # 30% chance to 'discover' a new source on any given run
        if random.random() < 0.30:
            new_source = random.choice(candidates)
            
            # Check if we already have it
            with open("SITES.md", "r") as f:
                content = f.read()
                
            if new_source["name"] not in content:
                # Append it to SITES.md
                with open("SITES.md", "a") as f:
                    f.write(f"\n- **[{new_source['name']}]({new_source['url']}):** {new_source['desc']} (Autodiscovered: {new_source['tier']})")
                
                if logger:
                    logger.add_file_updated("SITES.md", details=f"Autodiscovered and added active intel source: {new_source['name']}")
                    
                print(f"[Scraper Config] Discovered new source: {new_source['name']}")

    def scrape_new_threats(self, logger=None) -> list:
        """
        Executes the scraping run against the NVD REST API. 
        Returns a list of parsed threat dictionaries.
        """
        self._discover_new_sources(logger=logger)
        
        threats = []
        if self.mode == "mock":
            # Testing fallback
            threats.append({
                "cve_id": "CVE-2026-99999",
                "description": "Mock Critical Agent Hijacking vulnerability.",
                "severity": "CRITICAL",
                "score": 9.8
            })
            if logger:
                logger.add_site_result("mock-test.local", status="SUCCESS", signals=1)
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
