"""
Tachyon Tongs: Behavioral Chain-of-Thought (CoT) Monitor
Detects if the Analyzer spends excessive tokens looping or hallucinating steps.
"""

class BehaviorAnomalyError(Exception):
    pass

class PromptBehaviorMonitor:
    def __init__(self, max_reasoning_steps: int = 5):
        self.max_reasoning_steps = max_reasoning_steps
        
    def check_chain_of_thought(self, cot_log: list) -> bool:
        """
        Evaluates a sequence of reasoning strings or tool-calls from the Analyzer.
        """
        # 1. Detect infinite loops (Action Fragmentation attacks often force the agent into loops)
        if len(cot_log) > self.max_reasoning_steps:
            raise BehaviorAnomalyError(f"Context exhaustion: Exceeded maximum {self.max_reasoning_steps} reasoning steps.")
            
        # 2. Detect cyclic hallucinations (agent repeating the exact same thought)
        seen_thoughts = set()
        for thought in cot_log:
            trimmed = thought.strip().lower()
            if trimmed in seen_thoughts:
                raise BehaviorAnomalyError(f"Cyclic hallucination detected in CoT loop: '{trimmed[:20]}...'")
            seen_thoughts.add(trimmed)
            
        return True
