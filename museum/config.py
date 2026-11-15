"""Settings, paths and the mock/live switch.

Everything is mock by default so nothing costs money. A service only goes live
when it is named in LIVE (e.g. LIVE=llm,voice,video) *and* its key is present.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXHIBITS_DIR = ROOT / "exhibits"
WEB_DIR = ROOT / "web"


def _load_dotenv(path: Path) -> None:
    """Tiny .env reader; real environment variables win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_dotenv(ROOT / ".env")


def _env(name: str, default: str) -> str:
    return os.environ.get(name, "").strip() or default


CACHE_DIR = Path(_env("MUSEUM_CACHE_DIR", str(ROOT / "cache")))
OUTPUT_DIR = Path(_env("MUSEUM_OUTPUT_DIR", str(ROOT / "output")))

SERVICES = ("llm", "voice", "video")
_KEYS = {
    "llm": ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"),
    "voice": ("ELEVENLABS_API_KEY",),
    "video": ("FAL_KEY",),
}


def live_requested() -> set[str]:
    return {s.strip().lower() for s in os.environ.get("LIVE", "").split(",") if s.strip()}


def mode(service: str) -> dict:
    """{'live': bool, 'reason': str} for one of SERVICES."""
    if service not in live_requested():
        return {"live": False, "reason": f"mock ('{service}' not in LIVE)"}
    if not any(os.environ.get(k) for k in _KEYS[service]):
        return {"live": False, "reason": f"mock ({_KEYS[service][0]} not set)"}
    return {"live": True, "reason": "live"}


def is_live(service: str) -> bool:
    return mode(service)["live"]


def modes() -> dict:
    return {s: mode(s) for s in SERVICES}


# --- story (Claude) ---
STORY_MODEL = _env("STORY_MODEL", "claude-opus-5-5")

