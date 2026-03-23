import argparse
import sys
import os

# Ensure tachyon is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents._core.roles import SentinelRole, EngineerRole, GuardianRole, SentryRole, HealerRole

def main():
    parser = argparse.ArgumentParser(description="Tachyon Tongs Unified Substrate Controller")
    parser.add_argument("--role", required=True, choices=["sentinel", "engineer", "guardian", "sentry", "healer", "keys"], help="Agent role to assume")
    parser.add_argument("--action", required=True, help="Action to execute")
    parser.add_argument("--params", type=str, help="JSON parameters for the action")
    parser.add_argument("--agent-id", default="tachyon-master", help="Identity of the agent")

    args = parser.parse_args()

    import json
    params = json.loads(args.params) if args.params else {}

    # Key Management (Phase 25.1)
    if args.role == "keys":
        from scripts.generate_keys import genesis_ceremony, recovery_drill
        if args.action == "genesis":
            genesis_ceremony()
        elif args.action == "recover":
            recovery_drill()
        else:
            print(f"Error: Unknown keys action {args.action}")
            sys.exit(1)
        return

    # Role Factory
    if args.role == "sentinel":
        agent = SentinelRole(args.agent_id)
    elif args.role == "engineer":
        agent = EngineerRole(args.agent_id)
    elif args.role == "guardian":
        agent = GuardianRole(args.agent_id)
    elif args.role == "sentry":
        agent = SentryRole(args.agent_id)
    elif args.role == "healer":
        agent = HealerRole(args.agent_id)
    else:
        print(f"Error: Unknown role {args.role}")
        sys.exit(1)

    print(f"[*] Substrate: Assumed role '{args.role}' as {args.agent_id}")
    result = agent.handle_action(args.action, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
