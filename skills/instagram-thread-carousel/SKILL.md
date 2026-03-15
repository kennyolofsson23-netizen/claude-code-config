---
name: instagram-thread-carousel
description: Use when the user wants to turn a text thread into an Instagram carousel that looks like tweet/X post screenshots. Generates slide images with profile pic, name, verified badge, handle, and tweet text. Supports embedded images and combining short tweets on one slide.
---

# Thread-to-Carousel Generator

Convert a text thread into Instagram carousel slides styled as tweet/X post mockups. Each slide renders a clean tweet card with profile picture, display name, verified badge, handle, and the tweet text. Optionally embed images in tweets and combine short tweets 2-per-slide.

---

## Process

### Step 1: Gather the Thread

Get the thread content from the user. They may:
- Paste a thread of text directly
- Provide a topic and ask you to write the thread
- Share screenshots or existing tweets to recreate

If writing the thread, use the voice and tone from `CLAUDE.md`. Each tweet in the thread should be a self-contained thought that flows into the next.

### Step 2: Gather Profile Info

Ask for anything not already known:

1. **Display name** - the bold name shown on each tweet
2. **Handle** - e.g., `@itstylergermain`
3. **Verified** - show the blue checkmark? (default: true)
4. **Headshot** - path to profile photo. List available files with `ls .claude/skills/instagram-thread-carousel/headshots/` and let the user pick, or use the first one found.

If `CLAUDE.md` has been personalized (audit has been run), pull the name and handle from there.

### Step 3: Break the Thread into Slides

Rules for slide layout:

**One tweet per slide (default):**
- Any tweet with an embedded image gets its own slide
- Tweets longer than ~200 characters get their own slide
- The first tweet (hook) always gets its own slide
- **The title slide (slide 1) should ALWAYS have an image.** A strong image on the first slide is critical for stopping the scroll.

**Two tweets per slide:**
- Combine consecutive short tweets (under ~150 characters each, no images) onto one slide
- This keeps the carousel compact and scannable
- A light gray divider line separates the two tweets

Walk through the thread and decide the slide breakdown. Present it to the user before generating:

```
Slide 1: Tweet 1 (hook) - own slide
Slide 2: Tweet 2 + Tweet 3 - combined (both short)
Slide 3: Tweet 4 - own slide (has image)
Slide 4: Tweet 5 + Tweet 6 - combined (both short)
Slide 5: Tweet 7 (CTA) - own slide
```

### Step 4: Handle Images

Images make carousels significantly more engaging. For each tweet that could benefit from a visual, determine how to source the image:

**User-provided images:**
- The user provides file paths or URLs directly
- If they provide URLs, download the images to the carousel's `ref/` subfolder first

**Search for images with Tavily:**
If the user doesn't provide images (or asks you to find them), use the Tavily image search script to find relevant visuals:

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/tavily-image-search.py "search query" workspace/<date>/<title>/ref --count 5
```

This downloads images and creates a manifest JSON. Review the downloaded images and pick the best ones for each tweet. Good search queries are specific - e.g., "YouTube thumbnail example tech channel" not just "thumbnail".

Requires `TAVILY_API_KEY` in `.env`. If not set, skip image search and proceed with text-only slides.

**Search for GIFs with Giphy:**
When the carousel calls for animated content (reaction GIFs, demonstrations, etc.):

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/giphy-search.py "search query" workspace/<date>/<title>/ref --count 5
```

Downloads GIFs and creates a manifest JSON. The thread-to-carousel script automatically handles animated GIFs by outputting both an MP4 (for Instagram) and a PNG (static preview).

Requires `GIPHY_API_KEY` in `.env`.

**Website screenshots:**
When the carousel is about a website, product, or tool, take a fresh screenshot instead of relying on Tavily (which often returns outdated images):

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/website-screenshot.py "https://example.com" workspace/<date>/<title>/ref/homepage.png --width 1280 --height 800
```

Options: `--width` and `--height` set the viewport, `--full-page` captures the entire scrollable page. Requires `playwright` (`pip install playwright && playwright install chromium`).

Always prefer a live screenshot over a Tavily image search result when the carousel is about a specific website or product.

**Website recordings with Steel:**
When you need a video recording of browsing a website (for animated carousel slides or reference), use the Steel browser:

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/steel-browse.py browse-plan.json workspace/<date>/<title>/ref
```

