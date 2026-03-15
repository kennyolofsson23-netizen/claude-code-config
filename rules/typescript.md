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
- Node path: `C:\Program Files\nodejs\node.exe`
- npm global: `C:\Users\Kenny\AppData\Roaming\npm\`
- Use full paths for node/npm when Git Bash can't find them
