#!/usr/bin/env python3
"""
Generate carousel-ready concept images using Gemini 3 Pro Image Preview.

Produces 16:9 landscape images suitable for embedding inside
Instagram carousel slides below tweet text. Use when you need concept
illustrations, styled screenshots, or product mockups to fill out a carousel.

Usage:
    python3 scripts/generate_carousel_image.py \
        --prompt "A dark terminal showing Claude Code output" \
        --output workspace/carousel/my-carousel/ref/concept.png

    With reference images:
    python3 scripts/generate_carousel_image.py \
        --prompt "Show this UI in an elegant dark mockup" \
        --reference path/to/screenshot.png \
        --output workspace/carousel/my-carousel/ref/styled.png

    With headshot (person in image):
    python3 scripts/generate_carousel_image.py \
        --prompt "Person looking at laptop with AI output on screen" \
        --headshot .claude/skills/instagram-thumbnail/headshots/tyler-headshot.png \
        --output workspace/carousel/my-carousel/ref/person.png

Environment:
    GEMINI_API_KEY must be set (in .env or environment).
"""

import argparse
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Generate carousel concept images via Gemini")
    parser.add_argument(
        "--prompt", required=True,
        help="Detailed prompt for image generation"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the generated image"
    )
    parser.add_argument(
        "--headshot", nargs="*", default=[],
        help="Path(s) to headshot reference image(s) for person likeness"
    )
    parser.add_argument(
        "--reference", nargs="*", default=[],
        help="Path(s) to reference images (screenshots, products, etc.)"
    )
    parser.add_argument(
        "--examples", nargs="*", default=[],
        help="Path(s) to example images for style inspiration"
    )
    return parser.parse_args()


def validate_image_file(path):
    """Check that a file is actually an image, not HTML or other junk."""
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(p, "rb") as f:
        header = f.read(256)
    if b"<!DOCTYPE" in header or b"<html" in header or b"<HTML" in header:
        print(
            f"Error: '{path}' is an HTML file, not an image. "
            f"The download URL likely returned a web page instead of the actual image.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(header) < 8:
        print(f"Error: '{path}' is too small to be a valid image ({len(header)} bytes).", file=sys.stderr)
        sys.exit(1)


def resize_if_needed(img, max_edge=2048):
    """Resize image if larger than max_edge on any side."""
    w, h = img.size
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return img.resize(new_size, Image.LANCZOS)
    return img


def load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    args = parse_args()

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Build prompt with carousel style guide baked in
    prompt = args.prompt

    # Append carousel-specific style rules (like thumbnail skill's brand-style.md)
    prompt += """

CAROUSEL IMAGE STYLE GUIDE (follow these rules):

FORMAT: 16:9 landscape aspect ratio. This image will be embedded inside an Instagram carousel slide as an inline image below tweet text.

BACKGROUND:
- Dark, moody, cinematic backgrounds — NOT a solid black void.
- Use darkened real-world scenes, subtle gradients, or textured dark surfaces.
- Should feel like dramatic night photography or heavy cinematic color grading.
- Dark overall but with real environmental detail, texture, and depth.

COMPOSITION:
- Keep important content in the center 80% of the frame (carousel slides crop edges).
- Elements should be LARGE and clearly visible — this will display at roughly 400px wide inside a tweet-style card.
- Clean, uncluttered. Maximum 2-3 focal elements.
- Use depth and layering — foreground elements over blurred/dark backgrounds.

COLOR:
- Dark + neon accent (cyan, magenta, orange) works great for tech content.
- High contrast — elements must pop against the dark background.
- Saturated, bold colors for key elements. Muted backgrounds.
- White or bright text on dark backgrounds for maximum readability.

VISUAL ELEMENTS:
- For screenshots/UIs: show them on elegant device mockups or floating with subtle shadows and glow.
- For concepts/diagrams: use clean iconography, arrows, and simple shapes — not clipart.
- For product shots: dramatic lighting, slight angle, professional feel.
- Avoid text-heavy images — the carousel slide already has text around the image.

STYLE:
- Professional, polished, modern. Not stock-photo generic.
- Cinematic lighting with dramatic shadows.
- Tech-forward aesthetic — clean lines, subtle glows, dark themes.
- Should look like it belongs in a premium tech creator's Instagram carousel.
"""

    if args.examples:
        prompt += (
            "\nSTYLE EXAMPLES:\n"
            "The final attached images are style references. "
            "Study their composition, color usage, and visual hierarchy — "
            "then apply those patterns to create an ORIGINAL image. "
            "Do NOT copy these images directly."
        )

    # Build contents list
    contents = [prompt]

    for path in args.headshot:
        validate_image_file(path)
        img = resize_if_needed(Image.open(path))
        contents.append(img)

    for path in args.reference:
        validate_image_file(path)
        img = resize_if_needed(Image.open(path))
        contents.append(img)

    for path in args.examples:
        validate_image_file(path)
        img = resize_if_needed(Image.open(path))
        contents.append(img)

    print(f"Generating image...")
    print(f"  Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"  Headshots: {len(args.headshot)}")
    print(f"  References: {len(args.reference)}")
    print(f"  Examples: {len(args.examples)}")

    # Generate with 16:9 landscape aspect ratio for inline carousel images
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="16:9",
            ),
        ),
    )

    # Process response
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_saved = False
    text_response = ""

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            img = part.as_image()
            img.save(str(output_path))
            image_saved = True
            print(f"\nImage saved to: {output_path}")
        elif hasattr(part, "text") and part.text is not None:
            text_response += part.text

    if text_response:
        print(f"Model notes: {text_response}")

    if not image_saved:
        print("Error: No image was generated in the response.", file=sys.stderr)
        if text_response:
            print(f"Response text: {text_response}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
