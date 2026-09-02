---
name: Prisma DLL lock on Windows
description: prisma generate fails with EPERM on Windows when node processes hold the query engine DLL — kill them first
type: feedback
---

`npx prisma generate` fails with `EPERM: operation not permitted, rename query_engine-windows.dll.node` when any Node process (dashboard dev server, agent-runner) has the Prisma client loaded.

**Why:** Windows locks DLLs loaded by running processes. Prisma generate tries to overwrite the DLL.

**How to apply:** Before running `prisma generate`, find and kill Node processes holding the DLL:
```powershell
Get-Process | Where-Object { $_.Modules.FileName -like '*query_engine*' } | Select-Object Id, ProcessName
```
Then `taskkill //PID <pid> //F` and retry generate.

Also: `prisma db push` is safe for additive schema changes (new columns, new enum values) without data loss. Use it instead of `migrate reset` when there's migration drift on a dev DB with data you want to keep.
