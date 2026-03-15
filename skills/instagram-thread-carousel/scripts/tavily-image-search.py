#!/usr/bin/env python3
"""
Tavily Image Search

Searches for images using the Tavily API and downloads them to a local directory.

Usage:
    python3 scripts/tavily-image-search.py "search query" [output_dir] [--count N]

Requires TAVILY_API_KEY in environment or .env file.
"""

import json
import os
import sys
import re
import urllib.request
import urllib.error
from pathlib import Path


def load_env():
    """Load .env file if it exists."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


def search_images(query, count=5):
    """Search Tavily for images and return list of {url, description} dicts."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY not set. Add it to .env or export it.", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "query": query,
        "include_images": True,
        "include_image_descriptions": True,
        "search_depth": "advanced",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Tavily API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    images = data.get("images", [])
    # Normalize — could be list of strings or list of dicts
    results = []
    for img in images[:count]:
        if isinstance(img, str):
            results.append({"url": img, "description": ""})
        elif isinstance(img, dict):
            results.append({"url": img.get("url", ""), "description": img.get("description", "")})
    return results


def slugify(text, max_len=40):
    """Turn text into a safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:max_len].strip("-")


def guess_extension(url, content_type=""):
    """Guess file extension from URL or Content-Type."""
    # Try Content-Type first
    ct = content_type.lower()
    if "png" in ct:
        return ".png"
    if "gif" in ct:
        return ".gif"
    if "webp" in ct:
        return ".webp"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"

    # Try URL
    path = url.split("?")[0].lower()
    for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        if path.endswith(ext):
            return ext

    return ".jpg"  # default


def download_image(url, output_path):
    """Download an image from URL to output_path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()

            # Make sure we got an image
            if data[:4] == b"\x89PNG":
                ext = ".png"
            elif data[:2] == b"\xff\xd8":
                ext = ".jpg"
            elif data[:4] == b"RIFF":
                ext = ".webp"
            elif data[:3] == b"GIF":
                ext = ".gif"
            else:
                ext = guess_extension(url, content_type)

            # Update extension if needed
            final_path = Path(output_path).with_suffix(ext)
            final_path.write_bytes(data)
            return str(final_path)
    except Exception as e:
        print(f"  Failed to download {url[:80]}... — {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/tavily-image-search.py \"search query\" [output_dir] [--count N]")
        sys.exit(1)

    query = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "."
    count = 5
    if "--count" in sys.argv:
        idx = sys.argv.index("--count")
        if idx + 1 < len(sys.argv):
            count = int(sys.argv[idx + 1])

    load_env()
    os.makedirs(output_dir, exist_ok=True)

    print(f"Searching Tavily for: \"{query}\"")
    images = search_images(query, count=count)

    if not images:
        print("No images found.")
        sys.exit(0)

    print(f"Found {len(images)} images. Downloading...\n")

    downloaded = []
    for i, img in enumerate(images):
        slug = slugify(query)
        base_path = os.path.join(output_dir, f"{slug}-{i + 1:02d}")
        result = download_image(img["url"], base_path)
        if result:
            desc = img.get("description") or ""
            desc_short = (desc[:80] + "...") if len(desc) > 80 else desc
            print(f"  [{i + 1}] {result}")
            if desc_short:
                print(f"      {desc_short}")
            downloaded.append({"path": result, "description": desc, "url": img["url"]})

    print(f"\nDone — {len(downloaded)} images saved to {output_dir}/")

    # Write manifest for easy reference
    manifest_path = os.path.join(output_dir, f"{slugify(query)}-manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({"query": query, "images": downloaded}, f, indent=2)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
