# Environment (always loaded)
- Auto-detect platform, shell, and paths at session start (run `uname -s` or check `process.platform`)
- On Windows with Git Bash: use Unix syntax and forward slashes
- If Git Bash can't find node/npm/python: use `which` or `where` to locate full paths
- PowerShell: use `&` call operator, single quotes to avoid smart-quote issues
- Set `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` for non-ASCII output
