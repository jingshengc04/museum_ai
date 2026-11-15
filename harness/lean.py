"""Lean pipeline: photo → identify → web research → ONE writing call → final.json (ready for generate.py).

    uv run python lean.py --photo photos/four_ram_zun.webp [--label x] [--user-input "15s"] [--resolution 720p]

Three model calls instead of the staged pipeline's eight to ten (run.py): S0 identify, S0b research, then a single
writer that produces the story, the lines and the Seedance direction in one pass. No digest, asset-planning, concept or
review stages. What the reviewer used to do is done by code: every factual line must cite a research finding, lines
must be short, timings must fit, the request must stay under the word cap. One retry with the check feedback.

Fixed in code, never chosen by the model: the two reference images (identity anchor + character) and their prompt
templates, the video endpoint (Seedance 2.5, one generation up to 30 s), aspect and resolution.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

import agent
import checks
import images

VIDEO_ENDPOINT = os.environ.get("LEAN_VIDEO_ENDPOINT", "bytedance/seedance-2.5/reference-to-video")
MAX_LINE_WORDS = 12
MAX_PROMPT_WORDS = 430
SECONDS_PER_WORD = 0.4
USD_PER_S = {"480p": 0.2205, "720p": 0.473, "1080p": 1.164}  # Seedance 2.5 on fal


class Line(BaseModel):
    t_start: float = Field(description="Start time in seconds on the film's timeline.")
    text: str = Field(description="One plain spoken sentence, at most twelve words.")
    fact_ids: list[int] = Field(description="Numbers of the facts that state this; empty only for a greeting or remark with no claim.")


class Beat(BaseModel):
    t_start: float
    t_end: float
    action: str = Field(description="One sentence, about 30 words, verbs first: what the camera and the hero do in this part of the single take.")


class LeanFilm(BaseModel):
    title: str
    duration_s: Literal[15, 30]
    subject_name: str = Field(description="The object, as it should be called in the direction, e.g. 'the Four-Ram Square Zun'.")
    hero: str = Field(description="The one thing that comes alive, e.g. 'the front ram'.")
    still_parts: str = Field(description="What stays still, e.g. 'the other three rams and the vessel body'; empty if the whole object is the hero.")
    character_design: str = Field(description="One sentence for an image model describing the hero character.")
    look: str = Field(description="One line: animation style, place, light.")
    voice: str = Field(description="One sentence: the character's voice (age, warmth, accent, pace).")
    lines: list[Line]
    beats: list[Beat]
    sounds: list[str] = Field(description="Four or five named sounds tied to the events, in order.")


def facts_text(findings) -> str:
    return "\n".join(f"{n}. {f.text} (source: {f.url})" for n, f in enumerate(findings, 1))


def check(film: LeanFilm, n_facts: int) -> list[str]:
    problems = []
    want = (3, 4) if film.duration_s == 15 else (5, 6)
    if not want[0] <= len(film.lines) <= want[1]:
        problems.append(f"{len(film.lines)} lines for {film.duration_s} s; write {want[0]} to {want[1]}")
    end_prev = 0.5
    for k, l in enumerate(film.lines, 1):
        words = len(l.text.split())
        if words > MAX_LINE_WORDS:
            problems.append(f"line {k} has {words} words; at most {MAX_LINE_WORDS}")
        for i in l.fact_ids:
            if not 1 <= i <= n_facts:
                problems.append(f"line {k} cites fact {i}, which does not exist")
        if not l.fact_ids and re.search(r"\d|\b(years?|century|dynasty|made|built|found|used|held|biggest|largest|oldest)\b", l.text, re.I):
            problems.append(f"line {k} ('{l.text}') states something about the exhibit but cites no fact")
        if l.t_start < end_prev + 0.25:
            problems.append(f"line {k} starts at {l.t_start}s, before the previous line can finish (about {end_prev:.1f}s)")
        end_prev = l.t_start + words * SECONDS_PER_WORD
    if end_prev > film.duration_s - 0.4:
        problems.append(f"the last line ends at about {end_prev:.1f}s; it must finish by {film.duration_s - 0.5:.1f}s")
    t = 0.0
    for k, b in enumerate(film.beats, 1):
        if abs(b.t_start - t) > 0.05:
            problems.append(f"beat {k} starts at {b.t_start}s; beats must be contiguous (expected {t}s)")
        t = b.t_end
        if checks._text_on_screen(b.action):
            problems.append(f"beat {k} asks for text in the picture")
        if re.search(r"\b(people|person|visitors?|crowd|soldiers?|explosions?|bombs? (fall|drop|explod))", b.action, re.I):
            problems.append(f"beat {k} shows people or a staged real event; keep it fantasy with no people")
    if film.beats and abs(t - film.duration_s) > 0.05:
        problems.append(f"beats end at {t}s, the film is {film.duration_s}s")
    words = len(seedance_prompt(film).split())
    if words > MAX_PROMPT_WORDS:
        problems.append(f"the video request is {words} words; keep it under {MAX_PROMPT_WORDS} by shortening the beats")
    return problems


def seedance_prompt(film: LeanFilm) -> str:
    cap = lambda s: s[:1].upper() + s[1:]
    still = f" {cap(film.still_parts.strip().rstrip('.'))} stay still." if film.still_parts.strip() else ""
    beats = "\n".join(f"{b.t_start:g}-{b.t_end:g}s: {b.action.strip()}" for b in film.beats)
    vo = "; ".join(f'at {l.t_start:g}s: "{l.text.strip()}"' for l in film.lines)
    return (f"References: @Image1 = {film.subject_name}, identity anchor: shape, decoration and colours exactly as shown; "
            f"ignore its background. @Image2 = {film.hero} as a character: same design and markings throughout; ignore its background.\n"
            f"Only {film.hero} comes alive.{still} {cap(film.subject_name)} ends whole and unchanged.\n"
            f"Look: {film.look.strip().rstrip('.')}.\n"
            f"One continuous take, no cuts.\n{beats}\n"
            f"Voiceover, the character's voice, no lip-sync: {film.voice.strip()} Lines, exactly: {vo}.\n"
            f"Sound: {'; '.join(s.strip().rstrip('.') for s in film.sounds)}. No music.\n"
            f"Clean picture: no subtitles, captions, lettering, logos or watermark. No people in frame.")


def image_jobs(film: LeanFilm, photo: bool) -> list[dict]:
    """Two fixed reference images; only the object's name and the character sentence come from the writer."""
    initial = ["<visitor_photo>"] if photo else []
    spec = [
        ("subject_now", "subject_view",
         f"From this photo, show {film.subject_name} alone, whole, exactly as it is: same shape, decoration, material and colours, "
         f"three-quarter front view, even neutral studio light, plain light-grey background, no glass case, no plinth label. "
         f"{images.NO_PEOPLE} Avoid: text, labels, reflections, glare, a second copy of the object."),
        ("hero_awake", "living_form",
         f"From this photo, design {film.hero} of {film.subject_name} as a character: {film.character_design.strip().rstrip('.')}. "
         f"One single full-body three-quarter view, even light, plain light-grey background. {images.NO_PEOPLE} "
         f"Avoid: text, labels, expression sheets, several views, the rest of the object."),
    ]
    purpose = {"subject_view": "identity anchor: keeps the object's shape, decoration and colours the same in the video",
               "living_form": "the character that comes alive: keeps its design the same in the video"}
    return [{"id": i, "kind": k, "endpoint": images.ENDPOINT, "input": {"image_urls": initial, "prompt": p},
             "purpose": purpose[k], "est_usd": images.USD_PER_IMAGE} for i, k, p in spec]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", type=Path, required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--user-input", default="")
    ap.add_argument("--resolution", default="480p", choices=["480p", "720p", "1080p"])
    args = ap.parse_args()

    agent.NO_PACK = True
    stamp = time.strftime("%m%d-%H%M%S")
    run_dir = agent.RUNS / f"{stamp}-lean{('-' + args.label) if args.label else ''}"
    run_dir.mkdir(parents=True)
    t0 = time.time()
    marks = {}

    # live progress feed for the product (same format as run.py): stage starts/ends, searches, keyword batches
    feed = (run_dir / "events.jsonl").open("w")
    lock = threading.Lock()

    events: list[dict] = []

    def on_event(e: dict) -> None:
        with lock:
            e = {"t_run": round(time.time() - t0, 2), **e}
            events.append(e)
            feed.write(json.dumps(e, ensure_ascii=False) + "\n")
            feed.flush()
    agent.EMIT = on_event

    keywords: dict[str, list[dict]] = {}
    kw_threads = []

    def side_keywords(label: str, material: str) -> None:
        """Separate small request, in the background: a few short keywords for the progress screen."""
        def work():
            try:
                batch = [k.model_dump() for k in agent.keyword_batch(label, material, run_dir).keywords]
                keywords[label] = batch
                agent.emit(f"kw_{label}", type="keywords_batch", label=label, keywords=batch,
                           flags=checks.keywords(batch, material))
                print(f"  keywords ({label}): " + " · ".join(k["text"] for k in batch))
            except Exception as e:  # keywords must never break the film
                keywords[label] = []
                print(f"  keywords ({label}) failed: {e}")
        t = threading.Thread(target=work, daemon=True)
        t.start()
        kw_threads.append(t)

    ident = agent.s0_identify(args.photo, run_dir)
    if ident.confidence == "low" or not ident.short_name.strip():
        raise SystemExit(f"Could not recognise the object: {ident.reason}")
    exhibit_id = agent.register_adhoc(ident)
    marks["identify"] = time.time() - t0
    print(f"  see: {ident.short_name} ({ident.museum or 'museum unknown'}) · {marks['identify']:.0f}s")
    side_keywords("identify", f"From the visitor's photo (basis 'photo'): {ident.recognized_as} {ident.what_is_visible}")

    research = agent.s0b_research(exhibit_id, ident, args.photo, run_dir)
    tools_file = run_dir / "00_s0b_research" / "tools.json"
    retrieved = json.loads(tools_file.read_text())["retrieved_urls"] if tools_file.exists() else []
    bad = checks.research(research, retrieved)
    bad_urls = {checks._norm(b.split(": ", 1)[1].split(" (")[0]) for b in bad if ": " in b}
    findings = [f for f in research.findings if checks._norm(f.url) not in bad_urls]
    marks["search"] = time.time() - t0
    side_keywords("research", "Research findings:\n" + "\n".join(f"- {f.text} [quote: {f.quote}] (basis {f.url})" for f in findings))
    print(f"  search: {len(findings)} verified findings from {len(research.sources)} sources · {marks['search'] - marks['identify']:.0f}s")

    base = agent.photo_blocks(args.photo) + [agent._text(
        f"Object: {ident.short_name} — {ident.museum}\nWhat the photo shows: {ident.what_is_visible}\n\n"
        f"Facts (cite them by number):\n{facts_text(findings)}"
        + (f"\n\nUser input: {args.user_input.strip()}" if args.user_input.strip() else ""))]
    film = agent.call("lean_write", base, LeanFilm, run_dir, 1, effort="medium")
    problems = check(film, len(findings))
    attempts = 1
    if problems:
        for p in problems:
            print(f"  ! {p}")
        film = agent.call("lean_write", base + [agent._text(
            "Previous attempt:\n" + film.model_dump_json(indent=1) + "\n\nCheck feedback:\n" + "\n".join(f"- {p}" for p in problems))],
            LeanFilm, run_dir, 2, effort="medium")
        problems = check(film, len(findings))
        attempts = 2
        for p in problems:
            print(f"  ! still: {p}")
    marks["write"] = time.time() - t0
    print(f"  write: {attempts} attempt(s) · {marks['write'] - marks['search']:.0f}s")

    for t in kw_threads:
        t.join()
    agent.EMIT = None
    feed.close()
    prompt = seedance_prompt(film)
    subs = [{"t_start": l.t_start, "t_end": round(min(film.duration_s, l.t_start + max(1.6, len(l.text.split()) * SECONDS_PER_WORD + 0.4)), 2),
             "text": l.text} for l in film.lines]
    jobs = image_jobs(film, True)
    quoted = sum(len(l.text.split()) for l in film.lines)
    video_usd = round(film.duration_s * USD_PER_S.get(args.resolution, 0.0), 2)
    # Same top-level keys and item shapes as run.py's final.json (the hand-off teammates already read);
    # "problems", "lines" and "timing_s" are additions.
    final = {
        "exhibit_id": exhibit_id, "status": "PASS" if not problems else "NEEDS_HUMAN",
        "title": film.title, "duration_s": film.duration_s, "photo": str(args.photo),
        "keywords": [e for e in events if e.get("type") == "keywords_batch"],
        "image_jobs": jobs, "existing_images_used": [], "missing_images": [],
        "video_requests": [{"endpoint": VIDEO_ENDPOINT, "image_urls": ["<job:subject_now>", "<job:hero_awake>"],
                            "duration": str(film.duration_s), "resolution": args.resolution, "aspect_ratio": "16:9",
                            "generate_audio": True, "prompt": prompt, "prompt_words": len(prompt.split()),
                            "direction_words": len(prompt.split()) - quoted, "prompt_parts": {}, "est_usd": video_usd}],
        "subtitles": subs, "voice": film.voice, "music_style": "no music",
        "est_usd": {"images": images.total(jobs), "video": video_usd},
        "problems": problems,
        "lines": [{"t_start": l.t_start, "text": l.text,
                   "sources": [{"fact": findings[i - 1].text, "url": findings[i - 1].url} for i in l.fact_ids if 1 <= i <= len(findings)]}
                  for l in film.lines],
        "timing_s": {k: round(v, 1) for k, v in marks.items()},
    }
    (run_dir / "final.json").write_text(json.dumps(final, indent=2, ensure_ascii=False))
    (run_dir / "film.json").write_text(film.model_dump_json(indent=2))

    print(f"\n  {film.title} · {film.duration_s}s · {final['status']} · agent total {marks['write']:.0f}s")
    for l in final["lines"]:
        src = "; ".join(s["fact"][:70] for s in l["sources"]) or "(no claim)"
        print(f"   {l['t_start']:5.1f}  {l['text']}   ← {src}")
    print(f"\n  request: {final['video_requests'][0]['prompt_words']} words → {run_dir / 'final.json'}")
    print(f"  to generate: uv run python generate.py {run_dir} --resolution {args.resolution}")


if __name__ == "__main__":
    main()
