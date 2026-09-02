---
name: node-pty Windows path gotcha
description: node-pty on Windows requires forward slashes in shell path — backslashes get mangled and cause File not found
type: feedback
---

node-pty's `spawn()` on Windows fails with "File not found" when the shell path uses backslashes (`C:\\Program Files\\Git\\bin\\bash.exe`). Use forward slashes instead: `C:/Program Files/Git/bin/bash.exe`.

**Why:** Backslash escaping gets mangled through Node's string handling + node-pty's WindowsPtyAgent. Caused silent PTY spawn failure that was hard to debug.

**How to apply:** Always use forward slashes for paths passed to node-pty on Windows.
