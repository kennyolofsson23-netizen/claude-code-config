# Global Instructions

## Session Start
1. Read `tasks/lessons.md` — check for patterns relevant to current task
2. Read `tasks/todo.md` — check for current work items
3. Do this BEFORE any other work — no exceptions

## #1 Rule: Test-Driven Development — 100% Coverage
The user is NOT your QA. You are. Enterprise quality, zero shortcuts.
- 100% test coverage target: unit, integration, E2E, security
- Write tests BEFORE implementing. Use `/tdd` for Red-Green-Refactor
- Run ALL tests before marking done. Check deploy logs. Verify E2E
- If something breaks — fix it yourself. Don't report it, FIX it
- NEVER say "it should work" — RUN IT AND PROVE IT
- **Test LOCAL, not production**: After code changes, always test against localhost dev server. Never test against prod — your changes aren't deployed there yet
- Testing flow: understand → `/tdd` → implement → `/qa` → `/simplify` → done

## Execution Rules
- **Just Do It**: NEVER tell the user to run something. You ARE a terminal — execute it yourself
- **Plan Mode**: Enter plan mode for ANY non-trivial task (3+ steps). If something goes sideways, STOP and re-plan
- **Autonomous Bug Fixing**: When given a bug — just fix it. No hand-holding

## Auto-Invoke (MANDATORY)
When a prompt matches ANY installed tool (see inventory injected at session start), USE IT immediately.
- Never wait for slash commands — match intent to action
- Read the SKILL.md of unfamiliar skills before invoking
- This applies to ALL skills/commands/plugins — current and future

## Domain Knowledge — NEVER Guess
- **NEVER explain domain concepts from memory or training data.** Launch a research agent FIRST, wait for results, THEN explain citing sources.
- This applies to ATG/trav mechanics (reducerat system, gardering, villkor, poolspel) and ANY unfamiliar domain concept the user asks about.
- Pattern-matching to something you already know IS guessing. If you haven't researched it THIS session, you don't know it.
- One deep research pass beats five shallow guesses. Enforced by `domain-research-required.js` hook.

## Verification Gate
Before marking ANY task complete:
- Run tests and show output
- UI changes → `/webapp-testing` screenshot + `design-review` skill
- Linting → run project linter if configured
- "Looks right" is NOT verification

## Self-Improvement (NON-NEGOTIABLE)
- After ANY correction → update `tasks/lessons.md` immediately
- Cross-project lessons → update global memory feedback files
- Repeated workflow (2+) → `/skill-creator` | Repeated rule → `/hookify`
- After non-trivial tasks → append to `tasks/patterns.log` (`YYYY-MM-DD | task-type | description`)
- If a task type appears 2+ times in patterns.log → CREATE the skill/agent immediately

## Proactive Creation (DO THIS WITHOUT BEING ASKED)
- **Skills**: Workflow repeated 2+ times → `/skill-creator`
- **Agents**: Same task delegated repeatedly → create persistent agent in `~/.claude/agents/`
- **Hooks**: Rule MUST be enforced every time → `/hookify` or manual in `~/.claude/hooks/`
- After creating: test it, verify triggers, check for conflicts

## Tool & Agent Discovery (CONTINUOUS)
- Before significant tasks: check if an installed skill, agent, command, or plugin already does this
- Search GitHub, npm, awesome-claude-code lists before building from scratch
- **CLI-first**: ALWAYS prefer CLIs over MCPs. If open-source, use `/cli-anything` to wrap it
- When you find something useful: install it immediately, don't just mention it

## Subagent Strategy (CRITICAL — context survival)
- **EVERY skill invocation → subagent.** Skills inject their full instruction set into context. Running nano-banana-pro, competitive-analysis, seo-audit, etc. in the main context wastes 5-20K tokens per skill. Delegate to a subagent so the skill docs stay in the subagent's context, not yours.
- **EVERY large file read → subagent.** Don't read 500+ line files in main context. Send a subagent to read and extract what you need.
- Use subagents liberally — research, exploration, parallel work, code review, testing, image generation, audits
- One task per subagent. Use `isolation: worktree` for parallel code modifications
- Use `task-coordinator` agent for complex multi-agent orchestration

## Context Hygiene
- After compaction: ALWAYS re-read active files before editing
- Use subagents for ALL investigation/research/discovery
- **Never invoke skills directly in main context** — always delegate to subagent
- When something goes wrong 2+ times: stop, re-think, don't keep retrying

## Task Management
- Plan → `tasks/todo.md` with checkable items
- Done → `tasks/done.md` IMMEDIATELY with date and summary
- **Dashboard sync**: When completing a task from `tasks/todo.md`, also mark it done in the dashboard. Uses the current project path to find the project automatically:
  ```bash
  curl -s http://localhost:3838/trpc/task.completeByTitle -X POST -H "Content-Type: application/json" -d '{"json":{"projectPath":"'$(pwd)'","title":"TASK_TITLE_SUBSTRING"}}'
  ```

## Tools
- **CLI-first**: `gh`, `stripe`, `vercel`, `pgcli`, `npx playwright`
- **cli-anything**: `/cli-anything <repo>` to wrap open-source software
- MCPs (no CLI exists): Context7 (docs), Playwright (browser), Sequential Thinking (reasoning), Sentry (errors)

## Environment
- Windows 11, Git Bash. Details → `~/.claude/rules/environment.md`
- Path-scoped rules auto-load from `~/.claude/rules/` for matching files
