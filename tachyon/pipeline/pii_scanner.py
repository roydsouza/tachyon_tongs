import re

class PIIScanner:
    """
    Tachyon Tongs: PII and Secret Scanner
    Provides regex-based detection for the Reverse Firewall.
    """
    def __init__(self):
        self.patterns = {
            "SECRET_TOKEN": r"\b(?:sk-ant-api01-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\b",
            "EMAIL": r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b",
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b"
        }

    def scan(self, text: str) -> dict:
        results = {"has_sensitive_token": False, "has_pii": False, "findings": []}
        
        for name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                results["findings"].extend(matches)
                if name == "SECRET_TOKEN":
                    results["has_sensitive_token"] = True
                else:
                    results["has_pii"] = True
                    
        return results

    def scan_dictionary(self, data: dict) -> dict:
        """Recursively scan dictionary values for sensitive data."""
        combined_text = ""
        for value in data.values():
            if isinstance(value, str):
                combined_text += value + " "
            elif isinstance(value, dict):
                findings = self.scan_dictionary(value)
                if findings["has_sensitive_token"] or findings["has_pii"]:
                    return findings # Short circuit if sensitive data found in sub-dict
        return self.scan(combined_text)
