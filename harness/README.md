# harness: the core agent (read this first)

One photo of a museum exhibit in, one `final.json` out: everything the product needs to make a short film in which
the exhibit comes alive and introduces itself. This folder is isolated from the product code; the product only reads
the two output files described under "Interface".

Status as of 2026-11-15: the **lean pipeline (`lean.py`) is the one to use**. The older staged pipeline (`run.py`)
still works and writes the same output format, but takes about 12 minutes instead of 2 for the same quality of lines.

## Run it

```bash
cd harness
uv run python lean.py --photo photos/four_ram_zun.webp            # agent only: about 2 min, about $0.9 of Claude
uv run python generate.py runs/<run folder> --resolution 480p     # images + video on fal (costs fal credits)
```

- Keys: `harness/.env` holds `ANTHROPIC_API_KEY` and `FAL_KEY` (committed to this private repo at the owner's request;
  never print them, never copy them anywhere else).
- `--user-input "15s"` appends free text for the writer (a length or a wish).
- `uv run python smoke.py` checks prompts, schemas and imports offline, with no API calls.
- Every model call is cached by content hash under `runs/_cache`, so rerunning with the same photo and prompts is free.

## What the lean pipeline does

```
photo → ① see → ② search → ③ write (one call) → final.json → generate.py → 2 reference images → 1 video
              └ keywords ┘ └ keywords ┘
```

1. **See** (`prompts/s0_identify.md`, Claude vision): names the object and the museum, describes the photo's angle.
2. **Search** (`prompts/s0b_research.md`, Claude's built-in web search + fetch): finds sourced facts in four groups:
   what it is and how old; what it was for and what it meant; the big events in its history; where it is now.
   Every fact carries its URL and a verbatim quote; code drops any fact whose URL the tools never returned.
3. **Write** (`prompts/lean_write.md`, one call): the whole film in one pass.
   - Story: the exhibit introduces itself in the first person: who I am → what I was for → what happened to me →
     where I am now. A part with no fact is skipped, never invented. 30 s when three parts have facts, else 15 s.
   - Lines: plain everyday English, at most 12 words each, every factual line cites the facts that support it.
   - Picture: one hero comes alive as a stylized 3D character, the rest stays still, one continuous take written as
     timed beats, history shown as fantasy (no people, no text, no staged real events), ends on the photo's angle.
   - Sound: voiceover (no lip-sync), four or five sound effects, no music.
   - Code checks (`lean.check`), one rewrite if they fail: line count and length, citations, timing, contiguous
     beats, no people or text in the picture, request under 430 words. There is no reviewer model.
4. **Keywords** (`prompts/keywords.md`, `agent.keyword_batch(label, material, run_dir)`): a separate small request
   fired in the background after ① and after ②; returns any number of short keywords copied from the material,
   most important first (name, period, material and size, purpose or culture, where it is now). For the progress UI.

Fixed in code, not chosen by the model:

- **Reference images**: always two, built from templates in `lean.image_jobs`: `subject_now` (the object alone, as
  it is) and `hero_awake` (the character). The writer supplies only the object's name, the hero's name and one
  sentence of character design; the rest of each image prompt is fixed, including "no people, no reflections of
  people" (Seedance rejects references that may show a real person). Each job = visitor photo + prompt on
  `fal-ai/nano-banana-pro/edit`.
- **Video request**: assembled by `lean.seedance_prompt`: reference bindings (`@Image1`, `@Image2`) → "only the hero
  comes alive" → look → "One continuous take, no cuts." + timed beats → voiceover lines with times → sounds →
  "no subtitles, no people". Endpoint `bytedance/seedance-2.5/reference-to-video`, one generation of 15 or 30 s.

`PROMPTS.md` summarizes every prompt (in Chinese); the full texts are in `prompts/`.

## Interface (what the product reads)

Both files are written into the run folder, `runs/<stamp>-lean-<label>/`. The format is the same as the earlier
pushed examples; `lean.py` only adds three fields.

**`final.json`**

| Field | Meaning |
|---|---|
| `status` | `PASS` or `NEEDS_HUMAN` (code checks still failing; see `problems`) |
| `title`, `duration_s`, `photo`, `exhibit_id` | basics; `duration_s` is 15 or 30 |
| `image_jobs[]` | `id`, `kind`, `endpoint`, `input.image_urls` (`["<visitor_photo>"]`), `input.prompt`, `purpose`, `est_usd` |
| `video_requests[]` | `endpoint`, `image_urls` (`<job:id>` placeholders, in upload order), `duration` (string), `resolution`, `aspect_ratio`, `generate_audio`, `prompt`, `prompt_words`, `est_usd` |
| `subtitles[]` | `t_start`, `t_end`, `text` on the film's timeline (planned times, not measured from the audio) |
| `keywords[]` | the `keywords_batch` events: `label` (`identify` / `research`), `keywords[]` of `kind`, `text`, `basis` |
| `voice`, `music_style`, `est_usd` | voice description, `"no music"`, estimated image and video cost |
| `problems`, `lines`, `timing_s` | new in lean: open check problems; each line with its source facts and URLs; seconds per step |

To generate: replace `<visitor_photo>` with the uploaded photo URL, run the image jobs, replace each `<job:id>` in
`video_requests[].image_urls` with that job's image URL, then submit the video request. `generate.py` does exactly
this and is resumable (fal request ids are saved in `media/fal_state.json`; rerunning never pays twice).

**`events.jsonl`** (live progress, one JSON object per line, `t_run` = seconds since start):
`stage_start` / `stage_end` (stages `s0_identify`, `s0b_research`, `lean_write`, `kw_identify`, `kw_research`),
`search` (query text), `source` (URL), `fetch`, `thinking`, `writing`, `keywords_batch`.

Differences from the staged pipeline that a consumer may notice:

- A 30 s film is **one** video request with `duration: "30"` (Seedance 2.5), not two 15 s requests.
- Image job ids are always `subject_now` and `hero_awake`.
- There is no `image_jobs_ready` event; image jobs are known when `final.json` is written.

## Things learned the hard way

- Seedance moderation rejects reference images that may show real people, including a faint reflection of the
  photographer on a shiny object. `generate.py` treats that as fatal instead of retrying, and retries a rejected
  segment once without an in-place reference.
- A multi-shot prompt ("Shot 1, Shot 2…") makes Seedance cut and skip the moment the exhibit comes alive; "One
  continuous take" with timed beats does not.
- The review loop of the staged pipeline never passed a script in three real runs and added about ten minutes.
- Lines must be plain spoken English about what matters (age, purpose, culture, big events, where it is now);
  earlier prompts produced riddles and trivia.

## Files

- `lean.py`: the lean pipeline. `run.py`: the staged pipeline (kept for comparison). `generate.py`: fal generation.
- `agent.py`: Claude calls, caching, search tools, keyword function. `checks.py`, `schemas.py`, `seedance.py`,
  `images.py`, `timing.py`: used by the staged pipeline; `lean.py` reuses the research check and image constants.
- `prompts/`: current prompts; `prompts/archive/`: every earlier version. `CHANGELOG.md`: what changed and why.
- `examples/`: real outputs. `four_ram_zun_lean/` is a lean run (agent output only);
  `four_ram_zun_demo_seedance25_720p/` is the best film so far (hand-written script, same request format).
- `explainer/`: the harness explainer segment for the demo video (`harness_explainer_v3.mp4`, 32 s) and its source.
