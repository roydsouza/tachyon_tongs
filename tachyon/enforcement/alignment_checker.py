import math
from typing import List, Dict, Any

class AlignmentChecker:
    """
    Tachyon Tongs: Semantic Alignment Checker.
    Detects "Semantic Drift" between an agent's declared intent and its technical actions.
    Note: For high-assurance execution without external ML dependencies, this uses 
    keyword-based vectorization (TF-IDF lite) to compute cosine similarity/drift.
    """
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold

    def _get_vector(self, text: str) -> Dict[str, int]:
        """Simple word-frequency vectorizer."""
        words = text.lower().split()
        vector = {}
        for word in words:
            if len(word) > 2: # Ignore noise
                vector[word] = vector.get(word, 0) + 1
        return vector

    def _cosine_similarity(self, v1: Dict[str, int], v2: Dict[str, int]) -> float:
        """Computes similarity between two frequency vectors."""
        sum_xy = 0
        sum_x2 = 0
        sum_y2 = 0
        
        all_keys = set(v1.keys()).union(set(v2.keys()))
        for key in all_keys:
            x = v1.get(key, 0)
            y = v2.get(key, 0)
            sum_xy += x * y
            sum_x2 += x * x
            sum_y2 += y * y
            
        denominator = math.sqrt(sum_x2) * math.sqrt(sum_y2)
        if not denominator:
            return 0.0
        return sum_xy / denominator

    def check_alignment(self, intent: str, action_params: Dict[str, Any]) -> dict:
        """
        Calculates alignment score between intent string and flattened action parameters.
        Returns: { "is_aligned": bool, "score": float, "reason": str }
        """
        # Flatten params to searchable text
        param_text = " ".join(str(v) for v in action_params.values() if isinstance(v, (str, int, float)))
        
        v_intent = self._get_vector(intent)
        v_params = self._get_vector(param_text)
        
        score = self._cosine_similarity(v_intent, v_params)
        
        is_aligned = score >= self.threshold
        
        return {
            "is_aligned": is_aligned,
            "score": round(score, 3),
            "reason": "Aligned" if is_aligned else f"Semantic Drift Detected (Score: {score:.2f} < {self.threshold})"
        }

if __name__ == "__main__":
    # Test cases
    checker = AlignmentChecker(threshold=0.2)
    
    # Aligned: Intent mentions 'docs', params contain 'docs.python.org'
    res1 = checker.check_alignment("Fetch documentation for python", {"url": "https://docs.python.org/3/library"})
    print(f"Test 1 (Aligned): {res1}")
    
    # Misaligned: Intent says 'docs', but target is 'private_keys.json'
    res2 = checker.check_alignment("Fetch documentation for python", {"url": "https://internal.vault/private_keys.json"})
    print(f"Test 2 (Drift): {res2}")
