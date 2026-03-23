import os
import sys

def setup_hygiene_automation():
    """
    Sets up a macOS LaunchAgent to run scripts/safe_cleanup.py every 48 hours.
    """
    print("--- [Automation] Setting up macOS launchd Hygiene Loop ---")
    
    substrate_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script_path = os.path.join(substrate_root, "scripts", "safe_cleanup.py")
    python_path = sys.executable
    
    label = "com.tachyon.hygiene"
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    os.makedirs(plist_dir, exist_ok=True)
    plist_path = os.path.join(plist_dir, f"{label}.plist")
    
    # Standard output/error logs
    log_dir = os.path.join(substrate_root, "tmp")
    os.makedirs(log_dir, exist_ok=True)
    out_log = os.path.join(log_dir, "hygiene_out.log")
    err_log = os.path.join(log_dir, "hygiene_err.log")

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>StartInterval</key>
    <integer>172800</integer> <!-- 48 hours -->
    <key>StandardOutPath</key>
    <string>{out_log}</string>
    <key>StandardErrorPath</key>
    <string>{err_log}</string>
    <key>WorkingDirectory</key>
    <string>{substrate_root}</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    
    try:
        with open(plist_path, "w") as f:
            f.write(plist_content)
        print(f"[Success] LaunchAgent plist created at: {plist_path}")
        
        print("\n[ACTION REQUIRED] To activate the automation, run:")
        print(f"  launchctl load {plist_path}")
        print("\nTo verify status:")
        print(f"  launchctl list | grep {label}")
        
    except Exception as e:
        print(f"[Error] Failed to setup automation: {e}")

if __name__ == "__main__":
    setup_hygiene_automation()
