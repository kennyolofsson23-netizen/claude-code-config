# Project Alignment — Ready-to-Paste Prompt

Copy everything below the line, open a fresh terminal, cd into the project, start Claude Code, and paste.

---

I just completed a massive overhaul of my entire Claude Code global setup. This is the most comprehensive Claude Code configuration ever built — 39 skills, 10 plugins, 8 agents, 8 commands, 13 hooks, 6 rules, all self-documenting via inventory.sh.

Now this project needs to be brought up to speed with this new reality.

## Phase 1: Understand the new arsenal
1. Read ~/.claude/CLAUDE.md (global instructions — 76 lines, every line matters)
2. The session-start hook will inject the full tool inventory — READ IT
3. Read ~/.claude/projects/C--Users-Kenny--claude/memory/MEMORY.md for architecture overview
4. Read the project's memory MEMORY.md for project-specific context

## Phase 2: Audit current state
5. Read this project's CLAUDE.md — compare against the global setup
6. Read tasks/lessons.md — what patterns have we been repeating?
7. Read tasks/todo.md — what's pending?
8. Check tasks/patterns.log — any task types appearing 2+ times that need skills/agents?
9. Run `git log --oneline -20` — what's the recent trajectory?
10. Run test coverage: what's the current coverage % for backend AND frontend?

## Phase 3: Gap analysis
Compare project setup against the global arsenal and identify:
- Which global skills/plugins/commands are relevant but not referenced in the project CLAUDE.md?
- What project-specific rules are needed? (API conventions, domain language, UI rules)
- What E2E test flows are missing? (ALL critical user paths)
- What's the gap between current test coverage and 100%?
- Is the deploy pipeline ready for autonomous deployment? What's missing?

## Phase 4: Build the plan
Create a comprehensive tasks/todo.md with:
- [ ] Project CLAUDE.md rewrite — adapted to global setup, project-specific routing
- [ ] Test coverage roadmap to 100% — list every untested module with priority
- [ ] E2E test suite — Playwright tests for every critical user flow
- [ ] Security audit — run security-threat-model skill on the full codebase
- [ ] Design review — run design-review skill on the frontend
- [ ] Performance audit — Core Web Vitals, bundle size
- [ ] CI/CD pipeline — what needs to happen for autonomous deploys?

## Context
- I'm a solo founder, Claude is my engineering team
- Enterprise quality, 100% test coverage, zero shortcuts
- TDD always — test before implement
- This project is live with real users — quality matters

## Rules
- Plan mode first — this is a non-trivial task
- Don't start implementing yet — I want to review and approve the plan
- Be brutally honest about the gaps — I want the full picture, not sugar-coated
- Use the installed tools: run /qa-setup first to verify everything works in this project context
