"""Hard checks: things code can verify without asking a model. A problem here is never a matter of taste.

problems -> block shipping and are fed back to the writer and reviewer
notes    -> production facts a human must know (e.g. a reference image needs cropping), not the writer's fault
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import schemas
import seedance

WORDS_PER_SECOND = 2.5     # comfortable English narration pace
MAX_SEGMENT_S = 15         # one Seedance generation
MAX_REFS_PER_SEGMENT = 4   # research: 3-4 references work best; more invites duplicates
MIN_SHOT_S = 3.0
TAIL_S = 1.0               # last line must finish this long before its segment ends
HEAD_S = 0.8               # film opens on picture and sound

TEXT_ON_SCREEN = re.compile(
    r"\b(captions?|title cards?|lettering|handwritten|typed|inscriptions?|subtitles?|logos?|watermarks?|"
    r"on[- ]screen text|text (?:reads|reading|appears)|words? (?:appear|fade)|numbers? (?:appear|fade)|"
    r"figures? (?:appear|fade)|sign reading|label reading|superimposed)\b|[£$€]\s?\d", re.I)
NEGATED = re.compile(r"\b(?:no|not|without|avoid|avoiding|free of|never|exclude|excluding|remove|removed|removing|must not show)\b[^.;:]*", re.I)
SOCIAL = re.compile(r"//(www\.)?(x\.com|twitter\.com|facebook\.com|instagram\.com|tiktok\.com|threads\.net)/", re.I)
GLUED = re.compile(r"[a-z]{2}\.[a-z]{2,}")  # 'juvenile.of course': a sentence glued to stray words
MULTI_MOVE = re.compile(r"\b(then|followed by|before (?:a|it)|and then|while (?:tilting|panning|pushing|pulling|orbiting))\b", re.I)
NUMBERISH = re.compile(r"\d|\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
                       r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
                       r"hundred|thousand|million|billion|tonnes?|metres?|meters?|january|february|march|april|june|"
                       r"july|august|september|october|november|december)\b", re.I)

_SMALL = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
          "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]


def _say_int(n: int) -> int:
    """How many words it takes to say an integer aloud."""
    if n < 20:
        return 1
    if n < 100:
        return 1 if n % 10 == 0 else 2
    if n < 1000:
        return 2 + (0 if n % 100 == 0 else 1 + _say_int(n % 100))  # "two hundred (and) fifty"
    if 1100 <= n <= 2099 and n % 100 != 0:
        return _say_int(n // 100) + _say_int(n % 100)  # years: "eighteen ninety-one"
    if n < 1_000_000:
        rest = n % 1000
        return _say_int(n // 1000) + 1 + (0 if rest == 0 else _say_int(rest))
    return 3


def spoken_words(text: str) -> int:
    """Words as heard: '1891' is three words, '£250' is five, '25.2' is four."""
    total = 0
    for token in re.findall(r"[£$€]?\d[\d,]*(?:\.\d+)?%?|[A-Za-z'’]+(?:-[A-Za-z'’]+)*", text):
        if token[0].isdigit() or token[0] in "£$€":
            digits = token.lstrip("£$€").rstrip("%").replace(",", "")
            whole, _, frac = digits.partition(".")
            count = _say_int(int(whole)) + (1 + len(frac) if frac else 0)
            count += 1 if token[0] in "£$€" else 0
            count += 1 if token.endswith("%") else 0
            total += count
        else:
            total += 1
    return total


def word_budget(duration_s: float) -> int:
    """Narration ceiling for a segment: pace x (duration minus head/tail kept for picture and sound)."""
    return int((duration_s - 2) * WORDS_PER_SECOND)


def _expect(exhibit_id: str) -> dict:
    p = Path(__file__).resolve().parent / "knowledge" / exhibit_id / "expect.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _text_on_screen(text: str) -> bool:
    return bool(TEXT_ON_SCREEN.search(NEGATED.sub("", text)))


# ---------- per stage ----------

def _norm(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.strip()).rstrip("/").lower()


def research(rs: schemas.Research, retrieved: list[str]) -> list[str]:
    """Every source and finding URL must be one the search/fetch tools actually returned in that call."""
    got = {_norm(u) for u in retrieved}
    problems = []
    for src in rs.sources:
        if _norm(src.url) not in got:
            problems.append(f"source not returned by any search or fetch: {src.url}")
    for f in rs.findings:
        if _norm(f.url) not in got:
            problems.append(f"finding cites a URL no tool returned: {f.url} ('{f.text[:50]}')")
        elif SOCIAL.search(f.url):
            problems.append(f"finding cites a social-media post: {f.url} ('{f.text[:50]}')")
        else:
            for num in re.findall(r"\d[\d,.]*\d|\d", f.text):
                if num not in f.quote:
                    problems.append(f"finding says {num}, which is not in its own quote: {f.url} ('{f.text[:50]}')")
    if not rs.findings:
        problems.append("research returned no findings")
    return problems


def material(sheet: schemas.MaterialSheet, pack_text: str, exhibit_id: str,
             findings: list[schemas.Finding] | None = None) -> list[str]:
    problems = []
    facts = {f.id: f for f in sheet.facts}
    web = {_norm(f.url): f for f in (findings or [])}
    web_text = " ".join(f.text for f in (findings or []))
    for fact in sheet.facts:
        in_pack = fact.source in pack_text
        if not in_pack and _norm(fact.source) not in web:
            problems.append(f"fact '{fact.id}' cites a source that is neither in the pack nor a verified research finding: {fact.source}")
        for num in re.findall(r"\d[\d,.]*\d|\d", fact.text):
            if num.rstrip(".,") not in pack_text and num.rstrip(".,") not in web_text:
                problems.append(f"fact '{fact.id}' has the number {num}, which is in neither the pack nor the research findings")
    if len(facts) != len(sheet.facts):
        problems.append("duplicate fact ids")
    if not sheet.through_lines or not 0 <= sheet.lead_line < len(sheet.through_lines):
        problems.append("no valid lead through-line")
        return problems
    ci = sheet.controlling_idea
    for label, text in [("last_thought", ci.last_thought), ("actually", ci.actually), ("emotional_core", sheet.emotional_core)] + \
            [(f"spine '{t.name}'", t.spine) for t in sheet.through_lines]:
        if GLUED.search(text.replace("e.g.", "").replace("i.e.", "")):
            problems.append(f"{label} has glued or stray text: '{GLUED.search(text).group(0)}'")
    if not ci.actually_fact_ids:
        problems.append("controlling idea: 'actually' cites no fact; it must rest on a pack fact, not an inference")
    for f in ci.actually_fact_ids + ci.second_half_fact_ids:
        if f not in facts:
            problems.append(f"controlling idea cites unknown fact '{f}'")
        elif facts[f].about != "exhibit":
            problems.append(f"controlling idea cites context fact '{f}'; it must be about this exhibit")
    if len(ci.last_thought.split()) > 10:
        problems.append("controlling idea's last thought is longer than ten words")
    for t in sheet.through_lines:
        unknown = [f for f in t.fact_ids + t.turn_fact_ids if f not in facts]
        if unknown:
            problems.append(f"through-line '{t.name}' uses unknown facts {unknown}")
    for q in sheet.visitor_questions:
        unknown = [f for f in q.answer_fact_ids if f not in facts]
        if unknown:
            problems.append(f"visitor question '{q.question[:40]}' cites unknown facts {unknown}")
    for m in sheet.visual_motifs:
        if _text_on_screen(m):
            problems.append(f"visual motif puts text on screen: '{m[:60]}'")
    return problems


def regression(sheet: schemas.MaterialSheet, exhibit_id: str) -> list[str]:
    """Expectations from knowledge/<id>/expect.json. Reported, never fed back to the agent."""
    exp = _expect(exhibit_id)
    out = []
    if exp.get("duration_s") and sheet.duration_s != exp["duration_s"]:
        out.append(f"length {sheet.duration_s}s; expected {exp['duration_s']}s for this exhibit")
    return out


def concepts(cs: schemas.ConceptSet, sheet: schemas.MaterialSheet) -> list[str]:
    problems = []
    if len(cs.concepts) < 3:
        problems.append(f"only {len(cs.concepts)} concept(s); asked for 3")
    if not 0 <= cs.chosen < len(cs.concepts):
        problems.append(f"chosen index {cs.chosen} is out of range")
    known = {f.id for f in sheet.facts}
    engines = [c.engine.split()[0].lower() for c in cs.concepts if c.engine]
    if len(set(engines)) < len(engines):
        problems.append(f"concepts reuse the same engine: {[c.engine for c in cs.concepts]}")
    for c in cs.concepts:
        unknown = [f for f in c.fact_ids if f not in known]
        if unknown:
            problems.append(f"concept '{c.name}' uses unknown facts {unknown}")
        for field in ("hook_visual", "ending_visual"):
            if _text_on_screen(getattr(c, field)):
                problems.append(f"concept '{c.name}' {field} puts text or numbers on screen")
    return problems


def script(sc: schemas.Script, sheet: schemas.MaterialSheet, exhibit_id: str,
           existing: list[dict] | None = None, findings: list[schemas.Finding] | None = None) -> list[str]:
    problems = []
    facts = {f.id: f for f in sheet.facts}
    assets = {a.id: a for a in sc.assets}
    existing_ids = {a["id"] for a in (existing or [])}
    exp = _expect(exhibit_id)

    if sc.duration_s != sheet.duration_s:
        problems.append(f"script is {sc.duration_s}s but the material sheet chose {sheet.duration_s}s")
    expected_segments = 1 if sc.duration_s <= MAX_SEGMENT_S else 2
    if len(sc.segments) != expected_segments:
        problems.append(f"{len(sc.segments)} segment(s) for a {sc.duration_s}s film; expected {expected_segments}")
    total = sum(s.duration_s for s in sc.segments)
    if abs(total - sc.duration_s) > 0.5:
        problems.append(f"segments add up to {total}s, not {sc.duration_s}s")

    for a in sc.assets:
        if a.source == "existing" and a.id not in existing_ids:
            problems.append(f"asset '{a.id}' is marked existing but no such reference image exists")
        if a.source == "generate" and _text_on_screen(a.prompt):
            problems.append(f"asset '{a.id}' prompt asks for text in the image")

    labeled = {a["id"] for a in (existing or []) if a.get("has_text_labels")}
    sheets = {a["id"] for a in (existing or []) if a.get("kind") == "character_sheet"}
    for i, seg in enumerate(sc.segments, 1):
        for a in seg.ref_assets:
            if a in labeled or a in sheets or ("sheet" in a and not a.endswith("_side")):
                problems.append(f"segment {i} sends '{a}' to the video model; never send a character sheet or labelled image, use its single-view image")
        if seg.duration_s > MAX_SEGMENT_S:
            problems.append(f"segment {i} is {seg.duration_s}s, over the {MAX_SEGMENT_S}s generation limit")
        if len(seg.ref_assets) > MAX_REFS_PER_SEGMENT:
            problems.append(f"segment {i} uses {len(seg.ref_assets)} references; keep to {MAX_REFS_PER_SEGMENT}")
        missing = [a for a in seg.ref_assets if a not in assets]
        if missing:
            problems.append(f"segment {i} uses undefined assets {missing}")
        t = 0.0
        for j, shot in enumerate(seg.shots, 1):
            where = f"segment {i} shot {j}"
            if abs(shot.t_start - t) > 0.05:
                problems.append(f"{where} starts at {shot.t_start}s, previous ended at {t}s")
            if shot.t_end - shot.t_start < MIN_SHOT_S:
                problems.append(f"{where} is {shot.t_end - shot.t_start:.1f}s; shots under {MIN_SHOT_S}s rarely render cleanly")
            if _text_on_screen(shot.visual + " " + shot.action):
                problems.append(f"{where} seems to ask for text on screen")
            if MULTI_MOVE.search(shot.camera):
                problems.append(f"{where} camera has more than one move: '{shot.camera}'")
            states = {assets[r].depicts for r in shot.refs if r in assets} & {"exhibit_now", "living_form"}
            if len(states) > 1:
                problems.append(f"{where} shows the exhibit as it is now and its living form together; keep them in separate shots")
            stray = [r for r in shot.refs if r not in seg.ref_assets]
            if stray:
                problems.append(f"{where} shows {stray}, which are not in the segment's references")
            t = shot.t_end
        if seg.shots and abs(t - seg.duration_s) > 0.05:
            problems.append(f"segment {i} shots end at {t}s, segment is {seg.duration_s}s")

        lines = sorted(seg.narration, key=lambda l: l.t_start)
        for k, line in enumerate(lines):
            where = f"segment {i} line '{line.text[:40]}'"
            unknown = [f for f in line.fact_ids if f not in facts]
            if unknown:
                problems.append(f"{where} cites unknown facts {unknown}")
            if GLUED.search(line.text):
                problems.append(f"{where} has glued or stray text")
            if line.kind == "fact" and not line.fact_ids:
                problems.append(f"{where} is marked fact but cites no fact id")
            if line.kind != "fact" and line.fact_ids:
                problems.append(f"{where} is marked {line.kind} but cites facts; mark it fact or drop the ids")
            if line.kind != "fact" and NUMBERISH.search(line.text):
                problems.append(f"{where} states a number, date or measure but is not marked as a sourced fact")
            cited = " ".join(facts[f].text for f in line.fact_ids if f in facts)
            for num in re.findall(r"\d[\d,.]*\d|\d", line.text):
                if num not in cited:
                    problems.append(f"{where} says {num}, which is not in the facts it cites")
            end = line.t_start + spoken_words(line.text) / WORDS_PER_SECOND
            if k + 1 < len(lines) and end > lines[k + 1].t_start + 0.1:
                problems.append(f"{where} needs about {end - line.t_start:.1f}s and runs into the next line")
            if k > 0 and line.fact_ids and set(line.fact_ids) == set(lines[k - 1].fact_ids):
                problems.append(f"{where} carries the same fact as the line before it: padding")
            if k + 1 == len(lines) and end > seg.duration_s - TAIL_S + 0.15:
                problems.append(f"{where} ends at about {end:.1f}s; the last line must finish by {seg.duration_s - TAIL_S:.1f}s")
        if i == 1 and lines and lines[0].t_start < HEAD_S:
            problems.append(f"first line starts at {lines[0].t_start}s; open on {HEAD_S}s of picture and sound")
        req = seedance.render(sc, i - 1)
        if req["direction_words"] > seedance.MAX_DIRECTION_WORDS:
            p = req["prompt_parts"]
            problems.append(f"segment {i} request has {req['direction_words']} direction words (cap {seedance.MAX_DIRECTION_WORDS}, quoted narration not counted): "
                            f"references {p.get('refs', 0)}, shots {p.get('shots', 0)}, sound {p.get('sound', 0)}, voice {p.get('voice', 0)}, "
                            f"fixed {p.get('style', 0) + p.get('states', 0) + p.get('constraint', 0)}; cut the largest part you control")
        seg_words = sum(spoken_words(l.text) for l in seg.narration)
        if seg_words > word_budget(seg.duration_s):
            problems.append(f"segment {i} narration is {seg_words} spoken words; budget for {seg.duration_s}s is {word_budget(seg.duration_s)}")

    if sc.duration_s == 30 and sum(spoken_words(l.text) for s in sc.segments for l in s.narration) < 40:
        problems.append("a 30 s film with under 40 spoken words is a 15 s story stretched")
    spoken = " ".join(l.text for s in sc.segments for l in s.narration)
    subs = " ".join(s.text for s in sc.subtitles)
    if spoken and abs(len(re.findall(r"[A-Za-z]+", spoken)) - len(re.findall(r"[A-Za-z]+", subs))) > 4:
        problems.append("subtitles do not match the narration text")
    if re.search(r"[一-鿿]", spoken + subs):
        problems.append("narration or subtitles contain Chinese; must be English")
    low = spoken.lower()
    sourced_now = " ".join(f.text for f in (findings or [])).lower()
    for bad in exp.get("forbidden", []):
        if bad.lower() in low and bad.lower() not in sourced_now:
            problems.append(f"narration contains '{bad}', which this exhibit's material does not support")
    return problems


def notes(sc: schemas.Script, existing: list[dict] | None = None) -> list[str]:
    """Production notes for the humans running generation."""
    out = []
    labeled = {a["id"] for a in (existing or []) if a.get("has_text_labels")}
    for i, seg in enumerate(sc.segments, 1):
        for a in seg.ref_assets:
            if a in labeled:
                out.append(f"segment {i} uses '{a}', which carries text labels: crop it into text-free views before sending to Seedance")
    for i in range(len(sc.segments)):
        r = seedance.render(sc, i)
        if r["prompt_words"] > seedance.NOTE_TOTAL_WORDS:
            out.append(f"segment {i + 1} request is {r['prompt_words']} words including narration")
    styles = {a.get("style") for a in (existing or []) if a["id"] in {r for s in sc.segments for r in s.ref_assets}}
    styles.discard(None)
    if len(styles) > 1:
        out.append(f"references mix styles {sorted(styles)} in one film")
    if styles and sc.style not in styles:
        out.append(f"script style is {sc.style} but its references are {sorted(styles)}")
    return out


def stats(sc: schemas.Script) -> dict:
    words = sum(spoken_words(l.text) for s in sc.segments for l in s.narration)
    return {
        "duration_s": sc.duration_s,
        "style": sc.style,
        "narrator": sc.narrator_presence,
        "segments": len(sc.segments),
        "shots": sum(len(s.shots) for s in sc.segments),
        "spoken_words": words,
        "words_per_second": round(words / sc.duration_s, 2),
        "lines_by_kind": {k: sum(1 for s in sc.segments for l in s.narration if l.kind == k) for k in ("fact", "visible", "voice")},
        "assets": {"existing": sum(a.source == "existing" for a in sc.assets), "generate": sum(a.source == "generate" for a in sc.assets)},
    }


def keywords(batch: list[dict], material: str) -> list[str]:
    """Keywords are shown to visitors: each must be copied from the material it was made from."""
    out, low = [], material.lower()
    stop = {"the", "of", "a", "an", "and", "in", "at", "on", "to"}
    for k in batch:
        text = k.get("text", "")
        words = [w for w in re.findall(r"[\w£$€.,'’-]+", text.lower()) if w not in stop]
        missing = [w for w in words if w.strip(".,") not in low]
        if missing:
            out.append(f"'{text}' is not copied from its material (missing: {', '.join(missing)})")
        if len(text.split()) > 5:
            out.append(f"'{text}' is longer than 5 words")
    if not 5 <= len(batch) <= 10:
        out.append(f"{len(batch)} keywords; asked for 5-10")
    return out
