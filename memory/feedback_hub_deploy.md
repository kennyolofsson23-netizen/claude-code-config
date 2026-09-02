---
name: feedback_hub_deploy
description: Hub deploy requires no package-lock.json + no turbo.json + IIFE for CLI scripts (not top-level await)
type: feedback
---

Hub (usetools.dev) Vercel deploy has 3 known traps:

1. **No package-lock.json** — Vercel's Next.js detection fails to parse lockfiles from Node 24. Deploy without it.
2. **turbo.json in .vercelignore** — Turbo detection overrides rootDirectory. Already handled.
3. **Scripts must use static ESM imports** — `"type": "module"` means `require()` is undefined, but `await import()` fails in CJS mode. Solution: use plain `import fs from "node:fs"` at top level + `fileURLToPath(import.meta.url)` for __dirname. No IIFE, no require, no dynamic import.

**Why:** Spent 30+ failed deploys across two sessions. Node 22 on Vercel runs ESM when package.json has `"type": "module"` — so require() fails. But tsx locally transpiles to CJS where top-level await fails. Static ESM imports work in both.

**How to apply:** Deploy: `cp -r apps/hub /tmp/hub-deploy && rm -f /tmp/hub-deploy/package-lock.json && rm -r /tmp/hub-deploy/.next /tmp/hub-deploy/node_modules 2>/dev/null; cd /tmp/hub-deploy && vercel deploy --prod --yes --force`
