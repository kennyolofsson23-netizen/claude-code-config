#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "replicate>=0.34.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Fallback image generator using Replicate (FLUX models).
Used when Nano Banana Pro (Gemini) AND fal.ai are unavailable.

Usage:
    uv run replicate_generate.py --prompt "..." --filename "out.png" \
        [--model black-forest-labs/flux-1.1-pro] [--aspect-ratio 16:9]

Reads REPLICATE_API_TOKEN from environment.
"""
import argparse
import os
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--filename", "-f", required=True)
    p.add_argument("--model", default="black-forest-labs/flux-1.1-pro")
    p.add_argument("--aspect-ratio", default="16:9")
    args = p.parse_args()

    token = os.environ.get("REPLICATE_API_TOKEN") or os.environ.get("REPLICATE_API_KEY")
    if not token:
        print("Error: REPLICATE_API_TOKEN not set in environment.", file=sys.stderr)
        sys.exit(2)
    os.environ["REPLICATE_API_TOKEN"] = token

    import replicate
    import requests

    out = Path(args.filename)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Running {args.model} (aspect_ratio={args.aspect_ratio})...")
    output = replicate.run(
        args.model,
        input={
            "prompt": args.prompt,
            "aspect_ratio": args.aspect_ratio,
            "output_format": "png",
            "safety_tolerance": 5,
            "prompt_upsampling": False,
        },
    )

    # Output may be a FileOutput (with .read()/.url()), a URL string, or a list of those.
    item = output[0] if isinstance(output, list) else output

    data = None
    # FileOutput object exposes read()
    if hasattr(item, "read"):
        data = item.read()
    elif isinstance(item, (bytes, bytearray)):
        data = bytes(item)
    else:
        # treat as URL string
        url = str(item)
        print(f"Downloading: {url[:80]}...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        data = r.content

    if not data:
        print("Error: empty image data from Replicate.", file=sys.stderr)
        sys.exit(1)

    out.write_bytes(data)
    size = out.stat().st_size
    if size == 0:
        print("Error: written file is empty.", file=sys.stderr)
        sys.exit(1)
    print(f"\nImage saved: {out.resolve()} ({size} bytes)")


if __name__ == "__main__":
    main()
