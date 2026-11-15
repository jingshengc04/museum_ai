"""Build harness_explainer_v2.mp4: narration (fal ElevenLabs v3) -> timeline.js -> frames -> audio mix -> mux.

    uv run --no-project --with playwright --with fal-client python render_v2.py            # everything
    uv run --no-project --with playwright --with fal-client python render_v2.py --still mid  # PNG at the middle of every segment
    uv run --no-project --with playwright --with fal-client python render_v2.py --still 12.5 # PNG at one time
    ... --skip-video   reuse the silent render (video_v2_silent.mp4) and only redo audio + mux

Narration clips are cached in audio/ (keyed by text + voice + settings), so reruns do not pay again.
The picture follows the voice: each segment lasts as long as its narration plus breathing room, and the page
(harness_explainer_v2.html) reads those timings from timeline.js. FAL_KEY is read from ../.env and never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "audio"
PAGE = HERE / "harness_explainer_v2.html"
SILENT = HERE / "video_v2_silent.mp4"
MIX = AUDIO / "narration_mix.wav"
OUT = HERE / "harness_explainer_v2.mp4"

TTS_MODEL = "fal-ai/elevenlabs/tts/eleven-v3"
VOICE = "Matilda"       # warm, friendly narration voice; the same for every clip
STABILITY = 0.5
FPS = 30

LEAD_WHITE = 0.5        # pure white before anything appears (the editor cuts in from white)
NARR_DELAY = 0.3        # narration starts this long after its segment begins
BREATH = 0.8            # silence after the narration before the next segment
MIN_SEG = 4.0
END_HOLD = 1.2          # extra hold on the closing card

NARRATION = [
    ("title", "So what happens behind the screen? Here's how our agent turns one photo into a film."),
    ("see", "First, it looks. Claude studies the visitor's photo and recognizes the object: the Four-Ram Square Zun, "
            "a bronze vessel from the late Shang dynasty."),
    ("search", "Then it searches the web. Every finding has to quote its source word for word, so nothing is made up."),
    ("understand", "Next, it decides what matters. Trivia is dropped, and the facts become a story with an ending. "
                   "Then it picks the idea that brings the object most alive."),
    ("assets", "From the photo, it prepares the reference images: one keeps the object's look exact, "
               "and one designs the character."),
    ("script", "Now it writes the script. A second reviewer checks every line and every shot, "
               "and the script is refined until it passes."),
    ("generate", "Finally, one request goes to the video model, and thirty seconds of film come back, with voice and sound."),
    ("closing", "One photo in. One film out. Every line sourced."),
]


def load_key() -> None:
    if os.environ.get("FAL_KEY"):
        return
    env = HERE.parent / ".env"
    for line in env.read_text().splitlines():
        if line.strip().startswith("FAL_KEY"):
            os.environ["FAL_KEY"] = line.split("=", 1)[1].strip().strip("'\"")
            return
    raise SystemExit("FAL_KEY not found in environment or ../.env")


def probe(path: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())


def tts() -> dict[str, float]:
    """One clip per segment, cached. Returns {id: seconds}."""
    AUDIO.mkdir(exist_ok=True)
    cache_file = AUDIO / "cache.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    durs = {}
    for sid, text in NARRATION:
        key = hashlib.sha256(json.dumps([TTS_MODEL, VOICE, STABILITY, text]).encode()).hexdigest()[:16]
        mp3 = AUDIO / f"{sid}.mp3"
        if not (mp3.exists() and cache.get(sid, {}).get("key") == key):
            load_key()
            import fal_client
            print(f"tts (paid): {sid}  {len(text)} chars", flush=True)
            res = fal_client.subscribe(TTS_MODEL, arguments={"text": text, "voice": VOICE, "stability": STABILITY, "language_code": "en"})
            urllib.request.urlretrieve(res["audio"]["url"], mp3)
            cache[sid] = {"key": key, "chars": len(text), "voice": VOICE, "model": TTS_MODEL}
            cache_file.write_text(json.dumps(cache, indent=1))
        durs[sid] = probe(mp3)
    return durs


def build_timeline(durs: dict[str, float]) -> dict:
    t = LEAD_WHITE
    segs = []
    for sid, text in NARRATION:
        dur = max(MIN_SEG, NARR_DELAY + durs[sid] + BREATH)
        if sid == "closing":
            dur += END_HOLD
        dur = round(dur * FPS) / FPS
        segs.append({"id": sid, "start": round(t, 4), "dur": round(dur, 4), "narrStart": round(t + NARR_DELAY, 4),
                     "narrDur": round(durs[sid], 3), "text": text})
        t += dur
    tl = {"fps": FPS, "lead": LEAD_WHITE, "voice": VOICE, "duration": round(t, 4), "segs": segs}
    (HERE / "timeline.js").write_text("// written by render_v2.py from the narration clip lengths\nwindow.TIMELINE = " + json.dumps(tl, indent=1) + ";\n")
    return tl


def render_frames(tl: dict, stills: list[str]) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page.add_init_script("window.__capture = true;")
        page.goto(PAGE.as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        if stills:
            out = HERE / "stills"
            out.mkdir(exist_ok=True)
            times = []
            for s in stills:
                if s == "mid":
                    times += [(f"{i}_{g['id']}_{frac}", g["start"] + g["dur"] * f) for i, g in enumerate(tl["segs"]) for frac, f in (("a", .3), ("b", .6), ("c", .88))]
                else:
                    times.append((f"t{float(s):06.2f}", float(s)))
            for name, t in times:
                page.evaluate(f"render({t})")
                page.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=80)
            browser.close()
            return
        n = int(round(tl["duration"] * FPS))
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS),
                               "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                               "-preset", "medium", str(SILENT)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"render({i / FPS})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % 150 == 0:
                print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
        ff.stdin.close()
        ff.wait()
        browser.close()
    print(f"video: {SILENT.name} ({n} frames, {time.time() - t0:.0f}s)")


def mix_audio(tl: dict) -> None:
    """All clips on one track at their start times, then a plain gain to about -16 LUFS with a limiter."""
    inputs, chains, labels = [], [], []
    for i, g in enumerate(tl["segs"]):
        inputs += ["-i", str(AUDIO / f"{g['id']}.mp3")]
        ms = int(round(g["narrStart"] * 1000))
        chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.02,adelay={ms}:all=1[a{i}]")
        labels.append(f"[a{i}]")
    mixf = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad=whole_dur={tl['duration']}[m]"
    raw = AUDIO / "narration_raw.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", mixf, "-map", "[m]", "-t", str(tl["duration"]), str(raw)], check=True)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    measured = float(json.loads(err[err.rindex("{"):err.rindex("}") + 1])["input_i"])
    gain = -16.0 - measured
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:level=false",
                    "-ar", "48000", str(MIX)], check=True)
    raw.unlink()
    print(f"audio: measured {measured:.1f} LUFS, gain {gain:+.1f} dB -> {MIX.name}")


def mux() -> None:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(SILENT), "-i", str(MIX), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)], check=True)
    print(f"done: {OUT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", action="append", default=[], help="'mid' or a time in seconds: save JPEGs to stills/ and stop")
    ap.add_argument("--skip-video", action="store_true")
    ap.add_argument("--timeline-only", action="store_true")
    args = ap.parse_args()
    tl = build_timeline(tts())
    for g in tl["segs"]:
        print(f"  {g['id']:<11} start {g['start']:6.2f}  dur {g['dur']:5.2f}  narration {g['narrDur']:5.2f}s")
    print(f"  total {tl['duration']:.2f}s")
    if args.timeline_only:
        return
    if args.still:
        render_frames(tl, args.still)
        return
    if not args.skip_video:
        render_frames(tl, [])
    mix_audio(tl)
    mux()


if __name__ == "__main__":
    main()
