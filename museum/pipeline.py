"""Photo in, film out. Emits events as it works so the wait can be part of the show."""
from __future__ import annotations

import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from . import cache, config, edit, exhibits, script_agent, storyboard, video, voice
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

def fingerprint(exhibit: Exhibit, language: str, style: str, agent: bool | None = None) -> str:
    """Changes whenever the material a film is made from changes, so stale films are not reused."""
    if config.use_agent() if agent is None else agent:
        # The agent's prompts change often; a film stays good until the facts or reference images behind it change.
        assets = config.HARNESS_DIR / "knowledge" / exhibit.id / "assets"
        files = [f for f in [exhibit.pack, *sorted(assets.glob("*"))] if f and f.is_file()]
        return cache.key("film-agent-v1", config.VIDEO_MODEL, exhibit.id, language, style, [(f.name, cache.file_hash(f)) for f in files])
    board = exhibit.storyboard_file(language, style)
    if not board.exists():
        board = exhibit.storyboard_file(language, "first_person")
    files = [board, *exhibit.refs.values(), *sorted((exhibit.dir / "overrides").glob("*"))]
    return cache.key("film-v2", config.VIDEO_MODEL, exhibit.data, language, style, [(f.name, cache.file_hash(f)) for f in files if f.is_file()])


def library_hit(exhibit: Exhibit, language: str, style: str) -> Path | None:
    """The saved film for this exhibit, language and style, if it is still current."""
    folder = exhibit.demo_dir(language, style)
    if config.HOSTED:  # the hosted demo plays what was saved (its videos are served apart from the code) and makes nothing
        return folder if all((folder / name).exists() for name in ("manifest.json", "events.json")) else None
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


def replay_events(folder: Path) -> list[dict]:
    """The film's recorded making-of after recognition, re-timed (`t`, seconds from now) to take a few seconds."""
    events = json.loads((folder / "events.json").read_text())
    first = next(i for i, e in enumerate(events) if e["type"] == "step" and e["step"] == "identify" and e["status"] == "done") + 1
    events = events[first:]
    scale = config.REPLAY_SECONDS / max(events[-1]["t"] - events[0]["t"], 0.001)
    timed, at, previous = [], 0.0, events[0]["t"]
    for event in events:
        at += min((event["t"] - previous) * scale, 3.0)
        previous = event["t"]
        data = {k: v for k, v in event.items() if k not in ("type", "t")}
        if "thumb" in data:
            data["thumb"] = config.url_for(folder / "thumbs" / Path(data["thumb"]).name)
        timed.append({"type": event["type"], "t": round(at, 3), **data})
    return timed


def replay(folder: Path, emit: Emit) -> None:
    """Walk the visitor through the film's recorded making-of, compressed to a few seconds."""
    previous = 0.0
    for event in replay_events(folder):
        time.sleep(event["t"] - previous)
        previous = event["t"]
        emit(event["type"], **{k: v for k, v in event.items() if k not in ("type", "t")})


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


def _shoot(job_dir: Path, exhibit: Exhibit, plans: list, language: str, emit: Emit, paid: bool,
           fade: float | None = None) -> tuple[list[dict], float]:
    """Render (or fetch) every scene with its own sound, then join them. Returns the timeline and the film length."""
    def draw(p):
        emit("thought", text=f"Filming scene {p.shot.id}: {p.shot.action}")
        emit("shot", id=p.shot.id, stage="video", status="start", source=p.source)
        raw = video.render(p, exhibit, job_dir / "raw" / f"shot_{p.shot.id:02d}.mp4", language)
        if p.note:
            emit("thought", text=p.note, level="warn")
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
    slots = edit.scene_timeline([length for _, length in rendered], fade)
    total = edit.join([clip for clip, _ in rendered], slots, job_dir / "final.mp4", fade)
    return slots, total


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

    slots, total = _shoot(job_dir, exhibit, plans, language, emit, bool(paid))

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


# ---------- script agent (harness/) ----------

AGENT_CUT = 0.12  # the agent writes each scene to end on a near-still frame, so scenes meet with a short cut


