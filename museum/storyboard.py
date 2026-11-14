"""Storyboard: the shot list every later step works from.

Order of preference:
  1. hand-written file  exhibits/<id>/storyboards/<lang>-<style>.json
  2. Claude writes one from the exhibit's sourced facts, then fact-checks itself (LIVE=llm)
  3. fall back to the hand-written first-person storyboard for that language
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, Field

from . import cache, config
from .exhibits import Exhibit

Emit = Callable[..., None]

TAG = re.compile(r"\[[^\]]*\]")  # eleven_v3 emotion tags like [softly]

STYLE_GUIDE = {
    "first_person": "The exhibit narrates its own story in the first person: warm, a little wry, cinematic.",
    "kids": "For children aged 6-10, first person: short simple sentences, playful, full of wonder. No scary detail.",
    "expert": "For an informed adult, first person: precise, measured, exact dates and figures, no jokes.",
    "funny": "First person and dry-witted: gentle self-deprecating humour, but every fact stays exact.",
}


class Shot(BaseModel):
    id: int
    narration: str = Field(description="One or two short spoken sentences for this shot.")
    action: str = Field(description="The one main motion in the shot, as a full sentence.")
    camera: str
    location: str
    mood: str
    refs: list[str] = Field(default_factory=list, description="Reference image names to use, 2-4.")
    fact_ids: list[str] = Field(default_factory=list, description="Ids of the facts this narration states.")
    movement: Literal["auto", "small", "medium", "large"] = "auto"
    seconds: int = Field(default=0, description="Length of this scene's clip in seconds, 4-15.")


class Storyboard(BaseModel):
    title: str
    shots: list[Shot]
    exhibit_id: str = ""
    language: str = ""
    style: str = ""
    origin: str = ""  # hand-written | claude | fallback


class ShotFix(BaseModel):
    shot_id: int
    problem: str
    narration: str = Field(description="Corrected narration that only states listed facts.")
    fact_ids: list[str]


class Review(BaseModel):
    fixes: list[ShotFix]


class Identification(BaseModel):
    exhibit_id: str = Field(description="Id of the matching exhibit, or an empty string if none match.")
    reason: str


# ---------- helpers ----------

def spoken(text: str) -> str:
    """Narration without emotion tags: what is heard and what subtitles show."""
    return re.sub(r"\s+", " ", TAG.sub("", text)).strip()


def narration_units(text: str, language: str) -> int:
    """Words (English) or characters (Chinese) in the spoken text."""
    text = spoken(text)
    if language == "zh":
        return len(re.sub(r"[\W_]", "", text))
    return len(text.split())


def unit_budget(language: str, seconds: int = 0) -> int:
    """Longest narration that still fits a clip of `seconds` (about 2.4 English words or 4 Chinese characters a second)."""
    seconds = seconds or config.VIDEO_MAX_SECONDS
    return round(seconds * (4 if language == "zh" else 2.4))


def video_prompt(shot: Shot, exhibit: Exhibit) -> str:
    character = exhibit.data.get("character", {}).get("description", "")
    parts = [
        f"Action: {shot.action}",
        f"Camera: {shot.camera}",
        f"Location: {shot.location}",
        f"Mood: {shot.mood}",
        f"Character: {character}." if character else "",
        exhibit.data.get("style_suffix", ""),
    ]
    return " ".join(p for p in parts if p)


def scene_prompt(shot: Shot, exhibit: Exhibit, images: list[str]) -> str:
    """Prompt for a model that also makes the sound: the picture, then the exact words the character speaks."""
    character = exhibit.data.get("character", {})
    look = character.get("description", "")
    voice = character.get("voice_description", "a warm, calm voice")
    lines = [f"Action: {shot.action}", f"Camera: {shot.camera}", f"Location: {shot.location}", f"Mood: {shot.mood}"]
    if look:
        lines.append(f"Character: {look}.")
    if images:
        lines.append("References: " + "; ".join(f"@Image{i} is {what}" for i, what in enumerate(images, start=1)) + ".")
    lines.append(
        f"Voice-over: {character.get('name', 'the character')} narrates off-screen in {voice}, speaking clearly and unhurried, "
        f"saying exactly these words and nothing else: \"{spoken(shot.narration)}\""
    )
    lines.append(f"Sound: {exhibit.data.get('ambience', 'soft ambient sound')}, kept low under the voice. No music with lyrics.")
    lines.append(exhibit.data.get("style_suffix", ""))
    return " ".join(line for line in lines if line)


def validate(board: Storyboard, exhibit: Exhibit) -> list[str]:
    """Problems that must not reach the film. Unknown facts are errors, the rest are warnings."""
    known = {f["id"] for f in exhibit.facts}
    problems = []
    if not board.shots:
        raise ValueError("storyboard has no shots")
    for shot in board.shots:
        unknown = [f for f in shot.fact_ids if f not in known]
        if unknown:
            raise ValueError(
                f"shot {shot.id} cites facts without a source: {unknown}. "
                f"Add a source in exhibit.json or remove the claim."
            )
        missing = [r for r in shot.refs if r.lower() not in exhibit.refs]
        if missing and exhibit.refs:
            problems.append(f"shot {shot.id}: reference image(s) not found: {missing}")
        units = narration_units(shot.narration, board.language)
        if units > unit_budget(board.language, shot.seconds):
            problems.append(f"shot {shot.id}: narration is long ({units} units) for its clip and may be cut off")
    return problems


# ---------- sources ----------

def _from_file(path: Path) -> Storyboard:
    return Storyboard.model_validate(json.loads(path.read_text()))


def _client():
    import anthropic

    return anthropic.Anthropic()


def _ask(schema: type[BaseModel], system: str, content, effort: str = "medium"):
    """One structured-output call to Claude. Returns the parsed model."""
    response = _client().beta.messages.parse(
        model=config.STORY_MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_format=schema,
        output_config={"effort": effort},
        # If a safety classifier declines, Anthropic re-runs the request on a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined this request")
    if response.parsed_output is None:
        raise RuntimeError(f"Claude returned no usable output (stop_reason={response.stop_reason})")
    return response.parsed_output


def _facts_block(exhibit: Exhibit) -> str:
    return json.dumps([{"id": f["id"], "text": f["text"]} for f in exhibit.facts], ensure_ascii=False, indent=2)


WRITER_SYSTEM = """You write storyboards for short animated films about museum exhibits. \
The exhibit is the main character and tells its own story. The film is a sequence of {clip} \
video clips, each with its own voice-over, shown to a visitor standing in front of the exhibit.

