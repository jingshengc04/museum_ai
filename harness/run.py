"""Run the script agent on one exhibit and write a readable report.

    uv run python run.py hope                       # uses the exhibit's test photo if meta.json names one
    uv run python run.py hope --no-photo            # knowledge pack only
    uv run python run.py hope --photo shot.jpg      # a different visitor photo
    uv run python run.py hope --fresh s2,s3         # re-ask these stages instead of using the cache
    uv run python run.py hope --variant s3=counter  # use prompts/s3_script.counter.md for S3 (any stage)
    uv run python run.py hope --sample 2            # an independent draw (for comparing prompt versions fairly)
    uv run python run.py all                        # every exhibit in knowledge/
    uv run python run.py hope --user-input "选15s"   # appended to every core stage as "User input: 选15s"
    uv run python run.py --photo some.jpg           # any photo: matches a prepared pack, or runs on search alone
    uv run python run.py hope --no-pack             # hope's test photo with every pack hidden (search-only test)

Unchanged stages come from the cache, so editing one prompt only pays for that stage and the ones after it.
Output: runs/<time>-<exhibit>[-label]/report.md, script.json, seedance.json, plus each stage's archive.
"""
from __future__ import annotations

import argparse
import threading
import json
import sys
import time
import traceback
from pathlib import Path

import agent
import checks
import schemas
import seedance
import timing
import images

MAX_ATTEMPTS = 3  # first draft + up to two revisions
NO_SEARCH = False
SHORT = {"s0b": "s0b_research", "s0": "s0_identify", "s1": "s1_digest", "s1b": "s1b_assets", "s2": "s2_concept", "s3": "s3_script", "s4": "s4_review"}


GATES = {"aliveness": 4, "spectacle": 4, "return_shot": 4}  # the new centre; every other score needs 3


def passed(review: schemas.Review, problems: list[str]) -> bool:
    s = review.scores.model_dump()
    blocking = [i for i in review.issues if i.severity == "blocking"]
    gates = all(s[k] >= v for k, v in GATES.items())
    return (not problems and not blocking and s["truth"] == 5 and review.fantasy_legibility == "pass"
            and gates and min(s.values()) >= 3)


def rank(attempt: dict) -> tuple:
    r: schemas.Review = attempt["review"]
    s = r.scores.model_dump()
    return (len(attempt["problems"]), sum(i.severity == "blocking" for i in r.issues), -s["truth"],
            -(s["aliveness"] + s["spectacle"]), -min(s.values()), -sum(s.values()))


def run_one(exhibit_id: str | None, photo: Path | None, variants: dict[str, str], label: str) -> Path:
    stamp = time.strftime("%m%d-%H%M%S")
    run_dir = agent.RUNS / f"{stamp}-{exhibit_id or 'photo'}{'-nopack' if agent.NO_PACK else ''}{('-' + label) if label else ''}"
    run_dir.mkdir(parents=True)
    ctx: dict = {"exhibit_id": exhibit_id, "photo": photo, "log": [], "attempts": [], "error": None, "feed": [],
                 "keywords": {}, "kw_threads": []}
    print(f"[{exhibit_id}] {run_dir.name}  photo={photo.name if photo else 'none'}")
    t0 = time.time()
    feed_file = (run_dir / "events.jsonl").open("w")

    lock = threading.Lock()

    def on_event(e: dict) -> None:
        with lock:
            e = {"t_run": round(time.time() - t0, 2), **e}
            ctx["feed"].append(e)
            feed_file.write(json.dumps(e, ensure_ascii=False) + "\n")
            feed_file.flush()
        if e.get("type") == "keywords_batch":
            print(f"    ✦ {e['t_run']:6.1f}s  keywords ({e['label']}): " + " · ".join(k["text"] for k in e["keywords"]))

    agent.EMIT = on_event
    try:
        _pipeline(ctx, run_dir, variants)
    except Exception as e:
        ctx["error"] = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        print(f"  ERROR {type(e).__name__}: {e}")
    finally:
        for t in ctx["kw_threads"]:
            t.join()
        agent.EMIT = None
        feed_file.close()
        (run_dir / "report.md").write_text(render(ctx, run_dir))
        print(f"  status {ctx.get('status', 'ERROR')} · new spend ${cost(run_dir):.2f} → {run_dir / 'report.md'}")
    return run_dir