def _agent_exhibit(run: script_agent.AgentRun) -> Exhibit:
    """The exhibit the agent settled on: a prepared one, or one it only knows from the photo and its research."""
    exhibit_id = run.final["exhibit_id"]
    try:
        return exhibits.load(exhibit_id)
    except FileNotFoundError:
        # Learned from the photo: kept as a new exhibit with the facts the agent found, so a later photo of the
        # same object is recognised and gets this film from the library.
        seen = run.identity()
        museum, _, location = (seen.get("museum") or "").partition(",")
        data = {"name": seen.get("short_name") or run.final.get("title", exhibit_id), "museum": museum.strip(),
                "location": location.strip(), "hints": seen.get("recognized_as", ""),
                "facts": [{k: f[k] for k in ("id", "text", "source")} for f in run.facts], "learned": True}
        return Exhibit(id=exhibit_id, dir=config.EXHIBITS_DIR / exhibit_id, data=data)


def _board_from_agent(run: script_agent.AgentRun) -> storyboard.Storyboard:
    """One shot per video segment, in the shape the rest of the pipeline and the page expect."""
    if not run.script.get("segments"):  # a hand-written hand-off with no script.json
        shots, start = [], 0.0
        for n, request in enumerate(run.final.get("video_requests", []), start=1):
            seconds = int(request["duration"])
            said = [s["text"] for s in run.final.get("subtitles", []) if start <= s["t_start"] < start + seconds]
            cited = {f for line in run.final.get("lines", []) if start <= line["t_start"] < start + seconds
                     for f in line.get("fact_ids", [])}  # lean.py: the facts each line cites
            shots.append(storyboard.Shot(id=n, narration=" ".join(said), action=run.final.get("title", ""), camera="",
                                         location="", mood="", fact_ids=sorted(cited), seconds=seconds))
            start += seconds
        return storyboard.Storyboard(title=run.final.get("title", ""), shots=shots, origin="agent")
    shots = []
    for n, segment in enumerate(run.script.get("segments", []), start=1):
        lines = segment.get("narration", [])
        parts = segment.get("shots", [])
        shots.append(storyboard.Shot(
            id=n,
            narration=" ".join(line["text"] for line in lines),
            action=" Then ".join(part["action"].rstrip(".") + "." for part in parts) or segment.get("setting", ""),
            camera=parts[0]["camera"] if parts else "",
            location=segment.get("setting", ""),
            mood=run.script.get("narrator_attitude", ""),
            fact_ids=sorted({fact for line in lines for fact in line.get("fact_ids", [])}),
            seconds=round(segment.get("duration_s") or config.VIDEO_MAX_SECONDS),
        ))
    return storyboard.Storyboard(title=run.final.get("title") or run.script.get("title", ""), shots=shots, origin="agent")


# Agent picture kinds the video model accepts even for statues of people: the object small in its hall, and scenery.
SAFE_KINDS = {"in_place", "world_plate"}


