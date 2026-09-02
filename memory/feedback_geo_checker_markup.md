---
name: feedback_geo_checker_markup
description: GEO checker regex pitfalls — bold tags need [\s>] not just >, FAQ must use h3+p not dt/dd, content inside footer/header/nav is stripped
type: feedback
---

The kenny-corp geo-checker.ts has specific markup requirements that don't match all HTML patterns:

1. **Bold regex**: `<(?:strong|b)[\s>]` — tags with className like `<strong className="...">` now match after fix. Previously only bare `<strong>` matched.
2. **Paragraph extraction**: Only `<p>` tags are counted. Content in `<dd>`, `<span>`, `<div>` is invisible to the checker.
3. **Question headings**: Only `<h2>` and `<h3>` tags are checked. Questions in `<dt>` tags don't count.
4. **Footer/header/nav stripped**: The checker removes `<footer>`, `<header>`, `<nav>` before analysis. Privacy/terms links must appear outside these tags to score E-E-A-T points.
5. **Client-rendered content invisible**: `'use client'` components inside `<Suspense>` don't appear in SSR HTML. Add sr-only server-rendered copies of key content.

**Why:** Hub scored 65 despite having table, bold, FAQ because markup didn't match checker regexes. Fixed regex + restructured FAQ = jumped to 73.

**How to apply:** When building new tools or GEO-optimizing existing ones, use bare `<strong>` tags, wrap FAQ answers in `<p>` inside `<dd>`, use `<h3>` for FAQ question headings, and ensure key content is server-rendered.
