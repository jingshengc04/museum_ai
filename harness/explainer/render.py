"""Render harness_explainer.html to MP4, frame by frame, with the system Chrome.

    uv run --with playwright python render.py [--fps 30] [--out harness_explainer.mp4] [--frames 0-200] [--still 12.5]

The page exposes render(t); we call it for each frame time and screenshot, piping JPEGs into ffmpeg.
Deterministic: no real-time animation is involved, so every render is identical.
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", default=str(HERE / "harness_explainer.mp4"))
    ap.add_argument("--still", type=float, action="append", default=[], help="save a PNG at this time instead")
    args = ap.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page.add_init_script("window.__capture = true;")
        page.goto((HERE / "harness_explainer.html").as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        if args.still:
            for t in args.still:
                page.evaluate(f"render({t})")
                page.screenshot(path=str(HERE / f"still_{t:05.1f}.png"))
            browser.close()
            return
        duration = page.evaluate("DURATION")
        n = int(round(duration * args.fps))
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(args.fps),
                               "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                               "-preset", "medium", "-movflags", "+faststart", args.out], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"render({i / args.fps})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % 150 == 0:
                print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
        ff.stdin.close()
        ff.wait()
        browser.close()
    print(f"done: {args.out} ({n} frames, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
