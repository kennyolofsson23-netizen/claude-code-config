---
name: feedback_seo_geo_factory
description: SEO/GEO must be baked into pipeline scaffolding and build — every tool ships with perfect scores from day one, no manual fixing
type: feedback
---

Every tool is a factory product — SEO/GEO infrastructure must be built-in, not bolted on after deploy.

**Why:** Spent an entire session manually fixing SEO/GEO across 6 deployed tools (headings, JSON-LD, meta tags, llms.txt, robots.txt, canonical URLs, og:images, permissions-policy). This should never happen again.

**How to apply:**
- Pipeline SCAFFOLD stage includes full SEO/GEO boilerplate checklist
- Pipeline BUILD_FEATURES Phase 4 gate verifies all SEO/GEO infrastructure
- Pipeline WRITE_CONTENT stage verifies first-paragraph pattern and FAQ content
- Pipeline DEPLOY stage smoke-tests SEO/GEO on the live URL (H1, heading hierarchy, JSON-LD, sitemap, robots.txt, llms.txt)
- Growth reviewer catches any remaining gaps as BLOCKERs before ship
- Common gotchas: H3 in footer (use H2), closing tag mismatch, client-only H1, favicon must be RGBA PNG for Turbopack
