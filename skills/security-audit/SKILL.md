---
name: security-audit
description: |
  Comprehensive security audit: detects insecure defaults, hardcoded secrets, sharp edges, supply chain risks, and OWASP vulnerabilities. Based on Trail of Bits methodology. Use when auditing security, reviewing config, or pre-deployment checks. For PR diffs, use /security-review instead.
context: fork
argument-hint: "scope or focus area (optional)"
---

# Security Audit — Trail of Bits Methodology

Comprehensive security audit combining insecure defaults detection, sharp edges analysis, and supply chain risk assessment. Adapted from [Trail of Bits skills](https://github.com/trailofbits/skills).

## When to Use

- Pre-deployment security review of the full codebase
- Auditing configuration and secrets management
- Reviewing auth, crypto, API security, payment handling
- Evaluating dependency health and supply chain risk
- Periodic security checkups

## When NOT to Use

- Test fixtures in test directories
- Example/template files (`.example`, `.env.example`)
- Development-only configs (local Docker, dev scripts)
- Reviewing a single PR diff (use `/security-review` instead)

---

## Part 1: Insecure Defaults Detection

Finds **fail-open** vulnerabilities where the app runs insecurely with missing configuration.

- **Fail-open (CRITICAL):** `SECRET = env.get('KEY') or 'default'` — App runs with weak secret
- **Fail-secure (SAFE):** `SECRET = env['KEY']` — App crashes if missing

### Search Targets

Identify and scan project-specific high-risk areas, typically including:

- **Auth/session secrets** — JWT_SECRET, SESSION_KEY, etc. with fallback handling
- **Payment/billing keys** — Stripe, payment gateway secrets
- **Database connections** — DATABASE_URL fallback behavior
- **CORS configuration** — Origin allowlists
- **External API keys** — Third-party service credentials
- **Cache/queue connections** — Redis, RabbitMQ fallback behavior
- **Debug/verbose modes** — Debug flags, error verbosity settings

### Search Patterns

```
# Fallback secrets
getenv.*\) or ['"]
os.environ.get.*default
process\.env\.[A-Z_]+ \|\| ['"]

# Hardcoded credentials
password.*=.*['"][^'"]{8,}['"]
api[_-]?key.*=.*['"][^'"]+['"]
secret.*=.*['"][^'"]+['"]

# Weak defaults
DEBUG.*=.*true|True
AUTH.*=.*false|False
CORS.*=.*\*
verify.*=.*false|False

# Crypto
MD5|SHA1|DES|RC4|ECB in security contexts
```

### Verification Workflow

For each match:
1. **TRACE**: Follow code path — does app run with the default or crash?
2. **VERIFY**: Is this value used in auth/crypto/payment context?
3. **CHECK PROD**: Does the deployment config provide the variable?
4. **REPORT**: With file:line, pattern, exploitation scenario, production impact

### Rationalizations to Reject
- "It's just a development default" — If it reaches production code, it's a finding
- "The production config overrides it" — Verify prod config exists
- "We'll fix it before release" — Document now

---

## Part 2: Sharp Edges Analysis

Identifies error-prone APIs, dangerous configurations, and footgun designs.

### Sharp Edge Categories

**1. Configuration Cliffs**
- Auth secrets accepting empty/weak values
- CORS accepting wildcard with credentials
- Cache/queue fallback to in-memory (security implications?)
- Webhook secret validation bypass scenarios

**2. Silent Failures**
- Auth middleware that silently skips on error
- Webhook signature verification failure handling
- Database connection fallback behavior

**3. Input Validation Gaps**
- ID/slug format validation
- Numeric field bounds checking
- Pagination: max page_size enforced?
- Request body size limits?

**4. SQL Injection Surface**
- Any raw SQL usage — ALL queries parameterized?
- Any string interpolation in SQL?

**5. Type Confusion**
- Token types (access vs refresh) distinguishable?
- Role/tier strings validated against enum?

### Python-Specific Patterns (from Trail of Bits)

| Pattern | Risk |
|---------|------|
| `pickle.loads(user_data)` | Arbitrary code execution |
| `yaml.load()` without `safe_load` | Code execution |
| `subprocess.*(..., shell=True)` | Command injection |
| `eval(`, `exec(` | Code execution |
| `except:` or `except Exception: pass` | Swallowed security errors |
| `template.format(user_input)` | Format string injection |
| `def f(x=[])` mutable defaults | Shared state bugs |

### JavaScript/TypeScript Patterns

| Pattern | Risk |
|---------|------|
| `==` instead of `===` | Type coercion bugs |
| `obj[userInput]` | Prototype pollution |
| `eval(`, `new Function(` | Code execution |
| `as Type` assertions | Runtime type mismatch |
| `!` non-null assertion | Null pointer crash |
| Missing `await` | Race conditions |

### Edge Case Probing

For each security-relevant API, ask:
- **Zero/empty/null**: What happens with `0`, `""`, `null`?
- **Negative values**: What does `-1` mean?
- **Type confusion**: Can different security concepts be swapped?
- **Default values**: Is the default secure?
- **Error paths**: What happens on invalid input?

---

## Part 3: Supply Chain Risk Audit

Evaluates dependencies for exploitation or takeover risk.

### Risk Criteria

A dependency is high-risk if:
- **Single maintainer** — individual, not org-backed
- **Unmaintained** — stale, deprecated, archived
- **Low popularity** — few stars/downloads vs peers
- **High-risk features** — FFI, deserialization, code execution
- **Past CVEs** — high/critical severity
- **No security contact** — no SECURITY.md or responsible disclosure

### Workflow

1. Enumerate all direct dependencies from manifest files (requirements.txt, package.json, Cargo.toml, etc.)
2. For each, check GitHub: stars, last commit, maintainer count, open issues
3. Flag high-risk deps in report with risk factors and suggested alternatives
4. Run language-appropriate audit tools (`pip audit`, `npm audit`, `cargo audit`, etc.)

### Report Template

```markdown
# Supply Chain Risk Report

## Metadata
- Scan Date: YYYY-MM-DD
- Dependencies Scanned: N

## High-Risk Dependencies

| Dependency | Risk Factors | Notes | Suggested Alternative |
|------------|-------------|-------|-----------------------|

## Recommendations
```

---

## Report Format

Generate a markdown report at a suitable location in the project (e.g., `tasks/security-audit-report.md`):

```markdown
# Security Audit Report

## Executive Summary
| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH | Y |
| MEDIUM | Z |
| LOW | W |

## Findings
### [SEVERITY] Title
**File**: path:line
**Pattern**: [code pattern found]
**Verification**: [trace result]
**Production Impact**: [exploitability]
**Recommendation**: [specific fix]

## Supply Chain Summary
## Quality Checklist
- [ ] All env var fallbacks checked
- [ ] Auth flow verified
- [ ] Payment/webhook validation confirmed
- [ ] CORS configuration reviewed
- [ ] SQL injection surface audited
- [ ] Dependency audit complete
- [ ] Error handling reviewed (no silent failures)
```
