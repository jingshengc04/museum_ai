"""ffmpeg work: fit each clip to its narration, then join everything into one film.

Narration is the master timeline. Video models only return fixed lengths, so each clip is
trimmed, slowed (up to 25%) or frozen on its last frame to fill its slot. Cross-fades and a
continuous sound bed hide the seams.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config


def run(args: list, timeout: int = 600) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()[-800:]}")


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {result.stderr.strip()[-400:]}")
    return float(json.loads(result.stdout)["format"]["duration"])


def fit_plan(source: float, target: float) -> dict:
    """How to make a `source`-second clip last `target` seconds."""
    if source >= target:
        return {"how": "trim", "speed": 1.0, "freeze": 0.0}
    speed = min(target / source, config.MAX_SLOWDOWN)
    freeze = max(0.0, target - source * speed)
    return {"how": "slow+freeze" if freeze > 0.01 else "slow", "speed": round(speed, 4), "freeze": round(freeze, 3)}


def fit_clip(src: Path, target: float, out: Path) -> dict:
    """Re-encode `src` to exactly `target` seconds at the film's size and frame rate."""
    w, h = config.frame_size()
    plan = fit_plan(duration(src), target)
    filters = [
        f"scale={w}:{h}:force_original_aspect_ratio=increase",
        f"crop={w}:{h}",
        f"setpts={plan['speed']}*PTS",
        f"fps={config.FPS}",
        # Hold the last frame: covers the freeze, and half a second spare so `-t` always has frames.
        f"tpad=stop_mode=clone:stop_duration={plan['freeze'] + 0.5}",
        "format=yuv420p",
    ]
    run(["-i", src, "-vf", ",".join(filters), "-t", f"{target:.3f}", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
    return plan


def thumbnail(clip: Path, out: Path) -> None:
    run(["-ss", f"{duration(clip) / 2:.2f}", "-i", clip, "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "4", out])


def timeline(narration_lengths: list[float]) -> list[dict]:
    """Slot for each shot: where it starts, how long it lasts, when its narration starts."""
    slots, t = [], 0.0
    for length in narration_lengths:
        slot = config.LEAD + length + config.TAIL
        slots.append({"start": round(t, 3), "length": round(slot, 3), "voice_at": round(t + config.LEAD, 3)})
        t += slot
    return slots


def clip_length(slot: dict, is_last: bool) -> float:
    """A clip runs past its slot by the cross-fade, so fading never eats narration time."""
    return slot["length"] + (0 if is_last else config.XFADE)


def assemble(clips: list[Path], slots: list[dict], voices: list[Path], ambient: Path | None, out: Path) -> float:
    """Cross-fade the fitted clips, lay each narration at its slot, loop the sound bed under it all."""
    total = slots[-1]["start"] + slots[-1]["length"]
    args: list = []
    for clip in clips:
        args += ["-i", clip]
    for voice in voices:
        args += ["-i", voice]
    if ambient:
        args += ["-stream_loop", "-1", "-i", ambient]

    n = len(clips)
    graph = []
    last = "0:v"
    for i in range(1, n):
        label = f"v{i}"
        graph.append(f"[{last}][{i}:v]xfade=transition=fade:duration={config.XFADE}:offset={slots[i]['start']:.3f}[{label}]")
        last = label
    graph.append(f"[{last}]fade=t=in:d=0.5,fade=t=out:st={total - 0.6:.3f}:d=0.6,format=yuv420p[vout]")

    mix = []
    for i, slot in enumerate(slots):
        delay = int(slot["voice_at"] * 1000)
        graph.append(f"[{n + i}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={delay}:all=1[a{i}]")
        mix.append(f"[a{i}]")
    if ambient:
        graph.append(
            f"[{2 * n}:a]aresample=44100,aformat=channel_layouts=stereo,volume={config.AMBIENT_VOLUME},"
            f"atrim=0:{total:.3f},afade=t=in:d=1.5,afade=t=out:st={total - 1.5:.3f}:d=1.5[bed]"
        )
        mix.append("[bed]")
    graph.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest,alimiter=limit=0.95[aout]")

    run([*args, "-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]",
         "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    return total


# ---------- clips that already carry their own sound ----------

def has_audio(path: Path) -> bool:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    return bool(result.stdout.strip())


def conform(src: Path, out: Path) -> float:
    """Re-encode a clip to the film's size, frame rate and sound format, keeping its own audio. Returns its length."""
    w, h = config.frame_size()
    look = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={config.FPS},format=yuv420p"
    sound = ["-i", src] if has_audio(src) else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    length = duration(src)
    run(["-i", src, *sound, "-map", "0:v:0", "-map", "1:a:0", "-vf", look, "-t", f"{length:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "160k", out])
    return duration(out)


def scene_timeline(lengths: list[float], fade: float | None = None) -> list[dict]:
    """Where each clip sits when neighbours overlap by the cross-fade."""
    fade = config.XFADE if fade is None else fade
    slots, t = [], 0.0
    for i, length in enumerate(lengths):
        slots.append({"start": round(t, 3), "length": round(length, 3), "voice_at": round(t, 3)})
        t += length - (fade if i < len(lengths) - 1 else 0)
    return slots


def join(clips: list[Path], slots: list[dict], out: Path, fade: float | None = None) -> float:
    """Cross-fade conformed clips into one film, picture and sound together. A tiny `fade` is a clean cut."""
    fade = config.XFADE if fade is None else fade
    total = slots[-1]["start"] + slots[-1]["length"]
    args: list = []
    for clip in clips:
        args += ["-i", clip]
    graph, picture, sound = [], "0:v", "0:a"
    for i in range(1, len(clips)):
        graph.append(f"[{picture}][{i}:v]xfade=transition=fade:duration={fade}:offset={slots[i]['start']:.3f}[v{i}]")
        graph.append(f"[{sound}][{i}:a]acrossfade=d={fade}[a{i}]")
        picture, sound = f"v{i}", f"a{i}"
    graph.append(f"[{picture}]fade=t=in:d=0.5,fade=t=out:st={total - 0.6:.3f}:d=0.6,format=yuv420p[vout]")
    graph.append(f"[{sound}]afade=t=in:d=0.3,afade=t=out:st={total - 0.6:.3f}:d=0.6[aout]")
    run([*args, "-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out])
    return total