Create a `browse-plan.json` with a list of actions:
```json
{
  "viewport": { "width": 1920, "height": 1080 },
  "actions": [
    { "action": "navigate", "url": "https://example.com", "label": "Open homepage", "wait": 2000 },
    { "action": "click", "selector": "button.cta", "label": "Click CTA", "wait": 1500 },
    { "action": "click_at", "x": 960, "y": 540, "label": "Click center", "wait": 1000 },
    { "action": "scroll", "y": 500, "label": "Scroll down", "wait": 1000 },
    { "action": "hover", "selector": ".card", "label": "Hover card", "wait": 1000 },
    { "action": "type", "selector": "input.search", "text": "query", "label": "Type search", "wait": 1000 },
    { "action": "keyboard_type", "text": "hello world", "label": "Type text", "wait": 1000 },
    { "action": "keyboard_press", "key": "Enter", "label": "Press Enter", "wait": 1000 }
  ]
}
```

Outputs `recording.mp4` and `moments.json` to the output directory. Requires `STEEL_API_KEY` in `.env` and `pip install steel-sdk playwright`.

**Image rules:**
- Images appear below the tweet text with rounded corners
- Tweets with images always get their own slide (the image needs the space)
- Prefer landscape or square images - very tall images eat too much slide space
- Screenshots, product shots, and UI mockups work best for this format

### Step 5: Generate the Config

Each carousel gets its own folder under `workspace/` organized by date and title. Pick a short, descriptive name based on the topic (e.g., `thumbnail-generator`, `claude-youtube`, `ai-agents-101`).

Folder structure:
```
workspace/<date>/<title>/
├── config.json        # Slide config
├── ref/               # Reference images used in slides
│   ├── screenshot.png
│   └── ...
├── slide-01.png       # Generated slides
├── slide-02.png
└── ...
```

Create the config file at `workspace/<date>/<title>/config.json`:

```json
{
  "profile": {
    "name": "Display Name",
    "handle": "@handle",
    "verified": true,
    "headshot": ".claude/skills/instagram-thread-carousel/headshots/tyler-headshot.png"
  },
  "theme": "light",
  "slides": [
    {
      "tweets": [
        {
          "text": "This is the first tweet.\n\nIt can have multiple paragraphs.\n\nUse \\n for line breaks.",
          "image": null
        }
      ]
    },
    {
      "video": "workspace/<date>/<title>/ref/demo.mp4"
    },
    {
      "tweets": [
        { "text": "Short tweet one.", "image": null },
        { "text": "Short tweet two.", "image": null }
      ]
    },
    {
      "tweets": [
        {
          "text": "Tweet with an image below it.",
          "image": "workspace/<date>/<title>/ref/screenshot.jpg"
        }
      ]
    }
  ]
}
```

**Config options:**
- `theme` - `"light"` (white background, dark text) or `"dark"` (black background, light text). Default: `"light"`.

**Video slides:**
- Use `"video": "path/to/video.mp4"` at the slide level (no `tweets` needed)
- The script copies the MP4 to the output as `slide-XX.mp4` and extracts a `slide-XX.png` preview
- Instagram carousels support mixing images and videos - use video slides for screen recordings, demos, or animated content
- Use the screen-demo skill or Steel browser recordings to create polished demo videos, then reference the output MP4 in the carousel config
- Video slides do NOT render tweet-style cards - they're raw video files for Instagram

**Text formatting tips:**
- Use `\n` for line breaks within a tweet
- Use `\n\n` for paragraph breaks (adds extra spacing)
- Arrow bullets work: `→ Point one\n→ Point two`
- Emoji and special characters are supported (font-dependent)

