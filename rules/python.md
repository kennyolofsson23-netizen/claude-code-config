---
paths:
  - "**/*.py"
---
# Python Rules
- Use `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` for non-ASCII output
- Use `python3` (or `python` on Windows) — auto-detect with `which python3 || which python`
- Run tests with: `pytest backend/tests/ -v --tb=short`
- Auto-formatted with black (enforced by hook)
- Never use bare `except:` — always catch specific exceptions
- Prefer pathlib over os.path for file operations
