# CLAUDE.md — Project context

This file is background, not a spec. It collects what the team has decided, tested and learned so far. How to build the project (architecture, stack, structure, order of work) is up to you. Make good calls, and tell the team when a decision is big or costs money.

## The idea

A museum visitor takes a photo of an exhibit and gets back a short animated film (roughly 40–60 seconds) that tells that exhibit's story. Ideally the exhibit itself is a character and narrates in the first person. It should feel like an "AI animated short drama" (AI 漫剧): a sequence of storyboarded shots with a consistent character, voice-over, sound design and subtitles, not a slideshow.

Things the team is excited about (all optional, pick what makes the best demo):
- Different styles for different audiences: kids, expert, first-person, funny.
- Different languages (English and Chinese at minimum).
- Interactivity: a choice at the end ("go back to 1891" / "ask Hope a question"), or talking to the character afterwards.
- Showing the agent "thinking" while it works (reading the label, checking sources, drawing scene 3…). The wait becomes part of the show.
- An agent that checks its own output against the character sheet and fixes problems.

## Hackathon context

- Imperial AI Society hackathon, Sat 14 – Sun 15 Nov 2026. Submission deadline: `TODO: fill in`.
- Main track: **Voice, Vision & Generative Media** (sponsors: fal, ElevenLabs, Anam). Teams can also claim up to 2 sponsor sub-bounties; fal and ElevenLabs are the natural ones for us. Figma also gives a cross-track "Best-Designed AI Product" prize, so a good-looking UI is worth effort.
- Other sponsors present (in case they're useful): Tavily, Linkup (web search for agents), Databricks, MongoDB, Synthesia.
- Judges reward a clear "wow" moment, a story they get in one sentence, and a live demo.

## Demo exhibit: Hope the blue whale

The skeleton hanging in Hintze Hall, Natural History Museum, London. Verified facts (use these or fetch new sources; never invent facts):
- Juvenile female blue whale, stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891. https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html
- The 4.5-tonne skeleton was sold to the Natural History Museum for £250. https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html
- Hung in the Mammal Hall from 1934; moved to Hintze Hall and unveiled in July 2017, replacing Dippy the Diplodocus cast (there 1979 – Jan 2017). Named Hope "as a symbol of humanity's power to shape a sustainable future". https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html
- 25.2 m long. https://artsandculture.google.com/asset/GAG_J9wcz31GXw
- 221 bones, posed in a diving lunge (secondary source).

Assets the team has (or will put in the repo):
- A photo of Hintze Hall with the skeleton and lots of visitors.
- A character model sheet for Hope: semi-realistic stylized CG blue whale. Front view, side view, and four expressions (calm, curious, delighted, thoughtful). It has text labels ("HOPE", "FRONT", "CALM", …). Split it into separate crops without text before using it as a reference, or the labels leak into generated video.

## What we've learned about the tools

### fal (video and images). Credits are limited, so this matters most

- **Vidu Q2 reference-to-video** (`fal-ai/vidu/q2/reference-to-video`). Tested in the fal playground: style and character consistency look good. Params: `prompt`, `reference_image_urls` (≤ 7), `duration` 1–8 s (max 8 on fal), `resolution` 360p/520p/720p/1080p, `aspect_ratio` 16:9 / 9:16 / 1:1, `movement_amplitude` auto/small/medium/large, `bgm`, `seed`. Listed price per video: $0.10 (360p), $0.20 (520p), $0.30 (720p); 1080p adds per-second. Not confirmed whether 360–720p price changes with duration (the playground shows the cost before you submit). No start-frame input.
- **Vidu Q4 reference-to-video** (`fal-ai/vidu/q4/reference-to-video`): up to 12 refs, up to 16 s, up to 4K. Billed per second (pricier). fal's own web agent picked this for us.
- **Seedance 2.0**: about $0.24–0.30 per second at 720p on fal, roughly $3 per 10-second clip. Too expensive for a pipeline on our credits; maybe one hero shot at most.
- Other useful fal models: image editing with reference images (e.g. Nano Banana) for keyframes at a few cents each; first+last-frame video models (e.g. MiniMax H3 Max, Wan 2.7) for seamless transitions; cheap lip-sync models (FlashTalk around $0.02/s, Kling AI Avatar v2 Standard around $0.056/s) for exhibits that have faces. Verify ids and params on the model page before using any of them.
- **Concurrency**: new fal accounts process 2 requests at a time; extra requests wait in the queue (no error). Asking the fal team at the event for a higher limit or more credits is worth a try.
- **fal's web agent** (fal.ai UI) is a good playground for trying shots. As far as we know it isn't callable from code. Its workflow for a seamless "second room" reveal was smart: extract the last frame of clip 1 → generate a keyframe still (last frame + scene + character sheet) → first+last-frame video between them → join. It also checks a few frames against the character sheet after each render.
- Observed problems: Hope rendered paler/greyer than her sheet with less mottled texture, and "rippling underwater light" came out as warm light beams. Prompting explicitly for "deep blue mottled skin" helped in the still.

### ElevenLabs (voice and sound)
- `eleven_v3` understands inline emotion tags like `[softly]`, `[whispers]`, `[excited]`; other models read tags aloud.
- There's a "with timestamps" TTS endpoint (handy for word-level subtitles) and a sound-effects endpoint (ambient beds: museum hall reverb, deep ocean, whale song, 1891 Irish coastline).

### Sync between picture and voice
Video models ignore timestamps in prompts and only output fixed lengths, so sync happens in editing: treat narration audio as the master timeline, then trim, slightly slow (up to ~25%) or freeze the last frame of each clip to match. Cross-fades and a continuous ambient sound bed hide seams. Write each shot's narration to roughly fit one clip (about 12–13 English words or 18–20 Chinese characters per 5 s). Only lip-sync models are truly audio-driven.

### Prompting video that worked for us
`Camera: … Location: … Action: … Mood: …` plus a shared style suffix so every shot looks the same. One main action per shot, written first. Describe motion, not the whole scene. A whale's face barely changes, so show emotion through movement (curious = turns and glides closer; joyful = slow barrel roll; sad = drifts and sinks). Use 2–4 refs per shot, including the expression crop that fits.

## Existing code

`pipeline.py` is a working sketch: storyboard JSON → ElevenLabs narration per shot → Vidu clips submitted in parallel → each clip fitted to its narration length with ffmpeg → concatenated `final.mp4` with optional burned-in subtitles; content-hash caching of paid results. The ffmpeg fitting/joining/subtitles were tested with fake media; the fal and ElevenLabs calls have not been run with real keys yet. Reuse it, restructure it or replace it; your call.

## Things that matter (the only hard rules)

- **Don't burn fal credits.** Develop and test without paid calls (mocks, placeholders, cached results), use low resolution until things work, cache paid results, and check with the team before anything that will cost more than a few dollars.
- **Don't invent facts** in narration. Facts come from the museum label or fetched sources, and sources should be visible somewhere in the product.
- API keys come from environment variables and never get committed.
- Characters are our own originals; don't imitate existing film, TV or game characters.
- Keep a known-good demo output around at all times. A live demo that fails with nothing to fall back on is the worst outcome.