### Step 6: Run the Script

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/thread-to-carousel.py workspace/<date>/<title>/config.json workspace/<date>/<title>
```

This generates numbered PNG files: `slide-01.png`, `slide-02.png`, etc. inside the carousel folder.

### Step 7: Present the Results

Show the user:
1. How many slides were generated
2. The folder path where everything is saved
3. Offer to adjust - re-run with different text, different slide breakdown, or different images

Read and display the generated slide images so the user can see them inline.

**Animated slides:** When a slide contains an animated GIF, the script outputs both an `.mp4` (full-color video for Instagram) and a `.png` (a static preview of the first frame). **Always display the `.png` preview** - never try to read the `.mp4` file directly. Tell the user the MP4 version is saved alongside it for posting.

---

## Text Style Guide

When writing threads for the user, follow these patterns from high-performing tweet-style carousels:

### Hook Tweet (Slide 1) - The Most Important Slide

The hook makes or breaks the entire carousel. A bad hook means zero impressions; a great hook stops the scroll. The thread hook must work as a **standalone tweet** - if it wouldn't perform on its own, it won't perform as a carousel opener either.

**Core principles:**
- The hook must **stop someone from scrolling**. If it doesn't interrupt, nothing else matters.
- The first line and second line must **connect logically**. A disconnected transition kills the hook.
- **Match market awareness.** Audiences are desensitized - "I make $10K/month" or "I'm a millionaire" doesn't stop anyone anymore. The claim has to be genuinely surprising for the current landscape.
- **Cast a wide net AND deliver on it.** A broad hook only works if the content actually applies to the wide audience you promised.

**Proven hook frameworks (master these first, then experiment):**

1. **Borrowed Authority** - Open with a well-known person's name, then follow with a surprising claim or hot take. The name grabs attention; the claim holds it.
   - "Chris Williamson is undergoing massive toxin-induced mental health issues"
   - "You can copy Donald Trump.\nYou can copy Barack Obama.\nYou can copy Bill Clinton."

2. **Surprising Statistic** - Lead with a specific, hard-to-ignore number. Stats create instant credibility and curiosity.
   - "99% of lottery winners go broke within 5 years."
   - "20+ years of business in a nutshell:"

3. **Direct Listicle** - State exactly what the list is about. No cleverness needed - the format itself stops the scroll. Listicles and how-tos are the two highest-performing written content formats on the internet.
   - "Signs of high vibration:"
   - "7 supplements I'm getting my aging parents to take:"

4. **High-TAM "Everyone" Hook** - Cast the widest possible net, but ONLY if the content genuinely delivers for that audience. A bad "everyone" hook claims breadth but delivers niche content.
   - GOOD: "Everyone on the planet should read this book" - recommends a universally applicable book
   - GOOD: "Everyone needs to hear this" - shares a universal life lesson
   - BAD: "Everyone's teaching you tactics" - pivots to niche entrepreneur advice

5. **Numbers Up Front** - Start the hook with a number. Specific numbers outperform vague claims.
   - "20+ years of business in a nutshell:"
   - "7 supplements I'm getting my aging parents to take:"

6. **Direct "You" Address** - Point directly at the reader. Make them feel personally called out.
   - "You have the exact same tax code as Donald Trump."
   - "You can copy Barack Obama."

**What kills a hook:**
- **Desensitized claims** - "I'm a millionaire" doesn't stand out anymore. If using a flex, it has to be genuinely extraordinary for the platform.
- **Disconnected lines** - The first and second lines must flow. "I'm a millionaire. If you suddenly become rich overnight..." doesn't connect.
- **Cliches** - "Playing checkers while a small group is playing chess" means nothing. Everyone can say it.
- **Wide net, narrow delivery** - Don't say "everyone" if the content only applies to a niche audience.
- **Unlikely scenarios** - "If you suddenly become rich overnight" is more likely to get dunked on than to get authentic engagement.

### Body Tweets

- One idea per tweet
- Use arrow bullets (→) for lists
- Break up dense info across multiple tweets
- Numbers and dollar amounts grab attention
- Short paragraphs with line breaks between them
- **Waterfall structure for lists:** Order list items from shortest to longest sentence length. This creates a staircase/waterfall visual that's aesthetically pleasing and makes people stop to read.
  ```
  → People stare at you
  → Kids like you
  → Animals feel safe around you
  → Strangers tell you their life story
  → You walk into a room and the energy shifts
  ```
- **Contrasting pairs work well for frameworks:** Alternate between two categories to create rhythm.
  ```
  Chess: manage their energy
  Checkers: manage their time
  Chess: optimize their psychology
  Checkers: optimize their funnel
  ```
- **7 is the sweet spot for listicles.** Not too short, not too long - scans well on a carousel.

### CTA Tweet (Last Slide)

- Clear call to action: follow, save, share, comment
- Can summarize the key takeaway
- Keep it short - the carousel already delivered the value

---

## Layout Reference

Each slide is 1080x1350px (Instagram 4:5 portrait).

**Single tweet slide:**
- White background (light theme) or black background (dark theme)
- Circular profile pic (80px) - top left
- Bold name + blue verified badge + gray handle - next to pic
- Tweet text - large, clean sans-serif, generous line spacing
- Optional image - full width, rounded corners, below text
- Content vertically centered on the slide

**Two-tweet slide:**
- Same layout, two tweets stacked
- Light gray divider line between them
- Both vertically centered together

---

## Generating Images for Slides

If the user doesn't have enough screenshots or reference images to fill out a carousel, generate them with Gemini. The script produces **16:9 landscape images** designed to embed inside carousel slides below the tweet text. It has a built-in style guide that ensures dark, moody, cinematic results matching the carousel aesthetic.

```bash
python3 .claude/skills/instagram-thread-carousel/scripts/generate_carousel_image.py \
    --prompt "description of the image you need" \
    --output workspace/<date>/<title>/ref/generated-image.png
