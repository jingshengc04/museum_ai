"""Photo in, film out. Emits events as it works so the wait can be part of the show."""
from __future__ import annotations

import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from . import config, edit, exhibits, storyboard, video, voice

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


def make_film(job_dir: Path, language: str, style: str, emit: Emit,
              photo: Path | None = None, exhibit_id: str | None = None) -> dict:
    """Run the whole pipeline into `job_dir` and return the manifest."""
    started = time.time()
    job_dir.mkdir(parents=True, exist_ok=True)

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

    # 2. Storyboard
    emit("step", step="story", status="start")
    board = storyboard.build(exhibit, language, style, emit)
    emit("storyboard", title=board.title, origin=board.origin, shots=[
        {"id": s.id, "narration": storyboard.spoken(s.narration), "action": s.action, "fact_ids": s.fact_ids}
        for s in board.shots
    ])
    emit("step", step="story", status="done")

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
        emit("shot", id=p.shot.id, stage="video", status="done", source=p.source, thumb=f"thumbs/{thumb.name}")
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
                "voice_source": narration.origin,
                "fit": fit,
            }
            for shot, slot, p, narration, (_, fit) in zip(board.shots, slots, plans, narrations, rendered)
        ],
        "captions": cues,
        "facts": [dict(f, used=f["id"] in used) for f in exhibit.facts],
        "modes": {name: m["live"] for name, m in config.modes().items()},
        "ambient_source": bed_origin,
        "fal_cost_usd": cost,
        "seconds_to_make": round(time.time() - started, 1),
    }
    (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    emit("step", step="edit", status="done")
    return manifest


def promote(job_dir: Path, force: bool = False) -> Path:
    """Keep a finished film as the known-good demo for its exhibit, language and style."""
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
    for name in ("final.mp4", "manifest.json", "captions.vtt"):
        shutil.copyfile(job_dir / name, target / name)
    shutil.copytree(job_dir / "thumbs", target / "thumbs")
    return target
