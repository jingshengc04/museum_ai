"""Narration and sound bed.

Live: ElevenLabs text-to-speech with timestamps (word-level subtitles) and sound effects.
Mock: the macOS `say` voice if there is one, otherwise silence of the right length.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import cache, config, edit
from .exhibits import Exhibit
from .storyboard import narration_units, spoken

API = "https://api.elevenlabs.io/v1"


@dataclass
class Narration:
    path: Path
    duration: float
    words: list[dict]  # [{"w": "Look", "t0": 0.12, "t1": 0.31}], times from the start of this clip
    origin: str  # override | elevenlabs | cache | say | silence


# ---------- word timings ----------

def _is_cjk(ch: str) -> bool:
    return "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿"


def words_from_alignment(chars: list[str], starts: list[float], ends: list[float]) -> list[dict]:
    """Character timings to word timings. Each Chinese character is its own word; [tags] are dropped."""
    words: list[dict] = []
    current: dict | None = None
    in_tag = False

    def flush():
        nonlocal current
        if current:
            words.append(current)
        current = None

    for ch, t0, t1 in zip(chars, starts, ends):
        if ch == "[":
            in_tag = True
            flush()
            continue
        if ch == "]":
            in_tag = False
            continue
        if in_tag:
            continue
        if ch.isspace():
            flush()
        elif _is_cjk(ch):
            flush()
            words.append({"w": ch, "t0": round(t0, 3), "t1": round(t1, 3)})
        elif unicodedata.category(ch).startswith("P") and current is None and words:
            # Punctuation after a Chinese character or a tag rides with the previous word.
            words[-1]["w"] += ch
            words[-1]["t1"] = round(t1, 3)
        else:
            if current is None:
                current = {"w": "", "t0": round(t0, 3), "t1": round(t1, 3)}
            current["w"] += ch
            current["t1"] = round(t1, 3)
    flush()
    return words


def estimated_words(text: str, duration: float) -> list[dict]:
    """Even timings when there is no real alignment (mock voice, override audio)."""
    chars = list(spoken(text))
    if not chars:
        return []
    start, end = 0.05, max(0.1, duration - 0.15)
    step = (end - start) / len(chars)
    starts = [start + i * step for i in range(len(chars))]
    return words_from_alignment(chars, starts, [s + step for s in starts])


# ---------- mock ----------

def _say_voice(language: str) -> str | None:
    if not shutil.which("say"):
        return None
    listing = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    wanted = {"zh": ("zh_CN", ["Tingting", "Meijia"]), "en": ("en_GB", ["Daniel", "Kate"])}[language]
    names = [line.split(wanted[0])[0].strip() for line in listing.splitlines() if f" {wanted[0]} " in line]
    for preferred in wanted[1]:
        if preferred in names:
            return preferred
    return names[0] if names else None


def _mock_narration(text: str, language: str, out: Path) -> str:
    voice = _say_voice(language)
    if voice:
        aiff = out.with_suffix(".aiff")
        try:
            subprocess.run(["say", "-v", voice, "-o", str(aiff), spoken(text)], check=True, capture_output=True, timeout=60)
            edit.run(["-i", aiff, "-ar", "44100", "-ac", "2", "-b:a", "128k", out])
            return "say"
        except (subprocess.SubprocessError, RuntimeError):
            pass
        finally:
            aiff.unlink(missing_ok=True)
    seconds = max(1.5, narration_units(text, language) / (3.8 if language == "zh" else 2.5))
    edit.run(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{seconds:.2f}", "-b:a", "128k", out])
    return "silence"


# ---------- live ----------

def _headers() -> dict:
    return {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}


def _elevenlabs_tts(text: str, voice_id: str) -> tuple[bytes, list[dict]]:
    import httpx

    # Only eleven_v3 understands [tags]; other models would read them aloud.
    body = {"text": text if config.ELEVEN_MODEL == "eleven_v3" else spoken(text), "model_id": config.ELEVEN_MODEL}
    response = httpx.post(
        f"{API}/text-to-speech/{voice_id}/with-timestamps",
        params={"output_format": "mp3_44100_128"},
        headers=_headers(), json=body, timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(
            f"ElevenLabs TTS failed ({response.status_code}): {response.text[:300]} "
            f"[model={config.ELEVEN_MODEL}; try ELEVEN_MODEL=eleven_multilingual_v2 if the model is the problem]"
        )
    data = response.json()
    alignment = data.get("alignment") or data.get("normalized_alignment") or {}
    words = words_from_alignment(
        alignment.get("characters", []),
        alignment.get("character_start_times_seconds", []),
        alignment.get("character_end_times_seconds", []),
    )
    return base64.b64decode(data["audio_base64"]), words


def _live_narration(text: str, voice_id: str, out: Path) -> tuple[list[dict], str]:
    cache_key = cache.key("tts-v1", config.ELEVEN_MODEL, voice_id, text)
    audio, words_file = cache.path("tts", cache_key, ".mp3"), cache.path("tts", cache_key, ".json")
    origin = "cache"
    if not (audio.exists() and words_file.exists()):
        blob, words = _elevenlabs_tts(text, voice_id)
        audio.write_bytes(blob)
        words_file.write_text(json.dumps(words, ensure_ascii=False))
        origin = "elevenlabs"
    shutil.copyfile(audio, out)
    return json.loads(words_file.read_text()), origin


# ---------- public ----------

def narrate(shot_id: int, text: str, language: str, exhibit: Exhibit, out: Path) -> Narration:
    out.parent.mkdir(parents=True, exist_ok=True)
    words: list[dict] = []
    override = exhibit.override(shot_id, ".mp3")
    if override:
        shutil.copyfile(override, out)
        origin = "override"
        timings = exhibit.override(shot_id, ".words.json")
        if timings:
            words = json.loads(timings.read_text())
    elif config.is_live("voice"):
        words, origin = _live_narration(text, exhibit.voice_id(language), out)
    else:
        origin = _mock_narration(text, language, out)
    length = edit.duration(out)
    return Narration(path=out, duration=length, words=words or estimated_words(text, length), origin=origin)


def ambient(exhibit: Exhibit, out: Path) -> tuple[Path, str]:
    """A loopable sound bed for the whole film."""
    out.parent.mkdir(parents=True, exist_ok=True)
    override = exhibit.ambient_override()
    if override:
        edit.run(["-i", override, "-ar", "44100", "-ac", "2", "-b:a", "128k", out])
        return out, "override"
    prompt = exhibit.data.get("ambience", "")
    if config.is_live("voice") and prompt:
        def produce(tmp: Path) -> None:
            import httpx

            response = httpx.post(
                f"{API}/sound-generation", headers=_headers(), timeout=180,
                json={"text": prompt, "duration_seconds": 20, "prompt_influence": 0.4},
            )
            if response.status_code >= 400:
                raise RuntimeError(f"ElevenLabs sound effect failed ({response.status_code}): {response.text[:300]}")
            tmp.write_bytes(response.content)

        cached, was_cached = cache.cached_file("sfx", cache.key("sfx-v1", prompt, 20), ".mp3", produce)
        shutil.copyfile(cached, out)
        return out, "cache" if was_cached else "elevenlabs"
    # Mock: a slow low rumble, enough to prove the bed and the mix work.
    edit.run(["-f", "lavfi", "-i", "anoisesrc=color=brown:duration=20:amplitude=0.8:seed=7",
              "-af", "lowpass=f=260,tremolo=f=0.15:d=0.6,afade=t=in:d=1,afade=t=out:st=19:d=1",
              "-ar", "44100", "-ac", "2", "-b:a", "128k", out])
    return out, "mock"
