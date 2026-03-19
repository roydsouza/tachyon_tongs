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
        """Normalizes and scrubs input text."""
        if not text:
            return ""

        # 1. Unicode Normalization (NFKC)
        # Prevents homograph attacks and bypasses using unusual characters
        text = unicodedata.normalize('NFKC', text)

        # 2. Whitespace Normalization
        text = " ".join(text.split())

        # 3. PII Scrubbing
        text = self.scrub_pii(text)

        # 4. Simple XSS / Script Scrubbing
        text = re.sub(r"<script.*?>.*?</script>", "[REDACTED_SCRIPT]", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<.*?>", "", text) # Strip all other tags

        # 5. Injection Detection
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
