---
name: test-write
description: Write tests for the Travmaskinen codebase — backend (pytest, async, FastAPI), frontend (Vitest + React Testing Library), or E2E (Playwright). Use this skill whenever writing new tests, adding test coverage, implementing TDD red-green-refactor cycles, or when the user says "write tests", "add tests", "test this", "cover this", "TDD", or asks for test coverage on any module. Also triggers when implementing new features that need tests first (TDD flow).
---

# Test Writer — Travmaskinen

Write tests that match the project's established conventions exactly. The codebase has 2,032 backend tests and 101 frontend tests — new tests must be indistinguishable from existing ones in style.

## Decision: Which Layer?

| Target | Framework | Config | Run Command |
|--------|-----------|--------|-------------|
| Python module (`backend/**/*.py`) | pytest + asyncio | `pyproject.toml` | `pytest backend/tests/ -v --tb=short` |
| React component (`apps/web/**/*.tsx`) | Vitest + RTL | `apps/web/vitest.config.ts` | `pnpm --filter web test` |
| User flow (multi-page) | Playwright | `apps/web/playwright.config.ts` | `pnpm --filter web test:e2e` |

Coverage commands:
- Backend: `pytest backend/tests/ --cov=backend --cov-report=term-missing`
- Frontend: `pnpm --filter web test:coverage`

## TDD Flow (Always)

1. **Red**: Write the test first — it MUST fail
2. **Green**: Write minimal code to make it pass
3. **Refactor**: Clean up without changing behavior
4. Run the full suite to confirm no regressions

---

## Backend Tests (pytest)

### File Placement

```
backend/tests/
├── unit/          # Module-level logic, mocked dependencies
├── integration/   # Full endpoint tests via TestClient
└── ml/            # Model invariants, feature parity
```

Name: `test_{module_name}.py` — mirrors the source file.

### Shared Fixtures (from `conftest.py`)

Use these — don't recreate them:

- **`fixture_game`** (session): Full ATG game from `scripts/fixtures/v85_2026-03-07.json`
- **`fixture_race`** (function): First race from fixture_game
- **`fixture_horses`** (function): Horse entries from first race
- **`mock_intel`** (function): `MagicMock` of `V85DatabaseIntelligence` with sensible zero-data defaults for all 30+ methods
- **`client`** (function): `FastAPI TestClient` with mocked DB and settings

### Patterns

#### Async endpoint/service test
```python
@pytest.mark.asyncio
async def test_cache_miss_calls_predictor():
    """When cache is empty, predictor.predict() is called."""
    import backend.api.predict as mod

    mock_pred = MagicMock()
    mock_pred._loaded = True
    mock_pred.predict = AsyncMock(return_value=[{"horse_id": 1, "prob": 0.5}])

    with patch.object(mod, "predictor", mock_pred), \
         patch.object(mod, "cache_get", new_callable=AsyncMock, return_value=None), \
         patch.object(mod, "cache_set", new_callable=AsyncMock):
        result = await mod.predict_race("2026-03-15_1_1")

    mock_pred.predict.assert_called_once()
    assert result[0]["prob"] == 0.5
```

#### Pydantic validation
```python
def test_invalid_race_id_rejected():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        PredictRequest(race_id="bad-id")
```

#### Integration endpoint
```python
def test_endpoint_returns_200(client):
    resp = client.get("/api/v1/races/today")
    assert resp.status_code == 200
    assert "legs" in resp.json()
```

#### ML invariant
```python
def test_probabilities_sum_to_one(fixture_race, mock_intel):
    probs = predictor.predict(fixture_race, mock_intel)
    total = sum(p["win_probability"] for p in probs)
    assert abs(total - 1.0) < 0.01, f"Probabilities sum to {total}, expected ~1.0"
```

### Rules

- `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio` on fixtures, but DO use it on async test functions
- Use `AsyncMock` for any async return value
- Use `patch.object(module, "name")` — never `patch("string.path")` (brittle)
- Test BOTH success AND failure paths (cache hit/miss, model loaded/not, 200/404/500)
- `fail_under = 100` in pyproject.toml — every line must be covered or marked `# pragma: no cover`
- Exclude lines: `if TYPE_CHECKING:`, `if __name__ == "__main__":`, `raise NotImplementedError`

