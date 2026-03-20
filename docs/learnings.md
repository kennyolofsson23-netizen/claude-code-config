# Cross-Project Learnings

Curated patterns from production incidents across multiple projects. Each entry prevented (or would have prevented) a real failure.

---

## 1. Agent & Pipeline Reliability

### Stall Detection
**Rule:** Wrap Agent SDK `query()` iteration with a stall timer (10min+). If the stream dies silently, call `q.close()`.
**Why:** Streams can hang indefinitely with no error event. Without stall detection, pipelines freeze forever.
**Apply when:** Using Agent SDK or any long-running streamed process.

### Parallel Stage Execution
**Rule:** Use `Promise.allSettled`, not `Promise.all`, for parallel stages.
**Why:** `Promise.all` aborts everything when one stage fails, losing partial results from stages that succeeded.
**Apply when:** Running multiple independent async operations where partial success is useful.

### Stream Buffer Processing
**Rule:** Track a `processedCountRef` to avoid re-processing the entire buffer on each chunk.
**Why:** Re-processing grows O(n²) and produces duplicate output as the buffer accumulates.
**Apply when:** Incrementally processing a growing stream buffer.

### Loop Guard Completion
**Rule:** Loop guards must check actual completion, not just iteration count. Hitting the guard limit is a failure, not success.
**Why:** Silently exiting a retry loop at max iterations masks the real problem and produces incomplete results.
**Apply when:** Any retry or iteration loop with a safety limit.

### Review Iteration Scope
**Rule:** Review iteration 2+ must be diff-scoped. Full re-review on each pass raises new issues and never converges.
**Why:** Reviewers find new style nits on unchanged code, creating infinite loops.
**Apply when:** Multi-pass code review pipelines or any iterative refinement loop.

### Missing vs Quality Issues
**Rule:** Missing features go back to BUILD. Quality issues get fixed in review. Different problems, different paths.
**Why:** Mixing them causes review loops to attempt feature implementation, or builders to do style fixes.
**Apply when:** Triaging issues in any multi-stage pipeline.

### Infrastructure Errors
**Rule:** Auth errors (401), connection refused, and similar infrastructure failures must fail the pipeline immediately -- never loop back to retry the build.
**Why:** Retrying a build will not fix a missing API key or a down server. It just wastes time and tokens.
**Apply when:** Error handling in any automated pipeline.

---

## 2. Serverless & Deployment

### Serverless Constraints
**Rule:** Fire-and-forget async, in-memory state, and unprovisioned storage all fail on serverless.
**Why:** Serverless functions freeze after response. Anything not persisted or awaited is lost.
**Apply when:** Deploying to Vercel, AWS Lambda, Cloudflare Workers, or similar.

### Realistic Timeouts
**Rule:** Timeouts must account for actual model speed: 30s+ for text, 60s+ for images on serverless cold starts.
**Why:** Default 10s timeouts cause silent failures that look like empty responses.
**Apply when:** Setting timeouts for any AI model call, especially on serverless.

### Post-Deploy Smoke Tests
**Rule:** Post-deploy smoke tests are non-negotiable. "It compiles" does not mean "it works."
**Why:** Successful builds with broken runtime behavior ship to production undetected.
**Apply when:** Every deployment, no exceptions.

---

## 3. Authentication & Security

### Token Validation Changes
**Rule:** Never change JWT validation in a way that invalidates existing sessions. Use two-phase decode: strict first, then lenient fallback.
**Why:** Changing token shape or validation instantly logs out every active user.
**Apply when:** Modifying auth token structure, claims, or validation logic.

### API Key Leakage via Environment
**Rule:** `ANTHROPIC_API_KEY` in the agent-runner env causes "Credit balance too low" -- the SDK uses API auth instead of subscription OAuth.
**Why:** The presence of the key overrides the intended auth mechanism silently.
**Apply when:** Running Agent SDK processes alongside other Anthropic tooling.

---

## 4. Testing Philosophy

### E2E Over Unit Tests Alone
**Rule:** E2E tests catch integration bugs that unit tests miss. 2,032 passing unit tests caught zero integration bugs that a single E2E would have found.
**Why:** Unit tests verify components in isolation. Real bugs live at the boundaries.
**Apply when:** Deciding test strategy. Unit tests are necessary but not sufficient.

### API Integration Validation
**Rule:** Validate API integration code against current docs, never from training data.
**Why:** APIs change. Code written from memory uses deprecated endpoints, wrong parameters, or removed features.
**Apply when:** Writing or reviewing any third-party API integration.

---

## 5. Windows / Node.js Environment

