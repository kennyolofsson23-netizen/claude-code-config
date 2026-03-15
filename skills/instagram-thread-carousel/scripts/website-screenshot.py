#!/usr/bin/env python3
"""
Website Screenshot

Takes a screenshot of a website using Playwright (headless browser).

Usage:
    python3 scripts/website-screenshot.py "https://example.com" output.png [--width 1280] [--height 800] [--full-page]

Requires: pip install playwright && playwright install chromium
"""

import sys
import os
import argparse


def take_screenshot(url, output_path, width=1280, height=800, full_page=False):
    """Take a screenshot of a URL and save to output_path."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not installed.", file=sys.stderr)
        print("Run: pip install playwright && playwright install chromium", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})

        print(f"Loading {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)

        # Extra wait for any animations/lazy content
        page.wait_for_timeout(2000)

        print(f"Capturing screenshot...")
        page.screenshot(path=output_path, full_page=full_page)
        browser.close()

    print(f"Saved: {output_path} ({width}x{height}{'  full-page' if full_page else ''})")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Take a website screenshot")
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument("output", help="Output file path (PNG)")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width (default: 1280)")
    parser.add_argument("--height", type=int, default=800, help="Viewport height (default: 800)")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")

    args = parser.parse_args()
    take_screenshot(args.url, args.output, args.width, args.height, args.full_page)


if __name__ == "__main__":
    main()
