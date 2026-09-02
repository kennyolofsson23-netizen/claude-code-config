---
name: Dashboard Command Center Plan
description: 7-session plan to transform dashboard into traffic intelligence + remote execution command center. S1-S6 complete, S8 next.
type: project
---

Dashboard Command Center — 7 sessions, each independently valuable.

**S1: Traffic Intelligence — COMPLETE (2026-03-21)**
- `gsc.ts` — GSC OAuth2 client (org policy blocked service account keys, used refresh token instead)
- `seo-scorer.ts` — Deep HTML-based SEO scoring (12 weighted checks, no Lighthouse dependency)
- `geo-checker.ts` — Skill-based GEO scoring (citability, E-E-A-T, schema quality, crawler tiers)
- All wired into `traffic.snapshot` and `traffic.snapshotAll`
- 5 projects tracked: usetools.dev Hub, Travmaskinen, SEO Scorer, Dream Interpreter, Photo Transformer
- GSC OAuth2 creds in `.env.keys` (refresh token from kenny.olofsson23@gmail.com)
- Branch: merged to main

**S2: Score-to-Todo Engine — COMPLETE (2026-03-21)**
- `todo-generator.ts` — 12 rules (SEO critical/per-issue, GEO json-ld/llms.txt/crawlers/citability/sitemap, GSC low-CTR)
- `ProjectTask` Prisma model with status, priority, source, sourceRef dedup
- Auto-wired into `traffic.snapshot` and `traffic.snapshotAll`
- Deduplication (sourceRef + projectId) and auto-resolution (fixed issues auto-complete)
- 5 tRPC routes: task.list, task.create, task.update, task.bulkDismiss, task.topPriority
- Dashboard: Backlog tab on project pages + Top Tasks widget on home
- Branch: merged to main

**S7: Retroactive Test Suite — COMPLETE (2026-03-21)**
- 269 tests total: 244 vitest unit/integration + 25 Playwright E2E
- seo-scorer: 12 check functions (60 tests)
- geo-checker: 6 GEO checks (70 tests)
- todo-generator: 3 rule generators + dedup + auto-resolve (40 tests)
- gsc: URL derivation + date range + page filter helpers (15 tests)
- tRPC task routes: 5 routes with mocked Prisma (59 tests)
- Dashboard E2E: backlog page, top tasks widget, full user journeys (25 tests)
- Test infra: vitest for agent-runner, Playwright for dashboard
- Branch: `feat/s7-test-suite`

**S3: Project Import + Backlogs + Decision Cleanup — COMPLETE**
- Decision backend: listAll, bulkResolve, cleanup routes
- Project backend: update, delete routes + Import project UI
- Inbox: Cleanup Stale button, Resolved tab, bulk dismiss
- Backlog: source/priority filters, description in quick-add
- 272 unit + 49 E2E tests passing

**S4: Web Terminal + Cloudflare Tunnel + Security — COMPLETE**
- xterm.js terminal panel, WebSocket handler (node-pty), API key auth
- Cloudflare Tunnel (dash.usetools.dev + agent.usetools.dev) + Access (email OTP)
- Branch: `feat/s4-terminal-tunnel-security`

**S5: Light Pipeline + Affiliates + Service Page — COMPLETE (2026-03-21)**
- `LightPipeline` class — 6 stages, $15 budget, max 3 review iterations
- `pipelineType` field on DevPipeline, pipeline selector on dashboard (Light/Full toggle)
- Synthesizer `[PIPELINE_REC]` output + swarm parsing
- Build-as-a-Service page at `/build-service` with Cal.com booking
- Affiliates: SurferSEO + Mangools on seo.usetools.dev
- 305 unit/integration tests passing, 0 TS errors
- kenny-corp repo created on GitHub (private), PR #1 merged
- Branch: `feat/s5-light-pipeline-affiliates-service`

**S6: Marketing Content Engine — COMPLETE (2026-03-22)**
- 4 new agents: content-writer, image-generator, carousel-generator, voiceover-generator
- 5-round campaign flow: monitor → content → image+carousel → voiceover → social posting
- Content optimizer: SEO/AEO/GEO pre-publish quality gates
- Content scorer: composite scoring + self-improving brand voice feedback loop
- Cloudflare R2: `usetools-media` bucket, `media.usetools.dev` custom domain
- tRPC routes: contentScore + brandVoice routers
- 30 vitest tests, E2E verified: 39 drafts across 7 channels
- Dropped Vercel + Railway (tunnel + PostgreSQL sufficient)
- Branch: merged to main (17 commits)

**How to apply:** S8 (Travmaskinen content engine) is next. Pipeline speed optimization (Phases 2-6) after.
