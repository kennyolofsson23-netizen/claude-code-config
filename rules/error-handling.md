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
# Error Handling — Anti-Patterns to Prevent

- No empty catch blocks (`catch (e) {}`). Always handle or re-throw with context.
- No swallowing errors silently. If caught, either handle meaningfully or propagate.
- Do not log AND throw the same error (causes duplicate logs). Pick one.
- Do not use exceptions for control flow (e.g., throw to exit a loop).
- Do not return null/undefined to signal failure. Use Result types or throw typed errors.
- Do not catch generic `Exception` in Python — catch specific exception types.
- Never expose stack traces, internal paths, or DB details in user-facing messages.
