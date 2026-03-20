---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---
# TypeScript/JavaScript Rules
- After ANY .ts/.tsx change: run `npx tsc --noEmit` to verify types
- Run tests with: `pnpm test`
- Auto-formatted with prettier (enforced by hook, only if project has config)
- Use `node` and `npm`/`npx` from PATH — auto-detect with `which node`
