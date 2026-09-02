#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fal-client>=0.5.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Fallback image generator using fal.ai (FLUX models).
Used when Nano Banana Pro (Gemini) is unavailable (e.g. spend cap 429).

Usage:
    uv run fal_generate.py --prompt "..." --filename "out.png" \
        [--model fal-ai/flux-pro/v1.1] [--image-size landscape_16_9]

Reads FAL_KEY (or FAL_API_KEY) from environment.
"""
import argparse
import os
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--filename", "-f", required=True)
    p.add_argument("--model", default="fal-ai/flux-pro/v1.1")
    p.add_argument("--image-size", default="landscape_16_9")
    args = p.parse_args()

    key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
    if not key:
        print("Error: FAL_KEY / FAL_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(2)
    os.environ["FAL_KEY"] = key

    import fal_client
    import requests

    out = Path(args.filename)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Submitting to {args.model} (size={args.image_size})...")
    result = fal_client.subscribe(
        args.model,
        arguments={
            "prompt": args.prompt,
            "image_size": args.image_size,
            "num_images": 1,
            "enable_safety_checker": True,
            "output_format": "png",
        },
        with_logs=False,
    )

    images = result.get("images") or []
    if not images:
        print(f"Error: no images in result: {result}", file=sys.stderr)
        sys.exit(1)

    url = images[0]["url"]
    print(f"Downloading: {url[:80]}...")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    out.write_bytes(r.content)

    size = out.stat().st_size
    if size == 0:
        print("Error: downloaded file is empty.", file=sys.stderr)
        sys.exit(1)
    print(f"\nImage saved: {out.resolve()} ({size} bytes)")


if __name__ == "__main__":
    main()
