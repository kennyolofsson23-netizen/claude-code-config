---
name: project_race_video_analysis
description: Future idea — analyze ATG Play race videos/commentary to extract ML features (pace, incidents, race style)
type: project
---

Use ATG Play's race archive (GraphQL at `prod.streaming.aws.atg.se` + Contentful CMS) to analyze race content by race ID.

**Why:** Race replays contain context that raw results don't capture — pace scenarios, traffic problems, wide trips, breaks in stride, driver decisions. Extracting this as structured data would give the ML model features no competitor has.

**How to apply:** Build after ATG Play scraper (S8 Session 6) proves the API access pattern works. Potential pipeline:
1. Match race IDs to ATG Play video entries
2. Extract audio from race commentary (Swedish)
3. Transcribe via Groq Whisper (Swedish language)
4. NER extraction: horse names, incidents, pace descriptions, driver commentary
5. Structure as features: `horse_had_traffic_problems`, `horse_broke_stride`, `horse_wide_trip`, `race_pace_fast/slow`
6. Feed into ML as "race context" features for future predictions

**Dependencies:** ATG Play Contentful access (Session 6), Groq Whisper (already integrated), NER pipeline (Session 1 content engine)
