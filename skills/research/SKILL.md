---
name: research
description: |
  Structured deep research and investigation. ML papers, competitor analysis, market research, domain intelligence, data source discovery. Uses firecrawl for web search/scraping. Outputs actionable findings with sources and confidence levels.

  Use when the user says "research", "investigate", "deep dive", "analyze the market", "find papers on", "competitor analysis", or needs multi-source synthesis on any topic.
context: fork
argument-hint: "research topic or question"
---

# Research — Structured Investigation

Systematic research methodology for deep investigations. Provides structured workflows for ML research, competitor analysis, domain intelligence, market research, and data source discovery. Uses `/firecrawl` for web search and scraping.

> **Note:** If a project-specific research config exists at `.claude/skills/research/project-context.md`, load it for project context. Individual projects may define domain-specific research briefs, search queries, and competitor lists that extend these generic templates.

## When to Use

- Investigating ML techniques (papers, Kaggle solutions, new algorithms)
- Analyzing competitors in your market
- Researching domain changes (regulations, industry trends)
- Finding new data sources (APIs, databases, public datasets)
- Market research (market size, user demographics, pricing)
- Any multi-source investigation that needs synthesis

## When NOT to Use

- Simple factual lookups (just use firecrawl search directly)
- Code-level debugging or implementation (use other tools)
- News scraping for content publishing (use `/firecrawl` + `/seo-content`)

---

## Research Methodology

### Phase 1: Scope

Define the research question clearly before searching.

```markdown
## Research Brief
- **Question**: [Specific question to answer]
- **Why it matters**: [Impact on the project — model improvement, revenue, UX, strategy]
- **Depth**: Quick (15 min) | Standard (30 min) | Deep (1+ hr)
- **Output**: [What deliverable — findings doc, code prototype, decision recommendation]
- **Known context**: [What we already know — avoid re-searching]
```

### Phase 2: Search Strategy

Plan searches before executing. Different research types need different strategies.

**Academic / ML Research:**
```bash
# arXiv papers
firecrawl search "[topic] machine learning site:arxiv.org" --limit 10 -o .firecrawl/research/arxiv-results.json --json

# Google Scholar (via web search)
firecrawl search "[technique] prediction ranking 2024 2025" --limit 10 -o .firecrawl/research/scholar-results.json --json

# Papers with Code
firecrawl scrape "https://paperswithcode.com/task/[task-name]" -o .firecrawl/research/pwc.md

# Kaggle
firecrawl search "kaggle [domain] prediction winning solution" --limit 10 -o .firecrawl/research/kaggle-results.json --json
```

**Competitor Research:**
```bash
# Map competitor sites
firecrawl map https://competitor-a.com --search "[feature]" --limit 50 -o .firecrawl/research/competitor-a-urls.txt
firecrawl map https://competitor-b.com --search "[feature]" --limit 50 -o .firecrawl/research/competitor-b-urls.txt

# Scrape key pages
firecrawl scrape "https://competitor.com/pricing" --only-main-content -o .firecrawl/research/competitor-pricing.md

# Search for competitors
firecrawl search "[product category] [market/country]" --limit 20 -o .firecrawl/research/competitors.json --json
```

**Domain Research:**
```bash
# Industry news and regulation changes
firecrawl search "[industry] regulations changes 2025 2026" --limit 10 -o .firecrawl/research/regulations.json --json

# Industry trends
firecrawl search "[industry] statistics trends" --limit 10 -o .firecrawl/research/industry.json --json

# International parallels
firecrawl search "[similar product/market] international comparison" --limit 10 -o .firecrawl/research/international.json --json
```

**Market Research:**
```bash
# Market size
firecrawl search "[market] market size revenue 2025" --limit 10 -o .firecrawl/research/market.json --json

# User behavior
firecrawl search "[product category] user demographics behavior" --limit 10 -o .firecrawl/research/users.json --json
```

### Phase 3: Gather & Read

Execute searches, then read and extract key findings. Always use `.firecrawl/research/` for organization.

```bash
# Create research directory for this investigation
mkdir -p .firecrawl/research/[topic-slug]

# Search → identify promising URLs → scrape the best ones
firecrawl search "query" --limit 10 -o .firecrawl/research/[topic]/search.json --json

# Read search results, pick top 3-5 URLs
# Scrape each in parallel
firecrawl scrape "https://url1" --only-main-content -o .firecrawl/research/[topic]/source1.md &
firecrawl scrape "https://url2" --only-main-content -o .firecrawl/research/[topic]/source2.md &
firecrawl scrape "https://url3" --only-main-content -o .firecrawl/research/[topic]/source3.md &
wait
```

