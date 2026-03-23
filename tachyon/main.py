import argparse
import sys
import os

# Ensure tachyon is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Roles are now dynamically discovered via AgentRegistry

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
    # Key Management (Phase 25.1 / 25.2)
    if args.role == "keys":
        from scripts.agent_keys import cmd_status, cmd_delegate
        from tachyon.core.signing import IntegrityManager
        im = IntegrityManager()
        
        if args.action == "status":
            cmd_status(im)
        elif args.action == "delegate":
            # Extract role from params if available
            role_to_delegate = params.get("role", "unknown")
            cmd_delegate(im, role_to_delegate, 30)
        elif args.action == "genesis":
            from scripts.generate_keys import genesis_ceremony
            genesis_ceremony()
        elif args.action == "recover":
            from scripts.generate_keys import recovery_drill
            recovery_drill()
        else:
            print(f"Error: Unknown keys action {args.action}")
            sys.exit(1)
        return

    # Role Factory
    from agents._core.registry import AgentRegistry
    from agents._core.roles import BaseTachyonRole
    
    # Auto-discover plugins from the flat agents/ directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    agents_dir = os.path.join(root_dir, "agents")
    AgentRegistry.discover_plugins(agents_dir)
    
    available_roles = AgentRegistry.list_plugins()
    if args.role not in available_roles:
        print(f"Error: Unknown role '{args.role}'. Available: {', '.join(available_roles)}")
        sys.exit(1)

    print(f"[*] Substrate: Assumed role '{args.role}' for {args.agent_id}")
    
    # We now use the generic BaseTachyonRole which delegates to the registry
    agent = BaseTachyonRole(args.agent_id, args.role)
    result = agent.handle_action(args.action, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
