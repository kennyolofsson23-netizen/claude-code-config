---
name: project-init
description: "Initialize a new project with Kenny's universal conventions and stack-appropriate infrastructure. Use this skill whenever: setting up a new project, creating a new repo, scaffolding a new app, starting fresh on a new idea, 'init project', 'new project', 'set up a new app', 'create a project for X', or any variant of starting a new codebase from scratch. Also trigger when the user says 'bootstrap', 'scaffold', or 'kickstart'. This skill ensures every project gets the same quality gates and conventions while adapting infrastructure to the chosen stack."
---

# Project Init

Initialize any new project with Kenny's universal rules and stack-appropriate infrastructure. This skill adapts to whatever technology stack the project uses — Node, Python, Go, Rust, anything — while enforcing the same quality and workflow conventions everywhere.

## Why This Exists

Kenny runs multiple ventures simultaneously. Every project must follow the same quality gates (TDD, verification, autonomous execution) but use whatever stack makes sense. This skill prevents the "forgot to set up X" problem and ensures every project is Claude-ready from day one.

## Workflow

### Step 1: Gather Project Info

Ask the user (or infer from context) these questions. Skip any that are already answered:

1. **Project name** — kebab-case identifier (e.g., `my-saas-app`)
2. **One-line description** — what does it do?
3. **Primary language/framework** — Node/Next.js, Python/FastAPI, Go, Rust, etc.
4. **Database needed?** — PostgreSQL, SQLite, MongoDB, Redis, none
5. **Location** — default: `C:\Users\Kenny\projects/<name>`

Don't ask about deployment, CI, or advanced config — those come later when the project needs them.

### Step 2: Create Project Structure

Based on the answers, create the project directory and initialize it.

#### 2a. Project CLAUDE.md

Create `CLAUDE.md` in the project root. This is the most important file — it tells every future Claude session how to work in this project.

```markdown
# <Project Name>

## Overview
<one-line description>

## Stack
- **Language:** <language>
- **Framework:** <framework>
- **Database:** <database or "none">
- **Package Manager:** <npm/pnpm/pip/cargo/go modules>

## Quick Start
```bash
<stack-appropriate setup commands>
```

## Server Management
```bash
./scripts/servers.sh start    # Start all services
./scripts/servers.sh status   # Check health
./scripts/servers.sh restart  # Restart all services
./scripts/servers.sh stop     # Stop all services
```
Always run `./scripts/servers.sh start` at session start. Kenny does NOT manage servers manually.

## Universal Rules (DO NOT REMOVE)

### Test-Driven Development
- 100% test coverage target
- Write tests BEFORE implementing
- Run ALL tests before marking any task done
- If something breaks — fix it yourself, don't report it
- Never say "it should work" — run it and prove it

### Execution
- Never tell Kenny to run something — you ARE the terminal
- Enter plan mode for any non-trivial task (3+ steps)
- Fix bugs autonomously — no hand-holding

### Verification Gate
Before marking ANY task complete:
- Run tests and show output
- UI changes → screenshot with Playwright
- Linting → run project linter
- "Looks right" is NOT verification

### Self-Improvement
- After any correction → update `tasks/lessons.md`
- Repeated workflow (2+) → create a skill
- Repeated rule → create a hook

### Git
- Feature branches always — never push to main
- Never commit .env, credentials, or secrets
- Conventional commits: `type(scope): description`

## Project-Specific Rules
<add domain-specific rules here as the project evolves>

## Gotchas & Lessons
<add learnings here as they're discovered>
```

Adapt the Quick Start section to the actual stack. Examples:
- **Node/Next.js:** `pnpm install && pnpm dev`
- **Python/FastAPI:** `pip install -e . && uvicorn app.main:app --reload`
- **Go:** `go mod download && go run .`
- **Rust:** `cargo build && cargo run`

#### 2b. Task Files

Create `tasks/todo.md`:
```markdown
# <Project Name> — Tasks

## Setup
- [ ] Initial implementation
```

Create `tasks/lessons.md`:
```markdown
# <Project Name> — Lessons

Record learnings, gotchas, and corrections here. After ANY correction from Kenny, add an entry immediately.
```

#### 2c. Server Management Script

Create `scripts/servers.sh` — adapted to the stack. The script MUST:
- Be idempotent (safe to run multiple times)
- Use PID files to track processes
- Support `start`, `stop`, `restart`, `status` commands
- Kill stray processes on the expected ports
- Auto-clean any build caches on restart

**For Node/Next.js projects:**
- Start the dev server (next dev, vite dev, etc.)
- Start any backend service if separate

**For Python projects:**
- Start uvicorn/gunicorn/flask
- Activate venv if needed

**For Go projects:**
- Build and run the binary
- Watch mode if air/reflex is available

**For any project with a database:**
- Start Docker Compose
- Check DB is ready before starting the app

Read the reference file `references/servers-template.sh` for the template.

#### 2d. Docker Compose (if database needed)

Create `docker-compose.yml` for the database:
- PostgreSQL → port 5433 (avoids 5432 conflict with any local pg)
- Redis → port 6380 (avoids 6379 conflict)
- MongoDB → port 27018 (avoids 27017 conflict)

Always use non-default ports to avoid conflicts with locally installed services.

#### 2e. .gitignore

Create `.gitignore` appropriate for the stack. Always include:
```
# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# PID files
*.pid
.runner.pid
.dashboard.pid

# Logs
*.log
```

Plus stack-specific ignores (node_modules, __pycache__, target/, etc.)

#### 2f. Git Init

```bash
git init
git add -A
git commit -m "feat(init): scaffold project with conventions"
```

### Step 3: Verify

After creating everything:
1. Run `./scripts/servers.sh start` to verify the script works
2. Check that all files are in place
3. Show the user a summary of what was created

## What This Skill Does NOT Do

- Pick the stack for you (you choose)
- Set up CI/CD (that comes when you need it)
- Create application code (that's your next task)
- Configure deployment (project-specific, added later)
- Set up authentication (project-specific)

The skill creates the **foundation** — the rails every project runs on. Application logic comes next.
