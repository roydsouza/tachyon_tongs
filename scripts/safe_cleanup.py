import os
import subprocess
import sys

def run_git_cmd(cmd: list):
    """Run a git command with PAGER=cat."""
    env = os.environ.copy()
    env["PAGER"] = "cat"
    result = subprocess.run(
        cmd, 
        env=env, 
        capture_output=True, 
        text=True,
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
    return result

def safe_cleanup():
    """
    Tachyon Tongs: Safe Sanitation.
    1. Checks for dirty state.
    2. Pushes to GitHub.
    3. Triggers substrate cleanup.
    """
    print("--- [Safe-Cleanup] Starting Secure Sanitation Loop ---")
    
    # 1. Check for dirty state
    status = run_git_cmd(["git", "status", "--porcelain"])
    if status.stdout.strip():
        print("[Safe-Cleanup] Dirty state detected. Synchronizing to GitHub...")
        
        # Add all (non-ignored) changes
        run_git_cmd(["git", "add", "."])
        
        # Commit
        commit_msg = f"Auto-hygiene sync-and-purge [{os.getlogin()} @ {subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()}]"
        run_git_cmd(["git", "commit", "-m", commit_msg])
        
        # Push
        print("[Safe-Cleanup] Pushing changes...")
        push = run_git_cmd(["git", "push"])
        
        if push.returncode != 0:
            print(f"[ERROR] Git push failed: {push.stderr}")
            print("[Safe-Cleanup] ABORTING cleanup to prevent data loss.")
            sys.exit(1)
        else:
            print("[Safe-Cleanup] GitHub sync successful.")
    else:
        print("[Safe-Cleanup] Substrate is clean. No sync required.")

    # 2. Trigger Substrate Cleanup
    from cleanup_substrate import cleanup_substrate
    cleanup_substrate()
    
    print("--- [Safe-Cleanup] Substrate is Secure, Synced, and Pure. ---")

if __name__ == "__main__":
    safe_cleanup()
