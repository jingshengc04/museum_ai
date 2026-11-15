# Museum Alive

A museum visitor photographs an exhibit and gets back a short film with sound, narrated by the exhibit itself.
Every fact in the narration comes from a listed source, and the sources can be opened under the film.

Background, decisions and tool notes are in [claude.md](claude.md). This file is how to run and extend the code.

## Run it

    uv sync                                      # dependencies are listed in pyproject.toml
    uv run python -m museum serve --port 8001    # http://127.0.0.1:8001  (add --host 0.0.0.0 to open it from a phone)

Needs `ffmpeg` and `ffprobe` on the PATH.

Out of the box everything is **mock and free**: the story comes from a hand-written storyboard and each scene is an
animatic card that shows its prompt, with the macOS `say` voice standing in for the model's voice (silence
elsewhere). The whole flow works end to end, so the UI, timing and edit can be built without spending credits.

    uv run python -m museum status     # modes, prices, what material each exhibit has
    uv run python -m museum check      # test every API key and endpoint with free calls that spend nothing
    uv run python -m museum make       # one film from the command line, into output/
    uv run pytest                      # no paid calls

## Going live

Copy `.env.example` to `.env`, add keys, and name the services that may make paid calls:

    LIVE=llm          # the script agent (harness/) researches the exhibit and writes the film; Claude recognises the photo
    LIVE=video        # fal renders the scenes, with sound. This is the one that costs real money.
    LIVE=llm,video    # both

A service is live only if it is in `LIVE` **and** its key is set.

### Script: the agent in `harness/`

With `LIVE=llm` the script comes from the script agent in `harness/` (maintained separately, see
`harness/README.md`; nothing in `harness/` is edited by this code, so its branch merges cleanly). The bridge is
`museum/script_agent.py`: it runs the agent as its own process, reads its progress from
`runs/<run>/events.jsonl`, and takes its hand-off `final.json`. Which agent pipeline runs is `AGENT_PIPELINE`:

- `lean` (default): `harness/lean.py`, the one the harness README recommends. See, search, then one writing call;
  about 2 minutes. Its film is **one 30 s take on Seedance 2.5** (`bytedance/seedance-2.5/reference-to-video`),
  filmed at `AGENT_VIDEO_RESOLUTION` (480p by default, about $6.60; 720p about $14.20). Its facts are the ones its
  lines cite (`final.json` `lines[].sources`). It works from a photo only: a prepared exhibit uses its own `photo.jpg`.
- `staged`: `harness/run.py`, research, drafts and review; about 12 minutes. Two 15 s scenes on our `VIDEO_MODEL`.

Then this pipeline:

1. makes the agent's reference images from the visitor's photo (`IMAGE_MODEL`, about $0.15 each, cached by their inputs),
2. sends the agent's Seedance prompts, word for word, to fal (cached by their inputs): the endpoint and resolution
   the agent asked for when we know its price (Seedance 2.5), otherwise our `VIDEO_MODEL` at our resolution,
3. joins the scenes with a short cut, and places the agent's timed subtitles on the film,
4. shows the facts the agent worked from, each with its source, under the film.

If Seedance refuses a scene's reference pictures (`content_policy_violation`: it treats close-ups of statues of people
as real people), the scene is sent again with only the wide and scenery pictures (`in_place`, `world_plate`), then with
the prompt alone. Refused requests are not billed. A film that still fails shows the visitor a plain sentence; the
service's own message goes to the server log.

While the agent works, the waiting screen shows its stages and the keywords it picks out of its sources.

- **Time**: lean writes a film in about 2 minutes, staged in about 12; Seedance then takes several minutes.
  A live demo should play films already in the library.
- **Cost**: about $0.90 (lean) or $1.20-2.60 (staged) of Claude per new script, plus pictures and video. If
  `MAX_FAL_USD` is set, the check before generation counts pictures and video (not the Claude part, spent by then).
- **Review**: there is no human review in this first version. A script that does not pass the agent's own review
  (`NEEDS_HUMAN`, about two runs in three so far) is filmed and saved to the library like any other; its status is
  kept in the film's `manifest.json` under `agent.status`, so such films can be found and re-made later.
- **Exhibits**: an exhibit with a pack in `harness/knowledge/` but no folder in `exhibits/` is still recognised from
  photos; its films are kept in `exhibits/<id>/demo/`. An object with no pack at all is researched from scratch;
  it is kept as a new exhibit (`exhibits/adhoc-<name>/`, with the photo and the sourced facts) and its film goes
  into the library, so a later photo of it plays that film.
- Turn the agent off with `SCRIPT_AGENT=builtin` to use `storyboard.py` instead. Without `LIVE=llm` the
  hand-written storyboards are used, as before.

### Video and sound: Seedance 2.0 Fast on fal

`bytedance/seedance-2.0/fast/reference-to-video` makes each scene **with its own sound**: the narration is written
into the prompt and the model speaks it, with ambience. A film is two 15-second scenes, cross-faded.

- **Cost**: fal bills by the second, about $0.24 at 720p and $0.11 at 480p. One film (2 x 15 s) is about
  **$7.30 at 720p** or $3.20 at 480p. Set `VIDEO_RESOLUTION=480p` while tuning prompts.
- **Budget guard**: off by default. Set `MAX_FAL_USD` and a film estimated above it refuses to start.
- **Cache**: every paid clip is cached by a hash of its inputs (`cache/`), so re-running only pays for what changed.
- **Film library**: a finished film is reused for later visitors of the same exhibit (see below), so repeat
  visitors cost nothing: no agent run, no pictures, no video.
