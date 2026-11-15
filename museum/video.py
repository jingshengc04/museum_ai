"""One video clip per shot.

Order of preference per shot:
  1. drop-in clip  exhibits/<id>/overrides/shot_NN.mp4  (e.g. made in the fal playground)
  2. cached result of an earlier paid render with the same inputs
  3. live render on fal (LIVE=video), reference-to-video with the shot's reference images
  4. mock: an animatic card drawn locally, free

With a model that makes its own sound (Seedance) the clip arrives with the narration spoken in it,
and the mock clip gets a stand-in voice so the rest of the pipeline sees the same thing.
"""
from __future__ import annotations

import json
import math
import shutil
import textwrap
import threading
from dataclasses import dataclass
from pathlib import Path

from . import cache, config, edit, voice
from .exhibits import Exhibit
from .storyboard import Shot, scene_prompt, video_prompt

REFS_PER_SHOT = 4
_upload_lock = threading.Lock()


@dataclass
class ShotPlan:
    shot: Shot
    seconds: int  # length asked of the video model
    prompt: str
    refs: list[Path]
    source: str  # override | cache | generate | mock
    cache_key: str = ""
    override: Path | None = None
    safe_refs: list[Path] | None = None  # refs to retry with if the model refuses `refs` (e.g. close-ups of human figures)
    note: str = ""  # what happened while rendering that the visitor should hear about
    model: str = ""  # video endpoint, when not config.VIDEO_MODEL (the script agent may ask for another)
    resolution: str = ""  # likewise for config.VIDEO_RESOLUTION


def request_seconds(clip_length: float) -> int:
    return min(config.VIDEO_MAX_SECONDS, max(config.VIDEO_MIN_SECONDS, math.ceil(clip_length)))


def refs_for(shot: Shot, exhibit: Exhibit) -> list[Path]:
    chosen = [exhibit.refs[name] for name in shot.refs if name in exhibit.refs]
    if not chosen:
        chosen = list(exhibit.refs.values())
    return chosen[:REFS_PER_SHOT]


def plan(shot: Shot, exhibit: Exhibit, clip_length: float, photo: Path | None = None, language: str = "en") -> ShotPlan:
    """Decide where a shot's clip comes from. `photo` is the visitor's own picture, used as a reference when given."""
    seconds = request_seconds(clip_length)
    refs = refs_for(shot, exhibit)
    if config.NATIVE_AUDIO:
        images = ["the character" if i == 0 else "another view of the character" for i in range(len(refs))]
        if photo:
            refs, images = [photo, *refs], ["the visitor's photo of the real exhibit in the museum", *images]
        prompt = scene_prompt(shot, exhibit, images)
        if language == "zh":
            prompt += " The voice-over is spoken in Mandarin Chinese."
    else:
        prompt = video_prompt(shot, exhibit)
    override = exhibit.override(shot.id, ".mp4")
    if override:
        return ShotPlan(shot, seconds, prompt, refs, "override", override=override)
    if not config.is_live("video"):
        return ShotPlan(shot, seconds, prompt, refs, "mock")
    cache_key = cache.key(
        "video-v2", config.VIDEO_MODEL, prompt, [cache.file_hash(r) for r in refs], seconds,
        config.VIDEO_RESOLUTION, config.VIDEO_ASPECT, shot.movement, exhibit.data.get("seed"),
    )
    hit = cache.path("video", cache_key, ".mp4").exists()
    return ShotPlan(shot, seconds, prompt, refs, "cache" if hit else "generate", cache_key=cache_key)


def plan_request(shot: Shot, exhibit: Exhibit, prompt: str, refs: list[Path], seconds: int,
                 model: str | None = None, resolution: str | None = None) -> ShotPlan:
    """A clip whose prompt and reference images were prepared elsewhere (the script agent), in @Image order."""
    model, resolution = model or config.VIDEO_MODEL, resolution or config.VIDEO_RESOLUTION
    longest = config.MODEL_MAX_SECONDS.get(model, config.VIDEO_MAX_SECONDS)
    seconds = min(longest, max(config.VIDEO_MIN_SECONDS, int(seconds)))
    override = exhibit.override(shot.id, ".mp4")
    if override:
        return ShotPlan(shot, seconds, prompt, refs, "override", override=override, model=model, resolution=resolution)
    if not config.is_live("video"):
        return ShotPlan(shot, seconds, prompt, refs, "mock", model=model, resolution=resolution)
    cache_key = cache.key("video-v2", model, prompt, [cache.file_hash(r) for r in refs], seconds, resolution, config.VIDEO_ASPECT)
    hit = cache.path("video", cache_key, ".mp4").exists()
    return ShotPlan(shot, seconds, prompt, refs, "cache" if hit else "generate", cache_key=cache_key, model=model, resolution=resolution)


