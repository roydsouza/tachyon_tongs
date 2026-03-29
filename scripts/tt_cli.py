#!/usr/bin/env python3
import sys
import os
import argparse
import json
from datetime import datetime
from typing import Optional

# Setup path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from tachyon.core.forensics import ForensicStore
from tachyon.core.signing import IntegrityManager

def format_timestamp(ts: str) -> str:
    """Format an ISO timestamp to a readable CLI string."""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts[:19]

def bus_explore(args):
    """Interactive exploration of the telemetry bus (Forensic Ledger)."""
    store = ForensicStore()
    im = IntegrityManager()
    
    print(f"\n[CLI] Exploring Forensic Ledger: {store.db_path}")
    print(f"{'ID':<4} | {'TIMESTAMP':<19} | {'AGENT':<12} | {'TYPE':<15} | {'STATUS':<8} | {'PQC':<3}")
    print("-" * 75)
    
    events = store.query_latest(
        limit=args.limit, 
        event_type=args.type, 
        agent_id=args.agent
    )
    
    # query_latest returns events in DESC order. Re-sort ASC for streaming view?
    # User might want a "tail" like experience.
    if not args.reverse:
        events.reverse()
    
    for e in events:
        # Verify PQC signature in real-time
        # Signature logic from forensics.py: timestamp|agent_id|event_type|action|status|source|details_json
        details_json = json.dumps(e["details"])
        content = f"{e['timestamp']}|{e['agent_id']}|{e['event_type']}|{e['action']}|{e['status']}|{e['source']}|{details_json}"
        
        is_verified = im.verify_text_signature(content, e["signature"])
        sig_icon = "✅" if is_verified else "❌"
        
        ts = format_timestamp(e["timestamp"])
        print(f"{e['id']:<4} | {ts:<19} | {e['agent_id']:<12} | {e['event_type']:<15} | {e['status']:<8} | {sig_icon:<3}")
        
        if args.verbose:
            print(f"    Action:  {e['action']}")
            print(f"    Details: {json.dumps(e['details'], indent=4)}")
            print(f"    Sig:     {e['signature'][:32]}...")
            print("-" * 75)

    print(f"\n[CLI] Shown {len(events)} events (Limit: {args.limit})")

def forensic_bundle(args):
    """Packages logs, database, and alerts into a PQC-signed archive."""
    import tarfile
    import tempfile
    import shutil
    
    im = IntegrityManager()
    root_dir = ROOT_DIR
    mem_dir = os.path.join(root_dir, "memory", "operational")
    
    # 1. Mandatory files
    targets = [
        os.path.join(mem_dir, "forensics.db"),
        os.path.join(mem_dir, "telemetry.jsonl"),
        os.path.join(root_dir, "ALERT.md"),
    ]
    
    # 2. Add logs directory if it exists
    logs_dir = os.path.join(root_dir, "logs")
    if os.path.exists(logs_dir):
        targets.append(logs_dir)

    # 3. Create archive
    bundle_name = f"tachyon_forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    bundle_path = os.path.join(root_dir, bundle_name)
    
    print(f"[CLI] Creating Forensic Bundle: {bundle_name}...")
    try:
        with tarfile.open(bundle_path, "w:gz") as tar:
            for target in targets:
                if os.path.exists(target):
                    arcname = os.path.relpath(target, root_dir)
                    tar.add(target, arcname=arcname)
                    print(f"  + Added: {arcname}")
        
        # 4. Sign the archive
        print(f"[CLI] Anchoring bundle with Hybrid PQC signature...")
        im.sign_archive(bundle_path)
        
        print(f"\n[SUCCESS] Forensic bundle generated and signed.")
        print(f"  Archive:   {bundle_path}")
        print(f"  Signature: {bundle_path}.sig.json")
    except Exception as e:
        if os.path.exists(bundle_path):
            os.remove(bundle_path)
        print(f"[ERROR] Failed to create forensic bundle: {e}")
        sys.exit(1)

def debate_list(args):
    """Lists the last 10 debates in the debates directory."""
    debates_dir = os.path.join(ROOT_DIR, "debates")
    if not os.path.exists(debates_dir):
        print(f"[ERROR] Debates directory not found: {debates_dir}")
        return
    
    files = sorted([f for f in os.listdir(debates_dir) if f.endswith(".md")], reverse=True)
    print(f"\n[CLI] Last {min(10, len(files))} Debates (Root: {debates_dir})")
    print(f"{'TIMESTAMP ID':<25} | {'TITLE'}")
    print("-" * 75)
    
    for f in files[:10]:
        # DEBATE_20260318_144046_CVE-2025-46725.md
        parts = f.replace("DEBATE_", "").replace(".md", "").split("_")
        timestamp_id = "_".join(parts[:2])
        title = "_".join(parts[2:])
        print(f"{timestamp_id:<25} | {title}")

