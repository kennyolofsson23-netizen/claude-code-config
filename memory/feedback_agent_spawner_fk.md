---
name: Agent spawner FK constraint
description: AgentSession.brainstormId is a FK to Brainstorm, not Project — always pass brainstormId when spawning from Project context
type: feedback
---

AgentSession uses `brainstormId` (mapped as `projectId` column) which references the Brainstorm table. When spawning agents from a Project context (e.g., marketing campaigns), pass `project.brainstormId` not `project.id`.

**Why:** P2003 FK violation — marketing campaigns silently failed with 0 drafts because all agent spawns threw FK errors.

**How to apply:** Any code that calls `spawner.spawn({ projectId: ... })` from a Project context must look up and pass the project's `brainstormId`. This affects marketing-swarm.ts and any future Project-scoped agent spawning.