# --- voice (ElevenLabs) ---
ELEVEN_MODEL = _env("ELEVEN_MODEL", "eleven_v3")
# Fallback voice when an exhibit does not set one (an ElevenLabs premade voice).
ELEVEN_VOICE_ID = _env("ELEVEN_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# --- video (fal) ---
VIDEO_MODEL = _env("VIDEO_MODEL", "bytedance/seedance-2.0/fast/reference-to-video")
VIDEO_RESOLUTION = _env("VIDEO_RESOLUTION", "720p")
VIDEO_ASPECT = _env("VIDEO_ASPECT", "16:9")
FAL_CONCURRENCY = int(_env("FAL_CONCURRENCY", "2"))
# Seedance speaks the narration and makes the sound itself, so the film needs no separate voice track.
# With a silent model (Vidu) the narration is recorded first with ElevenLabs and the clips are fitted to it.
NATIVE_AUDIO = "seedance" in VIDEO_MODEL
if NATIVE_AUDIO:
    VIDEO_MIN_SECONDS, VIDEO_MAX_SECONDS, VIDEO_MAX_REFS = 4, 15, 9
    # fal bills Seedance 2.0 Fast by the second: $0.0112 per 1000 tokens, tokens = height * width * seconds * 24 / 1024.
    VIDEO_PRICE_PER_SECOND_USD = {"480p": 0.1076, "720p": 0.2419}
    VIDEO_PRICE_PER_CLIP_USD = {}
else:
    VIDEO_MIN_SECONDS, VIDEO_MAX_SECONDS, VIDEO_MAX_REFS = 2, 8, 7
    VIDEO_PRICE_PER_SECOND_USD = {}
    # Listed fal price per Vidu Q2 clip. 1080p is $0.20 + $0.10/s; estimated at 8 s.
    VIDEO_PRICE_PER_CLIP_USD = {"360p": 0.10, "520p": 0.20, "720p": 0.30, "1080p": 1.00}
# No spending limit per film by default (0). Set MAX_FAL_USD to make a film estimated above it refuse to start.
# One 2 x 15 s Seedance film at 720p is about $7.30.
MAX_FAL_USD = float(_env("MAX_FAL_USD", "0"))


def over_budget(cost: float) -> bool:
    return MAX_FAL_USD > 0 and cost > MAX_FAL_USD


# Other video endpoints the script agent may ask for: per-second fal price and longest clip.
# The lean agent films one continuous take of up to 30 s on Seedance 2.5 (prices from harness/lean.py).
SEEDANCE_25 = "bytedance/seedance-2.5/reference-to-video"
MODEL_PRICE_PER_SECOND_USD = {SEEDANCE_25: {"480p": 0.2205, "720p": 0.473, "1080p": 1.164}}
MODEL_MAX_SECONDS = {SEEDANCE_25: 30}


def clip_price_usd(seconds: float, model: str | None = None, resolution: str | None = None) -> float:
    """Estimated fal price of one generated clip (the configured model and resolution unless named)."""
    model, resolution = model or VIDEO_MODEL, resolution or VIDEO_RESOLUTION
    if model in MODEL_PRICE_PER_SECOND_USD:
        return MODEL_PRICE_PER_SECOND_USD[model][resolution] * seconds
    if NATIVE_AUDIO:
        return VIDEO_PRICE_PER_SECOND_USD[resolution] * seconds
    return VIDEO_PRICE_PER_CLIP_USD[resolution]

# --- edit ---
FPS = 24
XFADE = 0.4  # seconds of cross-fade between shots
TAIL = 0.35  # breathing room after each line of narration
LEAD = 0.15  # narration starts this long after its shot does
MAX_SLOWDOWN = 1.25
AMBIENT_VOLUME = 0.18

_HEIGHT = {"360p": 360, "480p": 480, "520p": 520, "720p": 720, "1080p": 1080}
_ASPECT = {"16:9": (16, 9), "9:16": (9, 16), "1:1": (1, 1)}


def frame_size() -> tuple[int, int]:
    """Output frame (w, h) for the configured resolution and aspect, even numbers."""
    short = _HEIGHT[VIDEO_RESOLUTION]
    aw, ah = _ASPECT[VIDEO_ASPECT]
    if aw >= ah:
        w, h = short * aw / ah, short
    else:
        w, h = short, short * ah / aw
    return int(w) // 2 * 2, int(h) // 2 * 2


# --- script agent (harness/, maintained separately; we only call it) ---
HARNESS_DIR = Path(_env("HARNESS_DIR", str(ROOT / "harness")))
SCRIPT_AGENT = _env("SCRIPT_AGENT", "harness")  # "harness" or "builtin" (storyboard.py)
# Which harness pipeline: "lean" (lean.py: see, search, write in one call; about 2 min) or "staged" (run.py; about 12 min).
AGENT_PIPELINE = _env("AGENT_PIPELINE", "lean")
AGENT_VIDEO_RESOLUTION = _env("AGENT_VIDEO_RESOLUTION", "480p")  # lean films: one 30 s take is about $6.60 at 480p
HARNESS_TIMEOUT = int(_env("HARNESS_TIMEOUT", "1500"))
IMAGE_MODEL = _env("IMAGE_MODEL", "fal-ai/nano-banana-pro/edit")
IMAGE_PRICE_USD = 0.15  # per reference image, nano-banana-pro/edit


def use_agent() -> bool:
    """Write the script with the harness agent (needs LIVE=llm); otherwise with storyboard.py or a hand-written file."""
    script = "lean.py" if AGENT_PIPELINE == "lean" else "run.py"
    return SCRIPT_AGENT == "harness" and is_live("llm") and (HARNESS_DIR / script).exists()


# A film already in the library is shown through the same making-of steps, replayed in this many seconds.
REPLAY_SECONDS = float(_env("REPLAY_SECONDS", "12"))


def url_for(path: Path) -> str:
    """Web address of a file under output/ or exhibits/."""
    for prefix, root in (("/output", OUTPUT_DIR), ("/exhibits", EXHIBITS_DIR)):
        if path.is_relative_to(root):
            return f"{prefix}/{path.relative_to(root).as_posix()}"
    raise ValueError(f"{path} is not served by the web app")


LANGUAGES = {"en": "English", "zh": "中文"}
STYLES = {
    "first_person": "First person",
    "kids": "For kids",
    "expert": "Expert",
    "funny": "Funny",
}
