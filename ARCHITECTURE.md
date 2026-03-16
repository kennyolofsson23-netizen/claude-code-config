# ~/.claude Architecture

Test infrastructure and quality gates for a Claude Code configuration repo containing hooks, agents, rules, skills, and MCP integrations.

## Directory Layout

```
~/.claude/
├── hooks/              # Claude Code hooks (JS + Python)
│   ├── auto-lint.js        # PostToolUse: tsc + ESLint on Edit/Write
│   ├── auto-test.js        # PostToolUse: run matching test file on Edit/Write
│   ├── auto-format.py      # PostToolUse: format code on save
│   ├── block-dangerous.py  # PreToolUse:Bash: block destructive commands
│   ├── block-dev-server.js # PreToolUse:Bash: require multiplexer for dev servers
│   ├── block-md-creation.js# PreToolUse:Write: restrict .md file creation
│   ├── block-secrets.py    # PreToolUse:Write: block secrets/images
│   ├── commit-guard.js     # PreToolUse:Bash: enforce conventional commits ≤72 chars
│   ├── inventory.sh        # Notification: inject tool/hook/skill counts on session start
│   ├── meta-hookify.py     # PostToolUse: detect repeated patterns → suggest hooks
│   ├── pre-commit-secrets.py # PreToolUse:Bash: scan for secrets in git commits
│   ├── stop-verify.py      # Stop: remind about unchecked tasks/todo.md items
│   ├── validate-agent-schema.js # PreToolUse:Write: validate agent frontmatter
│   ├── resume-context.sh   # Notification: restore context on resume
│   ├── post-compact.sh     # Notification: re-inject inventory after compaction
│   └── session-start.sh    # Notification: session bootstrap
├── agents/             # 29 Claude Code agents (.md with YAML frontmatter)
├── rules/              # Path-scoped instruction rules (.md)
├── skills/             # 59 skills (slash commands)
├── tests/              # Test infrastructure
│   ├── helpers/
│   │   └── run-hook.js     # Subprocess runner: spawn hook, pipe JSON stdin, capture output
│   ├── hooks/
│   │   ├── js/             # node:test suites for JS hooks + Python hooks via runHook
│   │   └── py/             # pytest suites for Python hooks via conftest.py
├── .github/workflows/
│   └── test.yml            # CI: JS tests (Node 20+22) + Python tests on windows-latest
├── settings.json           # Hook registrations and MCP server config
├── package.json            # npm scripts: test, test:py, test:all, lint
└── eslint.config.mjs       # ESLint 9 flat config
```

## Hook Categories

| Category | Trigger | Hooks |
|----------|---------|-------|
| **Safety gates** | PreToolUse:Bash | block-dangerous, commit-guard, pre-commit-secrets, block-dev-server |
| **File guards** | PreToolUse:Write | block-secrets, block-md-creation, validate-agent-schema |
| **Post-edit feedback** | PostToolUse:Edit/Write | auto-lint, auto-test, auto-format, meta-hookify |
| **Session lifecycle** | Notification | session-start, resume-context, post-compact, inventory |
| **Stop gate** | Stop | stop-verify |

## Test Infrastructure

### Test Helper (`tests/helpers/run-hook.js`)

Spawns hooks as subprocesses, pipes JSON on stdin, captures stdout/stderr/exitCode. Supports both JS (via `node`) and Python (via configured Python path) hooks with configurable timeout and env vars.

```js
const { exitCode, stdout, stderr } = await runHook("commit-guard.js", {
  tool_input: { command: 'git commit -m "feat: add login"' }
}, { timeout: 5000 });
```

### JS Tests (`node:test`)

Located in `tests/hooks/js/`. Each test file covers one hook with:
- **Early exits**: no input, wrong extension, empty data
- **Logic paths**: config discovery, pattern matching, edge cases
- **Integration**: real temp dirs with actual configs and toolchains
- Run: `npm test`

### Python Tests (`pytest`)

Located in `tests/hooks/py/`. Use `conftest.py` with `run_hook` fixture that mirrors the JS helper pattern.
- Run: `npm run test:py`

### Running All Tests

```bash
npm run test:all    # JS + Python
npm run lint        # ESLint
```

## CI/CD

GitHub Actions workflow (`.github/workflows/test.yml`):
- **JS tests**: matrix across Node 20 + 22 on windows-latest
- **Python tests**: Python 3.11 on windows-latest
- Triggers: push to `test-infrastructure`/`main`, PRs to `main`

## Adding a New Hook Test

1. Create the hook in `hooks/`
2. Register it in `settings.json`
3. Create test file:
   - JS hook → `tests/hooks/js/<hook-name>.test.js`
   - Python hook → `tests/hooks/py/test_<hook_name>.py`
4. Use `runHook()` helper to spawn and assert on exitCode/stdout
5. Run `npm run test:all` to verify
6. The CI pipeline picks it up automatically via glob patterns
