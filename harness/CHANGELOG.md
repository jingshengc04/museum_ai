# Prompt & harness changelog

Each entry: what changed, the hypothesis, the run(s) that test it, the verdict.

## v0 — baseline (2026-11-14)

- First version of all five stage prompts (`prompts/s0..s4`), schemas, hard checks, runner.
- Run `runs/1114-170409-hope-v0` (Hope, no photo): 11 facts → 30 s; concept "Not Even Grown" (huge, yet only a juvenile);
  S4 said revise once, then pass (hook 4, visitor_view 4, focus 4, truth 5, feasibility 4, length 4, ending 4). New spend $0.47.
- Problems seen by reading the output:
  - Reviewer can return `pass` while still listing fixes; the loop stops and those fixes are never applied.
  - Concept 1's hook puts "£250" on screen as text; nothing in S2 or the checks stops on-screen text in concepts.
  - A line ("Out there, I was blue, not bone") cites `juvenile_female`, which it does not state.
  - "Not finished growing" is an inference from "juvenile": borderline under the no-invention rule.
  - The S3 prompt guesses at Seedance prompt syntax; not yet grounded in the real model.

## Round 1 workflow (2026-11-14)

9 agents: Seedance/fal research from official docs and from practitioners, cross-checked claim by claim; four
independent critics of the v0 run (screenwriter, museum educator, video-feasibility engineer, harness engineer);
two new verified test packs (sophie, sequoia). Full output: `research/round1_raw.json`.

All four critics independently named the same top problem: S3 revisions never saw the draft they were revising.

## v1 — multimodal agent + critic consensus (2026-11-14)

Harness:
- Photo and existing reference images are sent to every stage, not only S0 (user direction: rely on multimodal ability).
- S0 recognises the object freely first, then matches a pack.
- New S1b stage plans reference images (restoration, character sheet, clean current view, detail) and the two
  canonical locks, following the ChatGPT flow the user shared. Hope's real sheets/restoration are registered in
  `knowledge/hope/assets/assets.json` (with `has_text_labels`).
- S3 revisions edit the previous script; S4 sees the concept, the raw pack, the rendered Seedance requests, the
  photo and its previous review; issues are blocking/polish; pass/fail is computed in code; best attempt is kept;
  status PASS / PASS_WITH_OPEN_POLISH / NEEDS_HUMAN.
- `seedance.py` renders each segment into the fal request; shown in the report and given to the reviewer.
- Checks: spoken-word counting (years = 3 words), per-line timing, head/tail silence, text-on-screen in concepts
  and assets, multi-move cameras, short shots, line kinds vs fact ids, numbers vs cited facts, refs per segment,
  forbidden strings per exhibit (`expect.json`), request length, mixed subject states in one shot.
- Cache key includes image hashes, prompt sha and a `--sample` number; errors leave error.json and raw.txt.

Prompts: all rewritten (v0 kept in `prompts/archive/v0/`): claim kinds, counterpoint, writing for the ear,
concept-as-brief, no morals, voice casting, cut design, Seedance craft limits, review audit-first with anchors.

Runs:
- `1114-172400-hope-v1`: S0 recognised Hope from the photo alone. Concept "Still Growing" (direct address + reveal,
  built on the visitor stepping back to fit her in frame). Truth 5 all attempts. NEEDS_HUMAN: one blocking issue
  survived 3 attempts. Cause was **the renderer**, not the writer: it declared every reference "one single subject:
  skeleton" even for the living-whale image (invites a fleshy skeleton / morph). Fixed in seedance.py v1.1.
- `1114-173051-hope-v1.1`: renderer still pasted the full lock for every reference and described the skull detail
  as the whole skeleton (invites a duplicate). Reviewer pinpointed it; fixed (v1.2 binding: one description per
  subject, extra views/details bound to it). Requests still 265-341 words vs 250 cap: writer verbosity, next round.
- Lesson: when the same blocking issue survives every revision, suspect the template/harness, not the writer.

## v1.2 on three exhibits (2026-11-14)

- `1114-173547-hope-v1.2` "Young Giant", `1114-173549-sophie-v1.2` "Almost Whole", `1114-173551-sequoia-v1.2`
  "Under the Dust". All NEEDS_HUMAN but converging (truth reaches 5 in every run). $3.41 total.
