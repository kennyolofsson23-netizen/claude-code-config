---
name: Content Hub Architecture
description: Kenny-corp as centralized CMS — content vs marketing separation, V85 data/ingest APIs, trav-content-writer agent
type: project
---

Kenny-corp content hub: Chunks 0-2 complete + tips migration (2026-03-22). 11-chunk plan ready for overnight execution.

**Why:** Centralize ALL content generation in kenny-corp (Claude subscription) instead of V85's Groq/Cerebras. Better quality, intelligence-enriched, SEO/GEO scoring, auto-publish.

**How to apply:**
- Content = PublishedContent model + /content dashboard. Marketing = Campaign/CampaignDraft + /marketing. Never mix.
- AEO removed — GEO covers it. Only seoScore + geoScore on models.
- V85 endpoints: /content-data/race-bundle (legs, predictions, equipment, signals), /articles/ingest, /tips/ingest, /tips/game-summary/ingest
- V85 tip_generation_loop DISABLED — kenny-corp generates all tips centrally
- V85 returns null if no kenny-corp content (no fallback text). Frontend shows "publiceras 36 timmar fore spelstart"
- trav-content-writer agent generates articles + per-leg tips + game summaries
- content-agent.ts: fetchRaceBundle(), publishArticle(), publishTip(), publishGameSummary(), fetchEvaluationBundle(), fetchEntityBundle()
- Auto-publish: qualityScore >= 70 pushes to V85 automatically. Below 70 → REVIEW for Kenny
- Content loop: 36h window, ATG calendar for today+tomorrow, multiple games per day
- Remaining plan: V85/docs/superpowers/plans/2026-03-22-content-hub-remaining.md (Chunks 1-11)
