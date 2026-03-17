"""
Tachyon Tongs: Autonomous Threat Intel Scraping 
Polls the National Vulnerability Database (NVD) for critical AI and LLM threats.
"""
import requests
import time
import json
import os
import datetime

class VulnerabilityScraper:
    def __init__(self, mode="live"):
        self.mode = mode
        self.api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # Focus exclusively on agentic security, indirect prompt injection, and web-based hijacking.
        self.search_keywords = [
            "prompt injection",
            "LLM jailbreak",
            "agent hijacking",
            "RAG poisoning",
            "indirect prompt injection",
        ]
        
        # Positive signal allowlist (Fix A2)
        self.agentic_allowlist = [
            "prompt injection",
            "large language model",
            " llm ",
            "model context protocol",
            "mcp server",
            "autonomous agent",
            "ai agent",
            "rag",
            "retrieval-augmented",
            "jailbreak",
            "instruction following",
            "system prompt",
            "tool call",
            "function call",
            "agent hijacking",
            "code interpreter",
            "ai model",
            "language model",
        ]
        
        # Immediate noise reduction: Discard anything related to hardware, industrial, or standard office software.
        self.noise_denylist = [
            "printer", "industrial", "firmware", "office suite", "car rental", 
            "expense tracker", "router", "switch", "iot", "camera", "medical", 
            "shuttle", "reservation", "aerospace", "automotive"
        ]

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
                    "keywordExactMatch": "",        # Fix A1: Enable exact/description-only matching
                    "cvssV3Severity": "CRITICAL",  # Only wake me up for the scary stuff
                    "resultsPerPage": 5             # Fix A1: Slightly larger per keyword
                }
                
                response = requests.get(self.api_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    for v in vulnerabilities:
                        cve_data = v.get("cve", {})
                        
                        # Extract the english description
                        desc = next((d.get("value") for d in cve_data.get("descriptions", []) if d.get("lang") == "en"), "No description available.")
                        desc_lower = desc.lower()

                        # --- Fix A2: Combined Noise & Agentic Filter ---
                        # 1. Reject if it matches the denylist (hardware/infra)
                        if any(noise in desc_lower for noise in self.noise_denylist):
                            continue 

                        # 2. Reject if no agentic signal is found in the description
                        if not any(signal in desc_lower for signal in self.agentic_allowlist):
                            continue

                        # Extract CVSS
                        metrics = cve_data.get("metrics", {})
                        cvss_data = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
                        score = cvss_data.get("baseScore", 0.0)
                        
                        # --- Fix A3: Extract CWE tags ---
                        cwe_ids = []
                        for weakness in cve_data.get("weaknesses", []):
                            for desc_entry in weakness.get("description", []):
                                cwe_val = desc_entry.get("value", "")
                                if cwe_val and cwe_val != "NVD-CWE-noinfo":
                                    cwe_ids.append(cwe_val)

                        results.append({
                            "cve_id": cve_data.get("id"),
                            "description": desc,
                            "severity": "CRITICAL",
                            "score": score,
                            "cwes": cwe_ids,              # NEW: Pass CWEs downstream
                            "source": "NVD"
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
        # In a recent refactor, SITES.md might have moved. 
        # We search for it in standard locations.
        sites_path = "intelligence/SITES.md"
        if not os.path.exists(sites_path):
            sites_path = "SITES.md"

        if not os.path.exists(sites_path):
            return # Skip if file doesn't exist

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
            try:
                with open(sites_path, "r") as f:
                    content = f.read()
                    
                if new_source["name"] not in content:
                    # Append it to SITES.md
                    with open(sites_path, "a") as f:
                        f.write(f"\n- **[{new_source['name']}]({new_source['url']}):** {new_source['desc']} (Autodiscovered: {new_source['tier']})")
                    
                    if logger:
                        logger.add_file_updated(sites_path, details=f"Autodiscovered and added active intel source: {new_source['name']}")
                        
                    print(f"[Scraper Config] Discovered new source: {new_source['name']}")
            except Exception as e:
                print(f"[Scraper Config] Failed to update SITES.md: {e}")

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
                "description": "Mock Critical Agent Hijacking vulnerability including Large Language Model context.",
                "severity": "CRITICAL",
                "score": 9.8,
                "cwes": ["CWE-1336"],
                "source": "Mock"
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
