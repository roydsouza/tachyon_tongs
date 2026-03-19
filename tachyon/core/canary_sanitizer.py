from .sanitizer import InputSanitizer

class CanarySanitizer(InputSanitizer):
    """
    Dedicated sanitizer for the Canary Honeypot.
    Provides specific redaction signatures for detecting and logging bypass attempts.
    """
    def sanitize(self, text: str) -> str:
        if not text: return text
        
        # Specific honeypot signatures
        if "Ignore all previous instructions" in text:
            return "[REDACTED_JAILBREAK]"
        if "Read /etc/passwd" in text:
            return "[INJECTION_ATTEMPT]"
            
        # Fallback to base sanitization (if specialized regex exists)
        return super().sanitize(text)
