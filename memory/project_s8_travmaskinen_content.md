---
name: project_s8_travmaskinen_content
description: S8 Travmaskinen Content Engine — scraping, article generation, social distribution, evaluation fix, feedback loop
type: project
---

S8 Content Engine for Travmaskinen (C:\Users\Kenny\V85\) — spec approved 2026-03-22.

**Why:** Transform Travmaskinen from a prediction tool into a full content platform. Current tip text sounds "super AI" — replace with editorial-quality content through a dashboard workflow.

**Scope (8 sessions planned):**
1. Data layer + scraping (30+ sources: news, YouTube, forums, weather, odds)
2. Evaluation fix (prediction snapshots at T-30min, system builder lock at race start)
3. Content generators (race preview, post-race, entity deep-dive, news digest) + editorial workflow
4. Frontend (article pages, sitemap, cross-linking)
5. Social distribution (X via agent-twitter-client, Facebook, Instagram)
6. YouTube Shorts (ElevenLabs TTS + Remotion)
7. Feedback loop (Plausible → strategy weights)
8. Integration tests + E2E + polish

**Key decisions:**
- Unified architecture: shared content_signal table → multiple generators
- Extend existing FastAPI backend (new async loops, not separate service)
- All loops opt-in via env vars (ENABLE_NEWS_SCRAPER etc.)
- X posting via agent-twitter-client (cookie-based, no $100/mo API)
- Tiered publishing: race previews/post-race auto-publish, entity/news queue for review
- Tips page falls back to GeneratedTip during transition, then serves from published articles
- NER via Groq extraction + rapidfuzz matching against cached entity names
- Brand voice refactor: kill AI-sounding auto-generated tips
- Evaluation snapshots at T-30min, evaluate against what users actually saw
- System builder disabled at race start (not before)

**Spec:** `V85/docs/superpowers/specs/2026-03-22-s8-content-engine-design.md`

**Session 1 plan:** `V85/docs/superpowers/plans/2026-03-22-s8-session1-data-layer-scraping.md` — written 2026-03-22, reviewed (10 findings fixed). 11 tasks, 13 new files, ~700 lines.

**Session 2:** COMPLETE (2026-03-22) — branch `feat/s8-session2-evaluation-fix`, 11 commits, 92 new tests, 3132 total passing.
- prediction_snapshot_loop (5min polling, T-30min freeze)
- Generation lock (precompute + tip gen skip snapshotted games)
- Evaluation rewrite (reads from snapshot, falls back to DB)
- System builder lock (HTTP 403 after race start)
- Tips page freeze (serves snapshot data when frozen)
- snapshot_available flag on ModelEvaluation + Alembic migration

**Session 3:** COMPLETE (2026-03-22) — branch `feat/s8-session3-content-generators`, 10 commits, 52 new tests, 3184 total passing.
- Brand voice system prompts (Swedish trav expert editorial voice, forbidden AI phrases)
- ContentGenerator base class (Groq→Cerebras fallback, slug generation, dedup)
- Quality scorer (0-100: word count, structure, attribution, data density, brand voice)
- 4 generators: race preview, post-race, entity deep-dive, news digest
- Content generator loop (trigger detection, auto-publish, stub body)
- Editorial API (list/get/publish/reject, admin-only, at /api/v1/articles)
- Plan: `V85/docs/superpowers/plans/2026-03-22-s8-session3-content-generators.md`

**Session 4:** COMPLETE (2026-03-22) — branch `feat/s8-session4-frontend-articles`, merged to main.
- Article index page (/artiklar), detail page with JSON-LD
- Tips page race preview integration
- Generator loop wired to ATG calendar + evaluations
- Public articles API with 13 unit tests
- Sitemap integration

**Session 5:** COMPLETE (2026-03-22) — branch `s8-session5-e2e-verification`, merged to main.
- Entity deep-dive + news digest trigger detection
- Plausible-based performance tracker loop
- E2E pipeline integration test
- 11 commits, 976 insertions

**Current state (2026-03-22):** Sessions 1-5 merged to main. All 3 content loops running locally (news scraper, content generator, performance tracker). Prediction snapshot has a type-mismatch bug fixed (str→date conversion). Session 6 next (production deploy).

**How to apply:** Start Session 6 — ATG Play scraper (Contentful CMS) + production deploy. Plan: `V85/docs/superpowers/plans/2026-03-22-s8-session6-atg-play-scraper.md`
