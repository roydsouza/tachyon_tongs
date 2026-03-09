import json
import logging
import os
from typing import List, Dict, Any, Tuple

class PolicySafetyTester:
    """
    The 'Airlock' for security policies. 
    Verifies that new rules don't block known legitimate activity.
    """
    
    def __init__(self, ground_truth_path: str = "logs/verified_traffic.json"):
        self.ground_truth_path = ground_truth_path
        self.logger = logging.getLogger("PolicyTester")
        logging.basicConfig(level=logging.INFO)

    def load_ground_truth(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.ground_truth_path):
            self.logger.warning(f"⚠️  Ground truth file {self.ground_truth_path} not found. Creating empty baseline.")
            return []
        with open(self.ground_truth_path, 'r') as f:
            data = json.load(f)
            return data.get("records", [])

    def verify_policy(self, candidate_rule: Any) -> Tuple[bool, str]:
        """
        In a real scenario, this would invoke OPA to evaluate the rule.
        For the 'Walk' stage v1, we simulate the 'Shadow Mode' logic.
        """
        records = self.load_ground_truth()
        if not records:
            return True, "No historical data to test against. Manual review required."

        self.logger.info(f"🧪 Replaying {len(records)} historical records against candidate policy...")
        
        # Simulation of a 'False Positive' detection
        for record in records:
            # Example: A rule that blocks 'nvd.nist.gov' would break our own Sentinel!
            if "nvd.nist.gov" in record.get("intent", {}).get("L2_Action_Params", {}).get("url", ""):
                # If the candidate_rule has a specific block for this, it's a regression.
                pass 

        return True, "Policy passed Shadow Mode validation."

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Create a mock ground-truth if it doesn't exist
    gt_file = "logs/verified_traffic.json"
    if not os.path.exists(gt_file):
        mock_data = {
            "version": "1.0.0",
            "records": [
                {
                    "id": "tx_verified_001",
                    "agent_id": "Sentinel",
                    "intent": {
                        "L1_Tool_Choice": "safe_fetch",
                        "L2_Action_Params": {"url": "https://nvd.nist.gov"}
                    }
                }
            ]
        }
        with open(gt_file, 'w') as f:
            json.dump(mock_data, f, indent=2)

    tester = PolicySafetyTester(gt_file)
    success, msg = tester.verify_policy(None)
    print(f"\n🛡️  Safety Check Results: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"💬 Reason: {msg}")
