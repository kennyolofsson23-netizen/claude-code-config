#!/usr/bin/env python3
"""
Giphy GIF Search

Searches for GIFs using the Giphy API and downloads them to a local directory.

Usage:
    python3 scripts/giphy-search.py "search query" [output_dir] [--count N]

Requires GIPHY_API_KEY in environment or .env file.
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


def search_gifs(query, count=5):
    """Search Giphy for GIFs and return list of result dicts."""
    api_key = os.environ.get("GIPHY_API_KEY")
    if not api_key:
        print("Error: GIPHY_API_KEY not set. Add it to .env or export it.", file=sys.stderr)
        sys.exit(1)

    params = urllib.request.quote(query)
    url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={params}&limit={count}&rating=g&lang=en"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: Giphy API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    results = []
    for item in data.get("data", [])[:count]:
        images = item.get("images", {})
        # Prefer fixed_height for reasonable file size, fall back to original
        rendition = images.get("fixed_height", images.get("original", {}))
        gif_url = rendition.get("url", "")
        if gif_url:
            results.append({
                "url": gif_url,
                "title": item.get("title", ""),
                "width": rendition.get("width", ""),
                "height": rendition.get("height", ""),
            })
    return results


def slugify(text, max_len=40):
    """Turn text into a safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text[:max_len].strip("-")


def download_gif(url, output_path):
    """Download a GIF from URL. Returns final path on success."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

            # Verify it's actually a GIF
            if data[:3] == b"GIF":
                ext = ".gif"
            else:
                ext = ".gif"  # Giphy should always return GIFs

            final_path = Path(output_path).with_suffix(ext)
            final_path.write_bytes(data)
            return str(final_path)
    except Exception as e:
        print(f"  Failed to download {url[:80]}... — {e}", file=sys.stderr)
        return None


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/giphy-search.py "search query" [output_dir] [--count N]')
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

    print(f'Searching Giphy for: "{query}"')
    gifs = search_gifs(query, count=count)

    if not gifs:
        print("No GIFs found.")
        sys.exit(0)

    print(f"Found {len(gifs)} GIFs. Downloading...\n")

    downloaded = []
    for i, gif in enumerate(gifs):
        slug = slugify(query)
        base_path = os.path.join(output_dir, f"{slug}-{i + 1:02d}")
        result = download_gif(gif["url"], base_path)
        if result:
            title = gif.get("title") or ""
            title_short = (title[:80] + "...") if len(title) > 80 else title
            print(f"  [{i + 1}] {result}")
            if title_short:
                print(f"      {title_short}")
            downloaded.append({
                "path": result,
                "title": title,
                "url": gif["url"],
                "width": gif.get("width"),
                "height": gif.get("height"),
            })

    print(f"\nDone — {len(downloaded)} GIFs saved to {output_dir}/")

    # Write manifest
    manifest_path = os.path.join(output_dir, f"{slugify(query)}-manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({"query": query, "gifs": downloaded}, f, indent=2)
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