### Path Normalization
**Rule:** Node.js `fs`/`execSync` need Windows paths, not Git Bash `/c/` paths. Normalize with `path.replace(/^\/([a-zA-Z])\//, "$1:/")`.
**Why:** Git Bash translates paths for shell commands but Node.js APIs expect native Windows paths.
**Apply when:** Any Node.js code that receives paths from Git Bash or environment variables.

### Agent SDK on Windows
**Rule:** Agent SDK needs Windows-format `pathToClaudeCodeExecutable` and `cwd` (e.g., `C:\\Users\\...`).
**Why:** Unix-style paths cause "file not found" errors that do not mention the path, making them hard to debug.
**Apply when:** Configuring Agent SDK on Windows.

---

## 6. Database & Data

### GROUP BY Semantics
**Rule:** `GROUP BY` name columns creates duplicates when data has variants. `GROUP BY` id only, use `MODE()` for display names.
**Why:** Invisible whitespace and encoding differences cause silent data duplication in aggregates.
**Apply when:** Writing aggregate queries on any user-facing text column.

### Type Coercion Across Stack
**Rule:** PostgreSQL `ROUND()` returns `Decimal`, FastAPI serializes it as a string, frontend `.toFixed()` crashes silently. Cast to `float()` at the API boundary.
**Why:** Type mismatches across language boundaries produce silent failures, not errors.
**Apply when:** Passing numeric values across database, API, and frontend layers.

### Large Aggregations
**Rule:** Never aggregate 2M+ rows per request on constrained environments. Use pre-aggregated tables with bounded enrichment queries.
**Why:** Unbounded aggregation causes timeouts, memory exhaustion, and cascading failures.
**Apply when:** Building analytics or reporting features on datasets that grow over time.

---

## 7. Configuration & MCP

### MCP Config Location
**Rule:** MCP config lives in `~/.claude.json`, not `~/.claude/.mcp.json`.
**Why:** Wrong location silently disables all MCP servers with no error message.
**Apply when:** Setting up or debugging MCP server configuration.

---

## 8. Multi-Phase Execution

### Phase Boundaries
**Rule:** Respect phase boundaries in multi-phase plans. Executing everything at once causes errors to compound.
**Why:** Phase 2 assumptions depend on phase 1 results. Skipping ahead means building on unverified foundations.
**Apply when:** Any multi-step plan where later steps depend on earlier results.

### Plan Persistence
**Rule:** Persist plans before starting new sessions. Conversation context is ephemeral.
**Why:** Session boundaries, compaction, and crashes lose the plan. Without persistence, the next session starts from scratch.
**Apply when:** Any multi-session project or task that spans conversation boundaries.

### Agent Runner Safety
**Rule:** Never restart the agent-runner while agents are running. Check `/health` first.
**Why:** Running agents lose all progress and may leave artifacts in an inconsistent state.
**Apply when:** Restarting or redeploying any orchestration service.

---

## 9. Frontend / React

### Stale Closures in Async Callbacks
**Rule:** `useCallback` captures stale state. Use `useRef` for mutable state accessed in async callbacks.
**Why:** Closures capture the value at render time. Async callbacks that run later see outdated values.
**Apply when:** Using `useCallback` or `useEffect` with state that changes between the closure creation and execution.

### Scope Performance Fixes
**Rule:** Scope performance optimizations to the actual problem. Do not disable a feature for all cases when only one case is slow.
**Why:** Broad fixes create regressions. A heavy query on one page does not justify removing functionality site-wide.
**Apply when:** Fixing performance issues -- measure first, scope the fix to the bottleneck.

### Sync I/O in Async Endpoints
**Rule:** Sync I/O in async endpoints blocks the event loop. Wrap in `run_in_executor` and serialize non-thread-safe resources with a `Lock`.
**Why:** A single blocking call stalls all concurrent requests, causing cascading timeouts.
**Apply when:** Calling file I/O, subprocess, or CPU-bound code from async Python (FastAPI, aiohttp) or Node.js handlers.

---

## 10. ML / Data Science

### Data Leakage Detection
**Rule:** If AUC > 0.85 on real-world problems, something is almost certainly leaking. AUC jump > 0.03 from adding a few features should trigger a leak audit.
**Why:** Real-world prediction problems are noisy. Suspiciously good metrics usually mean test data leaked into training.
**Apply when:** Evaluating model performance, especially after adding new features.

### Train/Serve Skew
**Rule:** Never use alias dicts to reconcile feature names between training and serving. Put "MUST MATCH" comments in both files.
**Why:** Alias dicts mask divergence. When training uses one name and serving uses another, predictions silently degrade.
**Apply when:** Any ML system where feature engineering happens in separate training and serving codepaths.
