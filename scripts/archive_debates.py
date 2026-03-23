import os
import shutil
from datetime import datetime, timedelta

def archive_debates(source_dir="debates", dest_dir="memory/archive/debates", max_age_days=7):
    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} not found. Skipping.")
        return

    os.makedirs(dest_dir, exist_ok=True)
    now = datetime.now()
    cutoff = now - timedelta(days=max_age_days)

    archived_count = 0
    for filename in os.listdir(source_dir):
        if filename.startswith("DEBATE_") and filename.endswith(".md"):
            filepath = os.path.join(source_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mtime < cutoff:
                print(f"Archiving {filename} (Modified: {mtime})")
                shutil.move(filepath, os.path.join(dest_dir, filename))
                archived_count += 1

    print(f"✅ Archived {archived_count} debate files.")

if __name__ == "__main__":
    archive_debates()
