"""Stop hook — checks unchecked todos and reminds to log task patterns."""

import os
import sys
import json
import datetime

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

# Remind to log task patterns only when patterns.log is actually stale.
# Firing this on every single stop makes it noise that gets tuned out, so it
# only speaks up when today's work hasn't been recorded yet.
if os.path.isdir("tasks"):
    log_path = os.path.join("tasks", "patterns.log")
    today = datetime.date.today()
    stale = True
    if os.path.exists(log_path):
        modified = datetime.date.fromtimestamp(os.path.getmtime(log_path))
        stale = modified < today
    if stale:
        messages.append("")
        messages.append("Not logged today: append this task to tasks/patterns.log")
        messages.append("Format: YYYY-MM-DD | task-type | short description")
        messages.append(
            "If task type already appears 2+ times → CREATE a skill or agent NOW"
        )

if messages:
    print("\n".join(messages), file=sys.stderr)

sys.exit(0)
