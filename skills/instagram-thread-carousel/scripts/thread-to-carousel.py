#!/usr/bin/env python3
"""
Thread-to-Carousel Generator

Converts a text thread into Instagram carousel slides styled as tweet/X post mockups.
Each slide renders a tweet-style card with profile pic, name, verified badge, handle,
tweet text, and optional embedded image.

Usage:
    python3 scripts/thread-to-carousel.py <config.json> [output_dir]

Config format: see SKILL.md for the full JSON schema.
"""

import json
import sys
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    from pilmoji import Pilmoji
    from pilmoji.source import AppleEmojiSource
    HAS_PILMOJI = True
except ImportError:
    HAS_PILMOJI = False

# ---------------------------------------------------------------------------
# Layout constants (1080x1350 — Instagram 4:5 portrait)
# ---------------------------------------------------------------------------
SLIDE_W = 1080
SLIDE_H = 1350

THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "text": "#0F1419",
        "handle": "#536471",
        "verified": "#1D9BF0",
        "divider": "#CFD9DE",
        "placeholder": "#CCD6DD",
    },
    "dark": {
        "bg": "#000000",
        "text": "#E7E9EA",
        "handle": "#71767B",
        "verified": "#1D9BF0",
        "divider": "#2F3336",
        "placeholder": "#2F3336",
    },
}

# Defaults — overwritten by _apply_theme() in main()
BG_COLOR = THEMES["light"]["bg"]
TEXT_COLOR = THEMES["light"]["text"]
HANDLE_COLOR = THEMES["light"]["handle"]
VERIFIED_BLUE = THEMES["light"]["verified"]
DIVIDER_COLOR = THEMES["light"]["divider"]
PLACEHOLDER_COLOR = THEMES["light"]["placeholder"]

PADDING_X = 80
PROFILE_SIZE = 80
NAME_SIZE = 34
HANDLE_SIZE = 34
TWEET_SIZE = 46
TWEET_LINE_HEIGHT = 1.50
NAME_HANDLE_GAP = 8
HEADER_TEXT_GAP = 28
TEXT_IMAGE_GAP = 40
TWEET_GAP = 60          # vertical space between two tweets on same slide
IMAGE_RADIUS = 20

# Max height budget per tweet when fitting 2 on a slide
MAX_SINGLE_TWEET_H = SLIDE_H - 160   # generous single-tweet budget
MAX_DOUBLE_TWEET_H = (SLIDE_H - TWEET_GAP - 120) // 2


# ---------------------------------------------------------------------------
# Font loading with cross-platform fallbacks
# ---------------------------------------------------------------------------
def _find_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    # Last resort
    try:
        return ImageFont.truetype("Arial", size)
    except (OSError, IOError):
        return ImageFont.load_default(size)


def load_fonts():
    bold_candidates = [
        # macOS
        "/System/Library/Fonts/SFNSTextBold.otf",
        "/Library/Fonts/SF-Pro-Display-Bold.otf",
        "/Library/Fonts/SF-Pro-Text-Bold.otf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    regular_candidates = [
        # macOS
        "/System/Library/Fonts/SFNSText.otf",
        "/Library/Fonts/SF-Pro-Display-Regular.otf",
        "/Library/Fonts/SF-Pro-Text-Regular.otf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
    ]
    return {
        "name_bold": _find_font(bold_candidates, NAME_SIZE),
        "handle": _find_font(regular_candidates, HANDLE_SIZE),
        "tweet": _find_font(regular_candidates, TWEET_SIZE),
    }


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def make_circular(img, size):
    """Crop an image into a circle with a solid background behind transparent areas."""
    img = img.convert("RGBA").resize((size, size), Image.LANCZOS)
    # Composite onto a black background so transparent headshots look clean
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    bg.paste(img, (0, 0), img)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


def draw_verified_badge(draw, x, y, size=28):
    """Draw a blue verified badge with white checkmark."""
    draw.ellipse([x, y, x + size, y + size], fill=VERIFIED_BLUE)
    # Checkmark coordinates relative to badge center
    cx, cy = x + size / 2, y + size / 2
    r = size * 0.28
    points = [
        (cx - r * 0.9, cy + r * 0.05),
        (cx - r * 0.15, cy + r * 0.75),
        (cx + r * 1.0, cy - r * 0.7),
    ]
    draw.line(points, fill="white", width=max(3, int(size * 0.13)))


def round_corners(img, radius):
    """Add rounded corners to an image."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.size[0], img.size[1]], radius=radius, fill=255
    )
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def wrap_text(text, font, max_width, draw):
    """Word-wrap text preserving explicit newlines."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph.strip() == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        cur = ""
        for word in words:
            test = f"{cur} {word}".strip() if cur else word
            w = draw.textbbox((0, 0), test, font=font)[2]
            if w <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Tweet measurement & rendering
