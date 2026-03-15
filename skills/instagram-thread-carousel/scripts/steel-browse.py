#!/usr/bin/env python3
"""
Steel Browser — Browse & Record

Creates a Steel.dev cloud browser session, executes a browsing plan via
Playwright, injects a large smooth cursor, and downloads the session recording.

Usage:
    python3 scripts/steel-browse.py <browse-plan.json> <output_dir>

Requires STEEL_API_KEY in environment or .env file.
Requires: pip install steel-sdk playwright
"""

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
def load_env():
    """Load .env file if it exists."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


# ---------------------------------------------------------------------------
# Custom cursor injection
# ---------------------------------------------------------------------------
CURSOR_JS = """
(() => {
    if (document.getElementById('steel-cursor')) return;

    // Hide native cursor
    const style = document.createElement('style');
    style.textContent = '* { cursor: none !important; }';
    document.head.appendChild(style);

    // Create large smooth cursor
    const cursor = document.createElement('div');
    cursor.id = 'steel-cursor';
    cursor.style.cssText = [
        'position: fixed',
        'width: 36px',
        'height: 36px',
        'border-radius: 50%',
        'background: rgba(255, 255, 255, 0.85)',
        'border: 3px solid rgba(0, 0, 0, 0.25)',
        'box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25)',
        'pointer-events: none',
        'z-index: 2147483647',
        'transition: left 0.10s ease-out, top 0.10s ease-out, transform 0.15s ease-out',
        'transform: translate(-50%, -50%)',
        'left: -100px',
        'top: -100px',
    ].join('; ');
    document.body.appendChild(cursor);

    // Follow mouse
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    }, { passive: true });

    // Click feedback — brief scale pulse
    document.addEventListener('mousedown', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(0.8)';
    });
    document.addEventListener('mouseup', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(1)';
    });
})();
"""


# ---------------------------------------------------------------------------
# Browsing actions
# ---------------------------------------------------------------------------
def execute_actions(page, actions, moments):
    """Execute a list of browsing actions and log moments."""
    start_time = time.time()

    for action in actions:
        action_type = action.get("action", "")
        wait_ms = action.get("wait", 1000)
        elapsed_ms = int((time.time() - start_time) * 1000)

        try:
            _execute_single_action(page, action, action_type, wait_ms, elapsed_ms, moments)
        except Exception as e:
            label = action.get("label", action_type)
            print(f"  [{elapsed_ms}ms] SKIPPED ({label}): {e}", file=sys.stderr)

        # Wait after each action
        if wait_ms > 0:
            page.wait_for_timeout(wait_ms)

    total_ms = int((time.time() - start_time) * 1000)
    return total_ms


def _execute_single_action(page, action, action_type, wait_ms, elapsed_ms, moments):
    """Execute a single browsing action. Raises on failure."""
    if action_type == "navigate":
        url = action["url"]
        print(f"  [{elapsed_ms}ms] Navigate → {url}", file=sys.stderr)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.evaluate(CURSOR_JS)
        moments.append({
            "time_ms": elapsed_ms,
            "type": "navigate",
            "url": url,
            "label": action.get("label", url),
        })

    elif action_type == "click":
        selector = action["selector"]
        print(f"  [{elapsed_ms}ms] Click → {selector}", file=sys.stderr)
        element = page.wait_for_selector(selector, timeout=10000)
        if element:
            box = element.bounding_box()
            if box:
                page.mouse.move(
                    box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2,
                    steps=20,
                )
                page.wait_for_timeout(300)
            element.click()
            moments.append({
                "time_ms": elapsed_ms,
                "type": "click",
                "selector": selector,
                "x": int(box["x"] + box["width"] / 2) if box else 0,
                "y": int(box["y"] + box["height"] / 2) if box else 0,
                "label": action.get("label", f"Click {selector}"),
            })

    elif action_type == "scroll":
        y = action.get("y", 500)
        print(f"  [{elapsed_ms}ms] Scroll → {y}px", file=sys.stderr)
        page.evaluate(f"window.scrollBy({{ top: {y}, behavior: 'smooth' }})")
        moments.append({
            "time_ms": elapsed_ms,
            "type": "scroll",
            "y": y,
            "label": action.get("label", f"Scroll {y}px"),
        })

    elif action_type == "hover":
        selector = action["selector"]
        print(f"  [{elapsed_ms}ms] Hover → {selector}", file=sys.stderr)
        element = page.wait_for_selector(selector, timeout=10000)
        if element:
            box = element.bounding_box()
            if box:
                page.mouse.move(
                    box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2,
                    steps=25,
                )
            moments.append({
                "time_ms": elapsed_ms,
                "type": "hover",
                "selector": selector,
                "label": action.get("label", f"Hover {selector}"),
            })

    elif action_type == "type":
        selector = action["selector"]
        text = action.get("text", "")
        print(f"  [{elapsed_ms}ms] Type → '{text}' into {selector}", file=sys.stderr)
        element = page.wait_for_selector(selector, timeout=10000)
        if element:
            box = element.bounding_box()
            if box:
                page.mouse.move(
                    box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2,
                    steps=15,
                )
                page.wait_for_timeout(200)
            element.click()
            page.keyboard.type(text, delay=80)
            moments.append({
                "time_ms": elapsed_ms,
                "type": "type",
                "selector": selector,
                "text": text,
                "label": action.get("label", f"Type into {selector}"),
            })

    elif action_type == "click_at":
        x = action["x"]
        y = action["y"]
        print(f"  [{elapsed_ms}ms] Click at → ({x}, {y})", file=sys.stderr)
        page.mouse.move(x, y, steps=20)
        page.wait_for_timeout(300)
        page.mouse.click(x, y)
        moments.append({
            "time_ms": elapsed_ms,
            "type": "click_at",
            "x": x,
            "y": y,
            "label": action.get("label", f"Click at ({x}, {y})"),
        })

    elif action_type == "keyboard_type":
        text = action.get("text", "")
        delay = action.get("delay", 80)
        print(f"  [{elapsed_ms}ms] Keyboard type → '{text}'", file=sys.stderr)
        page.keyboard.type(text, delay=delay)
        moments.append({
            "time_ms": elapsed_ms,
            "type": "keyboard_type",
            "text": text,
            "label": action.get("label", f"Type '{text}'"),
        })

    elif action_type == "keyboard_press":
        key = action["key"]
        print(f"  [{elapsed_ms}ms] Keyboard press → {key}", file=sys.stderr)
        page.keyboard.press(key)
        moments.append({
            "time_ms": elapsed_ms,
            "type": "keyboard_press",
            "key": key,
            "label": action.get("label", f"Press {key}"),
        })

    elif action_type == "wait":
        print(f"  [{elapsed_ms}ms] Wait → {wait_ms}ms", file=sys.stderr)

    else:
        print(f"  [{elapsed_ms}ms] Unknown action: {action_type}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Recording download
# ---------------------------------------------------------------------------
def download_recording(session_id, api_key, output_path, max_retries=6):
    """Download session recording via HLS → MP4 using ffmpeg."""
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if not os.path.exists(ffmpeg_bin):
        print("Error: ffmpeg not found. Install with: brew install ffmpeg", file=sys.stderr)
        return False

    hls_url = f"https://api.steel.dev/v1/sessions/{session_id}/hls"

    for attempt in range(max_retries):
        wait_secs = 5 * (attempt + 1)
        print(f"  Waiting {wait_secs}s for recording to be ready (attempt {attempt + 1}/{max_retries})...", file=sys.stderr)
        time.sleep(wait_secs)

        # Check if the HLS endpoint is ready
        req = urllib.request.Request(hls_url, headers={"steel-api-key": api_key})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
                if "#EXTM3U" not in content:
                    print(f"  HLS not ready yet (no playlist data)", file=sys.stderr)
                    continue
        except urllib.error.HTTPError as e:
            print(f"  HLS not ready yet (HTTP {e.code})", file=sys.stderr)
            continue
        except Exception as e:
            print(f"  HLS check failed: {e}", file=sys.stderr)
            continue

        # Download with ffmpeg
        print(f"  Downloading recording via ffmpeg...", file=sys.stderr)
        result = subprocess.run(
            [
                ffmpeg_bin, "-y",
                "-headers", f"steel-api-key: {api_key}\r\n",
                "-i", hls_url,
                "-c", "copy",
                "-movflags", "+faststart",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0 and os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  Recording saved: {output_path} ({size_mb:.1f} MB)", file=sys.stderr)
            return True
        else:
            print(f"  ffmpeg failed: {result.stderr[:200]}", file=sys.stderr)

    print("Error: Could not download recording after all retries.", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/steel-browse.py <browse-plan.json> <output_dir>", file=sys.stderr)
        sys.exit(1)

    load_env()

    plan_path = sys.argv[1]
    output_dir = sys.argv[2]

    api_key = os.environ.get("STEEL_API_KEY")
    if not api_key or api_key == "your_steel_api_key":
        print("Error: STEEL_API_KEY not set. Add it to .env", file=sys.stderr)
        sys.exit(1)

    # Load plan
    with open(plan_path, "r") as f:
        plan = json.load(f)

    actions = plan.get("actions", [])
    if not actions:
        print("Error: No actions in browsing plan.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # --- Create Steel session ---
    from steel import Steel
    client = Steel(steel_api_key=api_key)
    session = None

    try:
        print("Creating Steel browser session...", file=sys.stderr)
        session = client.sessions.create(
            api_timeout=300000,  # 5 minutes
        )
        print(f"  Session ID: {session.id}", file=sys.stderr)
        print(f"  Viewer URL: {session.session_viewer_url}", file=sys.stderr)

        # Output viewer URL for the skill to show the user
        print(json.dumps({"viewer_url": session.session_viewer_url}))

        # --- Connect Playwright ---
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        cdp_url = f"{session.websocket_url}&apiKey={api_key}"
        browser = pw.chromium.connect_over_cdp(cdp_url)

        # Use existing context (required for recording to work)
        context = browser.contexts[0]
        page = context.new_page()

        # Set viewport
        viewport = plan.get("viewport", {})
        page.set_viewport_size({
            "width": viewport.get("width", 1920),
            "height": viewport.get("height", 1080),
        })

        # --- Execute browsing plan ---
        moments = []
        print("Executing browsing plan...", file=sys.stderr)
        total_ms = execute_actions(page, actions, moments)
        print(f"  Browsing complete ({total_ms}ms total)", file=sys.stderr)

        # Brief pause to let recording finish
        page.wait_for_timeout(2000)

        # Close browser
        browser.close()
        pw.stop()

    finally:
        # Always release session
        if session:
            print("Releasing Steel session...", file=sys.stderr)
            try:
                client.sessions.release(session.id)
            except Exception as e:
                print(f"  Warning: session release failed: {e}", file=sys.stderr)

    # --- Save moments ---
    moments_path = os.path.join(output_dir, "moments.json")
    moments_data = {
        "session_id": session.id,
        "duration_ms": total_ms,
        "viewport": {
            "width": viewport.get("width", 1920),
            "height": viewport.get("height", 1080),
        },
        "moments": moments,
    }
    with open(moments_path, "w") as f:
        json.dump(moments_data, f, indent=2)
    print(f"  Moments saved: {moments_path}", file=sys.stderr)

    # --- Download recording ---
    recording_path = os.path.join(output_dir, "recording.mp4")
    success = download_recording(session.id, api_key, recording_path)

    if success:
        print(json.dumps({
            "recording": recording_path,
            "moments": moments_path,
            "viewer_url": session.session_viewer_url,
        }))
    else:
        print(json.dumps({
            "error": "Recording download failed",
            "moments": moments_path,
            "viewer_url": session.session_viewer_url,
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
