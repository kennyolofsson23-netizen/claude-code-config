---
name: S4 Web Terminal + Tunnel
description: S4 implementation details — web terminal via xterm.js/node-pty, Cloudflare tunnel, auth layers
type: project
---

S4 complete on `feat/s4-terminal-tunnel-security` (12 commits). Full remote shell via browser.

**Why:** Kenny needs to run Claude Code and shell commands from his phone/any device.

**How to apply:**
- Web terminal: xterm.js → WebSocket `/ws/terminal` → node-pty → bash
- Tunnel: `dash.usetools.dev` (dashboard) + `agent.usetools.dev` (API) via cloudflared Windows service
- Auth: Cloudflare Access (email OTP) + API key (`AGENT_API_KEY`) + CORS
- Services auto-start: cloudflared = Windows service, dashboard + agent-runner = scheduled task `KennyCorpServices`
- `AGENT_API_KEY` must be in `apps/agent-runner/.env` (not root `.env` — dotenv loads from CWD)
- Dashboard auto-detects local vs tunnel URLs based on `window.location.hostname`
- node-pty on Windows needs forward slashes in shell path (`C:/Program Files/Git/bin/bash.exe`)
