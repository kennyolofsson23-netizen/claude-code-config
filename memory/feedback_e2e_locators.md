---
name: Playwright E2E locator patterns
description: Locator best practices for kenny-corp dashboard E2E tests — exact matching, scoped selectors, unique task names
type: feedback
---

Use `{ exact: true }` on `getByRole("button", { name: "open" })` — Next.js dev tools button matches "open" otherwise.

**Why:** First E2E run had 4 failures from ambiguous locators — "open" matched Next.js dev tools, `filter({ hasText })` on `div` matched parent containers with multiple tasks.

**How to apply:**
- Use `.locator(".rounded-lg.border").filter({ hasText: taskName })` to scope to specific task rows
- Use `Date.now()` in task names to guarantee uniqueness across test runs
- Always use `exact: true` for filter tab buttons
- Create tasks via API helper before navigating, don't rely on state from prior tests