def side_keywords(ctx: dict, run_dir: Path, label: str, material: str) -> None:
    """Fire-and-forget keyword request; the core agent does not wait for it."""
    def work():
        try:
            batch = [k.model_dump() for k in agent.keyword_batch(label, material, run_dir).keywords]
            flags = checks.keywords(batch, material)
            ctx["keywords"][label] = {"keywords": batch, "flags": flags}
            agent.emit(f"kw_{label}", type="keywords_batch", label=label, keywords=batch, flags=flags)
        except Exception as e:  # keywords must never break the film
            ctx["keywords"][label] = {"keywords": [], "flags": [f"keyword request failed: {e}"]}
    t = threading.Thread(target=work, daemon=True)
    t.start()
    ctx["kw_threads"].append(t)


def _pipeline(ctx: dict, run_dir: Path, variants: dict[str, str]) -> None:
    exhibit_id, photo, log = ctx["exhibit_id"], ctx["photo"], ctx["log"]

    def note(stage, problems):
        log.append({"stage": stage, "problems": problems})
        for p in problems:
            print(f"  ! {stage}: {p}")

    photo_notes, ident = "", None
    if photo:
        ident = agent.s0_identify(photo, run_dir, variants.get("s0", ""))
        ctx["ident"] = ident
        print(f"  S0 sees: {ident.recognized_as} → '{ident.exhibit_id}' ({ident.confidence})")
        prepared = {e["id"] for e in agent.exhibits()}
        if ident.exhibit_id in prepared:
            if exhibit_id and ident.exhibit_id != exhibit_id:
                note("s0", [f"matched '{ident.exhibit_id}', expected '{exhibit_id}'"])
            exhibit_id = ident.exhibit_id
        elif ident.confidence == "low" or not ident.short_name.strip():
            raise RuntimeError(f"Could not recognise the object in the photo well enough to tell its story: {ident.reason}")
        else:
            exhibit_id = agent.register_adhoc(ident)
            print(f"  → no prepared pack: '{ident.short_name}' ({ident.museum or 'museum unknown'}); research will be the only source")
        ctx["exhibit_id"] = exhibit_id
        photo_notes = f"{ident.what_is_visible} Visitor interest: {ident.visitor_interest}"
        side_keywords(ctx, run_dir, "identify", f"From the visitor's photo (basis 'photo'): {ident.recognized_as} {ident.what_is_visible}")
    elif not exhibit_id:
        raise RuntimeError("Need a photo or an exhibit id")
    existing = agent.existing_assets(exhibit_id)
    ctx["photo_notes"] = photo_notes

    research = None
    if NO_SEARCH and exhibit_id in agent.ADHOC:
        raise RuntimeError("No prepared pack and search is off: nothing to tell the story from")
    if not NO_SEARCH:
        research = agent.s0b_research(exhibit_id, ident, photo, run_dir, variants.get("s0b", ""))
        tools_file = run_dir / "00_s0b_research" / "tools.json"
        retrieved = json.loads(tools_file.read_text())["retrieved_urls"] if tools_file.exists() else []
        bad = checks.research(research, retrieved)
        note("s0b", bad)
        bad_urls = {checks._norm(b.split(": ", 1)[1].split(" (")[0]) for b in bad if ": " in b}
        research.findings = [f for f in research.findings if checks._norm(f.url) not in bad_urls]  # drop unverifiable
        ctx["research"] = research
        ctx["retrieved"] = retrieved
        searches = sum(1 for c in json.loads(tools_file.read_text())["calls"] if c.get("tool") == "web_search") if tools_file.exists() else 0
        material = "\n".join(f"- {f.text} [quote: {f.quote}] (basis {f.url})" for f in research.findings)
        side_keywords(ctx, run_dir, "research", f"Research findings:\n{material}\n\nPrepared pack (basis 'pack'):\n{agent.pack(exhibit_id)}")
        print(f"  S0b {searches} searches, {len(retrieved)} URLs seen, {len(research.sources)} sources, {len(research.findings)} verified findings")
    findings = research.findings if research else []

    sheet = agent.s1_digest(exhibit_id, photo, photo_notes, run_dir, variants.get("s1", ""), research=research)
    s1_problems = checks.material(sheet, agent.pack(exhibit_id), exhibit_id, findings)
    if s1_problems:
        note("s1#0", s1_problems)
        sheet = agent.s1_digest(exhibit_id, photo, photo_notes, run_dir, variants.get("s1", ""),
                                previous=sheet, feedback="\n".join(f"- {p}" for p in s1_problems), research=research)
        s1_problems = checks.material(sheet, agent.pack(exhibit_id), exhibit_id, findings)
        note("s1#1", s1_problems)
    ctx["sheet"] = sheet
    lead = sheet.through_lines[sheet.lead_line] if 0 <= sheet.lead_line < len(sheet.through_lines) else None
    print(f"  S1 {len(sheet.facts)} facts → {sheet.duration_s}s · idea: thinks '{sheet.controlling_idea.visitor_assumes}', actually '{sheet.controlling_idea.actually}'")
    ctx["regression"] = checks.regression(sheet, exhibit_id)
    for r in ctx["regression"]:
        print(f"  ✗ regression: {r}")

    plan = agent.s1b_assets(exhibit_id, sheet, photo, run_dir, variants.get("s1b", ""))
    ctx["plan"] = plan
    print(f"  S1b {len(plan.images)} reference images planned")
    jobs = images.jobs(plan, existing, photo is not None)
    ctx["image_jobs"] = jobs
    (run_dir / "image_jobs.json").write_text(json.dumps(jobs, indent=2, ensure_ascii=False))
    agent.emit("s1b_assets", type="image_jobs_ready", count=len(jobs), est_usd=images.total(jobs))
    print(f"  → {len(jobs)} image jobs ready (photo + prompt, ~${images.total(jobs)}); generation can start now, in parallel with S2-S4")

    cs = agent.s2_concept(exhibit_id, sheet, plan, photo, photo_notes, run_dir, variants.get("s2", ""))
    ctx["concepts"] = cs
    concept = cs.concepts[cs.chosen] if 0 <= cs.chosen < len(cs.concepts) else cs.concepts[0]
    print(f"  S2 chose '{concept.name}' ({concept.engine}): {concept.logline}")
    note("s2", checks.concepts(cs, sheet))

    previous_script, previous_review, feedback = None, None, ""
    for attempt in range(MAX_ATTEMPTS):
        script = agent.s3_script(exhibit_id, sheet, plan, concept, photo, photo_notes, run_dir, attempt=attempt,
                                 previous=previous_script, feedback=feedback, variant=variants.get("s3", ""))
        s3_dir = run_dir / f"{4 + attempt * 2:02d}_s3_script"
        script, nudges = timing.nudge(script)
        if nudges:
            (s3_dir / "nudged.json").write_text(json.dumps({"changes": nudges, "script": script.model_dump()}, indent=2, ensure_ascii=False))
            for n in nudges:
                print(f"  ~ timing: {n}")
        problems = checks.script(script, sheet, exhibit_id, existing, findings)
        (s3_dir / "checks.json").write_text(json.dumps(problems, indent=2, ensure_ascii=False))
        if feedback:
            (s3_dir / "feedback.md").write_text(feedback)
        note(f"s3#{attempt}", problems)

        review = agent.s4_review(exhibit_id, script, sheet, concept, photo, photo_notes, problems, run_dir,
                                 attempt=attempt, previous=previous_review, variant=variants.get("s4", ""))
        ok = passed(review, problems)
        blocking = [i for i in review.issues if i.severity == "blocking"]
        polish = [i for i in review.issues if i.severity == "polish"]
        ctx["attempts"].append({"n": attempt, "script": script, "review": review, "problems": problems, "passed": ok})
        print(f"  S3/S4 #{attempt}: {'PASS' if ok else 'revise'} · {len(problems)} check, {len(blocking)} blocking, "
              f"{len(polish)} polish · scores {review.scores.model_dump()}")
        if ok and not polish:
            break
        if ok and attempt > 0 and ctx["attempts"][-2]["passed"]:
            break  # already did a polish round on a passing script
        items = [f"- [check] {p}" for p in problems] + [f"- [blocking] [{i.where}] {i.problem} → {i.fix}" for i in blocking]
        if not problems and not blocking:  # polish only once the script is otherwise shippable
            items += [f"- [polish] [{i.where}] {i.problem} → {i.fix}" for i in polish]
        feedback = "\n".join(items)
        previous_script, previous_review = script, review

    best = min(ctx["attempts"], key=rank)
    ctx["best"] = best
    open_polish = [i for i in best["review"].issues if i.severity == "polish"]
    ctx["status"] = ("PASS" if best["passed"] and not open_polish else
                     f"PASS_WITH_OPEN_POLISH ({len(open_polish)})" if best["passed"] else "NEEDS_HUMAN")
    if ctx.get("regression"):
        ctx["status"] += f" · REGRESSION_FAIL ({len(ctx['regression'])})"
    ctx["notes"] = checks.notes(best["script"], existing)
    (run_dir / "script.json").write_text(best["script"].model_dump_json(indent=2))
    requests = [seedance.render(best["script"], i) for i in range(len(best["script"].segments))]
    (run_dir / "seedance.json").write_text(json.dumps(requests, indent=2, ensure_ascii=False))
    write_final(ctx, run_dir, best["script"], requests)