def _agent_film(job_dir: Path, exhibit: Exhibit, run: script_agent.AgentRun, board, emit: Emit,
                clips: list[Path] | None = None) -> dict:
    """Make the agent's script: its reference images from the visitor's photo, then its Seedance requests.

    `clips` are finished segments (one per request) to use instead of generating anything.
    """
    emit("step", step="video", status="start")
    final, live = run.final, config.is_live("video")
    photo = run.photo()
    jobs = {job["id"]: job for job in final.get("image_jobs", [])}
    requests = final.get("video_requests", [])
    if len(requests) != len(board.shots):
        raise RuntimeError(f"The script has {len(board.shots)} segment(s) but {len(requests)} video request(s).")

    def prompt_of(job: dict) -> str:
        return job["input"]["prompt"]

    def photo_for(job: dict) -> Path | None:
        return photo if "<visitor_photo>" in job["input"].get("image_urls", []) else None

    if clips:
        if len(clips) != len(requests):
            raise RuntimeError(f"{len(clips)} clip(s) for {len(requests)} video request(s).")
        plans = [video.ShotPlan(shot, int(request["duration"]), request["prompt"], [], "override", override=clip)
                 for shot, request, clip in zip(board.shots, requests, clips)]
        slots, total = _shoot(job_dir, exhibit, plans, "en", emit, False, fade=AGENT_CUT)
        return _agent_finish(job_dir, run, board, plans, slots, total, 0.0, "model")

    # Budget first, before anything is paid for. A clip whose pictures are all cached may itself be cached.
    image_cost = sum(config.IMAGE_PRICE_USD for job in jobs.values() if live and not video.cached_image(prompt_of(job), photo_for(job)))
    if image_cost:
        emit("thought", text=f"Making {round(image_cost / config.IMAGE_PRICE_USD)} reference picture(s) from the photo, about ${image_cost:.2f}.")

    def resolve(tag: str, make: bool) -> Path | None:
        kind, _, asset = tag.strip("<>").partition(":")
        if kind == "existing":
            return run.existing_image(asset)
        if kind == "job" and asset in jobs:
            job = jobs[asset]
            return video.reference_image(prompt_of(job), photo_for(job)) if make else video.cached_image(prompt_of(job), photo_for(job))
        return None

    def model_of(request: dict) -> tuple[str | None, str | None]:
        """The endpoint and resolution the agent asked for, when it is one we know the price of (lean: Seedance 2.5)."""
        if request.get("endpoint") in config.MODEL_PRICE_PER_SECOND_USD:
            return request["endpoint"], request.get("resolution") or config.AGENT_VIDEO_RESOLUTION
        return None, None

    planned_cost = image_cost
    for request in requests:
        refs = [resolve(tag, make=False) for tag in request.get("image_urls", [])]
        if not live:
            continue
        if all(refs):
            probe = video.plan_request(board.shots[0], exhibit, request["prompt"], refs, int(request["duration"]), *model_of(request))
            if probe.source == "cache":
                continue
        planned_cost += config.clip_price_usd(int(request["duration"]), *model_of(request))
    if config.over_budget(planned_cost):
        raise RuntimeError(f"This film would spend about ${planned_cost:.2f} on fal, above MAX_FAL_USD=${config.MAX_FAL_USD:.2f}. "
                           f"Check with the team, then raise MAX_FAL_USD to go ahead.")

    plans = []
    for shot, request in zip(board.shots, requests):
        refs, safe = [], []
        for tag in request.get("image_urls", []):
            path = resolve(tag, make=live)
            if path:
                refs.append(path)
                if jobs.get(tag.strip("<>").partition(":")[2], {}).get("kind") in SAFE_KINDS:
                    safe.append(path)
            elif live:
                emit("thought", text=f"Reference {tag} is missing; scene {shot.id} goes ahead without it.", level="warn")
        plan = video.plan_request(shot, exhibit, request["prompt"], refs, int(request["duration"]), *model_of(request))
        plan.safe_refs = safe
        plans.append(plan)
    paid = [p for p in plans if p.source == "generate"]
    cost = round(image_cost + video.estimate_usd(plans), 2)
    if paid:
        emit("thought", text=f"Rendering {len(paid)} scene(s) with sound on fal, {sum(p.seconds for p in paid)} s at {paid[0].resolution or config.VIDEO_RESOLUTION}.")
    elif not live:
        emit("thought", text="Video is in mock mode: drawing animatic cards with a stand-in voice instead of spending fal credits.")

    slots, total = _shoot(job_dir, exhibit, plans, "en", emit, bool(paid), fade=AGENT_CUT)
    return _agent_finish(job_dir, run, board, plans, slots, total, cost, "model" if live else "mock")


