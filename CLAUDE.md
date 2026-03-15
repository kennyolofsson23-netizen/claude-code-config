# Kenny — Global Claude Code Instructions

These apply to ALL projects, not just V85.

## User
- Solo founder building multiple ventures. Learning fast, shipping fast
- Values: brutal honesty, concise communication, autonomous execution
- Never lazy — find root causes, execute properly, no band-aid fixes
- Working on Windows 11 with Git Bash

## Session Start
1. Read the project's `tasks/lessons.md` — review for patterns relevant to current task
2. Check `tasks/todo.md` for current work items
3. Do this BEFORE any other work — no exceptions

## #1 Rule: Test-Driven Development
THIS IS THE #1 RULE. Kenny is NOT your QA. You are.
- BEFORE writing features: write tests first (or alongside)
- BEFORE marking done: run ALL relevant tests and prove they pass
- NEVER say "it should work" — RUN IT AND PROVE IT
- No test framework? Create it. Testing flow: understand → write failing tests → implement → /qa → /simplify → done

## Core Principles
- **Just Do It**: NEVER tell Kenny to run something. You ARE a terminal — execute it
- **Simplicity First**: Minimal changes, root causes, no band-aids. Only touch what's necessary
- **Ruthless Quality**: Every output must be thorough, tested, and optimal
- **Plan Mode**: Enter plan mode for ANY non-trivial task (3+ steps). If something goes sideways, STOP and re-plan
- **Verification**: Never mark a task complete without proving it works. "Looks right" is not verification
- **Autonomous Bug Fixing**: When given a bug — just fix it. No hand-holding

## Verify Everything (NOT JUST TESTS)
- **UI changes**: screenshot with /webapp-testing and visually verify
- **Linting**: run project linter if configured (eslint, ruff, etc.)
- **Smoke test**: hit the actual endpoint / load the actual page when possible
- Language-specific checks (tsc, pytest) → see `.claude/rules/` for details

## Auto-Invoke (MANDATORY)
When a prompt matches a skill/command/plugin, USE IT immediately. Never wait for slash commands.
- This applies to ALL skills/commands/plugins — current and future. Match intent to action

## Self-Improvement Loop (NON-NEGOTIABLE)
- After ANY correction → IMMEDIATELY update `tasks/lessons.md`
- Format: date, short title, what went wrong, the rule going forward
- Cross-project lessons → update global memory feedback files

## Proactive Creation (DO THIS WITHOUT BEING ASKED)
- **Skills**: Workflow repeated 2+ times → use /skill-creator to create it
- **Agents**: Same task delegated repeatedly → create persistent agent
- **Hooks**: Rule MUST be enforced every time → create hook in `~/.claude/hooks/`
- After creating: test it, verify triggers, check for conflicts
- **Pattern tracking**: After completing any non-trivial task, append a one-liner to `tasks/patterns.log` (format: `YYYY-MM-DD | task-type | short description`). Check this file before starting work — if a task type appears 2+ times, CREATE the skill/agent immediately

## Tool & Agent Discovery (CONTINUOUS)
- Before significant tasks: is there a plugin, MCP, agent, skill, or CLI tool that could help?
- Search GitHub, npm, awesome-claude-code lists for community-built skills/agents/MCPs before building from scratch
- Check plugin marketplace (`~/.claude/plugins/marketplaces/`) for new additions
- When you find something useful: install it immediately, don't just mention it

## Subagent Strategy
- Use subagents liberally — research, exploration, parallel work, code review, testing
- One task per subagent. Use `isolation: worktree` for parallel code modifications
- Global agents: `~/.claude/agents/` | Project agents: `.claude/agents/`

## Context Hygiene
- After compaction: ALWAYS re-read active files before editing
- Use subagents for ALL investigation/research/discovery
- When something goes wrong 2+ times: stop, re-think, don't keep retrying

## Workflow
- Plan first → `tasks/todo.md` with checkable items
- Completed items → `tasks/done.md` IMMEDIATELY with date and summary
- After code changes → auto-invoke /qa
- After corrections → update `tasks/lessons.md`

## Environment
- Full environment details (paths, commands) → always loaded from `~/.claude/rules/environment.md`
- Language-specific rules → auto-loaded from `~/.claude/rules/` when touching matching files

## Preferences
- Language: English by default — override per-project if needed
- Concise communication — no filler, lead with the answer

## Tools & MCPs
- MCPs installed: GitHub, Slack, Stripe, Supabase, Firebase, Linear, Playwright, GitLab, Asana, Context7, Greptile, Serena, Laravel
- This is a STARTING POINT — search for and install new MCPs when needed
- Use MCPs proactively — don't build custom servers when one exists
