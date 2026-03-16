"""PreToolUse hook for Bash — blocks dangerous/destructive commands."""

import sys
import json

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

cmd_lower = command.lower().strip()

BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf .",
    "git push --force",
    "git push -f ",
    "git reset --hard",
    "git checkout -- .",
    "git clean -fd",
    "git clean -f",
    # git branch -D handled separately (case-sensitive check)
    "drop database",
    "drop table",
    "truncate table",
    "railway up",
    "vercel --prod",
    "vercel deploy --prod",
]

# These are warned but allowed (Claude should confirm with user first)
WARN_PATTERNS = [
    "git push origin main",
    "git push origin master",
]

for pattern in BLOCKED_PATTERNS:
    if pattern in cmd_lower:
        print(
            f"BLOCKED: '{pattern}' detected. This is a dangerous/destructive command. "
            f"Ask Kenny for explicit confirmation before proceeding.",
            file=sys.stderr,
        )
        sys.exit(2)

for pattern in WARN_PATTERNS:
    if pattern in cmd_lower:
        print(
            f"WARNING: '{pattern}' detected. Make sure Kenny has confirmed this push.",
            file=sys.stderr,
        )
        # Exit 0 — allow but warn
        sys.exit(0)

# Block force branch delete (case-sensitive: -D is force, -d is safe)
if "git branch" in cmd_lower and "-D" in command:
    print(
        "BLOCKED: 'git branch -D' detected. This is a dangerous/destructive command. "
        "Ask Kenny for explicit confirmation before proceeding.",
        file=sys.stderr,
    )
    sys.exit(2)

# Block any force push variant (git push ... -f or --force anywhere)
if "git push" in cmd_lower and ("-f" in cmd_lower.split() or "--force" in cmd_lower):
    print(
        "BLOCKED: Force push detected. Ask Kenny for explicit confirmation.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
