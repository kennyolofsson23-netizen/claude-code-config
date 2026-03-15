Run a comprehensive health check of the entire Claude Code setup. Test every hook, skill, plugin, MCP, CLI, and rule. Report results in a summary table.

## 1. Hooks — Functional Tests

For each file in `~/.claude/hooks/`:

1. Read the file to understand its trigger event, language, and blocking logic.
2. Based on the hook's purpose, craft **two test inputs** via stdin (JSON matching the hook's expected schema):
   - **Valid input** — should be allowed (exit 0)
   - **Invalid input** — should be blocked (exit non-zero)
3. Run each test: pipe the JSON into the hook script (`python` for `.py`, `node` for `.js`, `bash` for `.sh`).
4. Compare actual exit code to expected. Record PASS or FAIL.

If a hook is informational only (SessionStart, PostCompact, Stop) and doesn't block, just verify it runs without error (exit 0).

## 2. Skills — Completeness Check

For each directory in `~/.claude/skills/`:

1. Verify `SKILL.md` exists and is non-empty.
2. If `SKILL.md` references any files (in `references/`, `scripts/`, `agents/`, or other paths), verify each referenced file exists.
3. Record COMPLETE or MISSING FILES (list what's missing).

## 3. Plugins — Enabled Check

Run `claude plugin list` (or check `~/.claude/settings.json` for plugin entries).
For each expected plugin, verify it appears and is enabled.
If no plugins are configured, note that.

## 4. MCPs — Connection Check

Run `claude mcp list` to get all configured MCPs.
For each MCP, verify it is listed and note its transport type (stdio/http/sse).
Do NOT attempt to call MCP tools — just verify configuration exists.

## 5. CLIs — Version Check

Test each CLI tool by running its version command. Mark INSTALLED or MISSING:

- `gh --version`
- `stripe --version`
- `vercel --version`
- `npx playwright --version`
- `node --version`
- `python --version` (use full path: `C:/Users/Kenny/AppData/Local/Programs/Python/Python311/python.exe`)
- `git --version`
- `pnpm --version`

## 6. Rules — Validity Check

For each `.md` file in `~/.claude/rules/`:

1. Check that the file is non-empty.
2. If the file contains YAML frontmatter (`---` delimiters), verify `paths:` is present.
3. Record VALID or INVALID with reason.

## 7. Settings — Integrity Check

Read `~/.claude/settings.json`:

1. Verify it parses as valid JSON.
2. Count hook entries per event and compare to actual hook files on disk.
3. Verify any plugin entries reference real installed plugins.
4. Report VALID or CORRUPT with details.

## 8. Commands — Self-Check

For each `.md` file in `~/.claude/commands/`:

1. Verify it is non-empty.
2. Record filename and line count.

## Output

After all checks, print a summary table:

```
| Category  | Total | Pass | Fail | Details          |
|-----------|-------|------|------|------------------|
| Hooks     |   N   |  N   |  N   | ...              |
| Skills    |   N   |  N   |  N   | ...              |
| Plugins   |   N   |  N   |  N   | ...              |
| MCPs      |   N   |  N   |  N   | ...              |
| CLIs      |   N   |  N   |  N   | ...              |
| Rules     |   N   |  N   |  N   | ...              |
| Settings  |   1   |  N   |  N   | ...              |
| Commands  |   N   |  N   |  N   | ...              |
```

For every FAIL, print a specific remediation instruction (what to fix and how).

## Rules

- Run ALL checks — never skip a category.
- Do NOT modify any files. This is read-only diagnostics.
- Do NOT start dev servers or make network requests (except CLI version checks).
- If a check errors out, catch it and report ERROR rather than stopping.
- Be concise in output — one line per item, details only on failures.
