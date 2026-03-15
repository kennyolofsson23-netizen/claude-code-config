---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.py"
  - "**/*.go"
  - "**/*.rs"
---
# Coding Style — Enforced Limits

- Max file length: 300 lines. Split into sub-modules if exceeded.
- Max function length: 40 lines. Extract helpers if exceeded.
- Max function parameters: 3. Use an options object for more.
- No nested ternaries.
- Index files re-export only — no logic.
