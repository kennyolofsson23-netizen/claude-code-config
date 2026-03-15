---
name: seo-content
description: |
  SEO content strategy, writing, and auditing. Plans topic clusters, writes search-optimized articles, and audits existing pages. Use for blog posts, landing page copy, content calendars, keyword research, SEO audits, and content strategy planning. Use when the user says "SEO", "content plan", "write blog post", "optimize for search", "keyword research", "audit page", "content calendar", "write an article", "content strategy", or any content marketing task.
argument-hint: "topic, keyword, or URL to audit"
---

# SEO Content — Strategy, Writing & Auditing

SEO content planning, writing, and auditing methodology. Based on [wshobson/agents](https://github.com/wshobson/agents) SEO plugins, generalized for any project.

## When to Use

- Planning content strategy and topic clusters
- Writing blog posts, guides, or landing page copy optimized for search
- Auditing existing pages for SEO quality
- Building content calendars
- Creating news articles from scraped content (via `/firecrawl`)

## When NOT to Use

- Technical frontend/backend development (use other skills)
- Internal documentation not meant for search indexing
- Paid ad copy (different optimization goals)

---

## Part 1: Content Planning

### Topic Cluster Framework

Organize content around pillar pages and supporting articles.

**Pillar types:**
- **Commercial intent** — product/service pages, comparison pages, "best X" guides
- **Informational intent** — how-to guides, explainers, educational content
- **Engagement intent** — news, interviews, opinion pieces, community content
- **Informational-to-commercial** — beginner guides, getting started content that leads to product

**For each pillar, define:**
- Pillar page (broad keyword, high search volume)
- 5-10 supporting articles (long-tail keywords linking back to pillar)
- FAQ content (question-based keywords)

### Content Calendar Framework

```
Plan content around your project's natural cadence:
- Recurring events / release cycles → previews + recaps
- Evergreen guides → steady publishing schedule
- News / trends → reactive, publish quickly
- Deep-dives → weekly or biweekly, analytical pieces
```

### Planning Output Format

```markdown
## Content Plan — [Month YYYY]

### Week N (dates)
| Day | Topic | Target Keyword | Intent | Word Count | Internal Links |
|-----|-------|----------------|--------|------------|----------------|
| Mon | ... | ... | Informational | 800 | /page-a, /page-b |

### Topic Cluster: [Pillar Name]
- Pillar page: [URL + title]
- Supporting: [list of articles linking to pillar]
- FAQ: [common questions to answer]
```

---

## Part 2: Content Writing

### Voice & Style

Define these per project:
- **Language**: Primary language for the audience
- **Tone**: Match the brand (authoritative, friendly, technical, casual)
- **NOT**: Generic AI copy, clickbait, sensationalist headlines
- **Domain terms**: Use correct terminology for the niche

### Article Structures

**News Article (500-800 words):**
```
Headline: [Factual, keyword-rich, no clickbait]
Ingress: [2-3 sentences summarizing the key takeaway]

Body:
- What happened / what's new
- Expert context (why it matters)
- Data points backing the story
- Quotes or source attribution
- Impact / what to expect next

Fact Box: [Key stats relevant to the topic]
Related: [Links to related pages on your site]
```

**Guide / Evergreen (1000-2000 words):**
```
Headline: [How-to or definitive guide format]
Ingress: [Value prop + who this is for]

Sections (H2):
- Clear, scannable subheadings
- Short paragraphs (2-3 sentences)
- Bullet points for lists
- Data tables where relevant
- Screenshots / examples

FAQ section (H2):
- 3-5 common questions with concise answers
- Schema markup friendly (question/answer pairs)

CTA: [Clear next action for the reader]
```

**Review / Comparison (800-1200 words):**
```
Headline: [Product/service + year, comparison angle]
Ingress: [Quick verdict + who it's for]

Per item reviewed:
- Summary + key differentiator
- Pros / Cons
- Data or evidence backing claims

Comparison table
Winner / recommendation
```

### Keyword Integration

- Primary keyword in: title, H1, first paragraph, meta description, URL slug
- Secondary keywords: naturally in H2s and body
- Density: 0.5-1.5% (never forced)
- Semantic variations: mix related phrases naturally
- Internal links: always link to relevant pages on your own site

### Meta Tags

```
Title: [Primary keyword] — [Brand] (max 60 chars)
Description: [Compelling summary with keyword, 150-160 chars]
OG Title: [Same as title or slightly different angle]
OG Description: [Social-optimized version]
```

### E-E-A-T Signals

Build trust with Google through Experience, Expertise, Authoritativeness, and Trustworthiness:

- **Experience**: Show firsthand experience with the topic (original data, case studies, real usage)
- **Expertise**: Demonstrate deep knowledge (proprietary analysis, detailed methodology)
- **Authority**: Build reputation (backlinks, citations, industry recognition, data transparency)
- **Trust**: Be transparent (show methodology, acknowledge limitations, cite sources, display results honestly)

**How to signal E-E-A-T in content:**
- Reference your own data or analysis, not just third-party sources
- Show track record and be transparent about accuracy/limitations
- Link to primary sources and data backing claims
- Include author expertise where relevant
- Update content regularly with fresh data

---

## Part 3: Content Auditing

### Audit Checklist

| Category | Check | Target |
|----------|-------|--------|
| **Content Depth** | Covers topic comprehensively? | 8+/10 |
| **E-E-A-T** | Data, expertise, trust signals present? | 7+/10 |
| **Readability** | Short paragraphs, scannable, clear? | Grade 8-10 |
| **Keywords** | Primary in title/H1/intro? Natural density? | 0.5-1.5% |
| **Structure** | H2/H3 hierarchy? Logical flow? | Clean hierarchy |
| **Internal Links** | Links to relevant pages on site? | 3+ per article |
| **Meta** | Title <60 chars? Description 150-160? | Both optimized |
| **Language Quality** | Natural, native-level writing? | Native quality |
| **CTA** | Clear next action for reader? | Present |
| **Uniqueness** | Original analysis, not just rewritten content? | Original value |

### Audit Output Format

```markdown
# Content Audit — [Page Title]

## Score: X/10

| Category | Score | Issues | Recommendations |
|----------|-------|--------|-----------------|
| Content Depth | X/10 | ... | ... |
| E-E-A-T | X/10 | ... | ... |
| ... | ... | ... | ... |

## Priority Fixes
1. [Highest impact fix]
2. [Second priority]
3. [Third priority]

## Missing Topics
- [Subtopic that should be covered]

## Keyword Opportunities
- [Keywords the page should target but doesn't]
```

---

## SEO Tips by Market

- **Small-language markets**: Long-tail keywords matter more; competition is lower but so is volume
- **Mobile-first**: Most users browse on phones — optimize for mobile UX
- **Local search**: Use country-specific search engines and language preferences
- **Niche domains**: Low competition keywords often have high conversion intent
- **Seasonal content**: Plan around your industry's calendar (events, launches, cycles)
