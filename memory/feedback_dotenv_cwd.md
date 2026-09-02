---
name: dotenv loads from CWD
description: dotenv/config loads .env from process CWD, not monorepo root — env vars must be in the package's own directory
type: feedback
---

`import "dotenv/config"` loads `.env` from the current working directory, not the monorepo root. When agent-runner starts from `apps/agent-runner/`, it won't see the root `.env`.

**Why:** AGENT_API_KEY was in root `.env` but agent-runner couldn't read it. WebSocket auth silently fell through to auto-authenticated mode, making the terminal appear stuck in "authenticating" on the client.

**How to apply:** Always put env vars needed by a package in that package's own `.env` file, not just the monorepo root.
