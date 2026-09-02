---
name: feedback_v85_vercel_cli_too_large
description: V85 repo exceeds 2GB Vercel CLI upload limit — use git push to trigger GitHub integration deploy instead
type: feedback
---

V85 monorepo is ~3GB which exceeds Vercel CLI's 2GB upload limit. `npx vercel --prod` fails with "File size greater than 2 GiB".

**Why:** The repo contains ML models, event data, and backend code alongside the web app.

**How to apply:** For V85, always deploy via `git push` to trigger Vercel's GitHub integration. Never use `npx vercel --prod` from the V85 directory. Verify deploy status with `npx vercel ls v85-web`.