# ---------------------------------------------------------------------------
def _text_block_height(lines, font_size):
    """Height of wrapped text lines."""
    line_h = int(font_size * TWEET_LINE_HEIGHT)
    h = 0
    for line in lines:
        if line == "":
            h += int(line_h * 0.55)
        else:
            h += line_h
    return h


def measure_tweet(tweet, profile, fonts, max_text_w, draw):
    """Return the total pixel height a tweet will occupy."""
    h = PROFILE_SIZE + HEADER_TEXT_GAP
    lines = wrap_text(tweet["text"], fonts["tweet"], max_text_w, draw)
    h += _text_block_height(lines, TWEET_SIZE)
    if tweet.get("image") and os.path.exists(tweet["image"]):
        h += TEXT_IMAGE_GAP
        img = Image.open(tweet["image"])
        aspect = img.height / img.width
        h += int(max_text_w * aspect)
    return h


def _is_gif(path):
    """Check if a file is an animated GIF."""
    if not path.lower().endswith(".gif"):
        return False
    try:
        img = Image.open(path)
        return getattr(img, "is_animated", False)
    except Exception:
        return False


def draw_tweet(canvas, draw, tweet, profile, fonts, x, y, max_text_w, skip_gif=False):
    """Render one tweet mockup at (x, y).
    Returns (end_y, gif_rect) where gif_rect is (x, y, w, h, path) if a GIF
    was skipped, else None."""
    gif_rect = None

    # --- Profile pic ---
    headshot_path = profile.get("headshot", "")
    if headshot_path and os.path.exists(headshot_path):
        pic = make_circular(Image.open(headshot_path), PROFILE_SIZE)
        canvas.paste(pic, (x, y), pic)
    else:
        draw.ellipse(
            [x, y, x + PROFILE_SIZE, y + PROFILE_SIZE], fill=PLACEHOLDER_COLOR
        )

    # --- Name + badge + handle (single row) ---
    nx = x + PROFILE_SIZE + 16
    ny = y + (PROFILE_SIZE - NAME_SIZE) // 2 - 4

    name = profile.get("name", "Name")
    name_w = draw.textbbox((0, 0), name, font=fonts["name_bold"])[2]
    draw.text((nx, ny), name, fill=TEXT_COLOR, font=fonts["name_bold"])

    cursor_x = nx + name_w + NAME_HANDLE_GAP
    if profile.get("verified", False):
        badge_y = ny + (NAME_SIZE - 28) // 2 + 2
        draw_verified_badge(draw, cursor_x, badge_y, size=28)
        cursor_x += 28 + NAME_HANDLE_GAP

    handle = profile.get("handle", "@handle")
    draw.text((cursor_x, ny), handle, fill=HANDLE_COLOR, font=fonts["handle"])

    # --- Tweet text ---
    ty = y + PROFILE_SIZE + HEADER_TEXT_GAP
    lines = wrap_text(tweet["text"], fonts["tweet"], max_text_w, draw)
    line_h = int(TWEET_SIZE * TWEET_LINE_HEIGHT)

    if HAS_PILMOJI:
        with Pilmoji(canvas, source=AppleEmojiSource) as pmoji:
            for line in lines:
                if line == "":
                    ty += int(line_h * 0.55)
                    continue
                pmoji.text((x, ty), line, fill=TEXT_COLOR, font=fonts["tweet"], emoji_position_offset=(0, -6))
                ty += line_h
    else:
        for line in lines:
            if line == "":
                ty += int(line_h * 0.55)
                continue
            draw.text((x, ty), line, fill=TEXT_COLOR, font=fonts["tweet"])
            ty += line_h

    # --- Embedded image ---
    if tweet.get("image") and os.path.exists(tweet["image"]):
        ty += TEXT_IMAGE_GAP
        img = Image.open(tweet["image"])
        first_frame = img.convert("RGBA")
        aspect = first_frame.height / first_frame.width
        img_w = max_text_w
        img_h = int(img_w * aspect)

        if skip_gif and _is_gif(tweet["image"]):
            # Don't draw — return placement info for animated compositing
            gif_rect = (x, ty, img_w, img_h, tweet["image"])
        else:
            resized = first_frame.resize((img_w, img_h), Image.LANCZOS)
            resized = round_corners(resized, IMAGE_RADIUS)
            canvas.paste(resized, (x, ty), resized)
        ty += img_h

    return ty, gif_rect


