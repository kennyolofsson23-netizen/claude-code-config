---
name: Never skip TDD even under time pressure
description: S2 shipped 739 lines across 6 files with zero tests — caught by Kenny. TDD is non-negotiable regardless of task complexity or momentum.
type: feedback
---

Never skip TDD, even when the code is "simple" or "just wiring."

**Why:** S2 (Score-to-Todo Engine) shipped a rules engine, 5 tRPC routes, and 2 dashboard pages with zero tests. Only manually tested via curl at the end. Kenny called it out — his #1 rule is 100% test coverage, no exceptions. Pure functions like rule generators are the easiest code to TDD and the least excusable to skip.

**How to apply:** Before writing ANY implementation code, write the failing test first. Even for "obvious" code like Prisma models or tRPC routes. If the session is about building features, the tests come first, not as a separate "testing session" afterward. The /tdd skill exists — use it.
