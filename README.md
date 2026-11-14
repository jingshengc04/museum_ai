# Living Exhibit

A museum visitor photographs an exhibit and gets back a short animated film, narrated by the exhibit itself.
Every fact in the narration comes from a listed source, and the sources light up on screen as they are spoken.

Background, decisions and tool notes are in [claude.md](claude.md). This file is how to run and extend the code.

## Run it

    uv sync                         # dependencies are listed in pyproject.toml
    uv run python -m museum serve   # http://127.0.0.1:8000  (add --host 0.0.0.0 to open it from a phone)

Needs `ffmpeg` and `ffprobe` on the PATH.

Out of the box everything is **mock and free**: the story comes from a hand-written storyboard, the voice is the
macOS `say` voice (silence elsewhere), and each shot is an animatic card showing its prompt and reference crops.
The whole flow works end to end, so the UI, timing, subtitles and edit can be built without spending credits.

    uv run python -m museum status                      # modes, prices, what material each exhibit has
    uv run python -m museum make --lang zh              # one film from the command line, into output/
    uv run python -m museum make --promote              # ...and keep it as the known-good demo
    uv run pytest                                       # 15 tests, no paid calls

## Going live

Copy `.env.example` to `.env`, add keys, and name the services that may make paid calls:

    LIVE=llm            # Claude writes and fact-checks the storyboard, and recognises the photo
    LIVE=llm,voice      # + ElevenLabs narration with word timings, and the sound bed
    LIVE=llm,voice,video   # + fal video. This is the one that costs real money.

A service is live only if it is in `LIVE` **and** its key is set; the badges in the top right of the UI show the
state. Turn them on one at a time, in that order.

Guards on fal spend:

- Every paid result is cached by a hash of its inputs (`cache/`), so re-running a film only pays for shots that changed.
- Default resolution is 360p ($0.10 per clip, about $0.90 for a nine-shot film). Change with `VIDEO_RESOLUTION`.
- A film estimated above `MAX_FAL_USD` (default $2) refuses to start. Raise it on purpose, after checking with the team.
- Tests force `LIVE` empty, so `pytest` can never spend anything.

### Not yet run with real keys

The fal, ElevenLabs and Claude calls are written against the current API references but have not been executed.
Expect small fixes on first contact. Things to watch:

- **fal** `fal-ai/vidu/q2/reference-to-video`: `duration` is sent as an integer; the reference is ambiguous about
  integer versus string. Whether the 360p to 720p price changes with duration is still unconfirmed.
- **ElevenLabs**: the with-timestamps reference does not list `eleven_v3`. If it is rejected, set
  `ELEVEN_MODEL=eleven_multilingual_v2` (emotion tags are then stripped automatically). The default voice is a
  premade one; put Hope's real voice ids in `exhibits/hope/exhibit.json` under `character.voice`.
- **Claude** (`claude-opus-5-5`): requests opt in to Anthropic's server-side fallback, so a request declined by a
  safety classifier is re-run on another model instead of failing.

## Where existing material goes

Everything lives in the exhibit's folder. Each slot is optional and is picked up on the next run, with no code change.

| Put this here | And it is used as |
| --- | --- |
| `exhibits/hope/photo.jpg` | the exhibit's sample photo in the UI, and the backdrop of mock cards |
| `exhibits/hope/refs/<name>.png` | character reference crops; a shot lists them by name in `refs` ([details](exhibits/hope/refs/README.md)) |
| `exhibits/hope/storyboards/<lang>-<style>.json` | a hand-written storyboard, used instead of the LLM |
| `exhibits/hope/overrides/shot_03.mp4` | a ready-made clip for shot 3, used instead of generating one ([details](exhibits/hope/overrides/README.md)) |
| `exhibits/hope/overrides/shot_03.mp3` | ready-made narration for shot 3 |
| `exhibits/hope/overrides/ambient.mp3` | the sound bed under the whole film |
| `exhibits/hope/demo/<lang>-<style>/` | the known-good film; written by `promote`, played if a live run fails |
| `exhibits/hope/exhibit.json` | facts with sources, character description, style suffix, voice ids, sound-bed prompt |

Cut the labelled model sheet into text-free crops with `python -m museum.sheet` (see the refs README).

To let Claude write a storyboard for a language and style that has a hand-written file, rename or remove that file.

A new exhibit is a new folder with an `exhibit.json`. With more than one exhibit and `LIVE=llm`, Claude picks the
exhibit from the visitor's photo.

## Facts

Narration may only state facts listed in `exhibit.json`, and only facts that have a `source` URL. A fact without a
source (currently "221 bones, diving lunge") is shown as left out and cannot be cited; add a URL to enable it.
A storyboard that cites an unknown or unsourced fact is rejected before anything is rendered. When Claude writes the
storyboard, a second pass checks every line against the facts and rewrites any line that goes beyond them.

## How a film is made

1. **Recognise** the exhibit from the photo.
2. **Write** the storyboard: 8 to 9 shots, each with one line of narration, a video prompt
   (`Action / Camera / Location / Mood` + the exhibit's style suffix), reference crops and the facts it states.
3. **Voice** every line first. Narration is the master timeline: its length decides how long each clip must be.
4. **Draw** one clip per shot (override, cache, fal, or mock card), in parallel within fal's concurrency limit.
5. **Cut**: each clip is trimmed, slowed by up to 25%, or frozen on its last frame to fill its slot; clips are
   cross-faded; narration and a looped sound bed are mixed underneath.

Subtitles are word-timed and drawn by the web player, not burned into the video (this ffmpeg build has no
`subtitles` or `drawtext` filter). `captions.vtt` is written next to each film for other players.

## Layout

    museum/config.py      settings, mock/live switch, prices
    museum/exhibits.py    exhibit folders and their drop-in slots
    museum/storyboard.py  storyboard schema, Claude writer + fact check, photo recognition
    museum/voice.py       narration, word timings, sound bed
    museum/video.py       shot planning, budget guard, fal render, mock cards
    museum/edit.py        ffmpeg: fit, cross-fade, mix
    museum/pipeline.py    the five steps, progress events, manifest, promote
    museum/server.py      FastAPI: jobs, server-sent events, static files
    museum/sheet.py       cut a model sheet into reference crops
    web/index.html        the whole front end
    output/, cache/       generated, not committed

## Not built yet

- Talking to the character after the film ("ask Hope a question").
- Checking rendered frames against the character sheet and re-rendering shots that drift.
- Seamless transitions with first+last-frame video models, and lip-sync for exhibits with faces.
- Fetching new sources with a search tool instead of only using the facts in `exhibit.json`.