# ---------- reference images made from the visitor's photo (script agent) ----------

def _image_key(prompt: str, photo: Path | None) -> str:
    return cache.key("image-v1", config.IMAGE_MODEL, prompt, cache.file_hash(photo) if photo else None)


def cached_image(prompt: str, photo: Path | None) -> Path | None:
    path = cache.path("images", _image_key(prompt, photo), ".png")
    return path if path.exists() else None


def reference_image(prompt: str, photo: Path | None) -> Path:
    """One reference image: the visitor's photo edited by a prompt. Paid once, then cached by its inputs."""
    def produce(tmp: Path) -> None:
        import fal_client
        import httpx

        arguments = {"prompt": prompt, "resolution": "1K", "output_format": "png"}
        if photo:
            arguments["image_urls"] = [_upload(photo)]
        result = fal_client.subscribe(config.IMAGE_MODEL, arguments=arguments, client_timeout=600)
        with httpx.stream("GET", result["images"][0]["url"], timeout=120, follow_redirects=True) as response:
            response.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in response.iter_bytes():
                    fh.write(chunk)

    path, _ = cache.cached_file("images", _image_key(prompt, photo), ".png", produce)
    return path


def estimate_usd(plans: list[ShotPlan]) -> float:
    return round(sum(config.clip_price_usd(p.seconds, p.model, p.resolution) for p in plans if p.source == "generate"), 2)


def worst_case_usd(shots: int) -> float:
    return round(shots * config.clip_price_usd(config.VIDEO_MAX_SECONDS), 2)


def check_budget(plans: list[ShotPlan]) -> float:
    cost = estimate_usd(plans)
    if config.over_budget(cost):
        raise RuntimeError(
            f"This film would spend about ${cost:.2f} on fal, above MAX_FAL_USD=${config.MAX_FAL_USD:.2f}. "
            f"Check with the team, then raise MAX_FAL_USD to go ahead."
        )
    generating = [p for p in plans if p.source == "generate"]
    if generating and not config.NATIVE_AUDIO and not all(p.refs for p in generating):
        raise RuntimeError(
            "Reference-to-video needs at least one reference image. "
            "Drop the character crops (no text labels) into exhibits/<id>/refs/."
        )
    return cost


# ---------- live: fal ----------

def request_arguments(p: ShotPlan, image_urls: list[str]) -> dict:
    """The request body for the configured model family."""
    if "seedance" in (p.model or config.VIDEO_MODEL):  # Seedance 2.0 / 2.5 reference-to-video
        arguments = {
            "prompt": p.prompt,
            "duration": str(p.seconds),
            "resolution": p.resolution or config.VIDEO_RESOLUTION,
            "aspect_ratio": config.VIDEO_ASPECT,
            "generate_audio": True,
        }
        if image_urls:
            arguments["image_urls"] = image_urls
        return arguments
    return {  # Vidu Q2 reference-to-video
        "prompt": p.prompt,
        "reference_image_urls": image_urls,
        "duration": p.seconds,
        "resolution": config.VIDEO_RESOLUTION,
        "aspect_ratio": config.VIDEO_ASPECT,
        "movement_amplitude": p.shot.movement,
        "bgm": False,
    }


def _upload(path: Path) -> str:
    """Upload a reference image to fal storage once; remember the URL by content hash."""
    import fal_client

    with _upload_lock:  # shots render in parallel and share this index
        index = cache.path("uploads", "fal", ".json")
        known = json.loads(index.read_text()) if index.exists() else {}
        digest = cache.file_hash(path)
        if digest not in known:
            if Path(path).suffix.lower() in (".webp", ".heic"):  # JPEG is accepted everywhere
                from PIL import Image

                jpg = cache.path("uploads", digest, ".jpg")
                Image.open(path).convert("RGB").save(jpg, quality=92)
                path = jpg
            known[digest] = fal_client.upload_file(path)
            index.write_text(json.dumps(known, indent=2))
        return known[digest]


def refused(error: Exception) -> bool:
    """The model's moderation turned the request down (refused requests are not billed)."""
    return "content_policy_violation" in str(error)


