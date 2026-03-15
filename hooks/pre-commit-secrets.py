"""PreToolUse hook for Bash — scans for secrets in staged files before git commit."""
import sys
import json
import subprocess
import re

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

# Only trigger on git commit commands
if not re.search(r'\bgit\s+commit\b', command):
    sys.exit(0)

# Check staged files for dangerous patterns
try:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

    BLOCKED_FILES = {
        ".env", ".env.local", ".env.production", ".env.staging",
        "credentials.json", "secrets.json", "serviceaccount.json",
        "id_rsa", "id_ed25519",
    }
    BLOCKED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp"}

    violations = []
    for f in staged_files:
        basename = f.split("/")[-1].lower()
        ext = "." + basename.rsplit(".", 1)[-1] if "." in basename else ""

        if basename in BLOCKED_FILES:
            violations.append(f"  SECRET: {f}")
        elif ext in BLOCKED_EXTENSIONS:
            violations.append(f"  IMAGE: {f}")

    # Also scan staged content for common secret patterns
    if staged_files:
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "-U0"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        content = diff_result.stdout
        secret_patterns = [
            (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', "API key"),
            (r'(?:secret|password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}', "Password/secret"),
            (r'sk-[a-zA-Z0-9]{20,}', "Stripe/OpenAI secret key"),
            (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "Private key"),
        ]
        for pattern, label in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"  CONTENT: {label} detected in staged changes")

    if violations:
        msg = "BLOCKED: Secrets/sensitive files detected in staged changes:\n"
        msg += "\n".join(violations)
        msg += "\n\nUnstage these files before committing. Use: git reset HEAD <file>"
        print(msg, file=sys.stderr)
        sys.exit(2)

except Exception:
    pass  # Don't block commits if scanning fails

sys.exit(0)