def write_final(ctx: dict, run_dir: Path, sc: schemas.Script, requests: list[dict]) -> None:
    """One hand-off file for the generation pipeline: images to make, then the video requests that use them."""
    existing = {a["id"] for a in agent.existing_assets(ctx["exhibit_id"])}
    jobs = {j["id"]: j for j in ctx.get("image_jobs", []) if "endpoint" in j}
    used = [a for seg in sc.segments for a in seg.ref_assets]

    def ref(aid: str) -> str:
        return f"<existing:{aid}>" if aid in existing else f"<job:{aid}>" if aid in jobs else f"<missing:{aid}>"

    for r, seg in zip(requests, sc.segments):
        r["image_urls"] = [ref(a) for a in seg.ref_assets]
    needed = {a for a in used if a in jobs}
    final = {
        "exhibit_id": ctx["exhibit_id"], "status": ctx.get("status"), "title": sc.title, "duration_s": sc.duration_s,
        "photo": str(ctx["photo"]) if ctx.get("photo") else None,
        "keywords": [e for e in ctx.get("feed", []) if e.get("type") in ("keywords_batch", "highlight")],
        "image_jobs": [j for j in jobs.values() if j["id"] in needed],
        "existing_images_used": sorted({a for a in used if a in existing}),
        "missing_images": sorted({a for a in used if a not in existing and a not in jobs}),
        "video_requests": requests,
        "subtitles": [s.model_dump() for s in sc.subtitles],
        "voice": sc.voice, "music_style": sc.music_style,
        "est_usd": {"images": round(sum(j["est_usd"] for j in jobs.values() if j["id"] in needed), 2),
                    "video": round(sum(r["est_usd"] for r in requests), 2)},
    }
    (run_dir / "final.json").write_text(json.dumps(final, indent=2, ensure_ascii=False))