Facts. The narration may only state facts from the list you are given. Do not add dates, numbers, \
names, places, causes or events that are not in that list, even if you know them to be true: the \
visitor sees the sources, and anything unlisted has no source. Feelings and framing in the \
character's voice are welcome. Every shot lists the ids of the facts its narration states.

Narration. Narration is read aloud and is the master timeline, so each shot's line must fit one \
clip: at most {budget} {unit} per shot, usually fewer. You may open a line with one eleven_v3 \
emotion tag in square brackets such as [softly], [whispers] or [excited]; tags are always in English.

Picture. The video model sees only the shot description and the reference images, never the \
narration. Write action, camera, location and mood in English whatever the narration language. \
Each shot has one main motion, described as motion rather than as a full scene. The character's \
face barely changes, so show emotion through movement (curious: turns and glides closer; joyful: \
a slow roll; sad: drifts and sinks). Pick 2-4 reference images per shot by name, including the \
expression that fits. Keep the character an original design; do not reference existing film, TV \
or game characters. No on-screen text."""


def _generate(exhibit: Exhibit, language: str, style: str) -> Storyboard:
    seconds = config.VIDEO_MAX_SECONDS
    budget = unit_budget(language, seconds) - 4
    shape = (f"2 scenes of {seconds} seconds each (a scene may hold two or three shots, described in order)"
             if config.NATIVE_AUDIO else "8-9 shots that run 45-60 seconds in total")
    unit = "Chinese characters" if language == "zh" else "English words"
    user = (
        f"Exhibit: {exhibit.name}, {exhibit.data.get('location', '')}, {exhibit.data.get('museum', '')}\n"
        f"Character: {exhibit.data.get('character', {}).get('description', '')}\n"
        f"Reference images available: {sorted(exhibit.refs) or 'none yet (leave refs empty)'}\n\n"
        f"Facts (the only facts the narration may state):\n{_facts_block(exhibit)}\n\n"
        f"Narration language: {config.LANGUAGES[language]}\n"
        f"Audience and tone: {STYLE_GUIDE[style]}\n\n"
        f"Write a storyboard of {shape}, with a clear opening hook, "
        f"the story in order, and a closing line that stays with the visitor. Number shots from 1 and set seconds to {seconds}."
    )
    clip = f"{seconds}-second" if config.NATIVE_AUDIO else "5-8 second"
    board = _ask(Storyboard, WRITER_SYSTEM.format(budget=budget, unit=unit, clip=clip), user, effort="high")
    return board


REVIEW_SYSTEM = """You are the fact checker for a museum film. You get the list of sourced facts \
and a storyboard's narration. Find every narration line that states something not supported by \
the listed facts (a wrong or extra date, number, name, place, cause or event), or that lists \
fact ids it does not actually state. Feelings, greetings and framing in the character's voice \
are fine and are not errors. For each problem line, return a corrected narration in the same \
language, tone and length that only states listed facts, with its fact ids. Return an empty \
list when everything is supported."""


