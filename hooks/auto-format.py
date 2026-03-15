"""PostToolUse hook for Write/Edit — auto-formats Python and JS/TS files after changes."""
import sys
import json
import os
import subprocess

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
file_path = tool_input.get("file_path", "")

if not file_path or not os.path.isfile(file_path):
    sys.exit(0)

ext = os.path.splitext(file_path)[1].lower()
PYTHON = r"C:\Users\Kenny\AppData\Local\Programs\Python\Python311\python.exe"
NODE = r"C:\Program Files\nodejs\node.exe"
NPX = r"C:\Users\Kenny\AppData\Roaming\npm\npx.cmd"

try:
    if ext == ".py":
        subprocess.run(
            [PYTHON, "-m", "black", "--quiet", file_path],
            capture_output=True,
            timeout=10,
        )
    elif ext in {".ts", ".tsx", ".js", ".jsx", ".css", ".json"}:
        # Only format if a prettier config exists nearby (project uses prettier)
        dir_path = os.path.dirname(file_path)
        has_prettier = False
        check_dir = dir_path
        for _ in range(10):  # Walk up max 10 levels
            for config in [".prettierrc", ".prettierrc.json", ".prettierrc.js", "prettier.config.js", "prettier.config.mjs"]:
                if os.path.exists(os.path.join(check_dir, config)):
                    has_prettier = True
                    break
            # Also check package.json for prettier key
            pkg = os.path.join(check_dir, "package.json")
            if os.path.exists(pkg):
                try:
                    with open(pkg) as f:
                        if '"prettier"' in f.read():
                            has_prettier = True
                except Exception:
                    pass
            if has_prettier:
                break
            parent = os.path.dirname(check_dir)
            if parent == check_dir:
                break
            check_dir = parent

        if has_prettier:
            subprocess.run(
                [NPX, "prettier", "--write", file_path],
                capture_output=True,
                timeout=10,
            )
except Exception:
    pass  # Formatting failures should never block work

sys.exit(0)