```

**Options:**
- `--reference path/to/screenshot.png` - Pass existing images for context (e.g., a raw screenshot to stylize into a mockup)
- `--headshot .claude/skills/instagram-thread-carousel/headshots/tyler-headshot.png` - Include a person in the generated image
- `--examples path/to/style-ref.png` - Style inspiration images

Then reference the generated image in the slide config:
```json
{"text": "slide text here", "image": "workspace/<date>/<title>/ref/generated-image.png"}
```

### Good prompts for carousel images:

- **Product mockups:** "A sleek MacBook screen showing [product UI] floating on a dark cinematic background with subtle blue glow accents"
- **Concept illustrations:** "A dark moody illustration showing a terminal prompt on the left with a glowing arrow pointing to a finished YouTube thumbnail on the right"
- **Before/after:** "Split image: left side shows a messy manual process, right side shows clean automated output - dark tech aesthetic with cyan accents"
- **Process diagrams:** "Three connected nodes on a dark background showing: raw data → AI processing → polished output, with subtle neon connecting lines"
- **Styled screenshots:** Pass the raw screenshot as `--reference` and prompt: "Render this UI screenshot on an elegant floating device mockup with dramatic dark lighting and subtle shadow"

**Requires `GEMINI_API_KEY` in `.env`.**

---

## Troubleshooting

**Fonts look wrong:** The script tries SF Pro → Helvetica → Arial → DejaVu Sans. If none are found, it falls back to Pillow's default. Install a clean sans-serif font for best results.

**Text overflows the slide:** Break long tweets into multiple shorter ones. The script wraps text automatically, but very long tweets with images may push content off the bottom.

**Images look stretched:** Images maintain their aspect ratio. Very tall images will take up a lot of slide space - crop them to landscape or square before using.

**Profile pic not found:** Check the path in the config. Headshots should be in `.claude/skills/instagram-thread-carousel/headshots/`. The script draws a gray circle as a placeholder if no headshot is found.

**Animated slides look wrong or crash the session:** The script outputs `.mp4` (via ffmpeg) for animated slides instead of GIF, preserving full color. A `.png` preview is also saved for chat display. If ffmpeg is not installed, it falls back to GIF (which has color limitations). Install ffmpeg with `brew install ffmpeg`.

**Emoji rendering:** The script uses `pilmoji` with `AppleEmojiSource` for native Apple emoji rendering. If `pilmoji` is not installed (`pip3 install pilmoji`), emoji will render as blank squares. The emoji vertical alignment is corrected with `emoji_position_offset=(0, -6)` in the script.

---

## Image Fitting Rules

When a slide has both text AND an embedded image, the text must be short enough that the image isn't cut off or shrunk too small. Follow these rules:

**Slides with images should have SHORT text:**
- 1-3 short lines max when an image is present
- If the content needs more text, split it across two slides: one image slide with a brief label, and one text-only slide with the detail

**When the user provides their own images:**
- Always use the user's real screenshots/images over generated ones
- Check the image dimensions - landscape images fit best below tweet text
- If an image is getting cut off, shorten the text first before resizing the image

**Splitting content for image slides:**
Instead of cramming a long explanation + image onto one slide, do this:
- **Slide A (image slide):** Short punchy text (1-2 lines) + the image
- **Slide B (detail slide):** The longer explanation, text-only

This keeps image slides clean and readable at carousel-swiping speed.
