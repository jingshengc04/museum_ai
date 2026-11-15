"""Build harness_explainer_v3.mp4 (short cut, about 32-36 s): narration + synthesized UI sound effects.

    uv run --no-project --with playwright --with fal-client --with numpy python render_v3.py             # everything
    uv run --no-project --with playwright --with fal-client --with numpy python render_v3.py --still mid # check stills
    ... --skip-video    reuse video_v3_silent.mp4, redo audio + mux only

Narration: fal ElevenLabs v3, one short sentence per segment, cached in audio/v3/ (reruns do not pay again).
Picture: harness_explainer_v3.html reads segment timings from timeline_v3.js, which is written here from the clip lengths.
Sound effects: synthesized here with numpy (sines and filtered noise with envelopes), placed at the cue times the page
reports through sfxEvents(), and mixed well under the voice. FAL_KEY is read from ../.env and never printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "audio" / "v3"
PAGE = HERE / "harness_explainer_v3.html"
SILENT = HERE / "video_v3_silent.mp4"
OUT = HERE / "harness_explainer_v3.mp4"

TTS_MODEL = "fal-ai/elevenlabs/tts/eleven-v3"
VOICE = "Matilda"
STABILITY = 0.5
FPS = 30
SR = 48000

LEAD_WHITE = 0.5
NARR_DELAY = 0.25
BREATH = 0.55
MIN_STEP = 4.2
MIN_TITLE = 2.5
END_HOLD = 0.9
FX_GAIN = 1.8          # overall effects level: about 10 dB under the voice

NARRATION = [
    ("title", "So how does one photo become a film?"),
    ("see", "First, it looks at the photo and recognizes the object."),
    ("search", "Then it searches the web and checks every source."),
    ("understand", "It keeps what matters and shapes the facts into a story."),
    ("assets", "From the photo, it prepares reference images for the video."),
    ("script", "It writes the script, and a reviewer checks every line."),
    ("generate", "Finally, the video model turns it all into a film."),
    ("closing", "One photo in. One film out."),
]


def load_key() -> None:
    if os.environ.get("FAL_KEY"):
        return
    for line in (HERE.parent / ".env").read_text().splitlines():
        if line.strip().startswith("FAL_KEY"):
            os.environ["FAL_KEY"] = line.split("=", 1)[1].strip().strip("'\"")
            return
    raise SystemExit("FAL_KEY not found in environment or ../.env")


def decode(path: Path) -> np.ndarray:
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def trim(x: np.ndarray, thresh: float = 0.004) -> np.ndarray:
    """Cut leading/trailing near-silence so the timeline follows the spoken part."""
    idx = np.nonzero(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a, b = max(0, idx[0] - int(0.02 * SR)), min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b]


def tts() -> dict[str, np.ndarray]:
    AUDIO.mkdir(parents=True, exist_ok=True)
    cache_file = AUDIO / "cache.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    clips = {}
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
        clips[sid] = trim(decode(mp3))
    return clips


def build_timeline(clips: dict[str, np.ndarray]) -> dict:
    t = LEAD_WHITE
    segs = []
    for sid, text in NARRATION:
        n = len(clips[sid]) / SR
        dur = NARR_DELAY + n + BREATH
        dur = max(dur, MIN_TITLE if sid == "title" else MIN_STEP if sid != "closing" else 0)
        if sid == "closing":
            dur += END_HOLD
        dur = round(dur * FPS) / FPS
        segs.append({"id": sid, "start": round(t, 4), "dur": round(dur, 4), "narrStart": round(t + NARR_DELAY, 4), "narrDur": round(n, 3), "text": text})
        t += dur
    tl = {"fps": FPS, "lead": LEAD_WHITE, "voice": VOICE, "duration": round(t, 4), "segs": segs}
    (HERE / "timeline_v3.js").write_text("// written by render_v3.py from the narration clip lengths\nwindow.TIMELINE = " + json.dumps(tl, indent=1) + ";\n")
    return tl


def open_page(pw):
    browser = pw.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    page.add_init_script("window.__capture = true;")
    page.goto(PAGE.as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    return browser, page


def render_frames(tl: dict, stills: list[str]) -> list[dict]:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser, page = open_page(pw)
        events = page.evaluate("sfxEvents()")
        if stills:
            out = HERE / "stills_v3"
            out.mkdir(exist_ok=True)
            times = []
            for s in stills:
                if s == "mid":
                    times += [(f"{i}_{g['id']}_{frac}", g["start"] + g["dur"] * f) for i, g in enumerate(tl["segs"]) for frac, f in (("a", .3), ("b", .55), ("c", .85))]
                elif s != "none":
                    times.append((f"t{float(s):06.2f}", float(s)))
            for name, t in times:
                page.evaluate(f"render({t})")
                page.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=80)
            browser.close()
            return events
        n = int(round(tl["duration"] * FPS))
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS),
                               "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                               "-preset", "medium", str(SILENT)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            page.evaluate(f"render({i / FPS})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % 300 == 0:
                print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
        ff.stdin.close()
        ff.wait()
        browser.close()
    print(f"video: {SILENT.name} ({n} frames, {time.time() - t0:.0f}s)")
    return events


# ---------------- sound effects (all synthesized here) ----------------
def _t(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def _ad(t: np.ndarray, attack: float, tau: float) -> np.ndarray:
    """Soft attack, exponential decay, and a short fade at the very end (no clicks)."""
    e = np.minimum(1, t / attack) * np.exp(-t / tau)
    tail = int(0.01 * SR)
    e[-tail:] *= np.linspace(1, 0, tail)
    return e


def _noise_band(n: int, lo: np.ndarray, hi: np.ndarray, seed: int) -> np.ndarray:
    """White noise through two one-pole low-passes with moving cutoffs; their difference is a soft band."""
    x = np.random.default_rng(seed).standard_normal(n)
    a_hi = 1 - np.exp(-2 * np.pi * hi / SR)
    a_lo = 1 - np.exp(-2 * np.pi * lo / SR)
    y = np.zeros(n)
    s1 = s2 = 0.0
    for i in range(n):
        s1 += a_hi[i] * (x[i] - s1)
        s2 += a_lo[i] * (s1 - s2)
        y[i] = s1 - s2
    return y / (np.max(np.abs(y)) + 1e-9)


def sfx_tick(v: float = 0) -> np.ndarray:        # light tick: an item or card appears
    t = _t(0.09); f = 1320 * 2 ** (v / 12)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) * _ad(t, 0.002, 0.016) / 1.25


def sfx_drop(v: float = 0) -> np.ndarray:        # low soft thud: trivia struck out
    t = _t(0.16); f = 330 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _ad(t, 0.003, 0.04)


def sfx_check(v: float = 0) -> np.ndarray:       # single soft bell note: one check mark
    t = _t(0.35); f = 1046.5 * 2 ** (v / 12)
    return (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t)) * _ad(t, 0.004, 0.07) / 1.15


def sfx_confirm(v: float = 0) -> np.ndarray:     # two rising notes: a step's result is confirmed
    t = _t(0.6); out = np.zeros(len(t))
    for k, f in enumerate((880.0, 1318.5)):
        d = int(k * 0.085 * SR); tt = t[: len(t) - d]
        out[d:] += np.sin(2 * np.pi * f * tt) * _ad(tt, 0.005, 0.11)
    return out / np.max(np.abs(out))


def sfx_chime(v: float = 0) -> np.ndarray:       # soft major chord: title and closing cards land
    t = _t(1.6); out = np.zeros(len(t))
    for f, a in ((523.25, 1.0), (659.25, 0.8), (783.99, 0.7), (1046.5, 0.35)):
        out += a * np.sin(2 * np.pi * f * t) * _ad(t, 0.01, 0.42)
    return out / np.max(np.abs(out))


def sfx_whoosh(v: float = 0) -> np.ndarray:      # soft air whoosh: step transition
    n = int(0.55 * SR); u = np.arange(n) / n
    centre = 350 + 2200 * np.sin(np.pi * u) ** 2
    return _noise_band(n, centre * 0.5, centre * 1.6, seed=7) * np.sin(np.pi * u) ** 2


def sfx_riser(v: float = 0) -> np.ndarray:       # short riser into the closing card
    n = int(0.85 * SR); u = np.arange(n) / n
    centre = 300 * (12 ** u)
    env = u ** 2 * np.minimum(1, (1 - u) / 0.06)
    tone = np.sin(2 * np.pi * np.cumsum(220 * 3 ** u) / SR) * 0.35
    y = (_noise_band(n, centre * 0.6, centre * 1.5, seed=11) + tone) * env
    return y / np.max(np.abs(y))


SFX = {  # name: (generator, peak level, linear)
    "tick": (sfx_tick, 0.075), "drop": (sfx_drop, 0.10), "check": (sfx_check, 0.10), "confirm": (sfx_confirm, 0.12),
    "chime": (sfx_chime, 0.13), "whoosh": (sfx_whoosh, 0.13), "riser": (sfx_riser, 0.14),
}


def lufs(x: np.ndarray) -> float:
    tmp = AUDIO / "_measure.wav"
    write_wav(tmp, x)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    tmp.unlink()
    return float(json.loads(err[err.rindex("{"):err.rindex("}") + 1])["input_i"])


def write_wav(path: Path, x: np.ndarray) -> None:
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def mix_audio(tl: dict, clips: dict[str, np.ndarray], events: list[dict]) -> None:
    n = int(round(tl["duration"] * SR))
    voice = np.zeros(n)
    for g in tl["segs"]:
        c = clips[g["id"]].copy()
        f = int(0.015 * SR); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        a = int(round(g["narrStart"] * SR)); voice[a:a + len(c)] += c[: n - a]
    v_in = lufs(voice)
    voice *= 10 ** ((-16.0 - v_in) / 20)
    vpk = np.max(np.abs(voice))
    if vpk > 0.84:   # gentle safety: soft-knee the few peaks instead of turning the whole voice down
        voice = np.where(np.abs(voice) > 0.7, np.sign(voice) * (0.7 + 0.14 * np.tanh((np.abs(voice) - 0.7) / 0.14)), voice)

    fx = np.zeros((n, 2))
    cache: dict[tuple, np.ndarray] = {}
    counts: dict[str, int] = {}
    for e in events:
        gen, level = SFX[e["type"]]
        k = (e["type"], e.get("v", 0))
        if k not in cache:
            cache[k] = gen(e.get("v", 0)) * level * FX_GAIN
        s = cache[k]
        a = int(round(e["t"] * SR))
        if a < 0 or a >= n:
            continue
        s = s[: n - a]
        pan = float(e.get("pan", 0))            # -1 .. 1, kept narrow
        fx[a:a + len(s), 0] += s * (1 - 0.35 * max(0, pan))
        fx[a:a + len(s), 1] += s * (1 + 0.35 * min(0, pan))
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    write_wav(AUDIO / "sfx_only.wav", fx)
    write_wav(AUDIO / "voice_only.wav", voice)
    mix = fx + voice[:, None]
    peak = np.max(np.abs(mix))
    if peak > 0.89:
        mix *= 0.89 / peak
    write_wav(AUDIO / "mix.wav", mix)
    fx_l = lufs(fx)
    print(f"audio: voice {v_in:.1f} -> -16.0 LUFS (peak {20 * np.log10(np.max(np.abs(voice))):.1f} dBFS) | effects {fx_l:.1f} LUFS, "
          f"peak {20 * np.log10(np.max(np.abs(fx))):.1f} dBFS | mix peak {20 * np.log10(min(peak, 0.89)):.1f} dBFS | cues {counts}")


def mux() -> None:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(SILENT), "-i", str(AUDIO / "mix.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUT)], check=True)
    print(f"done: {OUT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", action="append", default=[], help="'mid' or a time in seconds: save JPEGs to stills_v3/ and stop")
    ap.add_argument("--skip-video", action="store_true")
    args = ap.parse_args()
    clips = tts()
    tl = build_timeline(clips)
    for g in tl["segs"]:
        print(f"  {g['id']:<11} start {g['start']:6.2f}  dur {g['dur']:5.2f}  narration {g['narrDur']:5.2f}s")
    print(f"  total {tl['duration']:.2f}s")
    if args.still:
        render_frames(tl, args.still)
        return
    events = render_frames(tl, ["none"] if args.skip_video else [])
    (AUDIO / "sfx_events.json").write_text(json.dumps(events, indent=1))
    mix_audio(tl, clips, events)
    mux()


if __name__ == "__main__":
    main()
