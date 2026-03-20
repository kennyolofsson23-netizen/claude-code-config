# Cross-Project Learnings

> Battle-tested patterns from production AI pipeline work. Each entry prevented (or would have prevented) a real production issue.

---

## 1. Agent & Pipeline Reliability

**Stall detection is mandatory for agent streams.**
Why: Agent SDK `query()` iterators can silently stop producing events. Without a stall timer (10min+), the process hangs forever. Always wrap iteration with a timer that calls `q.close()` on timeout.
Apply when: Any code that iterates over streaming agent responses.

**Use Promise.allSettled, never Promise.all, for parallel stages.**
Why: `Promise.all()` kills all parallel stages when one fails, losing completed results. `Promise.allSettled()` catches rejections as settled promises. Save each stage's output to DB immediately when it completes, before the group resolves.
Apply when: Running multiple agents or API calls in parallel.

**Loop guards must verify actual completion.**
Why: After a loop exits (hit guard limit), the code fell through to "All stages complete" without checking. Hitting the guard limit does not mean success.
Apply when: Any iteration loop with a max-iterations safety guard.

**Review iteration 2+ must be diff-scoped.**
Why: Full re-review of unchanged code causes reviewers to raise NEW issues on code they previously approved. The review loop never converges. Iteration 2+ should only verify previous blockers are fixed + review the git diff.
Apply when: Multi-round code review pipelines.

**Missing features vs quality issues need different routing.**
Why: Review blockers are for code quality. Missing features (entire components not built) loop back to BUILD with an ESCALATION tag, not back to review.
Apply when: Deciding whether to route a finding back to build or review.

**Auth/infrastructure errors must fail the pipeline immediately.**
Why: 401/403 auth errors, ECONNREFUSED, exhausted API billing = infrastructure problems. Looping back to BUILD wastes tokens trying to fix infra with code changes.
Apply when: Error handling in multi-stage pipelines.

---

## 2. Serverless & Deployment

**Post-deploy smoke tests are non-negotiable.**
Why: "It compiles" is not "it works." Code that passes CI/CD can fail in production. Every deployed tool must have core API endpoints smoke-tested after deploy.
Apply when: Any deployment pipeline.

**Fire-and-forget async fails on serverless.**
Why: Vercel kills the process after sending the response. In-memory state across requests fails (each invocation is fresh). Unprovisioned storage (Blob, KV) guarantees failure.
Apply when: Writing code for Vercel, AWS Lambda, or any serverless platform.

**Timeouts must account for actual model speed.**
Why: Hardcoded timeouts that work locally fail when AI APIs are slow. Set 30s+ for text, 60s+ for images. Always set `maxDuration` on serverless routes calling external AI providers.
Apply when: Any serverless function calling AI APIs.

**DNS resolution differs between local and serverless.**
Why: `dns.promises.lookup()` (OS resolver) fails unreliably on Vercel. Use `dns.promises.resolve4`/`resolve6` which query DNS servers directly. Unit tests mocking DNS can't catch this.
Apply when: Code that does DNS lookups deployed to serverless.

---

## 3. Authentication & Security

**Never break existing JWT sessions.**
Why: Changing token validation (adding iss/aud claims) invalidated all active user sessions. Implement two-phase decode: try strict validation, catch exceptions, fall back to lenient.
Apply when: Any auth system change with active user sessions.

**Admin pages must show auth errors, not empty state.**
Why: `/admin` showed empty. Looked like a hack. Actual cause: user had `is_admin=false`, NextAuth cached stale JWT. Always show "Not authenticated" instead of blank.
Apply when: Building admin or role-gated pages.

**ANTHROPIC_API_KEY in agent-runner env causes billing confusion.**
Why: If `ANTHROPIC_API_KEY` is present, Agent SDK uses API auth instead of subscription OAuth, causing "Credit balance too low" even with active subscription. Only set this key on deployed tools, never in agent-runner env.
Apply when: Configuring Agent SDK environments.

---

## 4. Testing Philosophy

**E2E catches integration bugs that unit tests miss.**
Why: 2,032 unit tests passed. Zero bugs caught. But refresh -> predictions didn't load. Root cause: an `isPast` guard silently disabled the entire feature. Real bugs live at integration boundaries.
Apply when: Deciding test strategy. Unit tests prove code shape; E2E tests prove behavior.

**Scope performance optimizations to the real problem.**
Why: Predict endpoint was slow for past races (5-30s). First fix: disabled predictions for ALL cache misses. This broke today/future races. Better: check race date, only optimize the slow case.
Apply when: Any performance fix that affects user-facing features.

**API integration code must validate against current docs.**
Why: Generated API client code from training data had wrong field names, endpoints, and auth headers. Always verify against current provider documentation.
Apply when: Writing code that calls external APIs.

---

## 5. Windows / Node.js Environment

