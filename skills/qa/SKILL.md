---
name: qa
description: |
  Full QA pass: run all tests, check types, catch regressions, write missing tests. Use when the user says "run tests", "QA", "verify changes", "check for regressions", "test everything", or "make sure it works".
context: fork
argument-hint: "scope or focus area (optional)"
---

# QA Skill — Full Quality Assurance Pass

Run a complete QA pass on all current changes.

## Step 1: Scope the Changes

```bash
git diff --name-only
git diff --cached --name-only
```

Categorize every changed file:
- **backend** → Python tests
- **frontend** → JS/TS tests + type checking
- **ML** → ML invariant tests + auditor check
- **config** → validate no secrets, correct formats
- **tests** → run them to make sure they pass

## Step 2: Detect Test Framework

Before running anything, detect the project's test setup:
- **Python**: Check `pyproject.toml`, `setup.cfg`, `pytest.ini`, `Makefile` for pytest/unittest/tox config
- **Node/JS/TS**: Check `package.json` scripts (`test`, `typecheck`), look for jest/vitest/mocha config
- **Type checking**: Check for `tsconfig.json` (tsc), `mypy.ini`/`pyproject.toml` (mypy)
- **Linting**: Check for eslint, ruff, flake8 configs
- **E2E**: Check for playwright, cypress configs
- **Monorepo**: Check for workspace config (pnpm-workspace.yaml, nx.json, turbo.json) — run tests per package

Use the detected commands for all subsequent steps.

## Step 3: Run Tests (ALL applicable)

Run the test commands discovered in Step 2. Examples:
- `pytest -v --tb=short` (or whatever the project uses)
- `npm test` / `pnpm test` / `yarn test`
- `npx tsc --noEmit` / `mypy .`

If new code has no tests → WRITE TESTS FIRST.

## Step 4: Write Missing Tests

For every new function, endpoint, or component without test coverage:
1. Create the test file in the appropriate `tests/` directory
2. Write tests covering: happy path, edge cases, error cases
3. Run them and confirm they pass

## Step 5: Regression Check

Run the FULL suite — not just tests for changed files. Use the same commands from Step 2, but ensure full scope (no path filters).

## Step 6: Report

```
QA PASS REPORT
==============
Scope:       [backend/frontend/ML/config]
Tests:       X passed, Y failed, Z new tests written
TypeScript:  clean/X errors
E2E:         ran/skipped (reason)
Regressions: none found / [list]

VERDICT: PASS / FAIL
```

## Step 7: Fix Issues

If FAIL: fix every issue found, then re-run from Step 3. Loop until PASS.

## Rules
- This skill produces EVIDENCE, not opinions
- "It should work" is NOT acceptable — run it
- If there's no test infrastructure: build it
- Every QA run must end with a clear PASS or FAIL verdict
