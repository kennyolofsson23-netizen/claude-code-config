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
    "git push origin main",
    "git push origin master",
    "git checkout -- .",
    "git clean -fd",
    "git clean -f",
    "git branch -D",
    "drop database",
    "drop table",
    "truncate table",
    "railway up",
    "vercel --prod",
    "vercel deploy --prod",
]

for pattern in BLOCKED_PATTERNS:
    if pattern in cmd_lower:
        print(
            f"BLOCKED: '{pattern}' detected. This is a dangerous/destructive command. "
            f"Ask Kenny for explicit confirmation before proceeding.",
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
