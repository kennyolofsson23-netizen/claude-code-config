---
name: feedback_no_shortcuts
description: Never use fallback values or band-aid fixes — find and fix the root cause
type: feedback
---

NEVER add fallback/default values to paper over failures. If data is null, fix WHY it's null.

**Why:** Kenny explicitly called out a fallback geoScore (structural * 0.8) as a "band shit fix." The real problem was the quality judge returning markdown instead of JSON — the parser was fine, the agent prompt wasn't forceful enough.

**How to apply:** When a value is unexpectedly null/missing, trace the full data path to find where the failure occurs. Add logging to capture the actual output, fix the source of the problem, not the consumer.
