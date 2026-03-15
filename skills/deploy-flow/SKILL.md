---
name: deploy-flow
description: Deploy code to production via feature branch → test → staging → PR → merge. Use when deploying changes, pushing to production, or when the user says "deploy", "push to prod", "merge to main", "stage this", or "ship it".
---

# Deploy Flow

Safe, tested deployment from local to production. Never skip steps.

## Flow

```
1. Branch  →  2. Test Local  →  3. Push  →  4. CI Green  →  5. Playwright vs Staging  →  6. PR  →  7. Merge
```

## Step 1: Feature Branch

```bash
git checkout -b <branch-name>
# Stage ONLY relevant files — never git add -A
git add <specific-files>
git commit -m "type(scope): description"
```

**Rules:**
- Never commit `.env`, `.pkl`, `.png`, credentials, temp scripts
- Use conventional commits: `feat|fix|refactor|test|docs(scope): lowercase description`
- Subject line ≤ 72 chars

## Step 2: Test Locally (ALL suites)

Run every test suite. If ANY fail, fix before proceeding.

```bash
# Backend
pytest backend/tests/ -v --tb=short --cov=backend --cov-report=term

# Frontend unit
pnpm --filter web test

# Lint
ruff check backend/ scripts/
pnpm --filter web lint

# E2E (if dev server available)
pnpm --filter web test:e2e
```

**Gate:** 0 failures across all suites. Coverage must meet threshold.

## Step 3: Push Feature Branch

```bash
git push -u origin <branch-name>
```

## Step 4: CI Must Be Green

```bash
gh pr checks <pr-number>
# Wait for ALL checks to pass
# If lint fails: fix locally, commit, push
# If tests fail: fix locally, commit, push
# NEVER merge with red CI
```

## Step 5: Playwright Against Staging/Preview

Run E2E tests against the Vercel preview or staging URL:

```bash
cd apps/web && BASE_URL=<preview-url> npx playwright test e2e/ --project=chromium --reporter=list
```

**Verify:**
- All navigation flows work
- Content renders correctly (prices, game types, "Avd" not "Lopp")
- Data integrity (odds positive, AI% sums to ~100%, dates chronological)
- No console errors
- Mobile responsive

## Step 6: Create PR

```bash
gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
## Summary
- <bullet points>

## Test plan
- [ ] pytest: X passed, 100% coverage
- [ ] vitest: X passed
- [ ] playwright: X passed
- [ ] Staging E2E verified

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Step 7: Merge

Only after ALL checks green + staging verified:

```bash
gh pr merge <number> --merge --delete-branch
git checkout main && git pull
```

## Post-Deploy Verification

After merge deploys to production:

```bash
# Health check
curl -s https://api.<domain>/health | jq .

# Smoke test production
cd apps/web && BASE_URL=https://<domain> npx playwright test e2e/smoke.spec.ts --project=chromium

# If model was updated: flush Redis cache
curl -X POST https://api.<domain>/api/v1/cache/flush-predictions -H "Authorization: Bearer <admin-token>"
```

## Emergency Rollback

If production breaks after merge:

```bash
# Revert the merge commit
git revert HEAD --no-edit
git push origin main
# This triggers a new deploy with the previous code
```

## Anti-Patterns (NEVER do these)

- Push directly to main
- Merge with failing CI
- Skip E2E tests "because unit tests pass"
- Deploy on Friday evening
- `git push --force` to main
- Lower test thresholds to make CI pass
- Commit secrets, screenshots, or model files