def _fal_render(p: ShotPlan, exhibit: Exhibit, tmp: Path) -> None:
    import fal_client
    import httpx

    # Seedance refuses references that look like real people, and marble statues count. Retry with the safe
    # references (wide views, scenery), then with the prompt alone.
    model = p.model or config.VIDEO_MODEL
    attempts = [p.refs]
    if "seedance" in model:
        attempts += [refs for refs in (p.safe_refs, []) if refs is not None and refs != p.refs]
    for number, refs in enumerate(attempts):
        arguments = request_arguments(p, [_upload(r) for r in refs][: config.VIDEO_MAX_REFS])
        if "seedance" not in model and exhibit.data.get("seed") is not None:
            arguments["seed"] = exhibit.data["seed"]
        try:
            result = fal_client.subscribe(model, arguments=arguments, client_timeout=1200)
            break
        except Exception as error:
            if not refused(error) or number == len(attempts) - 1:
                raise
            following = attempts[number + 1]
            p.note = (f"The video model would not use some reference pictures for scene {p.shot.id}; "
                      + (f"filming it from {len(following)} wider view(s) instead." if following else "filming it from the script alone."))
    with httpx.stream("GET", result["video"]["url"], timeout=300, follow_redirects=True) as response:
        response.raise_for_status()
        with tmp.open("wb") as fh:
            for chunk in response.iter_bytes():
                fh.write(chunk)


# ---------- mock: animatic card ----------

_FONTS = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size: int):
    from PIL import ImageFont

    for candidate in _FONTS:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _card(p: ShotPlan, exhibit: Exhibit, out: Path) -> None:
    """A still that shows what the shot will be: background, reference crops in use, shot text."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

    w, h = (v * 2 for v in config.frame_size())
    unit = min(w, h) / 720
    if exhibit.photo:
        bg = ImageOps.fit(Image.open(exhibit.photo).convert("RGB"), (w, h))
        bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(6 * unit))).enhance(0.38)
    else:
        top, bottom = (9, 38 + 6 * (p.shot.id % 5), 74 + 9 * (p.shot.id % 4)), (3, 9, 22)
        bg = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(bg)
        for y in range(h):
            mix = y / h
            draw.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * mix) for a, b in zip(top, bottom)))
    draw = ImageDraw.Draw(bg)
    margin = int(56 * unit)

    x = w - margin
    for ref in reversed(p.refs):
        thumb = ImageOps.contain(Image.open(ref).convert("RGB"), (int(210 * unit), int(210 * unit)))
        x -= thumb.width
        bg.paste(thumb, (x, margin))
        x -= int(14 * unit)

    draw.text((margin, margin), f"SHOT {p.shot.id:02d}", font=_font(int(30 * unit)), fill=(127, 219, 218))
    draw.text((margin, margin + int(44 * unit)), f"{p.seconds}s  ·  movement {p.shot.movement}  ·  mock, no credits used",
              font=_font(int(20 * unit)), fill=(150, 170, 190))
    y = int(h * 0.27)  # under the header, clear of where subtitles sit
    for label, text, size in (("", p.shot.action, 38), ("CAMERA", p.shot.camera, 22), ("MOOD", p.shot.mood, 22)):
        font = _font(int(size * unit))
        lines = textwrap.wrap(f"{label}  {text}" if label else text, width=int(1650 / size))
        draw.multiline_text((margin, y), "\n".join(lines), font=font, spacing=int(size * unit * 0.3),
                            fill=(244, 238, 226) if not label else (170, 186, 204))
        y += int(size * unit * 1.3) * len(lines) + int(14 * unit)
    bg.save(out, quality=90)


def _mock_render(p: ShotPlan, exhibit: Exhibit, out: Path, language: str = "en") -> None:
    card = out.with_suffix(".card.jpg")
    spoken = out.with_suffix(".voice.mp3")
    _card(p, exhibit, card)
    w, h = config.frame_size()
    frames = p.seconds * config.FPS
    picture = ["-loop", "1", "-i", card]
    look = f"zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={config.FPS},format=yuv420p"
    encode = ["-frames:v", frames, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20"]
    try:
        if config.NATIVE_AUDIO:  # stand in for the model's own voice track
            voice._mock_narration(p.shot.narration, language, spoken)
            edit.run([*picture, "-i", spoken, "-filter_complex", f"[0:v]{look}[v];[1:a]adelay=500:all=1,apad[a]",
                      "-map", "[v]", "-map", "[a]", *encode, "-c:a", "aac", "-t", p.seconds, out])
        else:
            edit.run([*picture, "-vf", look, *encode, out])
    finally:
        card.unlink(missing_ok=True)
        spoken.unlink(missing_ok=True)


# ---------- public ----------

def render(p: ShotPlan, exhibit: Exhibit, out: Path, language: str = "en") -> Path:
    """Produce the raw (unfitted) clip for a planned shot at `out`."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if p.source == "override":
        shutil.copyfile(p.override, out)
    elif p.source in ("cache", "generate"):
        cached, _ = cache.cached_file("video", p.cache_key, ".mp4", lambda tmp: _fal_render(p, exhibit, tmp))
        shutil.copyfile(cached, out)
    else:
        _mock_render(p, exhibit, out, language)
    return out
