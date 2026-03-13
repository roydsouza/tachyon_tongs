#!/usr/bin/env python3
import os
import re

def archive_tasks():
    tasks_file = "TASKS.md"
    accomplishments_file = "ACCOMPLISHMENTS.md"
    
    if not os.path.exists(tasks_file):
        print(f"Error: {tasks_file} not found.")
        return

    with open(tasks_file, "r") as f:
        content = f.read()

    # Regex to find phases that are 100% completed
    # A phase is completed if it has [COMPLETED] in its header
    # and all its bullet points are [x]
    
    sections = re.split(r"(?m)^(### .*)$", content)
    
    new_tasks_content = sections[0]
    archived_content = ""
    
    for i in range(1, len(sections), 2):
        header = sections[i]
        body = sections[i+1] if i+1 < len(sections) else ""
        
        if "[COMPLETED]" in header:
            print(f"Archiving section: {header.strip()}")
            archived_content += header + body
        else:
            new_tasks_content += header + body

    if archived_content:
        # Append to Accomplishments
        mode = "a" if os.path.exists(accomplishments_file) else "w"
        with open(accomplishments_file, mode) as f:
            if mode == "w":
                f.write("# Tachyon Tongs: Accomplishments\n\n")
            f.write(archived_content)
        
        # Write back filtered tasks
        with open(tasks_file, "w") as f:
            f.write(new_tasks_content)
        
        print(f"Successfully archived completed tasks to {accomplishments_file}")
    else:
        print("No completed phases found to archive (looking for '[COMPLETED]' keyword in headers).")

if __name__ == "__main__":
    archive_tasks()
