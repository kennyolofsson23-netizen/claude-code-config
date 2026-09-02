---
name: S6 Marketing Content Engine
description: S6 implementation — 4 new agents, R2 media, content scoring, feedback loop, 5-round campaign flow
type: project
---

S6 complete on `main` (17 commits). Full marketing content engine with self-improving feedback loop.

**Why:** Automate multi-channel marketing content creation for usetools.dev tools with quality gates and performance tracking.

**How to apply:**
- 5-round campaign flow: monitor → content writer → image+carousel (parallel) → voiceover → social posting (parallel)
- Content optimizer: SEO/AEO/GEO pre-publish quality gates (`packages/shared/src/content-optimizer.ts`)
- Content scorer: composite scoring with cold-start normalization (`packages/shared/src/content-scorer.ts`)
- Feedback loop: top/bottom 20% patterns auto-update BrandVoice per project (`extractPatterns` → `updateBrandVoiceFromScores`)
- R2 media: `media.usetools.dev` bucket, S3-compatible API via `@aws-sdk/client-s3`
- tRPC routes: `contentScore.*` + `brandVoice.*`
- Agent `.md` files: `image-generator.md`, `carousel-generator.md`, `voiceover-generator.md` in `~/.claude/agents/`
- E2E verified: 39 drafts across 7 channels (BLOG, CAROUSEL, VOICEOVER, TWITTER, REDDIT, META_ADS, DIRECTORY)

**Bugs fixed during E2E:**
- `AgentSession.brainstormId` FK — marketing swarm must pass `project.brainstormId` to spawner, not `project.id`
- `captureOutput: false` on sequential rounds — voiceover output was silently discarded (round 1 monitor is the only round that should skip capture)
- `AGENT_DEFAULT_CHANNEL` — new agents mapped to TWITTER instead of BLOG/CAROUSEL/VOICEOVER
- `ParsedDraft.channel` type — missing new channel values
- Voiceover model — haiku too weak for structured output, upgraded to sonnet
