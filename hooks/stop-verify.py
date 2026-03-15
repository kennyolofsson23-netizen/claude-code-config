"""Stop hook — checks unchecked todos and reminds to log task patterns."""

import os
import sys
import json

data = json.load(sys.stdin)
messages = []

# Check for unchecked todo items
if os.path.exists("tasks/todo.md"):
    with open("tasks/todo.md", "r", encoding="utf-8") as f:
        content = f.read()
    unchecked = [
        line.strip()
        for line in content.splitlines()
        if line.strip().startswith("- [ ]")
    ]
    if unchecked:
        messages.append(
            f"WARNING: {len(unchecked)} unchecked items remain in tasks/todo.md"
        )
        for item in unchecked[:5]:
            messages.append(f"  {item}")

# Remind to log task pattern if tasks/ directory exists
if os.path.isdir("tasks"):
    messages.append("")
    messages.append("BEFORE STOPPING: Did you log this task to tasks/patterns.log?")
    messages.append("Format: YYYY-MM-DD | task-type | short description")
    messages.append(
        "If task type already appears 2+ times → CREATE a skill or agent NOW"
    )

if messages:
    print("\n".join(messages), file=sys.stderr)

sys.exit(0)