**Node.js fs/execSync need Windows paths, not Git Bash paths.**
Why: `fs.existsSync`, `mkdirSync`, `execSync` don't understand `/c/Users/...` Git Bash paths. Normalize: `path.replace(/^\/([a-zA-Z])\//, "$1:/")`. Claude Code CLI handles `/c/` fine, only Node native calls need Windows format.
Apply when: Node.js code running on Windows with Git Bash.

**Agent SDK on Windows needs explicit Windows-format paths.**
Why: SDK can't auto-find `claude.exe`. Must set `pathToClaudeCodeExecutable: "C:/Users/.../claude.exe"` and `cwd` in Windows format. Git Bash `/c/...` causes ENOENT in Node's `spawn()`.
Apply when: Configuring Agent SDK on Windows.

---

## 6. Database & Data

**PostgreSQL ROUND() returns Decimal, JSON serializes as string.**
Why: `ROUND(x, 1)` returns `Decimal`. FastAPI JSON serialized it as `"11.2"` (string). Frontend `.toFixed(1)` crashed silently. Fix: cast aggregates to `float()` or `int()` before returning.
Apply when: FastAPI + PostgreSQL with aggregated numeric values.

**GROUP BY name columns creates duplicates with data variants.**
Why: `GROUP BY owner_id, owner_name` created separate rows for "Stall Zet" vs "Stall Zet (Reden Daniel)". Fix: `GROUP BY id` only, use `MODE() WITHIN GROUP (ORDER BY name)` for the most common name.
Apply when: Aggregating real-world data with name variants.

**Never aggregate 2M+ rows per request on constrained environments.**
Why: Browse endpoints joining 2.2M rows crashed Railway with "No space left on device." Fix: use pre-aggregated tables for defaults, bounded queries for page enrichment, full scans only with scoped filters.
Apply when: Analytics/browse endpoints on cloud infrastructure.

---

## 7. Configuration & MCP

**MCP config lives in ~/.claude.json, not ~/.claude/.mcp.json.**
Why: Claude Code only reads `~/.claude.json` under the `mcpServers` key. `~/.claude/.mcp.json` is silently ignored. Config changes require session restart.
Apply when: Setting up MCP servers.

**Official remote MCPs use OAuth, not API tokens.**
Why: Vercel, Cloudflare, Sentry official MCPs use browser OAuth on first use. No need for API tokens in config. Community stdio MCPs may still need tokens.
Apply when: Adding MCP servers to your setup.

---

## 8. Multi-Phase Execution

**Persist plans before new sessions.**
Why: Conversation context is ephemeral. If a multi-phase plan isn't written to task files before context clears, the next session starts blind.
Apply when: Any multi-session work.

**Respect phase boundaries.**
Why: When a plan says "each phase = separate session," implementing all at once removes review checkpoints. Errors compound. Each phase should complete, commit, wrap up, then the next session continues.
Apply when: Multi-phase implementation plans.

**Ship fast over perfection.**
Why: Compound growth from rapid iteration beats polishing individual runs. Pick the best available option and build. Don't re-run swarms unless completely broken.
Apply when: Deciding whether to iterate or ship.

---

## 9. Frontend / React

**React useCallback closures capture stale state.**
Why: `useCallback` with `[session?.accessToken]` as dependency. `.then()` callback captured stale version while NextAuth was still hydrating. Token was undefined. Retry effect never fired again. Fix: use `useRef` for mutable state in async callbacks.
Apply when: React async callbacks that depend on auth state or rapidly changing values.

**Sync I/O in async endpoints blocks the event loop.**
Why: `/predict` called sync ML inference on async event loop. Cache misses (1-2s blocking) with 8 parallel requests froze the server for 5-10s. Fix: `asyncio.get_event_loop().run_in_executor()` + `threading.Lock` for non-thread-safe resources.
Apply when: FastAPI or async Python servers with sync operations.

---

## 10. ML / Data Science

**If AUC > 0.85 on real-world prediction, something is leaking.**
Why: AUC jumped from 0.67 to 0.998. Felt great. Rigorous audit revealed it was fake (real: 0.66). Post-race data was leaking as training features. An AUC jump > 0.03 from a few features should trigger a full leak audit.
Apply when: Any ML model showing suspiciously good metrics.

**Train/serve skew is a silent killer.**
Why: 20+ features had different values between training and inference across 3 audit rounds. An "alias dict" masked the divergence. Fix: put `# MUST MATCH train_file.py line NNN` comments in both files. Never use mapping dicts to reconcile features.
Apply when: Any ML system with separate training and serving code.

---

## Document Maintenance

**Keep documentation current or delete it.**
Why: After 22 sessions, docs referenced files that hadn't existed for 15 sessions. ML metrics were 5 sessions stale. Schema descriptions were wrong. MEMORY.md should be topical, not chronological. Delete completed plans.
Apply when: Any project with shared documentation or team context.
