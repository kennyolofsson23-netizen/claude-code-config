---
paths:
  - "**/*.py"
---
# Python Rules
- Use `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` for non-ASCII output
- Python path: `C:\Users\Kenny\AppData\Local\Programs\Python\Python311\python.exe`
- Run tests with: `pytest backend/tests/ -v --tb=short`
- Auto-formatted with black (enforced by hook)
- Never use bare `except:` — always catch specific exceptions
- Prefer pathlib over os.path for file operations
