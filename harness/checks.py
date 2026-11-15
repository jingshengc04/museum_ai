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
MIN_SHOT_S = 2.0           # quick cuts render
MIN_TRANSFORM_S = 3.5      # a transformation needs time
MAX_SHOTS_PER_SEGMENT = 5
MAX_LINE_WORDS = 10        # short lines keep lip-sync clean
MAX_SEG_WORDS = 24         # lines are a counter-track, not a lecture
MAX_SHOT_WORDS = 60        # framing+camera+action+transformation+visual per shot
TAIL_S = 1.0               # last line must finish this long before its segment ends
HEAD_S = 0.8               # film opens on picture and sound

TEXT_ON_SCREEN = re.compile(
    r"\b(captions?|title cards?|lettering|handwritten|typed|inscriptions?|subtitles?|logos?|watermarks?|"
    r"on[- ]screen text|text (?:reads|reading|appears)|words? (?:appear|fade)|numbers? (?:appear|fade)|"
    r"figures? (?:appear|fade)|sign reading|label reading|superimposed)\b|[£$€]\s?\d", re.I)
NEGATED = re.compile(r"\b(?:no|not|without|avoid|avoiding|free of|never|exclude|excluding|remove|removed|removing|must not show)\b[^.;:]*", re.I)
SOCIAL = re.compile(r"//(www\.)?(x\.com|twitter\.com|facebook\.com|instagram\.com|tiktok\.com|threads\.net)/", re.I)
GLUED = re.compile(r"[a-z]{2}\.[a-z]{2,}")  # 'juvenile.of course': a sentence glued to stray words
MOVES = re.compile(r"\b(locked(?: off)?|static|push[- ]?in|pull[- ]?back|pull[- ]?out|tilt\w*|pan\w*|whip pan|orbit\w*|crane\w*|dolly\w*|track\w*|zoom\w*|crash zoom|fpv|drift\w*|handheld|arc\w*)\b", re.I)
QUICK = re.compile(r"\b(whip pan|crash zoom|locked(?: off)?|static)\b", re.I)
TIMED = re.compile(r"\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\s*s")
FORCE = re.compile(r"\b(fast|quickly|hard|snaps?|snapping|wrench\w*|leaps?|leaping|lunges?|bursts?|surges?|slams?|violently|heaves?|races?|racing|gallops?|crash\w*|shakes|whips?|explod\w*|dives?|diving|rockets?|spins?|spinning|bounds?|charges?|plunges?|soars?|thrash\w*|flips?|breaches?|breaching)\b", re.I)
TRANSFORM_VERBS = re.compile(r"\b(turns into|becomes|morphs?|dissolves?|melts?|transforms?|solidif\w+|reassembles?)\b", re.I)
RECORD = re.compile(r"\b(documentary|archival|newsreel|re-?enact\w*|reconstruction of|excavat\w+|foundry|casting workshop|air raid|bombing|bombers?|soldiers?|priests?|archaeologists?|the finders?)\b", re.I)
ADJECTIVES = re.compile(r"\b(magical|majestic|stunning|epic|breathtaking|8k|mystical|cinematic masterpiece)\b", re.I)
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