- sequoia chose 30 s (expected 15): S1 split 5 pack sections into 16 "facts" and judged richness by count.

## Round 2 workflow (2026-11-14)

8 agents: four diagnosticians (loop, length, craft, renderability) over all v1.2 runs; three blind judges
(director, first-time visitor, museum educator) comparing the v0 and v1.2 Hope scripts with labels hidden and
order swapped; one synthesiser. Output: `research/round2/`.

- **Blind verdict: v1 beat v0 3-0** (medium confidence). v1 wins hook, one idea, truth, spoken quality, ending.
  v0 broke truth ("not finished growing", a "lone" whale, a motionless body implying death, invented stained glass).
- **v1 still loses on counterpoint (3/3 judges)**: "From jaw to tail, I measure…" narrates a jaw-to-tail drift.
  Also thinner visuals (2/3), never says the name Hope or the Wexford origin (1/3), a filler pivot line.
- Main cause of NEEDS_HUMAN everywhere: the request template (about 186 fixed words of a 250 cap), not the writer.

## v1.3 (2026-11-14)

Adopted (synthesis items): short-name reference binding with roles (#1); cap counts direction words only, 230,
quoted narration excluded, with per-part breakdown shown to the writer on revision (#2); one clause per shot,
action and visual never repeat (#3); polish feedback only after blockers clear, S4 checks its own replacement
lines (#4); character sheets never go to Seedance, single-view `_side`, per-state and in-place images (#6);
negation regex fix (#9); film-level `music_style`, no default cello, end frame rendered (#10); regression failures
reported in the status but never fed back (#12); MIN_SHOT 3.0 s, tail tolerance 0.15 s, constraint wording (#14).

Adopted directly rather than A/B (deviation from the synthesis): S1 rewrite where length follows the lead
through-line's spoken spine, facts tagged exhibit/context, visitor questions with answer ids (#7), plus the S2
lines that tie a 30 s concept to the lead turn and rank the first visitor question (#8). Reason: it changes the S1
schema, so it cannot be a same-schema A/B, and it targets a measured failure (S1 chose 30 s in 6 of 6 runs);
the regression set is its test (sequoia must become 15 s; hope and sophie stay 30 s).

A/B arms (same baseline, one change each): `--variant s3=counter` (#5 picture and words as two tracks, one collision
per segment, at least one attitude line) and `--variant s2=endings --variant s3=endings` (#11 last line is a
thought not an instruction, at most one announcer line, keep concept lines verbatim).

Deferred: per-shot narration placement (#13) and voice chaining via @Audio1 (#16) need rendered video to judge;
concept-owned duration (#15) waits until #7 settles.

## v1.3 baseline + A/B arms (2026-11-14)

- Baseline: sequoia now 15 s and the first PASS (PASS_WITH_OPEN_POLISH); sophie had zero check/blocking problems but
  craft scores of 3; hope drifted into a multi-stop journey (focus 3 at first).
- Arms: `counter` (two tracks, one collision per segment) and `endings` (last line is a thought, verbatim concept lines).

## Progress keywords (2026-11-14, user request)

Every stage's first output field is `highlights` (2-6 keywords: name, period/dynasty, date, place, person, material,
measure, species, theme, visual, decision, check). Streamed: each keyword is emitted the moment its JSON object is
complete, written to `runs/<run>/events.jsonl`, replayed with original timings on cache hits, shown with a Replay
button in transcript.html. Rule in `prompts/_highlights.md` (appended to every system prompt); truth-checked by
`checks.highlights`. Live test on S0: four keywords at 4.9-5.4 s, stage ended at 10.0 s.

## Round 3 workflow: blind four-way ranking (2026-11-14)

Two judges per exhibit (director, museum educator), letters shuffled, judges read one anonymised file each.
Borda: v1.2 16, v1.3 16, counter 16, endings 12. Output: `research/round3/`.
- Director prefers v1.2's single idea with a turn; educator prefers v1.3's coverage and sourcing, and shows v1.2's
  drama partly rests on unsourced inference ("she would have grown bigger", "you had to step back").
- v1.3's through-line length rule regressed hope and sophie: a chronology always justifies another stop.
- endings rejected (never first; its new hook "25.2 m… across this whole hall" is false).
- counter is a narrow real gain, but its picture track drifted from the pack (visitors walking under Sophie's low plinth).
- Common weakness in 5 of 6 winners: place words ("here", "this", "what you see", "had to") without a pack link.

## v1.4 (2026-11-14)

- S1: a controlling idea is required before length: "the visitor thinks X, but actually Y", Y stated by an exhibit
  fact (no inference), plus the last thought. 15 s is the default; 30 s only if a second segment adds a new exhibit fact
  that advances the turn (`second_half_fact_ids`, checked in code).
- S2: all three concepts deliver the controlling idea through different engines; no stops added to fill time.
- S3: counterpoint adopted in narrowed form; the picture track must match how the pack and photo say the exhibit is
  displayed; place words need a pack sentence or the photo; never state why the visitor did something.
- S4: audits place words and display fidelity.
- expect.json: hope and sophie length no longer pinned (15 s default now); sequoia stays 15 s.
- The A/B variant files moved to `prompts/archive/v1.3/`.

v1.4 runs ($4.11): `1114-181730-hope-v1.4` 15 s "From Up There" (idea: thinks fully grown giant, actually a juvenile
female; NEEDS_HUMAN on counterpoint/length 3), `1114-181731-sophie-v1.4` 15 s "Found Whole" (PASS_WITH_OPEN_POLISH;
the polish round made it worse and best-attempt selection shipped the passing draft), `1114-181734-sequoia-v1.4`
30 s, REGRESSION_FAIL: the "second half adds a new exhibit fact" rule is too easy to satisfy (conservation facts).
Keywords: 46-49 per run. Next: tighten the 30 s rule; consider skipping polish rounds that touch timing/word budget.

## v1.5 — the user's flow: identify → search → keywords → images in parallel → script → final package (2026-11-14)

Fixes found while exporting the Hope v1.4 example:
- checks: the negation rule only recognised "no" directly before "text", so "No hall, cables, people, text…" was read as a
  request for text. It cost a revision and made the writer delete the protective "no text" lists. Now anything after
  no/not/without/avoid/free of/never/remove… to the clause end is ignored. Tested on the real failing prompts.
- timing.py: lines move up to 1 s automatically to meet the opening, overlap and tail rules, subtitles follow; applied
  before checks. On the v1.4 draft 3 that lost (first line at 0.3 s) every hard check now passes.
- checks: glued/stray text ("juvenile.of course") in S1 fields and narration.

New:
- S0b research stage: Claude's web_search + web_fetch server tools (5 searches, 4 fetches capped at 6,000 tokens),
  pause_turn continuation, every query/result logged to tools.json, live "search"/"source" events. Output: sources,
  findings with URLs, agreements with the pack, conflicts, not found, and 5-10 keywords sent at once
  (`keywords_batch`). checks.research rejects any source or finding URL the tools did not actually return;
  unverifiable findings are dropped before S1.
- S1 may cite the pack or a verified finding; numbers must appear in one of them. A banned phrase (expect.json) is
  allowed when a verified finding now states it (e.g. a bone count the pack marked unsourced).
- images.py: S1b plan → fal image jobs in two waves (nano-banana-pro/edit from the photo; qwen multiple-angles or
  sheet crops from wave 1); `image_jobs.json` and an `image_jobs_ready` event right after S1b so generation runs in
  parallel with S2-S4.
- final.json: the hand-off: image jobs actually needed, Seedance requests with `<job:id>`/`<existing:id>` image refs,
  subtitles, voice, music, estimated cost.

Live test of S0b on Hope (`runs/_smoke_s0b`): 3 searches, 18 URLs returned, 7 sources, 21 findings, all verified.
Found the NHM "secret history" page (Ned Wickham, royal fish law, about 15 years old, baleen suggesting pregnancy),
and flagged that "not yet fully grown" is safer than "juvenile". 250k input tokens / $1.17 before the fetch cap.
- (user direction) Image jobs simplified: each reference image is the visitor photo as the initial image plus the S1b text
  prompt (view, angle and must-avoid included); one endpoint (`IMAGE_ENDPOINT`, default nano-banana-pro/edit), no waves,
  no angle-model routing.
- (user direction) Image-generation configuration lives in code, not in the LLM: initial image is always the visitor
  photo (text-to-image when there is none), endpoint and price are constants in images.py. S1b writes only prompts;
  a sheet's single side view is generated from the photo by its own prompt. (An `input_image` field chosen by the LLM
  was tried and removed.) v1.5 runs' image_jobs.json/final.json regenerated offline in this format.

v1.5 runs ($8.04): hope 30 s NEEDS_HUMAN, sophie 30 s PASS_WITH_OPEN_POLISH (hook 5: "you assume it's a cast; it's the
real thing"), sequoia 30 s NEEDS_HUMAN + REGRESSION_FAIL. Search: 1-3 searches, 21-24 verified findings per exhibit.
New problem: search adds 30-41 facts and every exhibit now picks 30 s; the second-half rule is too easy to satisfy.

## Round 4 workflow: fact verification of v1.5 (2026-11-14)

6 skeptics opened every cited page (narration fact lines, web-sourced facts, URL-backed keywords) + 1 report.
65 items: 53 supported, 8 partly, 1 unsupported, 3 unreachable. No hard factual errors; all problems are overreach or
citations that do not hold. Output: `research/round4/`.
- Biggest: **our own pack** said "juvenile female" (copied from claude.md); neither cited NHM page says "juvenile"; they
  say "wasn't yet fully grown", about 15 years old, may already have had a calf.
- Keywords (4): cited to the wrong page ("Mark Twain Tree"), to a tweet ("felled in 1891"), or trimmed so the meaning
  changed ("Swantons Bank, Wexford Harbour" for "at the mouth of").
- Research (4): pages that cannot be fetched (403), dropped hedges ("about 94 m"), strengthened verbs ("proposed").
- Script (3): "This is bone" for "the real thing"; "one animal" inferred; two facts merged into one line.

## v1.6 — simplify: keywords as a side request; quotes in research (2026-11-14, user direction)

- Keywords removed from every core stage (no highlights field, no shared keyword appendix, no streaming parser).
  New side request `keyword_batch` (prompts/keywords.md, effort low, `KEYWORD_MODEL` overridable) fires in a background
  thread after S0 and after S0b; outputs 5-10 keywords at once; `checks.keywords` requires every word to be copied from
  the material it was given. The core agent only writes the script and prompts.
- Research findings carry a verbatim quote; numbers must be in the quote; social-media URLs rejected; qualifiers kept.
- Hope pack corrected ("juvenile" → "wasn't yet fully grown", with a note); "juvenile" banned in expect.json.
- (user direction) Length is free: 30 s is fine. Removed the two length checks and the sequoia 15 s expectation.
  New `--user-input "…"` (e.g. "选15s"): appended as "User input: …" to S1-S4 (not S0, S0b research or
  keywords); S1 uses it for length, S2/S3 follow it within the truth rules. Part of the cache key.

v1.6 runs: sophie 30 s NEEDS_HUMAN (counterpoint 3; quotes rule dropped 2 findings whose year was not in the quote),
sequoia 30 s NEEDS_HUMAN (quote rule dropped a finding; length expectation was still active in that run's code).
Keywords arrived from the side request at 88-90 s. hope crashed at start: deleting the old keyword parser also removed
the MEDIA table (only photo runs need it). Fixed; added `smoke.py`, an offline check that builds every stage's input
and schema (run it before spending tokens).
- Hope v1.6 crashed twice at S2 with ReadTimeout (API stream stalled). Added retries (2, backoff 10/20 s) for timeouts,
  connection errors, 429/5xx/529; emitted as `retry` events. Fired once in the rerun and recovered.
- User-input test (same photo, cached S0-S0b): no input → 15 s "All of Me in One Picture", PASS_WITH_OPEN_POLISH;
  `--user-input "选30s"` → 30 s "The Giant That Wasn't Finished", PASS_WITH_OPEN_POLISH. ("选15s" cannot show a
  difference because 15 s is S1's default; its line was confirmed present in S1-S4 inputs.)

## v1.7 — search-only mode (2026-11-14, user request)

- Any photo can start a run (`run.py --photo X`). S0 now gives `short_name` and `museum`. If the object matches a
  prepared exhibit, its pack is used; if it is recognised but has no pack, an ad-hoc exhibit is registered from S0
  (`agent.register_adhoc`) and the pack is replaced by an explicit "no pack: research findings are the only source";
  if S0's confidence is low, the run stops instead of telling the wrong story. `--no-pack` hides all prepared packs.
- Two launch failures from my wiring (an indentation error, then a variable used before definition), both caught at
  start with nothing spent. smoke.py now imports run.py and view.py; all CLI paths and the ad-hoc branch were
  dry-run offline before the live run.
- Live search-only run (`1114-195759-photo-nopack-v1.7`, Hope photo, no pack): recognised Hope; 4 searches, 13 verified
  findings; new idea from search: "you'd guess I was ancient; I'm thought to have been around fifteen when I died"
  (quoted NHM page). 15 s, truth 5 throughout, NEEDS_HUMAN on craft. $2.40.
- S0 on a niche object (Four-Ram Square Zun, user photo `photos/four_ram_zun.webp`): recognised with the label
  (form + label) and with the label cropped off (form alone; it hedged to "almost certainly" / "likely National
  Museum of China"). $0.03 each.

## First end-to-end film (2026-11-14): Four-Ram Square Zun, 480p

- `generate.py`: final.json → fal (upload photo; nano-banana-pro/edit per image job, parallel) → Seedance 2.0
  reference-to-video at 480p with audio → join segments → English subtitles burned in (Pillow PNG overlays, since this
  ffmpeg has no subtitle/drawtext filter) plus a soft mov_text track and film.srt → media/generation.json.
- Run `1114-200829-photo-e2e` (user photo, no pack, search only): S0 recognised the zun; 4 searches, 7 verified findings;
  idea "looks untouched; actually destroyed by bombs during the war"; 15 s "You Framed My Rams".
- Film `runs/1114-200829-photo-e2e/media/film.mp4`: 864x496, 15.1 s, video+audio+subtitles. Reference images faithful
  (correct form, no labels/people); video consistent, no duplicates or morphing; final shot matches the gallery view.
  Audio level pattern matches the three narration lines (words not verified by ear).
- Timing (media/timing.md): agent 441.6 s ($2.08 Claude), images 24 s, Seedance 470 s, total about 15.7 min, about
  $4.6 ($2.55 fal). Seedance is half the wall time; image jobs are ready at 199 s, long before the script.
- Content issue: the last line "During the war, bombs destroyed me" is sourced (China Daily) but the film never says the
  vessel was restored, because the museum page that explains the restoration failed the quote check and was dropped
  ("34.5" was not in its quote). Over a shot of the intact zun, it reads as a contradiction.

## v2.0 — re-centre the harness: "make the exhibit act" (2026-11-14, user direction)

The first film (zun, 480p) was technically clean but static. The user: the point is to bring the artifact alive with
Seedance's freedom, e.g. Hope cartoonized and talking on screen. The rigidity was designed in: the harness was
centred on avoiding mistakes ("the exhibit never moves or transforms", one slow camera move, no morphing, word caps,
a reviewer with nothing that rewards aliveness).

Round 6 workflow (5 agents: Seedance motion research, three directors for "awaken", "world returns", "character",
synthesis; `research/round6/`). New centre:
- Truth is split: SAID stays strict (spoken facts sourced); SHOWN is free but must read as fantasy, never staged as a
  documentary record of a real event, no identifiable people, no unsourced places or dates.
- Modes: character (DEFAULT, per user: stylized animated character with a face, speaking short lines on screen),
  awaken (one part wakes in place), world_returns (the object holds still while its world moves).
- Every 15 s: still -> stir -> act -> return; one hero; one high-amplitude beat with speed/force words; return to the
  real exhibit at the visitor's angle with one trace of life.
- Renderability = only Seedance's real failure modes (several movers, stacked moves, >1 transformation per shot,
  instruction overflow, unbound/conflicting references, text, long lip-synced lines).

Changes: schemas (Concept/Script mode, hero, want, big_move, return_trace, spectacle_shot, look, still_parts; ShotSpec
beat, transition_in, transformation; new Scores incl. aliveness/spectacle/return_shot; Review.fantasy_legibility),
S1b (identity anchor, in-place view, single-view character "_awake", optional turnaround/keyframe/world plates; no
restorations, no labelled sheets), S2 (modes, engines A-H, choose by aliveness), S3 (rewritten), S4 (new rubric),
seedance.py v2 (one job per reference, lock line instead of "no morphing", timecoded shots with transitions,
transformation phrasing, on-screen speech, no "documentary"), checks (removed the motion vetoes; added one act beat
with a force word, still/return beats, camera-move count, one transformation per shot, min transform time, short
lines, no speech over the act, three sounds, return shot shows the real object, record/adjective filters), pass gate
(aliveness/spectacle/return >= 4, fantasy pass, truth 5, rest >= 3).
- generate.py made resumable (user asked about network drops): each fal job is submitted once and its request id is
  saved in media/fal_state.json; on a network error it keeps polling that same job instead of resubmitting (which
  would pay twice); uploads and finished results are cached there too; downloads skip finished files. Rerunning
  `generate.py runs/<run>` after a crash resumes. Agent stages were already resumable through the cache.

## v2.1: first "alive" films, moderation, voiceover default (2026-11-14 evening)

- Hope, character mode, 30 s at 480p (`examples/hope_alive_480p`): the skeleton turns into a cartoon whale, swims the
  hall, talks to camera, dives back into the bones. The exhibit clearly acts now. Agent S3/S4 7.3 min ($1.65),
  generation 410 s (~$4.65).
- Four-Ram Zun from the photo, search only, 15 s at 480p (`examples/four_ram_zun_alive_480p`): the front ram wakes,
  jumps onto the plinth, flings its horns off glowing and catches them back; the vessel returns whole. Agent 516 s
  ($2.32), generation 407 s (~$2.55). Weak spot: the cut skips the ram pulling free of the vessel.
- Seedance (fal partner moderation) rejects any reference that may show a real person:
  `content_policy_violation / partner_validation_failed`. Hit twice: visitors in Hintze Hall, and the photographer's
  faint reflection on the bronze. Fixes: every image prompt ends with a hard-coded no-people rule (incl. reflections
  and silhouettes); S1b's in-place view and S3 keep people out of frame; the request builder adds "No people in frame";
  generate.py treats moderation/4xx as fatal (it used to wait forever thinking it was a network error), uses 60 s
  HTTP timeouts, and on a moderation rejection retries the segment once without the in-place reference (tags renumbered).
- Lines default to voiceover; on-screen talking only when a mouth suits the character (user: talking is not required;
  a bronze ram acts with its body).
- Direction-word cap 240 → 300 (S3 budget 280): the Hope film followed a ~300-word request well; 240 only kept the
  review loop failing. Both runs still ended NEEDS_HUMAN on this check after three drafts (336–353 words).

## v2.2: plain English, culture over trivia, one continuous take (2026-11-15)

User feedback on the zun script: lines were odd and hard to follow ("Find the join; it's hard to see"), the story
dwelt on trivia (400 silver dollars, a chip knocked off the rim) instead of culture, it had no ending, and in-clip cuts
skipped the moment the ram broke free. Changes (v2.1 prompts archived in prompts/archive/v2.1):
- S1: a "what matters" rule (identity, age, purpose, meaning, remarkable craft, big turns, where it is now; trivia
  left out); default through-line shape who I am → what I was for → what happened → where I am now, which must end;
  the controlling idea must be about significance, not a puzzle.
- S2: plain self-introductions allowed; lines told in story order with an ending, in plain everyday English;
  voiceover default.
- S3: each 15 s segment is one continuous take (beats with transition "continuous", never cut away from a
  transformation); lines rule rewritten for plain spoken English and importance; "collision" removed.
- S4: voice_fit now scores naturalness, importance and an ending; a cut inside a segment counts as a render fault;
  cap text 300.
- seedance.py: a one-take segment is written "One continuous take, no cuts." with timed beats instead of "Shot n".
