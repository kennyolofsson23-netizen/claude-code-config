# Environment (always loaded)
- Platform: Windows 11, shell: Git Bash (Unix syntax, forward slashes)
- Python: `C:\Users\Kenny\AppData\Local\Programs\Python\Python311\python.exe`
- Node: `C:\Program Files\nodejs\node.exe` | npm global: `C:\Users\Kenny\AppData\Roaming\npm\`
- Git Bash doesn't see Windows PATH fully — use full paths for node/npm/python when needed
- Stripe CLI: `export PATH="$PATH:/c/Users/Kenny/AppData/Local/Microsoft/WinGet/Links"` before using `stripe`
- PowerShell: use `&` call operator, single quotes to avoid smart-quote issues
- Set `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` for non-ASCII output