**Reading large scraped files:**
```bash
# Never read entire files — use targeted extraction
wc -l .firecrawl/research/[topic]/source1.md
head -50 .firecrawl/research/[topic]/source1.md
grep -n "keyword" .firecrawl/research/[topic]/source1.md
grep -A 10 "## Relevant Section" .firecrawl/research/[topic]/source1.md
```

### Phase 4: Triangulate

Cross-verify findings across sources. Don't trust a single source.

- **Consensus**: Do 2+ sources agree? -> High confidence finding
- **Contradiction**: Sources disagree? -> Note the disagreement, investigate further
- **Single source**: Only one source? -> Flag as unverified, lower confidence
- **Recency**: Prefer 2024-2026 sources over older material
- **Credibility**: Academic papers > industry blogs > forum posts > AI-generated content

### Phase 5: Synthesize & Report

Produce actionable findings, not literature summaries. Every finding should answer: "So what? What should we do differently?"

---

## Output Format

Save findings to `tasks/research_findings.md` (append, don't overwrite).

```markdown
## [Research Topic] — [Date]

### Question
[What we investigated]

### Key Findings

**Finding 1: [Actionable title]**
- Evidence: [What sources say, with URLs]
- Confidence: HIGH/MEDIUM/LOW
- Action: [Specific implementation step or decision]

**Finding 2: [Actionable title]**
- Evidence: [...]
- Confidence: [...]
- Action: [...]

### Contradictions / Open Questions
- [Unresolved disagreements between sources]
- [Things we couldn't verify]

### Sources
1. [Title] — [URL] — [Credibility: Academic/Industry/Blog/Forum]
2. [...]

### Recommended Next Steps
1. [Most impactful action]
2. [Second priority]
3. [Third priority]
```

---

## Research Templates

### ML Research

```markdown
## Research Brief
- Question: Can [technique] improve [model metric] beyond [current baseline]?
- Known context: Current model is [type], [N] features, [metric] = [value]
- Search targets:
  1. arXiv papers on [technique] for ranking/prediction
  2. Kaggle competitions using [technique]
  3. Blog posts with implementation details
  4. GitHub repos with working code
- Output: Findings + prototype feasibility assessment
```

**Key searches for ML research:**
- `"learning to rank" [domain] prediction` — ranking models
- `"isotonic regression" vs "platt scaling" calibration` — calibration methods
- `XGBoost [technique] 2024 2025` — latest improvements
- `"feature engineering" tabular prediction competition` — Kaggle patterns
- `[domain] prediction deep learning transformer` — neural approaches
- `"model combination" probability ensemble` — ensemble/blending research

### Competitor Analysis

```markdown
## Research Brief
- Question: What do competitors in [market] offer vs our product?
- Search targets:
  1. All sites ranking for [primary keyword] in [target market]
  2. Their pricing, features, accuracy claims
  3. Their content strategy (frequency, format, depth)
  4. Their social media presence
- Output: Competitive landscape matrix + feature gaps
```

**Competitor analysis framework:**

| Dimension | What to Find |
|-----------|-------------|
| **Product** | Free vs paid features, unique capabilities |
| **Pricing** | Monthly/annual, tiers, free tier scope |
| **Content** | Article frequency, depth, expert profiles |
| **Data** | What analytics/stats do they show? |
| **Technology** | Do they claim AI/ML? What kind? |
| **UX** | Mobile experience, speed, design quality |
| **Trust** | Track record claims, transparency, social proof |
| **SEO** | What keywords do they rank for? Content volume |

### Market Research

```markdown
## Research Brief
- Question: What is the size and shape of the [market] market?
- Search targets:
  1. Market size reports and estimates
  2. User demographics and behavior studies
  3. Pricing benchmarks across competitors
  4. Growth trends and forecasts
- Output: Market overview + opportunity assessment
```

### Data Source Discovery

```markdown
## Research Brief
- Question: What new data sources could improve [product/model]?
- Search targets:
  1. Public APIs relevant to the domain
  2. Open datasets (government, academic, community)
  3. Commercial data providers and pricing
  4. Alternative data (social media, satellite, IoT)
  5. International equivalents of local data sources
- Output: Data source inventory with access method, cost, and expected value
```

---

## Best Practices

1. **Start narrow, widen if needed** — don't search for everything at once
2. **Time-box research** — set a depth level and stick to it
3. **Bias toward action** — every finding should suggest a concrete next step
4. **Don't re-research** — check `tasks/research_findings.md` first for prior work
5. **Credit budget** — firecrawl costs credits; plan searches, don't spam
6. **Localize searches** — use `--country [code]` for market/domain research
7. **Parallel scraping** — use `&` and `wait` to scrape multiple URLs simultaneously
8. **Archive results** — keep scraped content in `.firecrawl/research/` for future reference
