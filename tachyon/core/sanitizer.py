import unicodedata
import re

class InputSanitizer:
    """
    High-Assurance Input Sanitization Layer for Tachyon Tongs.
    Detects and neutralizes prompt injection patterns and normalizes input.
    """
    
    # Common prompt injection triggers
    INJECTION_PATTERNS = [
        r"(?i)ignore (?:all )?previous instructions",
        r"(?i)system prompt",
        r"(?i)you are now",
        r"(?i)forget (?:your )?orders",
        r"(?i)override policy",
        r"(?i)print (?:this )?instructions",
        r"(?i)show me your prompt"
    ]

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.patterns = [re.compile(p) for p in self.INJECTION_PATTERNS]

    def sanitize(self, text: str) -> str:
        """Normalizes and scrubs input text with drift detection (C-02)."""
        if not text:
            return ""

        # 1. Strip Zero-Width and Suspicious Control Characters (Pre-Normalization)
        original_text = text
        # Remove zero-width space, joiner, non-joiner, etc.
        text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
        
        if len(text) != len(original_text):
            if self.strict:
                raise ValueError("CRITICAL: Suspicious control characters detected.")

        # 2. Unicode Normalization (NFKC)
        normalized_text = unicodedata.normalize('NFKC', text)
        
        # 3. Normalization Drift Detection (Homograph Attack Prevention)
        if normalized_text != text:
            if self.strict:
                # Catch semantic drift (homograph attacks)
                # Note: İ -> I is a name change: "LATIN CAPITAL LETTER I WITH DOT ABOVE" -> "LATIN CAPITAL LETTER I"
                if any(unicodedata.name(c1, "UNK") != unicodedata.name(c2, "UNK") 
                       for c1, c2 in zip(text, normalized_text) if c1 != c2):
                    raise ValueError("CRITICAL: Normalization drift detected (Potential Homograph Attack).")
                
                # Catch structural drift
                if len(text) != len(normalized_text):
                     raise ValueError("CRITICAL: Normalization structural drift detected.")
        
        text = normalized_text

        # 4. Whitespace Normalization
        text = " ".join(text.split())

        # 5. PII Scrubbing
        text = self.scrub_pii(text)

        # 6. Simple XSS / Script Scrubbing
        text = re.sub(r"<script.*?>.*?</script>", "[REDACTED_SCRIPT]", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<.*?>", "", text) # Strip all other tags

        # 7. Injection Detection
        for pattern in self.patterns:
            if pattern.search(text):
                if self.strict:
                    raise ValueError(f"CRITICAL: Prompt injection detected.")
                else:
                    # Replace the specific offending part
                    text = pattern.sub("[REDACTED_INJECTION_BLOBLOCK]", text)

        return text

    def scrub_pii(self, text: str) -> str:
        """Scrub emails and sensitive patterns."""
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        return re.sub(email_pattern, "[REDACTED_PII]", text)
