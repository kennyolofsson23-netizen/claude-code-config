---
name: content-to-social
description: Transform long-form content (blog posts, articles, newsletters, podcasts, videos) into platform-optimized social media posts
version: 1.0.0
author: Kenny (custom skill — no upstream repo found)
---

# Content-to-Social Transformer

Transform any long-form content into ready-to-publish social media posts for multiple platforms.

## Usage

```
/content-to-social <source>
```

`<source>` can be:
- A URL to a blog post, article, or page
- A file path to a markdown/text document
- Pasted text (if no URL/path, prompt for content)

## Workflow

### Step 1: Extract Core Content
1. Read/fetch the source content
2. Identify:
   - **Main thesis** — the single most important point
   - **Key insights** — 3-5 supporting points or takeaways
   - **Quotable lines** — punchy phrases that stand alone
   - **Data points** — stats, numbers, results
   - **Story hooks** — anecdotes, before/after, transformations

### Step 2: Generate Platform-Specific Posts

For each platform, generate **2-3 variations** with different angles:

#### Twitter/X (Thread + Standalone)
- **Thread (5-10 tweets)**: Hook tweet → key points → CTA
- **Standalone tweet**: Single high-impact tweet (< 280 chars)
- **Quote tweet format**: Pull a quotable line + brief commentary
- Style: conversational, punchy, use line breaks for readability
- Avoid: hashtag spam (0-2 max), corporate tone

#### LinkedIn
- **Long post** (1,200-1,500 chars): Hook line → story/insight → takeaway → question
- **Short post** (300-500 chars): Single insight with personal angle
- Style: professional but human, use line breaks every 1-2 sentences
- Start with a bold first line (it's the preview)
- End with a question or CTA to drive comments

#### Instagram Caption
- **Standard** (< 2,200 chars): Hook → value → CTA → hashtags
- **Carousel script**: 8-10 slides with title + body for each
- Include 20-30 relevant hashtags in a comment block (separated from main caption)

#### Facebook
- **Post** (300-500 chars): Conversational, question-driven
- **Long post** (1,000+ chars): Story format with personal angle
- Style: warm, community-oriented, encourage sharing

#### YouTube Community / Shorts Script
- **Community post**: Poll or discussion starter based on content
- **Shorts script** (< 60s): Hook (3s) → value (45s) → CTA (10s)

#### Newsletter Teaser
- **Email subject lines** (3 options): curiosity-driven, benefit-driven, urgency-driven
- **Preview snippet** (100-150 chars)
- **Teaser paragraph**: enough value to click through

### Step 3: Optimize

For each post:
1. **Hook score** — rate the opening line 1-10 for scroll-stopping power
2. **Readability** — ensure grade 6-8 reading level
3. **CTA clarity** — every post needs a clear next action
4. **Platform fit** — verify tone/length matches platform norms

### Step 4: Output

Present all posts in a clean, copy-pasteable format:
```
## Twitter/X
### Thread
1/7: [tweet text]
2/7: [tweet text]
...

### Standalone
[tweet text]

---

## LinkedIn
### Long Post
[post text]

### Short Post
[post text]

---
(continue for each platform)
```

## Options

- `--platforms <list>` — Only generate for specific platforms (e.g., `--platforms twitter,linkedin`)
- `--tone <tone>` — Override default tone (casual, professional, provocative, educational)
- `--audience <desc>` — Target audience description for better tailoring
- `--no-hashtags` — Skip hashtag generation
- `--thread-only` — Only generate Twitter thread
- `--carousel` — Focus on Instagram carousel format

## Tips for Best Results

1. **Longer source = better output** — More material to pull from
2. **Specify your audience** — "B2B SaaS founders" beats "business people"
3. **Mention your voice** — "I write like [person]" helps match tone
4. **Include context** — Why you wrote this, what response you want

## Examples

```
/content-to-social https://myblog.com/latest-post
/content-to-social ./content/article.md --platforms twitter,linkedin --tone casual
/content-to-social --audience "indie hackers" --tone provocative
```