- References sent with each scene: the visitor's own photo (when there is one) and the exhibit's character crops.
  Seedance works without any reference image, so missing crops do not block a render.

Not yet run with a real key. Things to watch on the first live film:

- **The model speaks the words, we cannot check them.** If it mispronounces or changes a date or number, the film
  states something the sources do not. Nothing checks this automatically yet.
- **Subtitles are estimated.** The model does not report when each word is spoken, so subtitle lines are spread
  over the scene by their length. They can drift from the voice.
- **Two scenes, two takes of the voice.** The voice is described in the prompt (`character.voice_description` in
  `exhibit.json`), but the two scenes may still sound slightly different.

### ElevenLabs and Vidu (not used now)

The earlier path is still in the code: with a silent video model (`VIDEO_MODEL=fal-ai/vidu/q2/reference-to-video`)
the narration is recorded first with ElevenLabs (`LIVE=voice`), with word timings, and every clip is fitted to its
line. The current two-scene storyboards are written for Seedance and are too long per shot for that path.

## The photo scan

When a visitor takes or uploads a photo, the page outlines the exhibit in it and a beam sweeps down to uncover the
outline. The outline comes from U2-Net segmentation run locally with onnxruntime (`museum/outline.py`, about 0.2 s on
a laptop CPU, no API, no cost). The model file `u2netp.onnx` (4.6 MB) is downloaded once into `cache/models/`.
If nothing stands out in the photo, or the model fails, the scan runs without an outline.

## Where existing material goes

Everything lives in the exhibit's folder. Each slot is optional and is picked up on the next run, with no code change.

| Put this here | And it is used as |
| --- | --- |
| `exhibits/hope/photo.jpg` | the exhibit's picture on the first screen, and the backdrop of mock cards |
| `exhibits/hope/refs/<name>.png` | character reference crops; a scene lists them by name in `refs` ([details](exhibits/hope/refs/README.md)) |
| `exhibits/hope/storyboards/<lang>-<style>.json` | a hand-written storyboard, used instead of the LLM |
| `exhibits/hope/overrides/shot_02.mp4` | a ready-made clip for scene 2, with its sound, used instead of generating one |
| `exhibits/hope/demo/<lang>-<style>/` | the film library entry: reused for later visitors, and played if a live run fails |
| `exhibits/hope/exhibit.json` | facts with sources, character look and voice, style suffix, ambience |
| `web/assets/background.jpg`, `intro.mp4`, `sample.jpg` | page background, intro film, and the picture shown for an exhibit without a `photo.jpg` |

Cut the labelled model sheet into text-free crops with `python -m museum.sheet` (see the refs README).

To let Claude write a storyboard for a language and style that has a hand-written file, rename or remove that file.

A new exhibit is a new folder with an `exhibit.json`. With more than one exhibit and `LIVE=llm`, Claude picks the
exhibit from the visitor's photo.

## Film library

Every finished film is saved under `exhibits/<id>/demo/<lang>-<style>/`. When a later visitor photographs the
same exhibit, nothing is rendered again: the saved film is served, and the visitor is walked through the film's
recorded making-of compressed to `REPLAY_SECONDS` (default 12). The recognition step still runs for real, since
it decides which film matches.

A saved film is not reused when the material behind it has changed (video model, exhibit.json, the storyboard file,
reference crops, overrides; with the agent on: the exhibit's knowledge pack and reference images), or when it is a
mock and real video is now live. Changing the agent's prompts does not throw saved films away. A mock film never replaces a saved
film that has real video.

To render again on purpose: open the app with `?fresh` in the address, or use `python -m museum make`, which
always renders (add `--no-save` to keep the result out of the library). `python -m museum promote <job>` puts an
earlier take from `output/` back into the library.

## Facts

Narration may only state facts listed in `exhibit.json`, and only facts that have a `source` URL. A fact without a
source (currently "221 bones, diving lunge") is left out and cannot be cited; add a URL to enable it.
A storyboard that cites an unknown or unsourced fact is rejected before anything is rendered. When Claude writes the
storyboard, a second pass checks every line against the facts and rewrites any line that goes beyond them.

## Layout

    museum/config.py      settings, mock/live switch, prices
    museum/exhibits.py    exhibit folders and their drop-in slots
    museum/storyboard.py  storyboard schema, prompts, Claude writer + fact check, photo recognition
    museum/video.py       scene planning, budget guard, fal render, mock cards
    museum/edit.py        ffmpeg: conform, cross-fade, join (and the older fit-to-narration path)
    museum/pipeline.py    the steps, progress events, manifest, film library
    museum/outline.py     exhibit outline for the scan effect
    museum/voice.py       mock voice; ElevenLabs narration for the older path
    museum/check.py       free checks of keys and endpoints
    museum/script_agent.py  bridge to the script agent in harness/
    harness/              the script agent (separate owner, see harness/METHOD.md)
    museum/server.py      FastAPI: jobs, server-sent events, outline, static files
    museum/sheet.py       cut a model sheet into reference crops
    web/index.html        the whole front end, styled after the Figma code layer "Museum Alive" (V2)
    web/assets/           background, intro film, sample picture
    output/, cache/       generated, not committed

## Not built yet

- Talking to the character after the film.
- Checking what the model actually said against the script (speech-to-text on the finished clip).
- Checking rendered frames against the character sheet and re-rendering scenes that drift.
- Fetching new sources with a search tool instead of only using the facts in `exhibit.json`.
