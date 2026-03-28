import math
from typing import Union

class EntropyAnalyzer:
    """
    Shannon Entropy analyzer for detecting unusual information density.
    Typical English text: ~4.0 - 5.0 bits/byte.
    Base64 encoded data: ~5.95 bits/byte.
    Encrypted/Compressed data: 7.5 - 8.0 bits/byte.
    """
    
    @staticmethod
    def calculate(data: Union[str, bytes]) -> float:
        """Calculates Shannon entropy in bits per byte."""
        if not data:
            return 0.0
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        if len(data) == 0:
            return 0.0
            
        # Count frequency of each byte
        counts = {}
        for b in data:
            counts[b] = counts.get(b, 0) + 1
            
        entropy = 0.0
        length = len(data)
        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)
            
        return entropy

    @staticmethod
    def is_suspicious(data: Union[str, bytes], threshold: float = 5.8) -> bool:
        """
        Heuristic check for suspicious entropy levels.
        Default threshold of 5.8 flags most compressed/encrypted Base64 data.
        """
        # Exclude very short strings from entropy analysis to avoid noise
        if len(data) < 64:
            return False
            
        return EntropyAnalyzer.calculate(data) > threshold
