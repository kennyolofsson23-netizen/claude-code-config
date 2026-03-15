---
name: security-review
description: |
  Security-focused differential code review for PRs, commits, and diffs. Calculates blast radius, checks test coverage, models attacks, and generates markdown reports. Based on Trail of Bits methodology. Use for PR reviews, commit audits, and pre-deployment diff checks. For full codebase audits, use /security-audit instead.
context: fork
argument-hint: "PR number, commit range, or branch"
---

# Security Review — Differential Analysis

Security-focused code review for PRs, commits, and diffs. Adapted from [Trail of Bits differential-review](https://github.com/trailofbits/skills).

## Core Principles

1. **Risk-First**: Focus on auth, crypto, payments, external calls, validation
2. **Evidence-Based**: Every finding backed by git history, line numbers, attack scenarios
3. **Adaptive**: Scale analysis to change size (SMALL/MEDIUM/LARGE)
4. **Honest**: State coverage limits and confidence level
5. **Output-Driven**: Always generate markdown report file

## When to Use

- Reviewing PRs before merge to main
- Auditing commit ranges for security regressions
- Pre-deployment diff checks
- Any code change touching auth, payments, API security, or user data

## When NOT to Use

- Greenfield code with no baseline (use `/security-audit` instead)
- Documentation-only or formatting changes
- Quick summary explicitly requested by user

---

## Quick Reference

### Codebase Size Strategy

| Size | Strategy | Approach |
|------|----------|----------|
| SMALL (<20 files) | DEEP | Read all deps, full git blame |
| MEDIUM (20-200) | FOCUSED | 1-hop deps, priority files |
| LARGE (200+) | SURGICAL | Critical paths only |

### Risk Level Triggers

| Risk | Triggers |
|------|----------|
| HIGH | Auth, crypto, payments, JWT, external calls, validation removal, DB queries |
| MEDIUM | Business logic, state changes, new public API endpoints |
| LOW | Comments, tests, UI styling, logging |

### Red Flags (Stop and Investigate)

- Removed code from "security", "CVE", or "fix" commits
- Auth/permission checks removed
- Validation removed without replacement
- External calls added without checks
- High blast radius (50+ callers) + HIGH risk change

---

## Workflow

```
Phase 0: Triage → Phase 1: Code Analysis → Phase 2: Test Coverage
    ↓                    ↓                        ↓
Phase 3: Blast Radius → Phase 4: Deep Context → Phase 5: Adversarial → Phase 6: Report
```

### Phase 0: Triage

```bash
git diff <base>..<head> --stat
git diff <base>..<head> --name-only
```

Risk-score each changed file. Focus effort on HIGH risk.

### Phase 1: Changed Code Analysis

For each changed file:
1. Read both versions (before/after)
2. Analyze each diff region: BEFORE → AFTER → CHANGE → SECURITY implications
3. Git blame removed code — was it a security fix?
4. Check for regressions (previously removed code re-added)
5. Micro-adversarial: What attack did removed code prevent? What new surface exposed?

### Phase 2: Test Coverage

```bash
# Production code changes (exclude tests)
git diff <range> --name-only | grep -v "test"
# Test changes
git diff <range> --name-only | grep "test"
```

Risk elevation: NEW function + NO tests → MEDIUM→HIGH

### Phase 3: Blast Radius

Count callers for each modified function. Classify:
- 1-5: LOW · 6-20: MEDIUM · 21-50: HIGH · 50+: CRITICAL

### Phase 4: Deep Context (HIGH risk only)

Map complete function flow:
- Entry conditions, state reads/writes, external calls, return values
- Trace internal + external calls
- Identify invariants — are they maintained after changes?

### Phase 5: Adversarial Modeling (HIGH risk only)

Define attacker model:
- **WHO**: Unauthenticated user? Authenticated user? Compromised service?
- **ACCESS**: Public API? User role? Admin?
- **INTERFACE**: Which endpoint/function?

Build concrete exploit scenario:
```
ENTRY POINT: [exact endpoint]
ATTACK SEQUENCE:
1. [specific action with parameters]
2. [how it reaches vulnerable code]
3. [impact achieved]
EXPLOITABILITY: EASY/MEDIUM/HARD
CONCRETE IMPACT: [specific, measurable harm]
```

### Phase 6: Report

Generate report at project root or a tasks directory:

```markdown
# Security Review — [PR/Commit Description]

## Executive Summary
| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH | Y |
| MEDIUM | Z |
| LOW | W |

**Overall Risk:** CRITICAL/HIGH/MEDIUM/LOW
**Recommendation:** APPROVE/REJECT/CONDITIONAL

## What Changed
| File | +Lines | -Lines | Risk | Blast Radius |
|------|--------|--------|------|--------------|

## Findings
### [SEVERITY] Title
**File**: path:line
**Commit**: hash
**Blast Radius**: N callers
**Test Coverage**: YES/NO
**Description**: ...
**Attack Scenario**: ...
**Recommendation**: ...

## Test Coverage Analysis
## Recommendations
### Immediate (Blocking)
### Before Production
### Technical Debt

## Methodology
- Strategy: DEEP/FOCUSED/SURGICAL
- Files reviewed: X/Y
- Confidence: HIGH/MEDIUM/LOW
```

---

## Project-Specific High-Risk Areas

Before starting a review, identify and examine with extra scrutiny the project-specific high-risk areas, typically including:

- **Auth endpoints** — login, registration, token creation/refresh
- **Payment handling** — payment gateway integration, webhook handlers
- **Middleware/config** — CORS, error handlers, security middleware
- **Database layer** — connection management, credential handling, raw SQL queries
- **External API integrations** — API key management, prompt injection surface
- **Client-side auth** — API URL handling, auth token transmission, session management

---

## Quality Checklist

Before delivering:
- [ ] All changed files analyzed
- [ ] Git blame on removed security code
- [ ] Blast radius calculated for HIGH risk
- [ ] Attack scenarios are concrete (not generic)
- [ ] Findings reference specific line numbers + commits
- [ ] Report file generated
- [ ] User notified with summary
