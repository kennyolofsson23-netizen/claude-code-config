---
name: feedback_trav_content_quality
description: Content quality rules for trav articles — naming, terminology, system sections
type: feedback
---

Never quote or name-drop video experts (no "Pihlström säger", no "YouTubern väljer", no "experten pekar ut"). Absorb the intelligence from transcripts and rewrite as Travmaskinen's own analysis. The reader should think our editorial team did the analysis, not that we summarized someone's YouTube video.

**Why:** Citing experts makes Travmaskinen look like a summary site, not a primary source. The transcripts are research input, not content to attribute.

**How to apply:** Update trav-content-writer agent prompt — transcripts are background intelligence only. Never attribute, quote, or reference the source. Rewrite insights in Travmaskinen's own voice.

---

The user-facing term for ML win probability is "AI%" or "AI-ranking", NOT "ML" or "ML%". Never expose internal ML terminology.

**Why:** "ML" means nothing to trav bettors. "AI%" is the brand term on Travmaskinen.

**How to apply:** Update trav-content-writer agent prompt and formatDataPackageForPrompt to use "AI%" instead of "ML" in all user-facing output.
