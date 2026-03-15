---
name: webapp-testing
description: |
  Test and debug local web applications using Playwright. Captures screenshots, verifies UI behavior, checks browser logs, and runs E2E test scenarios. Use when the user says "test the app", "check the UI", "take a screenshot", "debug the frontend", "run E2E tests", "verify the page works", or "Playwright test".
argument-hint: "URL or test scenario"
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

> **Note:** For project-specific selectors and components, check `.claude/skills/webapp-testing/` in the project directory.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Start the dev server(s), then write Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Server Lifecycle

If the project has a helper script (e.g. `scripts/with_server.py`), run it with `--help` first to see usage. Otherwise start dev servers manually before running tests.

Typical dev server commands:
- **Next.js**: `npm run dev` / `pnpm dev` → http://localhost:3000
- **Vite**: `npm run dev` → http://localhost:5173
- **FastAPI**: `uvicorn app.main:app --reload --port 8000`

For multi-server setups (e.g. separate backend + frontend), start each in the background and wait for ports to be available before testing.

## Example: Basic Playwright Test

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')  # CRITICAL for Next.js / SSR apps

    # Screenshot for visual inspection
    page.screenshot(path='/tmp/page.png', full_page=True)

    # Discover elements
    buttons = page.locator('button').all()
    print(f"Found {len(buttons)} buttons")

    # Interact
    page.click('button:has-text("Submit")')
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect**: `page.screenshot()` → view the PNG to understand layout
2. **Discover**: `page.locator('button').all()` → enumerate elements
3. **Act**: `page.click('button:has-text("Submit")')` → interact with discovered selectors

## Wait Patterns

- **`networkidle`** — Wait for no network requests for 500ms. Essential for Next.js / SSR apps before any DOM inspection.
- **`domcontentloaded`** — Faster, but only safe for static or server-rendered content that doesn't hydrate.
- **`page.wait_for_selector(selector)`** — Wait for a specific element to appear. Use when you know what to expect.
- **`page.wait_for_url(pattern)`** — Wait after navigation/redirect.
- **`page.wait_for_timeout(ms)`** — Last resort. Prefer explicit waits above.

## Best Practices

- Wait `networkidle` before any DOM inspection on Next.js / SSR pages
- Use `text=` selectors over CSS classes (classes may change across builds)
- Test API endpoints directly with `httpx` or `requests` before testing UI
- Always take a screenshot first when debugging unexpected behavior
- Use `headless=True` for CI/automated runs; `headless=False` for local debugging
- Capture console logs for debugging: `page.on('console', lambda msg: print(msg.text))`
