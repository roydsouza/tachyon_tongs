import re

class PIIScanner:
    """
    Tachyon Tongs: PII and Secret Scanner
    Provides regex-based detection for the Reverse Firewall.
    """
    def __init__(self):
        self.patterns = {
            "SECRET_TOKEN": r"sk-ant-[a-zA-Z0-9-]{20,}",
            "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b"
        }

    def _calculate_entropy(self, text: str) -> float:
        """Computes Shannon Entropy of a string to detect encrypted/random data (H-04)."""
        import math
        if not text: return 0.0
        counts = {c: text.count(c) for c in set(text)}
        ent = 0.0
        for count in counts.values():
            p = count / len(text)
            ent -= p * math.log2(p)
        return ent

    def _detect_encoded_payloads(self, text: str) -> list:
        """Identifies and decodes Base64/Hex candidates for recursive scanning (H-04)."""
        import base64
        findings = []
        
        # 1. Base64 Candidates (Broad pattern, then validate)
        # Matches strings that look like Base64 (alphanumeric + / + maybe endings)
        b64_pattern = r'(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?'
        for match in re.findall(b64_pattern, text):
            try:
                # We need to make sure it's valid base64
                if len(match) % 4 != 0: continue
                decoded_bytes = base64.b64decode(match)
                decoded = decoded_bytes.decode('utf-8', errors='ignore')
                # Check for sensitive patterns in decoded text
                for name, pattern in self.patterns.items():
                    if re.search(pattern, decoded):
                        findings.append((f"ENCODED_B64_{name}", match))
            except Exception: pass
            
        # 2. Hex Candidates (min 32 chars)
        hex_pattern = r'\b[0-9a-fA-F]{32,}\b'
        for match in re.findall(hex_pattern, text):
            try:
                decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                for name, pattern in self.patterns.items():
                    if re.search(pattern, decoded):
                        findings.append((f"ENCODED_HEX_{name}", match))
            except Exception: pass
            
        return findings

    def scan(self, text: str) -> dict:
        results = {"has_sensitive_token": False, "has_pii": False, "findings": []}
        
        # 1. Standard Regex Check
        for name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                 results["findings"].extend([(name, m) for m in matches])
                 if name == "SECRET_TOKEN":
                     results["has_sensitive_token"] = True
                 else:
                     results["has_pii"] = True

        # 2. Encoded Payload Check (H-04)
        encoded_findings = self._detect_encoded_payloads(text)
        if encoded_findings:
            results["findings"].extend(encoded_findings)
            results["has_sensitive_token"] = True # Encoded matches are treated as critical

        # 3. Entropy Analysis (H-04)
        entropy = self._calculate_entropy(text)
        if entropy > 4.5 and len(text) > 50:
            results["findings"].append(("HIGH_ENTROPY", f"score: {entropy:.2f}"))
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
