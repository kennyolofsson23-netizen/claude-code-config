---
name: project_content_markdown_first
description: Content pipeline refactor — markdown-first writer + Haiku extraction replaces fragile JSON output
type: project
---

Content pipeline R3 (WRITE) is being refactored to eliminate JSON-output from the writer agent.

**Decision:** Let the writer output natural markdown, then use a cheap Haiku extraction step (R3b: EXTRACT) to produce structured tips[] and game_summary as JSON. Eliminates all regex fallback code.

**Why:** Sonnet fights JSON-inside-JSON output. The writer frequently produced malformed JSON, triggering regex extraction fallbacks that produced lower-quality tips/game_summary. Tips and game_summary also skipped all optimization (SEO/GEO/quality judge only process the article body).

**How to apply:**
- Spec: `docs/superpowers/specs/2026-03-24-content-writer-markdown-extraction-design.md`
- Plan: `docs/superpowers/plans/2026-03-24-markdown-first-extraction.md`
- Status: COMPLETE — merged to main 2026-03-24. 4 commits, 148 tests passing.
- New agent: `trav-content-extractor` (Haiku, tools: [], ~$0.05-0.10 per run)
- Pipeline flow: WRITE → EXTRACT → OPTIMIZE_SEO → OPTIMIZE_GEO → SCORE → PUBLISH

Also fixed in same session (V85 repo, pushed to prod):
- Game summary now persisted to DB (was Redis-only with 20min TTL → disappeared)
- LegExpertCommentary in deep analysis now correctly resets per-leg (was showing leg 1 for all legs)
- Deep analysis expert commentary hidden until kenny-corp publishes content
