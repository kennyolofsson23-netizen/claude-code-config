# Image Generation Providers

<!-- Updated: 2026-03-12 -->
<!-- Used by: ads-generate, ads-photoshoot, generate_image.py -->

## Provider Overview

| Provider | Env Var | Default Model | Package |
|----------|---------|---------------|---------|
| `gemini` (default) | `GOOGLE_API_KEY` | `gemini-2.5-flash-image` | `google-genai>=1.16.0` |
| `openai` | `OPENAI_API_KEY` | `gpt-image-1` | `openai>=1.75.0` |
| `stability` | `STABILITY_API_KEY` | `stable-diffusion-3.5-large` | `stability-sdk>=0.8.4` |
| `replicate` | `REPLICATE_API_TOKEN` | `black-forest-labs/flux-1.1-pro` | `replicate>=1.0.4` |

Set provider via environment variable:
```bash
export ADS_IMAGE_PROVIDER="gemini"    # default
export ADS_IMAGE_PROVIDER="openai"
```

---

## Pricing Reference (2026)

### Gemini (`gemini-2.5-flash-image`)

| Resolution | Standard | Batch API (50% off) |
|------------|----------|---------------------|
| 512px | $0.045/image | $0.023/image |
| 1K (default) | $0.067/image | $0.034/image |
| 2K | $0.101/image | $0.051/image |
| 4K | $0.151/image | $0.076/image |

**Batch API**: 24-hour turnaround. Pass `--batch prompts.json` to `generate_image.py`.
Use for bulk campaign generation (10+ images). Not available for interactive single-image calls.

**Deprecated model**: `gemini-3-pro-image-preview` (Nano Banana Pro) was shut down March 9, 2026.
Official migration path: `gemini-3.1-flash-image-preview` (Nano Banana 2, per Google docs).

**Preview upgrade**: `gemini-3.1-flash-image-preview` (Nano Banana 2) is available for higher quality
but carries preview status — Google may update behavior without the GA deprecation notice window.
Override: `python generate_image.py "prompt" --model gemini-3.1-flash-image-preview`

### OpenAI (`gpt-image-1`)

| Size | Price |
|------|-------|
| 1024×1024 (1:1) | ~$0.040/image |
| 1024×1536 or 1536×1024 | ~$0.060/image |

No batch discount. Inline only.

### Stability AI (`stable-diffusion-3.5-large`)

~$0.065/image flat. Inline generation. Good for photorealistic product shots.

### Replicate (`black-forest-labs/flux-1.1-pro`)

~$0.055/image. Inline. FLUX.1 Pro has strong prompt adherence and text rendering.

---

## Model Capabilities by Provider

| Capability | Gemini | OpenAI | Stability | Replicate |
|-----------|--------|--------|-----------|-----------|
| Text rendering accuracy | High (94%+) | High | Medium | High |
| Brand color adherence | Good | Good | Good | Excellent |
| Multi-image input (up to 14) | Yes | No | No | No |
| Web search grounding | Yes | No | No | No |
| SynthID watermark | Yes | No | No | No |
| Batch API | Yes | No | No | No |
| Max aspect ratios | 14 | 3 | 8 | 12 |

---

## Supported Aspect Ratios

### Gemini (all 14 ratios)

`1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`,
`8:1`, `9:16`, `16:9`, `21:9`

### generate_image.py Ratio Aliases

The script maps ad-friendly shorthand to API ratio strings:

| Alias | API ratio | Dimensions | Used for |
|-------|-----------|-----------|---------|
| `1:1` | `1:1` | 1080×1080 | Meta Feed, LinkedIn, Carousel |
| `9:16` | `9:16` | 1080×1920 | TikTok, Reels, Shorts, Stories |
| `16:9` | `16:9` | 1920×1080 | YouTube, Google Display |
| `4:5` | `4:5` | 1080×1350 | Meta Feed (preferred) |
| `1.91:1` | `16:9` (closest) | 1200×628 | Google PMax, LinkedIn |
| `4:1` | `4:1` | 1200×300 | Google Logo landscape |

Note: Gemini does not natively support `1.91:1`. The script maps it to `16:9` (closest
supported Gemini ratio: 1.78 vs 1.33 for `4:3`). For exact 1200×628 output, crop the
generated 1920×1080 image with Pillow or any image editor after download.

---

## Setup Instructions

### Gemini (recommended)

```bash
# 1. Get API key
# Visit: console.cloud.google.com/apis/credentials
# Enable: "Generative Language API"

# 2. Set env var
export GOOGLE_API_KEY="AIza..."

# 3. Install package
pip install google-genai>=1.16.0

# 4. Test
python ~/.claude/skills/ads/scripts/generate_image.py \
  "professional ad for software product" --ratio 16:9 --json
```

### OpenAI

```bash
export ADS_IMAGE_PROVIDER="openai"
export OPENAI_API_KEY="sk-..."
pip install openai>=1.75.0
```

### Stability AI

```bash
export ADS_IMAGE_PROVIDER="stability"
export STABILITY_API_KEY="sk-..."
pip install stability-sdk>=0.8.4
```

### Replicate

```bash
export ADS_IMAGE_PROVIDER="replicate"
export REPLICATE_API_TOKEN="r8_..."
pip install replicate>=1.0.4
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `GOOGLE_API_KEY not set` | Missing env var | `export GOOGLE_API_KEY="..."` |
| `ImportError: google.genai` | Package not installed | `pip install google-genai` |
| `429 Too Many Requests` | Rate limit hit | Script uses exponential backoff; wait and retry |
| `Image generation blocked` | Safety filter | Rephrase prompt; remove potentially flagged terms |
| `aspect_ratio not supported` | Invalid ratio for provider | Check supported ratios table above |

---

## Rate Limits (Gemini)

| Tier | RPM | Daily Images |
|------|-----|-------------|
| Free | 5 | 100 |
| Tier 1 (<$250 spend) | 15 | 1,500 |
| Tier 2 (>$250 spend) | 1,000+ | Unlimited |

For bulk campaign generation (10+ images/session), Tier 2 is recommended.
The script implements exponential backoff (1s, 2s, 4s, 8s) for 429 errors.
