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

`four_ram_zun_lean/` is the output of the lean pipeline (`lean.py`, see `../README.md`) on the same photo: `final.json`
(same format, plus `problems`, `lines`, `timing_s`), `events.jsonl`, and `film.json` (the writer's raw output). No
video was generated from it. `four_ram_zun_demo_seedance25_720p/` is the best film so far (Seedance 2.5, 720p, 30 s,
one continuous take), made from a hand-written script in the same request format.