---

## Frontend Tests (Vitest + RTL)

### File Placement

Tests live next to source: `ComponentName.test.tsx` beside `ComponentName.tsx`.

### Test Utilities (from `lib/test-utils.tsx`)

Use these factories — don't create ad-hoc objects:

- `createHorse(overrides?)` — full `BackendHorse` with sensible defaults
- `createScratchedHorse(overrides?)` — scratched variant
- `createFreeSession()` / `createProSession()` / `createAdminSession()` — auth sessions
- `createUnauthenticatedSession()` — no auth

### Required Mocks

Most components need these at the top of the file:

```typescript
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), forward: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}))
```

### Patterns

#### Component render + content assertion
```typescript
it('renders horse name', () => {
  const horse = createHorse({ horse: { name: 'Elitlansen', id: 101 } })
  render(<HorseCard horse={horse} />)
  expect(screen.getByText('Elitlansen')).toBeInTheDocument()
})
```

#### Negative assertion (element NOT present)
```typescript
it('hides badge when scratched', () => {
  const horse = createScratchedHorse()
  render(<HorseCard horse={horse} />)
  expect(screen.queryByText('FAVORIT')).not.toBeInTheDocument()
})
```

#### User interaction
```typescript
it('calls onToggle when clicked', () => {
  const onToggle = vi.fn()
  render(<HorseCard horse={createHorse()} onToggle={onToggle} />)
  fireEvent.click(screen.getByText('Elitlansen').closest('[class*="rounded-lg"]')!)
  expect(onToggle).toHaveBeenCalledTimes(1)
})
```

#### API/fetch mocking
```typescript
beforeEach(() => { vi.useFakeTimers() })
afterEach(() => { vi.useRealTimers(); vi.restoreAllMocks() })

it('fetches data with auth header', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ data: [] }),
  }))

  await api.get('/api/v1/races', { token: 'jwt-123' })

  expect(fetch).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer jwt-123' }),
    }),
  )
})
```

### Rules

- `vi.mock()` calls must be at file top (before imports that use the mocked module)
- Always `vi.restoreAllMocks()` in `afterEach`
- Use `screen.getByText()` / `screen.getByRole()` — never `container.querySelector()` (fragile)
- Use `queryByText()` for "should NOT exist" — returns null instead of throwing
- Use `expect.objectContaining()` for partial object matching
- Import alias: `@/lib/...` maps to `./lib/...`

---

## E2E Tests (Playwright)

### File Placement

`apps/web/e2e/{feature}.spec.ts`

### Patterns

```typescript
import { test, expect } from '@playwright/test'

test.describe('Game page interactions', () => {
  test('loads V85 game with predictions', async ({ page }) => {
    await page.goto('/spel/V85')
    await expect(page.locator('h1')).toBeVisible()
    await expect(page).toHaveURL(/spel\/V85/)
  })

  test('navigates between legs', async ({ page }) => {
    await page.goto('/spel/V85')
    const tab = page.getByRole('tab', { name: 'Avd 2' })
    await tab.click()
    await expect(tab).toHaveAttribute('aria-selected', 'true')
  })
})
```

### Rules

- Tests run on 3 browsers: chromium, firefox, mobile-chrome
- `baseURL = http://localhost:3000` — dev server auto-starts locally
- Use `page.locator()` for CSS, `page.getByRole()` for semantic elements
- Always `await` interactions and assertions
- Traces on first retry, screenshots only on failure

---

## Checklist Before Done

1. All new tests pass: run the relevant suite
2. No existing tests broken: run the full suite
3. Coverage check: run with `--cov` / `test:coverage`
4. Test names are descriptive: `test_cache_miss_returns_fresh_prediction` not `test_1`
5. Both happy path AND error path covered
6. Factories/fixtures used (no inline 50-line objects)
