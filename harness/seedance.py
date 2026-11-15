"""Turn one script segment into the fal Seedance 2.0 reference-to-video request.

The agent decides *what* happens (schemas.Script); this file decides *how it is written for Seedance*.
v2 (round 6, "make the exhibit act"): the old rules that kept the exhibit still are gone. Sources in
research/round6 (fal docs, ByteDance launch post and technical report, creator guides):
  - endpoint bytedance/seedance-2.0/reference-to-video, duration "4".."15", generate_audio on
  - each reference gets ONE stated job; @Image1..n follow upload order
  - numbered shots with time ranges "Shot n (a-bs)" for multi-shot clips, or timed beats of "One continuous take, no cuts."
  - motion amplitude only comes from wording: speed/force verbs and physical consequences
  - one transformation per shot (start; change with mechanism and speed; end)
  - spoken words in double quotes; short lines; the same voice description in every segment
  - name the sounds; "No music" unless a score is part of the concept
  - essentials first: references, lock, look, shots, voice, sound, constraint; keep it short
"""
from __future__ import annotations

import os
import re

import schemas

ENDPOINT = os.environ.get("SEEDANCE_ENDPOINT", "bytedance/seedance-2.0/reference-to-video")
RESOLUTION = os.environ.get("SEEDANCE_RESOLUTION", "720p")
ASPECT = os.environ.get("SEEDANCE_ASPECT", "16:9")
USD_PER_SECOND = {"480p": 0.14, "720p": 0.30}  # standard tier, from verified token pricing
MAX_DIRECTION_WORDS = 380   # hard limit: instruction overflow is a real failure
SOFT_DIRECTION_WORDS = 330  # above this: a note
NOTE_TOTAL_WORDS = 320


def _s(text: str) -> str:
    return (text or "").strip().rstrip(".;, ")


def _lc(text: str) -> str:
    t = _s(text)
    return t[:1].lower() + t[1:] if t else t


def _words(text: str) -> int:
    return len(re.sub(r'"[^"]*"', "", text).split())


def render(script: schemas.Script, index: int) -> dict:
    seg = script.segments[index]
    assets = {a.id: a for a in script.assets}
    tag = {aid: f"@Image{n}" for n, aid in enumerate(seg.ref_assets, 1)}
    subject = _s(script.subject_name) or "the exhibit"
    hero = _s(script.hero_mover) or _s(script.living_form_name) or "the character"
    parts: dict[str, str] = {}

    # References: one job each, printed in @Image order.
    jobs, named = [], {}
    for a in seg.ref_assets:
        asset = assets.get(a)
        if not asset:
            jobs.append(f"{tag[a]} = {a}")
            continue
        if asset.depicts == "exhibit_now":
            job = f"{subject}, identity anchor: shape, decoration and colours exactly as shown; ignore its background"
            named[a] = subject
        elif asset.depicts == "living_form":
            job = f"{hero}, the character: same design, colours and markings in every shot; ignore its background"
            named[a] = hero
        elif asset.depicts == "keyframe":
            job = f"{hero} at the big pose"
            named[a] = hero
        elif asset.depicts == "detail":
            job = f"close-up of {_s(asset.view)}, part of {subject}"
            named[a] = f"the {_s(asset.view)}"
        else:  # environment: in-place view or world plate
            in_place = subject.lower().removeprefix("the ") in asset.view.lower() or "in place" in asset.view.lower()
            job = f"{_s(asset.view)} ({'setting and final framing' if in_place else 'setting only'})"
            named[a] = "the setting"
        jobs.append(f"{tag[a]} = {job}")
    parts["refs"] = ("References: " + "; ".join(jobs) + ".") if seg.ref_assets else f"Subject: {_s(script.subject_lock)}."

    if script.mode == "world_returns":
        parts["lock"] = f"{subject[:1].upper() + subject[1:]} stays perfectly still and ends whole; only its world moves."
    else:
        still = f" {_s(script.still_parts)[:1].upper() + _s(script.still_parts)[1:]} stay still." if _s(script.still_parts) else ""
        parts["lock"] = f"Only {hero} comes alive.{still} {subject[:1].upper() + subject[1:]} ends whole and unchanged."

    look = _s(script.look) or ("photoreal live-action fantasy, real museum gallery" if script.style == "realistic"
                               else "stylized 3D animated feature, expressive character animation")
    parts["style"] = f"{look[:1].upper() + look[1:]}."

    shots = []
    last = len(seg.shots)
    # A segment whose beats all continue one take is written as timed beats, never "Shot n" (which invites cuts).
    one_take = all(_s(s.transition_in).lower().startswith("continu") for s in seg.shots[1:])
    for n, s in enumerate(seg.shots, 1):
        refs = ", ".join(f"{named.get(r, r)} from {tag[r]}" for r in s.refs if r in tag)
        lead = f"{s.t_start:g}-{s.t_end:g}s" if one_take else f"Shot {n} ({s.t_start:g}-{s.t_end:g}s)"
        trans = _s(s.transition_in)
        opener = f"{trans[:1].upper() + trans[1:]}: " if (n > 1 and trans and trans.lower() != "cut"
                                                          and not one_take) else ""
        body = f"{opener}{_s(s.framing)}, {_lc(s.camera)}. {_s(s.action)}"
        if _s(s.transformation):
            body += f"; {_lc(s.transformation)}"
        if _s(s.visual):
            body += f"; {_lc(s.visual)}"
        text = f"{lead}{(' [' + refs + ']') if refs else ''}: {body}."
        if n == last and index < len(script.segments) - 1 and seg.end_frame:
            text += f" End on a near-still image: {_lc(seg.end_frame)}."
        shots.append(text)
    parts["shots"] = ("One continuous take, no cuts. " if one_take and last > 1 else "") + " ".join(shots)

    lines = " ".join(f'"{l.text.strip()}"' for l in seg.narration)
    if lines:
        who = f"{hero[:1].upper() + hero[1:]} speaks on screen, lips in sync" if script.narrator_presence == "on_screen" else "Voiceover"
        parts["voice"] = f"{who}, {_lc(script.voice)}: {lines}"

    a = seg.audio
    sfx = "; ".join(_s(x) for x in a.sfx if _s(x))
    sound = "; ".join(x for x in (_s(a.ambience), sfx) if x)
    style = _s(script.music_style)
    music = "No music." if not style or style.lower() in ("none", "no music") else \
        f"Music: {style}{', ' + _lc(a.music) if _s(a.music) else ''}."
    parts["sound"] = f"Sound: {sound}. {music}"
    parts["constraint"] = (f"Clean picture: no subtitles, captions, lettering, logos or watermark. "
                           f"No people in frame. Never two copies of {subject} or of {hero} in one frame.")

    order = ("refs", "lock", "style", "shots", "voice", "sound", "constraint")
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
