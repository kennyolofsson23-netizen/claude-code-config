"""PreToolUse hook for Write/Edit — blocks writing to secret/binary files."""
import sys
import json
import os

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "")

basename = os.path.basename(file_path).lower()
ext = os.path.splitext(file_path)[1].lower()

# Block secret/env files
BLOCKED_FILES = {
    ".env", ".env.local", ".env.production", ".env.staging",
    "credentials.json", "secrets.json", "serviceaccount.json",
    "id_rsa", "id_ed25519", ".npmrc", ".pypirc",
}

if basename in BLOCKED_FILES:
    print(
        f"BLOCKED: Cannot write to '{basename}'. "
        f"Secrets and env files must be edited manually by Kenny.",
        file=sys.stderr,
    )
    sys.exit(2)

# Block image/binary files
BLOCKED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp"}

if ext in BLOCKED_EXTENSIONS:
    print(
        f"BLOCKED: Cannot write image files ('{ext}'). "
        f"Binary/image files should not be created by Claude.",
        file=sys.stderr,
    )
    sys.exit(2)

# Block if path contains common secret directories
SECRET_DIRS = {"/.ssh/", "/secrets/", "/private/"}
path_lower = file_path.replace("\\", "/").lower()
for secret_dir in SECRET_DIRS:
    if secret_dir in path_lower:
        print(
            f"BLOCKED: Cannot write to path containing '{secret_dir}'. "
            f"This looks like a sensitive directory.",
            file=sys.stderr,
        )
        sys.exit(2)

sys.exit(0)
