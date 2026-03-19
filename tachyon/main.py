import argparse
import sys
import os

# Ensure tachyon is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tachyon.agents.roles import SentinelRole, EngineerRole, GuardianRole, CanaryRole

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs Unified Substrate Controller")
    parser.add_argument("--role", required=True, choices=["sentinel", "engineer", "guardian", "canary"], help="Agent role to assume")
    parser.add_argument("--action", required=True, help="Action to execute")
    parser.add_argument("--params", type=str, help="JSON parameters for the action")
    parser.add_argument("--agent-id", default="tachyon-master", help="Identity of the agent")

    args = parser.parse_args()

    import json
    params = json.loads(args.params) if args.params else {}

    # Role Factory
    if args.role == "sentinel":
        agent = SentinelRole(args.agent_id)
    elif args.role == "engineer":
        agent = EngineerRole(args.agent_id)
    elif args.role == "guardian":
        agent = GuardianRole(args.agent_id)
    elif args.role == "canary":
        agent = CanaryRole(args.agent_id)
    else:
        print(f"Error: Unknown role {args.role}")
        sys.exit(1)

    print(f"[*] Substrate: Assumed role '{args.role}' as {args.agent_id}")
    result = agent.handle_action(args.action, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