def _review(board: Storyboard, exhibit: Exhibit) -> list[ShotFix]:
    lines = [{"shot_id": s.id, "narration": s.narration, "fact_ids": s.fact_ids} for s in board.shots]
    user = (
        f"Facts:\n{_facts_block(exhibit)}\n\n"
        f"Narration ({config.LANGUAGES[board.language]}):\n{json.dumps(lines, ensure_ascii=False, indent=2)}"
    )
    return _ask(Review, REVIEW_SYSTEM, user).fixes


def _write_with_claude(exhibit: Exhibit, language: str, style: str, emit: Emit) -> Storyboard:
    cache_key = cache.key("storyboard-v2", config.VIDEO_MODEL, config.STORY_MODEL, exhibit.data, sorted(exhibit.refs), language, style)

    def produce() -> dict:
        emit("thought", text=f"Writing a {config.STYLES[style].lower()} script from {len(exhibit.facts)} sourced facts…")
        board = _generate(exhibit, language, style)
        board.language = language
        emit("thought", text="Checking every line against the sources…")
        fixes = _review(board, exhibit)
        by_id = {s.id: s for s in board.shots}
        for fix in fixes:
            if fix.shot_id in by_id:
                emit("thought", text=f"Shot {fix.shot_id}: {fix.problem} Rewriting the line.")
                by_id[fix.shot_id].narration = fix.narration
                by_id[fix.shot_id].fact_ids = fix.fact_ids
        if not fixes:
            emit("thought", text="Every line is backed by a source.")
        return board.model_dump()

    data, was_cached = cache.cached_json("storyboard", cache_key, produce)
    if was_cached:
        emit("thought", text="Found a script I already wrote for this exhibit and style.")
    board = Storyboard.model_validate(data)
    board.origin = "claude"
    return board


def build(exhibit: Exhibit, language: str, style: str, emit: Emit) -> Storyboard:
    hand_written = exhibit.storyboard_file(language, style)
    if hand_written.exists():
        board = _from_file(hand_written)
        board.origin = "hand-written"
        emit("thought", text=f"Using the hand-written storyboard {hand_written.name}.")
    elif config.is_live("llm"):
        board = _write_with_claude(exhibit, language, style, emit)
    else:
        fallback = exhibit.storyboard_file(language, "first_person")
        if not fallback.exists():
            raise FileNotFoundError(
                f"No storyboard for {exhibit.id} in {language}/{style}. "
                f"Add {hand_written} or run with LIVE=llm."
            )
        board = _from_file(fallback)
        board.origin = "fallback"
        emit("thought", text=f"Story writer is in mock mode, so the '{style}' style falls back to the first-person script.")
    board.exhibit_id, board.language, board.style = exhibit.id, language, style
    for index, shot in enumerate(board.shots, start=1):
        shot.id = index
        shot.refs = [r.lower() for r in shot.refs]
    for problem in validate(board, exhibit):
        emit("thought", text=f"Note: {problem}", level="warn")
    return board


# ---------- which exhibit is in the photo? ----------

def identify(photo: Path | None, candidates: list[Exhibit], emit: Emit) -> Exhibit:
    if len(candidates) == 1 and not (photo and config.is_live("llm")):
        emit("thought", text=f"One exhibit is set up, so this is {candidates[0].name}. (Photo recognition is in mock mode.)")
        return candidates[0]
    if not (photo and config.is_live("llm")):
        emit("thought", text=f"Photo recognition is in mock mode; assuming {candidates[0].name}.")
        return candidates[0]

    emit("thought", text="Looking at your photo…")
    media = {".png": "image/png", ".webp": "image/webp"}.get(photo.suffix.lower(), "image/jpeg")
    listing = [{"id": e.id, "name": e.name, "where": e.data.get("location", ""), "looks_like": e.data.get("hints", "")} for e in candidates]
    result = _ask(
        Identification,
        "You match a museum visitor's photo to one of the exhibits in a list. "
        "Answer with the id of the exhibit shown, or an empty string when none of them is in the photo.",
        [
            {"type": "image", "source": {"type": "base64", "media_type": media, "data": base64.standard_b64encode(photo.read_bytes()).decode()}},
            {"type": "text", "text": f"Exhibits:\n{json.dumps(listing, ensure_ascii=False, indent=2)}"},
        ],
        effort="low",
    )
    for exhibit in candidates:
        if exhibit.id == result.exhibit_id:
            emit("thought", text=f"This is {exhibit.name}. {result.reason}")
            return exhibit
    raise LookupError(f"I could not match the photo to an exhibit I know. {result.reason}")
