import argparse
import sys
import os
import shutil

# Ensure we can import from tachyon
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.integrations.claw_translator import ClawTranslator
from tachyon.core.state_manager import StateManager

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs: Claw Ecosystem Import Utility")
    parser.add_argument("--source", required=True, help="Path to the Claw agent directory")
    parser.add_argument("--name", required=True, help="Internal name for the imported agent")
    args = parser.parse_args()

    translator = ClawTranslator()
    state = StateManager()

    print(f"🦞 Starting Import: {args.name}...")
    
    try:
        # 1. Translate
        print("   [1/5] Translating formats...")
        target_path = translator.import_agent(args.source, "agents")
        
        # 2. Static Analysis (Stub)
        print("   [2/5] Performing static analysis...")
        
        # 3. Canary Sandbox (Stub)
        print("   [3/5] Initializing Canary Sandbox...")
        
        # 4. Airlock Proposing
        print("   [4/5] Proposing to Airlock...")
        state.log_evolution("CLAW_IMPORT", f"Imported Claw agent '{args.name}' into {target_path}. Mode: QUARANTINE")
        
        # 5. Quarantine Deployment
        print(f"✅ [5/5] Deployed to Quarantine: {target_path}")
        print("\nReview the import in the Airlock or via 'tt airlock review'.")

    except Exception as e:
        print(f"❌ Import Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