def cost(run_dir: Path) -> float:
    total = 0.0
    for meta in run_dir.glob("*/meta.json"):
        m = json.loads(meta.read_text())
        if not m.get("cached"):
            total += m.get("cost_usd") or 0
    return total


# ---------- report ----------

def render(ctx: dict, run_dir: Path) -> str:
    out: list[str] = []
    best = ctx.get("best")
    sc: schemas.Script | None = best["script"] if best else None
    shas = sorted({f"{json.loads(m.read_text())['prompt_file'].split('/')[-1]}@{json.loads(m.read_text())['prompt_sha']}"
                   for m in run_dir.glob("*/meta.json")})
    out += [f"# {sc.title if sc else ctx['exhibit_id']}", ""]
    if sc:
        out += [f"*{sc.logline}*", ""]
    out += [f"**Status: {ctx.get('status', 'ERROR')}**" + (f" · chosen attempt #{best['n']}" if best else ""), "",
            f"Run `{run_dir.name}` · exhibit `{ctx['exhibit_id']}` · photo `{ctx['photo'].name if ctx['photo'] else 'none'}` · "
            f"model `{agent.MODEL}` · new spend ${cost(run_dir):.2f}", "", f"Prompts: {', '.join(shas)}", "",
            f"User input: {agent.USER_INPUT or '(none)'}", ""]
    if ctx.get("error"):
        out += ["## Error", "", "```", ctx["error"], "```", ""]

    if ctx["attempts"]:
        out += ["## Attempts", "", "| # | checks | blocking | polish | truth | min score | sum | words |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for a in ctx["attempts"]:
            s = a["review"].scores.model_dump()
            out.append(f"| {a['n']}{' ✅' if best and a is best else ''} | {len(a['problems'])} | "
                       f"{sum(i.severity == 'blocking' for i in a['review'].issues)} | {sum(i.severity == 'polish' for i in a['review'].issues)} | "
                       f"{s['truth']} | {min(s.values())} | {sum(s.values())} | {checks.stats(a['script'])['spoken_words']} |")
        out.append("")

    if ctx.get("ident"):
        i = ctx["ident"]
        out += ["## S0 What the photo shows", "", f"- **Recognised as:** {i.recognized_as} → `{i.exhibit_id}` ({i.confidence})",
                f"- **Visible:** {i.what_is_visible}", f"- **Visitor interest:** {i.visitor_interest}", ""]

    if ctx.get("keywords"):
        out += ["## Progress keywords (separate side requests)", ""]
        for label, kw in ctx["keywords"].items():
            t = next((e["t_run"] for e in ctx.get("feed", []) if e.get("type") == "keywords_batch" and e.get("label") == label), None)
            out += [f"**{label}**" + (f" (at {t:.1f}s)" if t is not None else "") + ": " + " · ".join(f"{k['text']}" for k in kw["keywords"])]
            out += [f"- ⚠️ {f}" for f in kw["flags"]]
        out.append("")

    if ctx.get("research"):
        rs = ctx["research"]
        tools_file = run_dir / "00_s0b_research" / "tools.json"
        calls = json.loads(tools_file.read_text())["calls"] if tools_file.exists() else []
        out += ["## S0b Web research", "", f"{rs.queries_summary}", "", "Tool calls:"]
        out += [f"- {c['tool']}: `{json.dumps(c.get('input'), ensure_ascii=False)}`" for c in calls if c.get("tool")]
        out += ["", "Sources:"] + [f"- {'🏛 ' if x.official else ''}[{x.title}]({x.url}) — {x.publisher}" for x in rs.sources]
        out += ["", "Findings (verified URLs only):"] + [f"- ({f.about}) {f.text} — <{f.url}>" for f in rs.findings]
        if rs.conflicts:
            out += ["", "Conflicts:"] + [f"- {c}" for c in rs.conflicts]
        if rs.not_found:
            out += ["", "Not found:"] + [f"- {c}" for c in rs.not_found]
        out.append("")

    if (run_dir / "final.json").exists():
        fin = json.loads((run_dir / "final.json").read_text())
        out += ["## Final package (final.json)", "",
                f"- Image jobs (visitor photo + prompt): {len(fin['image_jobs'])} (~${fin['est_usd']['images']}): " + ", ".join(j["id"] for j in fin["image_jobs"]),
                f"- Existing images used: {', '.join(fin['existing_images_used']) or 'none'}",
                f"- Missing images: {', '.join(fin['missing_images']) or 'none'}",
                f"- Video requests: {len(fin['video_requests'])} (~${fin['est_usd']['video']}), image_urls: " + " | ".join(", ".join(r["image_urls"]) for r in fin["video_requests"]), ""]

    if ctx.get("regression"):
        out += ["## Regression failures", ""] + [f"- ✗ {r}" for r in ctx["regression"]] + [""]

    if ctx.get("sheet"):
        sh = ctx["sheet"]
        out += ["## S1 Material", "", f"**Emotional core:** {sh.emotional_core}", "",
                f"**Length:** {sh.duration_s}s — {sh.duration_reason}", "", "Facts:"]
        out += [f"- `{f.id}` ({f.about}) {f.text}" for f in sh.facts]
        out += ["", "Visitor questions:"] + [f"- {q.question} → {', '.join(q.answer_fact_ids) or '(pack cannot answer)'}" for q in sh.visitor_questions]
        if sh.conflicts:
            out += ["", "Conflicts:"] + [f"- {c}" for c in sh.conflicts]
        ci = sh.controlling_idea
        out += ["", f"**Controlling idea:** the visitor thinks *{ci.visitor_assumes}*, but actually *{ci.actually}* "
                f"[{', '.join(ci.actually_fact_ids)}] · second half: [{', '.join(ci.second_half_fact_ids) or 'none'}] · last thought: \"{ci.last_thought}\""]
        out += ["", "Through-lines:"]
        for n, t in enumerate(sh.through_lines):
            out += [f"- **{t.name}**{' ✅ lead' if n == sh.lead_line else ''} ({t.needs_s}s): {t.beginning} → *{t.turn}* → {t.end}",
                    f"  > spine ({checks.spoken_words(t.spine)} words): {t.spine}"]
        out.append("")

    if ctx.get("plan"):
        p = ctx["plan"]
        out += ["## S1b Reference-image plan", "", f"**Names:** {p.subject_name} / {p.living_form_name or '—'}", "",
                f"**Subject lock:** {p.subject_lock}", "",
                f"**Living form lock:** {p.living_form_lock or '—'}", ""]
        out += [f"- **{im.id}** ({im.kind}) — {im.purpose}\n  > {im.prompt}\n  > avoid: {im.must_avoid}" for im in p.images] + [""]

    if ctx.get("concepts"):
        cs = ctx["concepts"]
        out += ["## S2 Concepts", ""]
        for n, c in enumerate(cs.concepts):
            out += [f"### {n}. {c.name}{' ✅ chosen' if n == cs.chosen else ''} — {c.mode} / {c.engine}", f"- **Logline:** {c.logline}",
                    f"- **Hero:** {c.hero_mover} wants {c.want} · first sign: {c.first_sign} · big move: {c.big_move}",
                    f"- **Spectacle shot:** {c.spectacle_shot} · return trace: {c.return_trace}",
                    f"- **Hook:** {c.hook_visual} — \"{c.hook_line}\"", f"- **Arc:** {c.emotional_arc}",
                    f"- **Ending:** {c.ending_visual} — \"{c.ending_line}\"", f"- **Answers:** {c.answers_question}", ""]
        out += [f"**Why this one:** {cs.choice_reason}", ""]

    if sc:
        out += ["## S3 Script (chosen attempt)", "", "```", json.dumps(checks.stats(sc), indent=2), "```", "",
                f"- **Mode / hero:** {sc.mode} / {sc.hero_mover} (wants {sc.hero_want}); still: {sc.still_parts or '—'}",
                f"- **Look:** {sc.look} · style {sc.style} · narrator {sc.narrator_presence}", f"- **Voice:** {sc.voice}",
                f"- **Attitude:** {sc.narrator_attitude}", f"- **Music:** {sc.music_style}", f"- **Subject lock:** {sc.subject_lock}", ""]
        offset = 0.0
        for n, seg in enumerate(sc.segments, 1):
            out += [f"### Segment {n} ({seg.duration_s}s · {seg.setting} · refs: {', '.join(seg.ref_assets) or 'none'})", "",
                    "| t | refs | framing / camera | action | visual |", "| --- | --- | --- | --- | --- |"]
            out += [f"| {offset + s.t_start:.1f}–{offset + s.t_end:.1f} **{s.beat}** | {', '.join(s.refs)} | {s.transition_in} → {s.framing} / {s.camera} | {s.action}{(' ⟶ ' + s.transformation) if s.transformation else ''} | {s.visual} |" for s in seg.shots]
            out += ["", "Narration:"]
            out += [f"- `{offset + l.t_start:.1f}s` *{l.kind}* \"{l.text}\" {('[' + ', '.join(l.fact_ids) + ']') if l.fact_ids else ''}" for l in seg.narration]
            out += ["", f"Audio: {seg.audio.ambience}; sfx: {', '.join(seg.audio.sfx)}; music: {seg.audio.music}",
                    f"End frame: {seg.end_frame}", ""]
            offset += seg.duration_s
        out += ["### Assets", ""] + [f"- **{a.id}** ({a.source}, {a.view}) — {a.purpose}" + (f"\n  > {a.prompt}" if a.prompt else "") for a in sc.assets]
        out += ["", "## Seedance requests", ""]
        for n in range(len(sc.segments)):
            r = seedance.render(sc, n)
            out += [f"Segment {n + 1}: `{r['endpoint']}` · duration {r['duration']} · {r['resolution']} {r['aspect_ratio']} · "
                    f"refs {r['image_urls']} · {r['direction_words']} direction words {r['prompt_parts']} · {r['prompt_words']} total · ~${r['est_usd']}", "", "```", r["prompt"], "```", ""]

        rv: schemas.Review = best["review"]
        out += ["## S4 Review of chosen attempt", "", f"Fantasy legibility: **{rv.fantasy_legibility}**", "", "```", json.dumps(rv.scores.model_dump()), "```", "", rv.summary, "",
                "Claim audit:"]
        out += [f"- {'✅' if c.supported else '❌'} *{c.kind}* \"{c.line}\" — {c.claim} — {c.supporting_fact}" for c in rv.claims]
        out += ["", "Issues:"] + [f"- **{i.severity}** [{i.where}] {i.problem} → {i.fix}" for i in rv.issues] + [""]

        out += ["## Checks and production notes", ""]
        out += [f"- ❌ {p}" for p in best["problems"]] or ["- All hard checks pass on the chosen attempt."]
        out += [f"- 📝 {n}" for n in ctx.get("notes", [])]
        earlier = [e for e in ctx["log"] if e["problems"]]
        if earlier:
            out += ["", "Problems along the way:"] + [f"- {e['stage']}: {p}" for e in earlier for p in e["problems"]]

        if len(ctx["attempts"]) > 1:
            out += ["", "## Narration across attempts", ""]
            for a in ctx["attempts"]:
                out += [f"**#{a['n']}:** " + " / ".join(l.text for s in a["script"].segments for l in s.narration), ""]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("exhibit", nargs="?", default="", help="exhibit id, 'all', or omit and give --photo")
    ap.add_argument("--photo", type=Path)
    ap.add_argument("--no-photo", action="store_true")
    ap.add_argument("--fresh", default="", help="comma-separated stages to re-ask (s0,s1,s1b,s2,s3,s4 or all)")
    ap.add_argument("--variant", action="append", default=[], help="stage=name, e.g. s3=counter → prompts/s3_script.counter.md")
    ap.add_argument("--sample", type=int, default=0, help="independent draw number (part of the cache key)")
    ap.add_argument("--label", default="")
    ap.add_argument("--no-search", action="store_true", help="skip the web research stage")
    ap.add_argument("--no-pack", action="store_true", help="ignore every prepared pack: search is the only source")
    ap.add_argument("--user-input", default="", help='free text appended to every core stage as "User input: ...", e.g. "选15s"')
    args = ap.parse_args()

    agent.FRESH = {SHORT.get(s.strip(), s.strip()) for s in args.fresh.split(",") if s.strip()}
    agent.SAMPLE = args.sample
    global NO_SEARCH
    NO_SEARCH = args.no_search
    agent.USER_INPUT = args.user_input.strip()
    variants = {}
    for v in args.variant:
        stage, _, name = v.partition("=")
        if stage not in SHORT or not agent.prompt_file(SHORT[stage], name).exists():
            sys.exit(f"bad --variant {v}: need stage in {list(SHORT)} and prompts/{SHORT.get(stage, stage)}.{name}.md")
        variants[stage] = name

    if args.no_pack:
        test_photo = None
        if args.exhibit and args.exhibit != "all" and (agent.KNOWLEDGE / args.exhibit / "meta.json").exists():
            m = agent.meta(args.exhibit)
            test_photo = agent.HERE / m["test_photo"] if m.get("test_photo") else None
        agent.NO_PACK = True
        photo = args.photo or test_photo
        if not photo:
            sys.exit("--no-pack needs a photo (give --photo, or an exhibit whose meta.json has a test_photo)")
        run_one(None, photo, variants, args.label)
        return
    if not args.exhibit:
        if not args.photo:
            sys.exit("give an exhibit id or --photo")
        run_one(None, args.photo, variants, args.label)
        return

    ids = [e["id"] for e in agent.exhibits()] if args.exhibit == "all" else [args.exhibit]
    for exhibit_id in ids:
        if not (agent.KNOWLEDGE / exhibit_id / "pack.md").exists():
            sys.exit(f"no knowledge pack for '{exhibit_id}'")
        photo = None
        if not args.no_photo:
            photo = args.photo or (agent.HERE / agent.meta(exhibit_id)["test_photo"] if agent.meta(exhibit_id).get("test_photo") else None)
        run_one(exhibit_id, photo, variants, args.label)


if __name__ == "__main__":
    main()
