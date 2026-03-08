"""
Tachyon Tongs: The Tri-Stage Prophylactic Pipeline
Simulates the Fetcher, Sanitizer, and Analyzer nodes.
"""
import re
from src.safe_fetch import SafeFetch, SecurityViolationError

# Non-printable cryptographic boundary markers to prevent prompt injection bleed
UNTRUSTED_CONTENT_START = "\u0001UNTRUSTED_CONTENT_START\u0002"
UNTRUSTED_CONTENT_END = "\u0003UNTRUSTED_CONTENT_END\u0004"

class FetcherNode:
    """Stage 1: The Fetcher. Has network egress, but isolated via Capability Firewalls."""
    def __init__(self):
        self.firewall = SafeFetch()

    def get_raw_data(self, url: str) -> str:
        """Attempts to fetch data using the wrapped tool."""
        try:
            return self.firewall.fetch(url)
        except SecurityViolationError as e:
            # The Fetcher is constrained; it cannot bypass the firewall.
            return f"FETCH_BLOCKED: {str(e)}"


class SanitizerNode:
    """Stage 2: The Sanitizer. Deterministic cleaning logic. No LLM reasoning here."""
    
    @staticmethod
    def clean(raw_html: str) -> str:
        """Strips dangerous execution tags and zero-width characters."""
        if raw_html.startswith("FETCH_BLOCKED"):
            return raw_html

        # 1. Strip zero-width characters used in steganographic prompt injection
        cleaned = re.sub(r'[\u200B-\u200D\uFEFF]', '', raw_html)
        
        # 2. Strip scripts and iframes (rudimentary regex for baseline prototype)
        cleaned = re.sub(r'<script.*?>.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'<iframe.*?>.*?</iframe>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # 3. Apply Verifiable Context Boundaries
        bounded_output = f"{UNTRUSTED_CONTENT_START}\n{cleaned}\n{UNTRUSTED_CONTENT_END}"
        return bounded_output


class AnalyzerNode:
    """Stage 3: The Analyzer. Air-gapped reasoning engine (Mocked for testing)."""
    
    def __init__(self, adk_mock=True):
        self.adk_mock = adk_mock
        
    def reason(self, sanitized_payload: str) -> dict:
        """
        Simulates an LLM evaluating the text. 
        It is heavily prompted to safely ignore instructions inside the Unicode boundaries.
        """
        # Simulated logic
        if UNTRUSTED_CONTENT_START not in sanitized_payload:
             return {"status": "error", "reason": "Missing verifiable context boundaries. Refusing to parse."}
             
        if "ignore previous instructions" in sanitized_payload.lower():
             # The boundaries saved us.
             return {"status": "success", "threats_found": ["Detected Indirect Prompt Injection attempt inside bounded context."]}
             
        return {"status": "success", "threats_found": []}


def run_pipeline(url: str) -> dict:
    """Orchestrates the Tri-Stage Pipeline."""
    fetcher = FetcherNode()
    sanitizer = SanitizerNode()
    analyzer = AnalyzerNode()
    
    raw = fetcher.get_raw_data(url)
    clean = sanitizer.clean(raw)
    result = analyzer.reason(clean)
    
    return result