def _agent_finish(job_dir: Path, run: script_agent.AgentRun, board, plans: list, slots: list[dict], total: float,
                  cost: float, voiced: str) -> dict:
    """Subtitles on the real timeline, and the parts of the manifest that describe the clips."""
    final = run.final
    # The agent times its subtitles against back-to-back segments; move each onto the real timeline.
    starts, t = [], 0.0
    for shot in board.shots:
        starts.append(t)
        t += shot.seconds
    cues = []
    for cue in final.get("subtitles", []):
        k = max(i for i, start in enumerate(starts) if start <= cue["t_start"] + 1e-6) if starts else 0
        shift = slots[k]["start"] - starts[k]
        start, end = round(cue["t_start"] + shift, 3), round(min(cue["t_end"] + shift, total), 3)
        cues.append({"start": start, "end": end, "text": cue["text"],
                     "words": [{"w": w, "t0": start, "t1": end} for w in cue["text"].split()]})
    (job_dir / "captions.vtt").write_text(_vtt(cues))
    return {"slots": slots, "total": total, "plans": plans, "fits": [{"how": "native", "speed": 1.0, "freeze": 0.0} for _ in plans],
            "voices": [voiced for _ in plans], "cues": cues, "ambient": "model", "cost": cost}


def make_film(job_dir: Path, language: str, style: str, emit: Emit, photo: Path | None = None,
              exhibit_id: str | None = None, fresh: bool = False, save: bool = True,
              prepared: script_agent.AgentRun | None = None, clips: list[Path] | None = None) -> tuple[dict, Path]:
    """Make the film, or reuse the library's. Returns the manifest and the folder that holds the film.

    `fresh` renders even when the library has this film; `save` adds a new film to the library.
    `prepared` is a finished agent run to use instead of running the agent, and `clips` its finished segments.
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
    try:
        exhibit = storyboard.identify(photo, candidates, emit)
    except LookupError:
        if not (config.use_agent() and photo):
            raise
        exhibit = None
        emit("thought", text="This is not one of the exhibits I know yet, so I will research it from scratch.")
    if exhibit:
        emit("exhibit", exhibit=exhibit.public())
        if exhibit.facts:
            sources = sorted({f["source"].split("/")[2] for f in exhibit.facts})
            emit("thought", text=f"Reading the label: {len(exhibit.facts)} facts, each with a source ({', '.join(sources)}).")
        for fact in exhibit.unsourced_facts:
            emit("thought", text=f"Leaving out \"{fact['text']}\" because it has no source yet.", level="warn")
    emit("step", step="identify", status="done")

    saved = None if fresh or exhibit is None else library_hit(exhibit, language, style)
    if saved:
        replay(saved, emit)
        return json.loads((saved / "manifest.json").read_text()), saved

    # 2. Storyboard: the script agent when it is on, otherwise storyboard.py or a hand-written file
    emit("step", step="story", status="start")
    agent_run = prepared
    if agent_run:
        board = _board_from_agent(agent_run)
    elif config.use_agent():
        # The agent only takes an exhibit id it has a knowledge pack for; otherwise it works from the photo.
        agent_run = script_agent.run(emit, exhibit_id=exhibit.id if exhibit and exhibit.pack else None,
                                     photo=photo or (exhibit.photo if exhibit else None))
        # The staged agent may recognise the photo differently from us. lean.py always names its own adhoc id,
        # so with it an exhibit we already recognised keeps its id (and its place in the library).
        lean = config.AGENT_PIPELINE == "lean"
        if exhibit is None or (not lean and agent_run.final.get("exhibit_id") not in (exhibit.id, None)):
            exhibit = _agent_exhibit(agent_run)
            emit("exhibit", exhibit=exhibit.public())
        board = _board_from_agent(agent_run)
        emit("thought", text=f"Script ready: \"{board.title}\", {len(board.shots)} scene(s), {agent_run.status}.")
        if not agent_run.passed:  # first version: no human review, the film is made and kept either way
            emit("thought", text=f"The script did not fully pass its own review ({agent_run.status}); filming it anyway.", level="warn")
    else:
        board = storyboard.build(exhibit, language, style, emit)
    emit("storyboard", title=board.title, origin=board.origin, shots=[
        {"id": s.id, "narration": storyboard.spoken(s.narration), "action": s.action, "fact_ids": s.fact_ids}
        for s in board.shots
    ])
    emit("step", step="story", status="done")

    # 3-5. Sound and picture: either the model voices its own clips, or we record narration and fit clips to it.
    if agent_run:
        made = _agent_film(job_dir, exhibit, agent_run, board, emit, clips)
    elif config.NATIVE_AUDIO:
        made = _native_film(job_dir, exhibit, board, language, emit, photo)
    else:
        made = _narrated_film(job_dir, exhibit, board, language, emit)
    slots, total, plans, cues, cost = made["slots"], made["total"], made["plans"], made["cues"], made["cost"]

    facts = (agent_run.facts if agent_run else None) or exhibit.facts
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
        "facts": [{k: f[k] for k in ("id", "text", "source")} | {"used": f["id"] in used} for f in facts],
        # Finished clips handed in are real video, whatever the services are set to now.
        "modes": {name: m["live"] for name, m in config.modes().items()} | ({"llm": True, "video": True} if clips else {}),
        "fingerprint": fingerprint(exhibit, language, style, agent=True if agent_run else None),
        "ambient_source": made["ambient"],
        "video_model": config.VIDEO_MODEL,
        "fal_cost_usd": cost,
        "seconds_to_make": round(time.time() - started, 1),
    }
    if agent_run:
        manifest["agent"] = {"run": agent_run.dir.name, "status": agent_run.status, "claude_cost_usd": agent_run.cost_usd,
                             "voice": agent_run.final.get("voice"), "music": agent_run.final.get("music_style")}
    (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    emit("step", step="edit", status="done")
    (job_dir / "events.json").write_text(json.dumps(recorded, ensure_ascii=False))
    # Every finished film is reused for other visitors; the agent's review status stays in the manifest.
    if save and exhibit.data.get("learned") and not (exhibit.dir / "exhibit.json").exists():
        exhibit.dir.mkdir(parents=True, exist_ok=True)
        (exhibit.dir / "exhibit.json").write_text(json.dumps(exhibit.data, ensure_ascii=False, indent=2) + "\n")
        if photo and not exhibit.photo:
            save_photo(photo, exhibit)
    if save:
        try:
            promote(job_dir)
        except (RuntimeError, FileNotFoundError):
            pass  # the library holds a real film and this one is a mock, or the exhibit has no home to keep films in
    return manifest, job_dir


def save_photo(photo: Path, exhibit: Exhibit) -> Path:
    """Keep a photo as the exhibit's picture on the first screen (JPEG, at most 1600 px)."""
    from PIL import Image, ImageOps

    target = exhibit.dir / "photo.jpg"
    image = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
    image.thumbnail((1600, 1600))
    image.save(target, quality=88)
    return target


