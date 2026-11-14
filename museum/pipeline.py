"""Photo in, film out. Emits events as it works so the wait can be part of the show."""
from __future__ import annotations

import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from . import cache, config, edit, exhibits, storyboard, video, voice
from .exhibits import Exhibit

Emit = Callable[..., None]

SENTENCE_END = tuple(".?!。？！")


def captions_for(words: list[dict], offset: float, language: str) -> list[dict]:
    """Group timed words into subtitle lines on the film's timeline."""
    joiner = "" if language == "zh" else " "
    limit = 15 if language == "zh" else 38
    cues, line = [], []

    def flush():
        if line:
            cues.append({
                "start": round(offset + line[0]["t0"], 3),
                "end": round(offset + line[-1]["t1"] + 0.25, 3),
                "text": joiner.join(w["w"] for w in line),
                "words": [{"w": w["w"], "t0": round(offset + w["t0"], 3), "t1": round(offset + w["t1"], 3)} for w in line],
            })
            line.clear()

    for word in words:
        if line and len(joiner.join(w["w"] for w in line)) + len(word["w"]) > limit:
            flush()
        line.append(word)
        if word["w"].endswith(SENTENCE_END):
            flush()
    flush()
    for cue, following in zip(cues, cues[1:]):
        cue["end"] = min(cue["end"], following["start"])
    return cues


