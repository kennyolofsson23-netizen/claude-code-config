---
name: project-alignment
description: Align any project with Kenny's global Claude Code setup. Audits test coverage, CI/CD, security, skills usage, and creates a prioritized quality roadmap. Use when opening a project for the first time, after a global setup change, or when the user says "align", "bring up to speed", "audit this project", "quality check", or "what's missing".
---

# Project Alignment — Global Setup Audit & Quality Roadmap

Bring any project up to speed with the global Claude Code arsenal. Produces a brutally honest gap analysis and prioritized action plan.

## Phase 1: Understand the Arsenal

1. Read `~/.claude/CLAUDE.md` — global instructions (every line matters)
2. The session-start hook injects the full tool inventory — READ IT
3. Read `~/.claude/projects/C--Users-Kenny--claude/memory/MEMORY.md` for architecture overview
4. Read the project's memory MEMORY.md for project-specific context

## Phase 2: Audit Current State

5. Read this project's CLAUDE.md — compare against global setup
6. Read `tasks/lessons.md` — what patterns have we been repeating?
7. Read `tasks/todo.md` — what's pending?
8. Check `tasks/patterns.log` — any task types appearing 2+ times that need skills/agents?
9. Run `git log --oneline -20` — what's the recent trajectory?
10. Run test coverage: backend AND frontend current %

## Phase 3: Gap Analysis

Compare project setup against the global arsenal and identify:

- **Skills/plugins/commands**: Which global tools are relevant but not referenced in the project CLAUDE.md?
- **Project-specific rules**: What conventions does this project need? (API patterns, domain language, UI rules)
- **E2E test flows**: What critical user paths are untested? (signup, payment, core features)
- **Test coverage gap**: Current % vs 100% — list every untested module with priority
- **Deploy pipeline**: Is autonomous deployment ready? What's missing?
- **Security**: Has a threat model been run? Are there unauthenticated endpoints?
- **Performance**: Core Web Vitals, bundle size, slow queries, cache hit rates

## Phase 4: Build the Plan

Create a comprehensive `tasks/todo.md` with checkable items:

- [ ] Project CLAUDE.md rewrite — adapted to global setup, project-specific routing
- [ ] Test coverage roadmap to 100% — every untested module with priority
- [ ] E2E test suite — Playwright tests for every critical user flow
- [ ] Security audit — run `security-threat-model` skill on the full codebase
- [ ] Design review — run `design-review` skill on the frontend
- [ ] Performance audit — Core Web Vitals, bundle size
- [ ] CI/CD pipeline — what needs to happen for autonomous deploys?

## Rules

- **Plan mode first** — this is always a non-trivial task
- **Don't implement yet** — present the plan for review and approval
- **Be brutally honest** about gaps — full picture, not sugar-coated
- **Run `/qa-setup` first** to verify everything works in this project context
- **100% test coverage target** — no exceptions, no lowering thresholds
- **TDD always** — test before implement

## Context

- Kenny is a solo founder, Claude is the engineering team
- Enterprise quality, zero shortcuts
- Every project is live with real users — quality matters
- Use the installed tools: check what skills/agents/plugins apply before building from scratch
