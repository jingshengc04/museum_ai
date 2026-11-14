# Example output

`four_ram_zun_e2e/` is one complete run (user photo of the Four-Ram Square Zun, no prepared pack, search only, 480p),
kept so the product code can be built against real data:

- `final.json`: the hand-off: image jobs (visitor photo + prompt), Seedance requests (`<job:id>` image refs), subtitles,
  voice, music, estimated cost.
- `events.jsonl`: the live progress feed: `stage_start`/`stage_end`, `search`, `source`, `keywords_batch`,
  `image_jobs_ready`, `retry`; `t_run` = seconds since the run started.
- `script.json`, `seedance.json`, `image_jobs.json`, `report.md`: the agent's script, rendered video requests, image jobs, report.
- `media/`: generated reference images, `film.mp4` (subtitles burned in + soft track), `film.srt`, `generation.json`
  (fal results and timings), `timing.md`.

Produce your own: `uv run python run.py --photo photo.jpg` then `uv run python generate.py runs/<run>`.