def _s(t: str) -> str:
    return (t or "").strip()


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
        if not _s(c.hero_mover):
            problems.append(f"concept '{c.name}' has no hero_mover")
        if not FORCE.search(c.big_move):
            problems.append(f"concept '{c.name}' big_move has no speed or force word: '{c.big_move[:60]}'")
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
    if not _s(sc.hero_mover):
        problems.append("no hero_mover: name the one character or part that comes alive")
    for i, seg in enumerate(sc.segments, 1):
        for a in seg.ref_assets:
            if a in labeled or "expression" in a:
                problems.append(f"segment {i} sends '{a}' to the video model; never send a labelled image or expression grid, use its single-view image")
        if len(seg.shots) > MAX_SHOTS_PER_SEGMENT:
            problems.append(f"segment {i} has {len(seg.shots)} shots; keep to {MAX_SHOTS_PER_SEGMENT}")
        acts = [sh for sh in seg.shots if sh.beat == "act"]
        if len(acts) != 1:
            problems.append(f"segment {i} has {len(acts)} act shots; give it exactly one high-amplitude beat")
        for sh in acts:
            if not FORCE.search(sh.action + " " + sh.camera + " " + sh.transformation):
                problems.append(f"segment {i} act shot has no speed or force word; the model defaults to gentle motion")
        if seg.shots and seg.shots[0].beat != "still" and i == 1:
            problems.append("the film should open on the still, real exhibit (beat 'still')")
        if seg.shots and seg.shots[-1].beat != "return" and i == len(sc.segments):
            problems.append("the film should end on the return to the real exhibit (beat 'return')")
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
            moves = {m.group(0).lower() for m in MOVES.finditer(shot.camera)}
            if len(moves) >= 3 or (len(moves) == 2 and not QUICK.search(shot.camera) and not TIMED.search(shot.camera)):
                problems.append(f"{where} camera stacks moves ('{shot.camera}'); cut, or write timed beats")
            shot_words = len(" ".join([shot.framing, shot.camera, shot.action, shot.transformation, shot.visual]).split())
            if shot_words > MAX_SHOT_WORDS:
                problems.append(f"{where} is {shot_words} words; keep each beat to about 55 (one tight sentence, verbs first)")
            n_tr = len(TRANSFORM_VERBS.findall(shot.action)) + (1 if _s(shot.transformation) else 0)
            if n_tr > 1:
                problems.append(f"{where} has more than one transformation; give each its own shot")
            if _s(shot.transformation) and shot.t_end - shot.t_start < MIN_TRANSFORM_S:
                problems.append(f"{where} transforms in {shot.t_end - shot.t_start:.1f}s; give a transformation at least {MIN_TRANSFORM_S}s")
            if ADJECTIVES.search(shot.action + " " + shot.visual):
                problems.append(f"{where} uses adjectives for action; write verbs and physics")
            if sc.style != "stylized" and RECORD.search(shot.action + " " + shot.visual) and not re.search(r"ink|shadow puppet|rubbing", shot.visual + shot.transition_in, re.I):
                problems.append(f"{where} stages history as record; show it as fantasy or in one stated stylised look")
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
                            f"fixed {p.get('style', 0) + p.get('lock', 0) + p.get('constraint', 0)}; cut sound and light words first, never speed, force or consequence words")
        seg_words = sum(spoken_words(l.text) for l in seg.narration)
        if seg_words > MAX_SEG_WORDS:
            problems.append(f"segment {i} has {seg_words} spoken words; keep to {MAX_SEG_WORDS} per 15 s so the action can breathe")
        for l in seg.narration:
            if spoken_words(l.text) > MAX_LINE_WORDS:
                problems.append(f"segment {i} line '{l.text[:40]}' is {spoken_words(l.text)} words; keep lines to {MAX_LINE_WORDS} for clean lip-sync")
        for act in acts:
            for l in seg.narration:
                l_end = l.t_start + spoken_words(l.text) / WORDS_PER_SECOND
                if l.t_start < act.t_end - 0.3 and l_end > act.t_start + 0.3:
                    problems.append(f"segment {i} line '{l.text[:40]}' talks over the act beat; leave the big move without speech")
        if len(seg.audio.sfx) < 3:
            problems.append(f"segment {i} names {len(seg.audio.sfx)} sounds; sound is the second actor, name three or four")

    if sc.segments and sc.segments[-1].shots:
        last = sc.segments[-1].shots[-1]
        if not any(assets.get(r) and assets[r].depicts in ("exhibit_now", "environment") for r in last.refs):
            problems.append("the return shot lists neither the exhibit nor the in-place view; the visitor must see the real object at the end")
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
        if r["direction_words"] > seedance.SOFT_DIRECTION_WORDS:
            out.append(f"segment {i + 1} request has {r['direction_words']} direction words (soft limit {seedance.SOFT_DIRECTION_WORDS})")
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
        "mode": sc.mode,
        "hero_mover": sc.hero_mover,
        "act_shots": [f"{i + 1}.{j + 1}" for i, s in enumerate(sc.segments) for j, sh in enumerate(s.shots) if sh.beat == "act"],
        "force_words": sum(len(FORCE.findall(sh.action)) for s in sc.segments for sh in s.shots),
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
    if not batch:
        out.append("no keywords returned")
    return out