def import_film(run_dir: Path, exhibit_id: str, emit: Emit, name: str = "", museum: str = "", location: str = "",
                photo: Path | None = None) -> tuple[dict, Path]:
    """Put a film the agent's own tools already made (harness run or example folder) into the library."""
    run = script_agent.load(run_dir)
    clips = sorted((run_dir / "media" / "segments").glob("seg_*.mp4"), key=lambda p: int(p.stem.split("_")[1]))
    if not clips:
        raise FileNotFoundError(f"No finished segments in {run_dir / 'media' / 'segments'}")
    try:
        exhibit = exhibits.load(exhibit_id)
    except FileNotFoundError:
        if not name:
            raise ValueError(f"'{exhibit_id}' is a new exhibit: give its name") from None
        museum_name, _, place = museum.partition(",")
        exhibit = Exhibit(id=exhibit_id, dir=config.EXHIBITS_DIR / exhibit_id, data={
            "name": name, "museum": museum_name.strip(), "location": (location or place).strip(),
            "hints": name, "facts": [{k: f[k] for k in ("id", "text", "source")} for f in run.facts], "learned": True})
        exhibit.dir.mkdir(parents=True, exist_ok=True)
        (exhibit.dir / "exhibit.json").write_text(json.dumps(exhibit.data, ensure_ascii=False, indent=2) + "\n")
    if photo and not exhibit.photo:
        save_photo(photo, exhibit)
    run.final["exhibit_id"] = exhibit.id
    job_dir = config.OUTPUT_DIR / f"{time.strftime('%m%d-%H%M%S')}-import-{exhibit.id}"
    return make_film(job_dir, "en", "first_person", emit, exhibit_id=exhibit.id, fresh=True, prepared=run, clips=clips)


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
