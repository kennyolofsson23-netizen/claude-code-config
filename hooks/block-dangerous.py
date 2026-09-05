"""PreToolUse hook for Bash — blocks dangerous/destructive commands."""

import re
import shlex
import sys
import json

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

cmd_lower = command.lower().strip()

# Paths a recursive delete must never target. Anything NOT in this set (e.g.
# /c/Users/me/build) is a normal subpath and is allowed through.
PROTECTED_PATHS = {
    "/", ".", "..", "~", "$home", "${home}", "%userprofile%", "$env:userprofile",
    "/etc", "/usr", "/bin", "/sbin", "/lib", "/lib64", "/var", "/boot",
    "/dev", "/proc", "/sys", "/opt", "/root", "/home", "/tmp",
    "/windows", "/c", "/d", "/e", "/c/windows", "/c/users", "/c/programdata",
    "/c/program files", "/c/program files (x86)",
    "c:", "c:/", "c:\\", "d:", "d:/", "d:\\",
}


def recursive_rm_targets(cmd):
    """Protected paths hit by a recursive rm, checking the TARGET not a substring.

    A plain "rm -rf /" in cmd test also matches rm -rf /c/Users/me/build, which
    is a perfectly ordinary delete. This parses each rm invocation and compares
    its actual arguments against PROTECTED_PATHS instead.
    """
    hits = []
    for segment in re.split(r"[;&|\n]+", cmd):
        segment = segment.strip()
        if not re.match(r"^(sudo\s+)?rm\b", segment):
            continue
        try:
            parts = shlex.split(segment)
        except ValueError:
            parts = segment.split()
        flags = "".join(p.lstrip("-") for p in parts if p.startswith("-"))
        if "r" not in flags.lower():
            continue  # not recursive; cannot remove a directory tree
        for target in [p for p in parts[1:] if not p.startswith("-")]:
            norm = target.strip("\"'")
            if norm.endswith("/*") or norm.endswith("\\*"):
                norm = norm[:-2]
            norm = norm.replace("\\", "/").rstrip("/") or "/"
            if norm.lower() in PROTECTED_PATHS:
                hits.append(target)
    return hits


_rm_hits = recursive_rm_targets(command)
if _rm_hits:
    print(
        f"BLOCKED: recursive delete of protected path {_rm_hits[0]!r} detected. "
        f"This is a dangerous/destructive command. "
        f"Ask the user for explicit confirmation before proceeding.",
        file=sys.stderr,
    )
    sys.exit(2)

BLOCKED_PATTERNS = [
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
]

# These are warned but allowed (Claude should confirm with user first)
WARN_PATTERNS = [
    "git push origin main",
    "git push origin master",
    "vercel --prod",
    "vercel deploy --prod",
]

for pattern in BLOCKED_PATTERNS:
    if pattern in cmd_lower:
        print(
            f"BLOCKED: '{pattern}' detected. This is a dangerous/destructive command. "
            f"Ask the user for explicit confirmation before proceeding.",
            file=sys.stderr,
        )
        sys.exit(2)

for pattern in WARN_PATTERNS:
    if pattern in cmd_lower:
        print(
            f"WARNING: '{pattern}' detected. Make sure the user has confirmed this push.",
            file=sys.stderr,
        )
        # Exit 0 — allow but warn
        sys.exit(0)

# Block force branch delete (case-sensitive: -D is force, -d is safe)
if "git branch" in cmd_lower and "-D" in command:
    print(
        "BLOCKED: 'git branch -D' detected. This is a dangerous/destructive command. "
        "Ask the user for explicit confirmation before proceeding.",
        file=sys.stderr,
    )
    sys.exit(2)

# Block any force push variant (git push ... -f or --force anywhere)
if "git push" in cmd_lower and ("-f" in cmd_lower.split() or "--force" in cmd_lower):
    print(
        "BLOCKED: Force push detected. Ask the user for explicit confirmation.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