def debate_replay(args):
    """Streams a PQC-verified debate transcript with color-coded personas."""
    debates_dir = os.path.join(ROOT_DIR, "debates")
    im = IntegrityManager()
    
    # 1. Discovery
    files = [f for f in os.listdir(debates_dir) if args.id in f and f.endswith(".md")]
    if not files:
        print(f"[ERROR] No debate found matching ID: {args.id}")
        return
    
    target_file = os.path.join(debates_dir, files[0])
    
    # 2. PQC Verification
    print(f"[CLI] Replaying: {os.path.basename(target_file)}")
    is_verified = im.verify_integrity(target_file)
    sig_status = "✅ PQC VERIFIED" if is_verified else "❌ SIGNATURE FAILURE (UNTRUSTED)"
    
    if not is_verified:
        print(f"\n{'!' * 40}")
        print(f"  WARNING: {sig_status}")
        print(f"{'!' * 40}\n")
    else:
        print(f"[STATUS] {sig_status}\n")

    # 3. Rendering
    try:
        with open(target_file, "r") as f:
            content = f.read()
        
        # Color codes
        CYAN = "\033[96m"
        YELLOW = "\033[93m"
        MAGENTA = "\033[95m"
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"
        BOLD = "\033[1m"
        
        lines = content.split("\n")
        for line in lines:
            if line.startswith("## 🏗️ The Engineer"):
                print(f"{CYAN}{BOLD}{line}{RESET}")
            elif line.startswith("## 🧐 The Skeptic"):
                print(f"{YELLOW}{BOLD}{line}{RESET}")
            elif line.startswith("## ⚖️ The Meta-Critic"):
                print(f"{MAGENTA}{BOLD}{line}{RESET}")
            elif "Verdict" in line:
                color = GREEN if "allow" in line.lower() else RED
                print(f"{color}{BOLD}{line}{RESET}")
            else:
                print(line)
                
    except Exception as e:
        print(f"[ERROR] Failed to read debate: {e}")

def main():
    parser = argparse.ArgumentParser(prog="tt", description="Tachyon Tongs CLI Shell")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    
    # Bus Subcommand
    bus_parser = subparsers.add_parser("bus", help="Telemetry Bus operations")
    bus_sub = bus_parser.add_subparsers(dest="subcommand")
    
    explore_parser = bus_sub.add_parser("explore", help="Explore the signed telemetry ledger")
    explore_parser.add_argument("--limit", type=int, default=20, help="Number of events to display (default: 20)")
    explore_parser.add_argument("--type", type=str, help="Filter by event type (e.g. TOOL_CALL)")
    explore_parser.add_argument("--agent", type=str, help="Filter by agent id")
    explore_parser.add_argument("--reverse", action="store_true", help="Show events in descending ID order (newest first)")
    explore_parser.add_argument("--verbose", "-v", action="store_true", help="Display full details and actions")

    # Forensic Subcommand
    forensic_parser = subparsers.add_parser("forensic", help="Forensic management")
    forensic_sub = forensic_parser.add_subparsers(dest="subcommand")
    forensic_sub.add_parser("bundle", help="Create a signed forensic export bundle")
    
    # Debate Subcommand
    debate_parser = subparsers.add_parser("debate", help="Debate replay tools")
    debate_sub = debate_parser.add_subparsers(dest="subcommand")
    
    debate_sub.add_parser("list", help="List recent debates")
    replay_parser = debate_sub.add_parser("replay", help="Replay a specific debate by ID")
    replay_parser.add_argument("id", help="Debate ID or partial name")
    
    # Health Subcommand
    subparsers.add_parser("health", help="Run substrate health check")
    
    args = parser.parse_args()
    
    if args.command == "bus" and args.subcommand == "explore":
        bus_explore(args)
    elif args.command == "forensic" and args.subcommand == "bundle":
        forensic_bundle(args)
    elif args.command == "debate" and args.subcommand == "list":
        debate_list(args)
    elif args.command == "debate" and args.subcommand == "replay":
        debate_replay(args)
    elif args.command == "health":
        import subprocess
        subprocess.run([sys.executable, "scripts/health_check.py"])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