# ---------------------------------------------------------------------------
# Slide generation
# ---------------------------------------------------------------------------
def _slide_has_gif(tweets):
    """Check if any tweet in a slide references an animated GIF."""
    for t in tweets:
        img_path = t.get("image", "")
        if img_path and os.path.exists(img_path) and _is_gif(img_path):
            return True
    return False


def generate_gif_slide(slide_tweets, profile, fonts, output_path):
    """Generate an animated GIF slide by compositing GIF frames onto a static base."""
    # Step 1: Render the static base (text, profile, etc.) with GIF area blank
    base = Image.new("RGB", (SLIDE_W, SLIDE_H), BG_COLOR)
    draw = ImageDraw.Draw(base)
    max_text_w = SLIDE_W - PADDING_X * 2
    gif_rect = None

    if len(slide_tweets) == 1:
        h = measure_tweet(slide_tweets[0], profile, fonts, max_text_w, draw)
        start_y = max(60, (SLIDE_H - h) // 2)
        _, gif_rect = draw_tweet(
            base, draw, slide_tweets[0], profile, fonts, PADDING_X, start_y, max_text_w,
            skip_gif=True,
        )
    elif len(slide_tweets) >= 2:
        h1 = measure_tweet(slide_tweets[0], profile, fonts, max_text_w, draw)
        h2 = measure_tweet(slide_tweets[1], profile, fonts, max_text_w, draw)
        total = h1 + TWEET_GAP + h2
        start_y = max(40, (SLIDE_H - total) // 2)

        end_y1, rect1 = draw_tweet(
            base, draw, slide_tweets[0], profile, fonts, PADDING_X, start_y, max_text_w,
            skip_gif=True,
        )
        gif_rect = gif_rect or rect1

        div_y = end_y1 + TWEET_GAP // 2
        draw.line(
            [(PADDING_X, div_y), (SLIDE_W - PADDING_X, div_y)],
            fill=DIVIDER_COLOR, width=2,
        )

        start_y2 = end_y1 + TWEET_GAP
        _, rect2 = draw_tweet(
            base, draw, slide_tweets[1], profile, fonts, PADDING_X, start_y2, max_text_w,
            skip_gif=True,
        )
        gif_rect = gif_rect or rect2

    if not gif_rect:
        # No GIF found (shouldn't happen), fall back to static
        base.save(output_path, "PNG", quality=95)
        return output_path

    gx, gy, gw, gh, gif_path = gif_rect

    # Step 2: Extract GIF frames and composite each onto the base
    src_gif = Image.open(gif_path)
    frames = []
    durations = []

    try:
        while True:
            frame = src_gif.convert("RGBA")
            frame = frame.resize((gw, gh), Image.LANCZOS)

            # Composite onto a copy of the base
            composite = base.copy().convert("RGBA")
            composite.paste(frame, (gx, gy), frame)
            # Convert to P mode (palette) for GIF saving
            frames.append(composite.convert("RGB"))
            durations.append(src_gif.info.get("duration", 100))

            src_gif.seek(src_gif.tell() + 1)
    except EOFError:
        pass

    if not frames:
        base.save(output_path, "PNG", quality=95)
        return output_path

    # Step 3: Save a static PNG preview (first frame) for safe display in chat
    preview_path = Path(output_path).with_suffix(".png")
    frames[0].save(str(preview_path), "PNG", quality=95)

    # Step 4: Save as MP4 via ffmpeg (full color, small file, Instagram-ready)
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        # No ffmpeg — fall back to GIF
        gif_output = Path(output_path).with_suffix(".gif")
        frames[0].save(
            gif_output, save_all=True, append_images=frames[1:],
            duration=durations, loop=0, optimize=True,
        )
        return str(gif_output)

    mp4_output = Path(output_path).with_suffix(".mp4")

    # Calculate average FPS from frame durations (GIF durations are in ms)
    avg_duration_ms = sum(durations) / len(durations) if durations else 100
    fps = 1000.0 / max(avg_duration_ms, 1)

    # Repeat frames so the video is at least 3 seconds (Instagram minimum)
    total_duration_s = sum(durations) / 1000.0
    loops = max(1, int(3.0 / total_duration_s) + 1) if total_duration_s < 3.0 else 1
    looped_frames = frames * loops

    # Pipe raw RGB frames to ffmpeg
    proc = subprocess.Popen(
        [
            ffmpeg_bin, "-y",
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{SLIDE_W}x{SLIDE_H}",
            "-r", str(fps),
            "-i", "pipe:0",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "slow",
            "-movflags", "+faststart",
            str(mp4_output),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    for frame in looped_frames:
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        stderr = proc.stderr.read().decode()
        print(f"  Warning: ffmpeg failed (exit {proc.returncode}): {stderr[:200]}")
        # Fallback: save as GIF
        gif_output = Path(output_path).with_suffix(".gif")
        frames[0].save(
            gif_output, save_all=True, append_images=frames[1:],
            duration=durations, loop=0, optimize=True,
        )
        return str(gif_output)

    return str(mp4_output)


def handle_video_slide(video_path, output_path):
    """Copy a video file as a carousel slide and extract a PNG preview frame."""
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    mp4_output = Path(output_path).with_suffix(".mp4")
    preview_output = Path(output_path).with_suffix(".png")

    # Copy (or symlink) the video to the output
    shutil.copy2(video_path, str(mp4_output))

    # Extract first frame as PNG preview
    if os.path.exists(ffmpeg_bin):
        subprocess.run(
            [
                ffmpeg_bin, "-y",
                "-i", str(mp4_output),
                "-vframes", "1",
                "-update", "1",
                "-q:v", "2",
                str(preview_output),
            ],
            capture_output=True,
            timeout=30,
        )

    return str(mp4_output)


def generate_slide(slide_tweets, profile, fonts, output_path):
    """Generate one carousel slide. Outputs animated GIF if tweet has a GIF, else PNG."""
    # Check for animated GIF — delegate to GIF renderer
    if _slide_has_gif(slide_tweets):
        return generate_gif_slide(slide_tweets, profile, fonts, output_path)

    canvas = Image.new("RGB", (SLIDE_W, SLIDE_H), BG_COLOR)
    draw = ImageDraw.Draw(canvas)
    max_text_w = SLIDE_W - PADDING_X * 2

    if len(slide_tweets) == 1:
        h = measure_tweet(slide_tweets[0], profile, fonts, max_text_w, draw)
        start_y = max(60, (SLIDE_H - h) // 2)
        draw_tweet(canvas, draw, slide_tweets[0], profile, fonts, PADDING_X, start_y, max_text_w)

    elif len(slide_tweets) >= 2:
        h1 = measure_tweet(slide_tweets[0], profile, fonts, max_text_w, draw)
        h2 = measure_tweet(slide_tweets[1], profile, fonts, max_text_w, draw)
        total = h1 + TWEET_GAP + h2
        start_y = max(40, (SLIDE_H - total) // 2)

        end_y1, _ = draw_tweet(
            canvas, draw, slide_tweets[0], profile, fonts, PADDING_X, start_y, max_text_w
        )

        div_y = end_y1 + TWEET_GAP // 2
        draw.line(
            [(PADDING_X, div_y), (SLIDE_W - PADDING_X, div_y)],
            fill=DIVIDER_COLOR,
            width=2,
        )

        start_y2 = end_y1 + TWEET_GAP
        draw_tweet(
            canvas, draw, slide_tweets[1], profile, fonts, PADDING_X, start_y2, max_text_w
        )

    canvas.save(output_path, "PNG", quality=95)
    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/thread-to-carousel.py <config.json> [output_dir]")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "workspace/carousel"

    with open(config_path, "r") as f:
        config = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    # Apply theme
    theme_name = config.get("theme", "light")
    if theme_name not in THEMES:
        print(f"  Warning: unknown theme '{theme_name}', falling back to 'light'")
        theme_name = "light"
    theme = THEMES[theme_name]
    global BG_COLOR, TEXT_COLOR, HANDLE_COLOR, VERIFIED_BLUE, DIVIDER_COLOR, PLACEHOLDER_COLOR
    BG_COLOR = theme["bg"]
    TEXT_COLOR = theme["text"]
    HANDLE_COLOR = theme["handle"]
    VERIFIED_BLUE = theme["verified"]
    DIVIDER_COLOR = theme["divider"]
    PLACEHOLDER_COLOR = theme["placeholder"]

    profile = config["profile"]
    slides = config["slides"]
    fonts = load_fonts()

    generated = []
    for i, slide in enumerate(slides):
        path = os.path.join(output_dir, f"slide-{i + 1:02d}.png")

        # Video slide — copy MP4 directly instead of generating a tweet card
        if slide.get("video") and os.path.exists(slide["video"]):
            result = handle_video_slide(slide["video"], path)
            generated.append(result)
            print(f"  [{i + 1}/{len(slides)}] {result} (video)")
            continue

        generate_slide(slide["tweets"], profile, fonts, path)
        generated.append(path)
        print(f"  [{i + 1}/{len(slides)}] {path}")

    print(f"\nDone — {len(generated)} slides saved to {output_dir}/")


if __name__ == "__main__":
    main()
