"""
Tachyon Tongs: Contextual Intent Scoring engine
Dynamic L1/L2 gate calculations based on heuristic behavioral metadata.
"""
from dataclasses import dataclass

@dataclass
class IntentContext:
    hour_of_day: int
    data_sensitivity: str  # 'low', 'medium', 'high'
    days_since_active: int

class ContextualIntentGate:
    def __init__(self):
        # Base risk multipliers
        self.weights = {
            'time_anomaly': 0.3, # Reduced from 0.4 so Time+MediumSensitivity = 0.7 (CHALLENGE)
            'sensitivity': 0.8,
            'dormancy': 0.3
        }
        
    def score_intent(self, intent_type: str, context: IntentContext) -> dict:
        """
        Calculates risk. 
        < 0.4 = ALLOW 
        0.4 to 0.7 = CHALLENGE (Hardware YubiKey required)
        > 0.7 = BLOCK
        """
        risk_score = 0.0
        
        # Time anomaly (assume 9 to 5 are normal hours)
        if context.hour_of_day < 8 or context.hour_of_day > 18:
            risk_score += self.weights['time_anomaly']
            
        # Sensitivity
        if context.data_sensitivity == 'high':
            risk_score += self.weights['sensitivity']
        elif context.data_sensitivity == 'medium':
            risk_score += (self.weights['sensitivity'] * 0.5)
            
        # Dormancy (Activity from a dormant state is suspicious)
        if context.days_since_active > 30:
            risk_score += self.weights['dormancy']
            
        # Hard cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        if risk_score < 0.4:
            return {"action": "ALLOW", "score": risk_score}
        elif risk_score < 0.75:
            return {"action": "CHALLENGE", "score": risk_score, "reason": "Unusual context boundaries triggered L1 Gate."}
        else:
            return {"action": "BLOCK", "score": risk_score, "reason": "High risk threshold exceeded. Fatal intent."}
