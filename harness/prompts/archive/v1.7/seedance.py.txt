"""Turn one script segment into the fal Seedance 2.0 reference-to-video request.

The agent decides *what* to show and say (schemas.Script); this file decides *how it is written for Seedance*,
so a change of prompt style never needs the agent re-tuned. Written from research/round1 (verified against
fal docs on 2026-11-14):
  - endpoint bytedance/seedance-2.0/reference-to-video, duration "4".."15" (string), 720p, generate_audio on
  - reference images are named @Image1..@Image9 in upload order; bind each once, then reuse the same name
  - shots in event order joined with "Cut to"; precise per-shot timings are unreliable, so no timecodes
  - spoken words go in double quotes; describe the narrator once, identically in every segment
  - state the sound you want, and "no music" if none, or a score appears
  - constraint block last: subtitle-free, no lettering/logos/watermark, one subject in frame
  - keep requests short: the first instructions are followed most reliably
Unverified (research/round1_raw.json "still_open"): timing syntax, voice consistency across calls.

History: v1.1 kept references of different states apart; v1.2 stopped repeating locks; v1.3 (round 2) binds
references by short names with a role, prints each shot as one clause, adds film-level music and the end frame,
and counts only direction words (quoted narration excluded) against the cap.
"""
from __future__ import annotations

import os
import re

import schemas

ENDPOINT = os.environ.get("SEEDANCE_ENDPOINT", "bytedance/seedance-2.0/reference-to-video")
RESOLUTION = os.environ.get("SEEDANCE_RESOLUTION", "720p")
ASPECT = os.environ.get("SEEDANCE_ASPECT", "16:9")
USD_PER_SECOND = {"480p": 0.13, "720p": 0.30}  # standard tier, from verified token pricing
MAX_DIRECTION_WORDS = 230   # words the writer controls, quoted narration excluded
NOTE_TOTAL_WORDS = 300

ROLE = {
    "exhibit_now": "copy its shape, pose and colour exactly; ignore its background",
    "living_form": "copy its body shape, colours and markings; ignore its background",
    "environment": "setting reference only: architecture, light and space",
}


def _s(text: str) -> str:
    """Field text without trailing punctuation, so joining never produces '..'."""
    return (text or "").strip().rstrip(".;, ")


def _lc(text: str) -> str:
    t = _s(text)
    return t[:1].lower() + t[1:] if t else t


def _overlap(a: str, b: str) -> float:
    words = lambda t: {x for x in re.findall(r"[a-z]+", t.lower()) if len(x) > 3}
    wa = words(a)
    return len(wa & words(b)) / max(1, len(wa))


def _words(text: str) -> int:
    return len(re.sub(r'"[^"]*"', "", text).split())


def render(script: schemas.Script, index: int) -> dict:
    seg = script.segments[index]
    assets = {a.id: a for a in script.assets}
    tag = {aid: f"@Image{n}" for n, aid in enumerate(seg.ref_assets, 1)}
    name = {"exhibit_now": script.subject_name, "detail": script.subject_name, "living_form": script.living_form_name}
    parts: dict[str, str] = {}

    # References: pass 1 = whole subjects and places, pass 2 = details; printed in @Image order.
    binds, described = {}, {}
    for a in seg.ref_assets:
        asset = assets.get(a)
        if not asset:
            binds[a] = f"{tag[a]} is {a}"
        elif asset.depicts == "environment":
            view = re.sub(r",?\s*without (the )?\w+.*$", "", _s(asset.view))
            binds[a] = f"{tag[a]} is {view} ({ROLE['environment']})"
        elif asset.depicts != "detail":
            if asset.depicts in described:
                binds[a] = f"{tag[a]} is another view of {described[asset.depicts]}"
            else:
                label = _s(name.get(asset.depicts) or asset.view)
                described[asset.depicts] = f"{label} ({tag[a]})"
                binds[a] = f"{tag[a]} is {label} ({ROLE[asset.depicts]})"
    for a in seg.ref_assets:
        asset = assets.get(a)
        if asset and asset.depicts == "detail":
            whole = described.get("exhibit_now", _s(script.subject_name or script.subject_lock))
            binds[a] = f"{tag[a]} is a close-up of {_s(asset.view)}, part of {whole}"
    parts["refs"] = ("References: " + "; ".join(binds[a] for a in seg.ref_assets) + ".") if seg.ref_assets \
        else f"Subject: {_s(script.subject_lock)}."

    states = [a for a in seg.ref_assets if a in assets and assets[a].depicts in ("exhibit_now", "living_form")]
    kinds = {assets[a].depicts for a in states}
    if len(kinds) > 1:
        living = next(tag[a] for a in states if assets[a].depicts == "living_form")
        now = next(tag[a] for a in states if assets[a].depicts == "exhibit_now")
        parts["states"] = f"{living} and {now} never appear in the same shot: hard cut between them, no morphing."

    look = "photorealistic documentary footage, natural light" if script.style == "realistic" else "lightly stylized animation, clean shapes, soft light"
    parts["style"] = f"Style: {look}. Setting: {_s(seg.setting)}."

    shots = []
    last = len(seg.shots)
    for n, s in enumerate(seg.shots, 1):
        refs = ", ".join(tag[r] for r in s.refs if r in tag)
        lead = "Shot 1" if n == 1 else f"Cut to shot {n}"
        body = _s(s.action)
        v = _s(s.visual)
        if v and _overlap(v, s.action) < 0.5:
            body += "; " + _lc(v)
        text = f"{lead}{(' (' + refs + ')') if refs else ''}: {_s(s.framing)}, {_lc(s.camera)}; {body}."
        if n == last and index < len(script.segments) - 1 and seg.end_frame:
            text += f" End on a near-still image: {_lc(seg.end_frame)}; the music has faded out by then."
        shots.append(text)
    parts["shots"] = " ".join(shots)

    lines = " ".join(f'"{l.text.strip()}"' for l in seg.narration)
    if lines:
        who = "Voiceover, an unseen narrator" if script.narrator_presence == "voiceover" else "The subject speaks on screen"
        parts["voice"] = f"{who}, {_lc(script.voice)}: {lines}"

    a = seg.audio
    sfx = "; ".join(_s(x) for x in a.sfx if _s(x))
    sound = "; ".join(x for x in (_s(a.ambience), sfx) if x)
    style = _s(script.music_style)
    if not style or style.lower() in ("none", "no music"):
        music = "No music."
    else:
        music = f"Music: {style}{', ' + _lc(a.music) if _s(a.music) else ''}."
    parts["sound"] = f"Sound: {sound}. {music}"

    subject = _s(script.subject_name) or "subject"
    parts["constraint"] = (f"Keep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. "
                           f"Only one {subject.removeprefix('the ').removeprefix('The ')} in any frame.")

    order = ("refs", "states", "style", "shots", "voice", "sound", "constraint")
    prompt = "\n".join(parts[k] for k in order if k in parts)
    breakdown = {k: _words(parts[k]) for k in order if k in parts}
    duration = max(4, min(15, round(seg.duration_s)))
    return {
        "endpoint": ENDPOINT,
        "image_urls": [f"<{a}>" for a in seg.ref_assets],
        "duration": str(duration),
        "resolution": RESOLUTION,
        "aspect_ratio": ASPECT,
        "generate_audio": True,
        "prompt": prompt,
        "prompt_words": len(prompt.split()),
        "direction_words": sum(breakdown.values()),
        "prompt_parts": breakdown,
        "est_usd": round(duration * USD_PER_SECOND.get(RESOLUTION, 0.30), 2),
    }