def _vtt(cues: list[dict]) -> str:
    def stamp(t: float) -> str:
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:06.3f}"

    blocks = [f"{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in cues]
    return "WEBVTT\n\n" + "\n\n".join(blocks) + "\n"


# ---------- film library: an exhibit that already has a film does not get rendered again ----------

def fingerprint(exhibit: Exhibit, language: str, style: str) -> str:
    """Changes whenever the material a film is made from changes, so stale films are not reused."""
    board = exhibit.storyboard_file(language, style)
    if not board.exists():
        board = exhibit.storyboard_file(language, "first_person")
    files = [board, *exhibit.refs.values(), *sorted((exhibit.dir / "overrides").glob("*"))]
    return cache.key("film-v2", config.VIDEO_MODEL, exhibit.data, language, style, [(f.name, cache.file_hash(f)) for f in files if f.is_file()])


def library_hit(exhibit: Exhibit, language: str, style: str) -> Path | None:
    """The saved film for this exhibit, language and style, if it is still current."""
    folder = exhibit.demo_dir(language, style)
    if not all((folder / name).exists() for name in ("final.mp4", "manifest.json", "events.json")):
        return None
    saved = json.loads((folder / "manifest.json").read_text())
    if saved.get("fingerprint") != fingerprint(exhibit, language, style):
        return None
    # A mock film must not stand in once the real service is switched on.
    services = ("video",) if config.NATIVE_AUDIO else ("voice", "video")
    if any(config.is_live(service) and not saved["modes"][service] for service in services):
        return None
    if config.is_live("llm") and saved["storyboard_origin"] == "fallback":
        return None
    return folder


def replay(folder: Path, emit: Emit) -> None:
    """Walk the visitor through the film's recorded making-of, compressed to a few seconds."""
    events = json.loads((folder / "events.json").read_text())
    first = next(i for i, e in enumerate(events) if e["type"] == "step" and e["step"] == "identify" and e["status"] == "done") + 1
    events = events[first:]
    scale = config.REPLAY_SECONDS / max(events[-1]["t"] - events[0]["t"], 0.001)
    previous = events[0]["t"]
    for event in events:
        time.sleep(min((event["t"] - previous) * scale, 3.0))
        previous = event["t"]
        data = {k: v for k, v in event.items() if k not in ("type", "t")}
        if "thumb" in data:
            data["thumb"] = config.url_for(folder / "thumbs" / Path(data["thumb"]).name)
        emit(event["type"], **data)


def _narrated_film(job_dir: Path, exhibit: Exhibit, board, language: str, emit: Emit) -> dict:
    """Silent video model: record the narration first, then fit every clip to its line and mix the sound."""
    # 3. Voice first: narration length decides how long every clip must be.
    emit("step", step="voice", status="start")
    character = exhibit.data.get("character", {}).get("name") or exhibit.name
    emit("thought", text=f"Recording {character}'s voice, one line per shot…")

    def record(shot):
        narration = voice.narrate(shot.id, shot.narration, language, exhibit, job_dir / "audio" / f"shot_{shot.id:02d}.mp3")
        emit("shot", id=shot.id, stage="voice", seconds=round(narration.duration, 2), source=narration.origin)
        return narration

    with ThreadPoolExecutor(max_workers=4) as pool:
        narrations = list(pool.map(record, board.shots))
    bed, bed_origin = voice.ambient(exhibit, job_dir / "audio" / "ambient.mp3")
    slots = edit.timeline([n.duration for n in narrations])
    total = slots[-1]["start"] + slots[-1]["length"]
    emit("thought", text=f"Voice is {total:.0f} seconds long. That is now the film's timeline.")
    emit("step", step="voice", status="done")

    # 4. Video
    emit("step", step="video", status="start")
    lengths = [edit.clip_length(slot, i == len(slots) - 1) for i, slot in enumerate(slots)]
    plans = [video.plan(shot, exhibit, length) for shot, length in zip(board.shots, lengths)]
    cost = video.check_budget(plans)
    paid = sum(1 for p in plans if p.source == "generate")
    if paid:
        emit("thought", text=f"Rendering {paid} new clip(s) on fal at {config.VIDEO_RESOLUTION}, about ${cost:.2f}.")
    elif not config.is_live("video"):
        emit("thought", text="Video is in mock mode: drawing animatic cards instead of spending fal credits.")

    def draw(args):
        p, length = args
        emit("thought", text=f"Drawing shot {p.shot.id}: {p.shot.action}")
        emit("shot", id=p.shot.id, stage="video", status="start", source=p.source)
        raw = video.render(p, exhibit, job_dir / "raw" / f"shot_{p.shot.id:02d}.mp4")
        fitted = job_dir / "fit" / f"shot_{p.shot.id:02d}.mp4"
        fitted.parent.mkdir(exist_ok=True)
        fit = edit.fit_clip(raw, length, fitted)
        if fit["how"] != "trim":
            slowed = f"slowing it {round((fit['speed'] - 1) * 100)}%"
            frozen = f" and holding the last frame {fit['freeze']:.1f}s" if fit["freeze"] else ""
            emit("thought", text=f"Shot {p.shot.id}'s clip is shorter than its line, so {slowed}{frozen}.")
        thumb = job_dir / "thumbs" / f"shot_{p.shot.id:02d}.jpg"
        thumb.parent.mkdir(exist_ok=True)
        edit.thumbnail(fitted, thumb)
        emit("shot", id=p.shot.id, stage="video", status="done", source=p.source, thumb=config.url_for(thumb))
        return fitted, fit

    workers = config.FAL_CONCURRENCY if paid else 4
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rendered = list(pool.map(draw, zip(plans, lengths)))
    emit("step", step="video", status="done")

    # 5. Edit
    emit("step", step="edit", status="start")
    emit("thought", text="Cutting it together: cross-fades, voice, sound bed, subtitles.")
    final = job_dir / "final.mp4"
    edit.assemble([clip for clip, _ in rendered], slots, [n.path for n in narrations], bed, final)

    cues = []
    for narration, slot in zip(narrations, slots):
        cues += captions_for(narration.words, slot["voice_at"], language)
    (job_dir / "captions.vtt").write_text(_vtt(cues))
    return {"slots": slots, "total": total, "plans": plans, "fits": [fit for _, fit in rendered],
            "voices": [n.origin for n in narrations], "cues": cues, "ambient": bed_origin, "cost": cost}


def _native_film(job_dir: Path, exhibit: Exhibit, board, language: str, emit: Emit, photo: Path | None) -> dict:
    """Model that makes its own sound: each clip arrives with the narration spoken in it, so clips are only joined."""
    emit("step", step="video", status="start")
    plans = [video.plan(shot, exhibit, shot.seconds or config.VIDEO_MAX_SECONDS, photo, language) for shot in board.shots]
    cost = video.check_budget(plans)
    paid = [p for p in plans if p.source == "generate"]
    if paid:
        seconds = sum(p.seconds for p in paid)
        emit("thought", text=f"Rendering {len(paid)} new scene(s) with sound on fal, {seconds} s at {config.VIDEO_RESOLUTION}, about ${cost:.2f}.")
    elif not config.is_live("video"):
        emit("thought", text="Video is in mock mode: drawing animatic cards with a stand-in voice instead of spending fal credits.")

    def draw(p):
        emit("thought", text=f"Filming scene {p.shot.id}: {p.shot.action}")
        emit("shot", id=p.shot.id, stage="video", status="start", source=p.source)
        raw = video.render(p, exhibit, job_dir / "raw" / f"shot_{p.shot.id:02d}.mp4", language)
        clip = job_dir / "fit" / f"shot_{p.shot.id:02d}.mp4"
        clip.parent.mkdir(exist_ok=True)
        length = edit.conform(raw, clip)
        thumb = job_dir / "thumbs" / f"shot_{p.shot.id:02d}.jpg"
        thumb.parent.mkdir(exist_ok=True)
        edit.thumbnail(clip, thumb)
        emit("shot", id=p.shot.id, stage="video", status="done", source=p.source, thumb=config.url_for(thumb))
        return clip, length

    with ThreadPoolExecutor(max_workers=config.FAL_CONCURRENCY if paid else 4) as pool:
        rendered = list(pool.map(draw, plans))
    emit("step", step="video", status="done")

    emit("step", step="edit", status="start")
    emit("thought", text="Joining the scenes and writing subtitles.")
    slots = edit.scene_timeline([length for _, length in rendered])
    total = edit.join([clip for clip, _ in rendered], slots, job_dir / "final.mp4")

    # The model does not say when each word falls, so subtitle lines are spread over the scene by their length.
    cues = []
    for shot, slot in zip(board.shots, slots):
        lines = captions_for(voice.estimated_words(shot.narration, slot["length"] - 1.0), slot["start"] + 0.5, language)
        for line in lines:
            for word in line["words"]:
                word["t0"] = line["start"]  # whole line lights up at once: no false word-by-word precision
        cues += lines
    (job_dir / "captions.vtt").write_text(_vtt(cues))
    voiced = "model" if config.is_live("video") else "mock"
    return {"slots": slots, "total": total, "plans": plans, "fits": [{"how": "native", "speed": 1.0, "freeze": 0.0} for _ in plans],
            "voices": [voiced if p.source != "override" else "override" for p in plans], "cues": cues, "ambient": "model", "cost": cost}


def make_film(job_dir: Path, language: str, style: str, emit: Emit, photo: Path | None = None,
              exhibit_id: str | None = None, fresh: bool = False, save: bool = True) -> tuple[dict, Path]:
    """Make the film, or reuse the library's. Returns the manifest and the folder that holds the film.

    `fresh` renders even when the library has this film; `save` adds a new film to the library.
    """
    started = time.time()
    job_dir.mkdir(parents=True, exist_ok=True)
    recorded: list[dict] = []
    send = emit

    def emit(kind: str, **data) -> None:  # noqa: F811 - records what the visitor saw, for replay
        recorded.append({"type": kind, "t": round(time.time() - started, 3), **data})
        send(kind, **data)

    # 1. Which exhibit?
    emit("step", step="identify", status="start")
    candidates = [exhibits.load(exhibit_id)] if exhibit_id else exhibits.all_exhibits()
    if not candidates:
        raise RuntimeError("No exhibits are set up. Add exhibits/<id>/exhibit.json.")
    exhibit = storyboard.identify(photo, candidates, emit)
    emit("exhibit", exhibit=exhibit.public())
    sources = sorted({f["source"].split("/")[2] for f in exhibit.facts})
    emit("thought", text=f"Reading the label: {len(exhibit.facts)} facts, each with a source ({', '.join(sources)}).")
    for fact in exhibit.unsourced_facts:
        emit("thought", text=f"Leaving out \"{fact['text']}\" because it has no source yet.", level="warn")
    emit("step", step="identify", status="done")

    saved = None if fresh else library_hit(exhibit, language, style)
    if saved:
        replay(saved, emit)
        return json.loads((saved / "manifest.json").read_text()), saved

    # 2. Storyboard
    emit("step", step="story", status="start")
    board = storyboard.build(exhibit, language, style, emit)
    emit("storyboard", title=board.title, origin=board.origin, shots=[
        {"id": s.id, "narration": storyboard.spoken(s.narration), "action": s.action, "fact_ids": s.fact_ids}
        for s in board.shots
    ])
    emit("step", step="story", status="done")

    # 3-5. Sound and picture: either the model voices its own clips, or we record narration and fit clips to it.
    made = (_native_film(job_dir, exhibit, board, language, emit, photo) if config.NATIVE_AUDIO
            else _narrated_film(job_dir, exhibit, board, language, emit))
    slots, total, plans, cues, cost = made["slots"], made["total"], made["plans"], made["cues"], made["cost"]

    used = {fact_id for shot in board.shots for fact_id in shot.fact_ids}
    manifest = {
        "title": board.title,
        "exhibit": {k: exhibit.public()[k] for k in ("id", "name", "museum", "location", "character")},
        "language": language,
        "style": style,
        "storyboard_origin": board.origin,
        "video": "final.mp4",
        "captions_vtt": "captions.vtt",
        "duration": round(total, 3),
        "word_joiner": "" if language == "zh" else " ",
        "shots": [
            {
                "id": shot.id,
                "start": slot["start"],
                "end": round(slot["start"] + slot["length"], 3),
                "narration": storyboard.spoken(shot.narration),
                "fact_ids": shot.fact_ids,
                "thumb": f"thumbs/shot_{shot.id:02d}.jpg",
                "prompt": p.prompt,
                "refs": [r.stem for r in p.refs],
                "video_source": p.source,
                "voice_source": voiced,
                "fit": fit,
            }
            for shot, slot, p, voiced, fit in zip(board.shots, slots, plans, made["voices"], made["fits"])
        ],
        "captions": cues,
        "facts": [dict(f, used=f["id"] in used) for f in exhibit.facts],
        "modes": {name: m["live"] for name, m in config.modes().items()},
        "fingerprint": fingerprint(exhibit, language, style),
        "ambient_source": made["ambient"],
        "video_model": config.VIDEO_MODEL,
        "fal_cost_usd": cost,
        "seconds_to_make": round(time.time() - started, 1),
    }
    (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    emit("step", step="edit", status="done")
    (job_dir / "events.json").write_text(json.dumps(recorded, ensure_ascii=False))
    if save:
        try:
            promote(job_dir)
        except RuntimeError:
            pass  # the library already holds a real film and this one is a mock
    return manifest, job_dir


def promote(job_dir: Path, force: bool = False) -> Path:
    """Put a finished film in the library: reused for later visitors and played if a live run fails."""
    manifest = json.loads((job_dir / "manifest.json").read_text())
    exhibit = exhibits.load(manifest["exhibit"]["id"])
    target = exhibit.demo_dir(manifest["language"], manifest["style"])
    if target.exists():
        current = json.loads((target / "manifest.json").read_text()) if (target / "manifest.json").exists() else {}
        if current.get("modes", {}).get("video") and not manifest["modes"]["video"] and not force:
            raise RuntimeError(
                f"{target} holds a film with real video and this one is a mock. "
                f"Pass --force to replace it anyway."
            )
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name in ("final.mp4", "manifest.json", "captions.vtt", "events.json"):
        shutil.copyfile(job_dir / name, target / name)
    shutil.copytree(job_dir / "thumbs", target / "thumbs")
    return target
