---
name: Content vs Marketing Separation
description: Content and marketing are separate workflows — different data models, dashboard sections, nav items, agent types
type: feedback
---

Content and marketing must never be mixed in the same data model or UI.

**Why:** Kenny explicitly requested separation. Marketing = social distribution (Twitter, Reddit, Meta Ads). Content = editorial articles (race previews, analysis, deep-dives). Different lifecycles, different quality metrics, different agents.

**How to apply:**
- Marketing: Campaign + CampaignDraft models, /marketing page, MarketingSwarm agent
- Content: PublishedContent model, /content page, content-agent + trav-content-writer
- Never add article/editorial fields to CampaignDraft or campaign fields to PublishedContent
