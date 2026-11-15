"""Make the film from a run's final.json: reference images on fal, then Seedance video, then subtitles.

    uv run python generate.py runs/<run>                 # 480p by default
    uv run python generate.py runs/<run> --resolution 720p

Everything about generation is fixed here (endpoints, resolution, aspect); the agent only wrote prompts.
Writes runs/<run>/media/: images/, segments/, film.mp4 (subtitles burned in), film.srt, generation.json.
Spends fal credits: images ~$0.15 each; Seedance standard ~$0.14/s at 480p, ~$0.30/s at 720p.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import agent  # loads .env (FAL_KEY)
import images

VIDEO_USD_PER_S = {"480p": 0.14, "720p": 0.30}
VIDEO_USD_PER_S_25 = {"480p": 0.2205, "720p": 0.473, "1080p": 1.164}  # Seedance 2.5, fal model page
FONT = next((f for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
                         "/Library/Fonts/Arial.ttf") if Path(f).exists()), None)


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


STATE: dict = {}
CLIENT = None
STATE_FILE: Path | None = None
STATE_LOCK = None


def _save_state() -> None:
    if STATE_FILE:
        with STATE_LOCK:
            STATE_FILE.write_text(json.dumps(STATE, indent=2, ensure_ascii=False))


def fal_run(endpoint: str, arguments: dict, key: str) -> dict:
    """Submit once, remember the fal request id, then wait for that same job.

    A network drop never resubmits (which would pay twice): we keep polling the saved request id until the
    network is back. Rerunning generate.py after a crash picks up the saved ids and finished results."""
    import fal_client
    entry = STATE.setdefault(key, {})
    if entry.get("result"):
        return entry["result"]
    if not entry.get("request_id"):
        for attempt in range(6):
            try:
                entry["request_id"] = fal_client.submit(endpoint, arguments=arguments).request_id
                entry["endpoint"] = endpoint
                _save_state()
                log(f"  submitted {key}: {entry['request_id']}")
                break
            except Exception as e:  # nothing was queued if submit itself failed
                if attempt == 5:
                    raise
                log(f"  submit {key} failed ({type(e).__name__}); retrying in {15 * (attempt + 1)}s")
                time.sleep(15 * (attempt + 1))
    rid, waited = entry["request_id"], 0
    global CLIENT
    CLIENT = CLIENT or fal_client.SyncClient(default_timeout=60)  # a hung socket must not hang the run
    while True:
        try:
            st = CLIENT.status(endpoint, rid)
            if isinstance(st, fal_client.Completed):
                entry["result"] = CLIENT.result(endpoint, rid)
                _save_state()
                return entry["result"]
            time.sleep(5)
            waited += 5
        except Exception as e:  # offline or transient: keep waiting on the same job
            code = getattr(getattr(e, "response", None), "status_code", None) or getattr(e, "status_code", None)
            if "content_policy" in str(e) or (code and 400 <= code < 500 and code not in (408, 429)):
                raise RuntimeError(f"{key}: fal rejected request {rid}: {str(e)[:400]}") from e
            log(f"  waiting on {key} ({type(e).__name__}: {str(e)[:80]}); will reconnect")
            time.sleep(20)
            waited += 20
        if waited > 3600:
            raise RuntimeError(f"{key}: no result after an hour (request {rid})")


def drop_ref(prompt: str, n: int) -> str:
    """Remove @Image{n} from a Seedance prompt: its binding clause, its mentions, and shift later tags down."""
    import re
    prompt = re.sub(rf"@Image{n} = [^;\n]*(; |(?=\n))", "", prompt)
    prompt = re.sub(rf"(the [\w\s-]{{1,40}}?) from @Image{n}\b", r"\1", prompt)
    prompt = re.sub(rf"\s*@Image{n}\b", "", prompt)
    return re.sub(r"@Image(\d+)", lambda m: f"@Image{int(m[1]) - 1}" if int(m[1]) > n else m[0], prompt)


def upload(path: Path) -> str:
    import fal_client
    from PIL import Image
    if path.suffix.lower() == ".webp":  # convert for maximum compatibility
        jpg = path.with_suffix(".upload.jpg")
        Image.open(path).convert("RGB").save(jpg, quality=92)
        path = jpg
    return fal_client.upload_file(str(path))


def download(url: str, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return target
    for attempt in range(10):
        try:
            urllib.request.urlretrieve(url, target)
            return target
        except Exception as e:
            log(f"  download {target.name} failed ({type(e).__name__}); retrying in 20s")
            time.sleep(20)
    raise RuntimeError(f"could not download {url}")


def srt(cues: list[dict]) -> str:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i}\n{ts(c['t_start'])} --> {ts(c['t_end'])}\n{c['text']}\n" for i, c in enumerate(cues, 1))


def subtitle_png(text: str, width: int, target: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    size = max(18, width // 32)
    font = ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()
    draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    words, lines, cur = text.split(), [], ""
    for w in words:  # wrap to ~85% of the frame
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) > width * 0.85 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    line_h = int(size * 1.3)
    img = Image.new("RGBA", (width, line_h * len(lines) + size // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = (width - d.textlength(line, font=font)) / 2
        d.text((x, i * line_h), line, font=font, fill=(255, 255, 255, 255),
               stroke_width=max(2, size // 12), stroke_fill=(0, 0, 0, 255))
    img.save(target)


def probe(path: Path) -> tuple[int, int, float]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=Path)
    ap.add_argument("--resolution", default="480p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--photo", type=Path, help="visitor photo, if final.json does not name one")
    args = ap.parse_args()

    run = args.run.resolve()
    final = json.loads((run / "final.json").read_text())
    media = run / "media"
    media.mkdir(exist_ok=True)
    global STATE, STATE_FILE, STATE_LOCK
    import threading
    STATE_LOCK = threading.Lock()
    STATE_FILE = media / "fal_state.json"
    STATE = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    if STATE:
        log(f"resuming: {sum(1 for v in STATE.values() if v.get('result'))} finished, "
            f"{sum(1 for v in STATE.values() if v.get('request_id') and not v.get('result'))} waiting on fal")
    record: dict = {"run": run.name, "resolution": args.resolution, "started": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "images": [], "segments": [], "est_usd": 0.0}
    t0 = time.time()

    # 1. inputs: the visitor photo and any existing reference images
    photo = args.photo or (Path(final["photo"]) if final.get("photo") else None)
    if photo and not photo.is_absolute():
        photo = agent.HERE / photo
    urls: dict[str, str] = {}
    def cached_upload(key: str, path: Path) -> str:
        if STATE.get(key, {}).get("url"):
            return STATE[key]["url"]
        for attempt in range(6):
            try:
                url = upload(path)
                STATE[key] = {"url": url}
                _save_state()
                return url
            except Exception as e:
                log(f"  upload {path.name} failed ({type(e).__name__}); retrying in 20s")
                time.sleep(20)
        raise RuntimeError(f"could not upload {path}")

    if photo:
        urls["<visitor_photo>"] = cached_upload("upload:visitor_photo", photo)
        log(f"uploaded visitor photo {photo.name}")
    for aid in final.get("existing_images_used", []):
        asset = next(a for a in agent.existing_assets(final["exhibit_id"]) if a["id"] == aid)
        urls[f"<existing:{aid}>"] = cached_upload(f"upload:{aid}", Path(asset["path"]))
        log(f"uploaded existing reference {aid}")

    # 2. reference images (all start from the photo + prompt; run in parallel)
    def make_image(job: dict) -> dict:
        t = time.time()
        inp = job["input"]
        arguments = {"prompt": inp["prompt"], "resolution": "1K", "output_format": "png"}
        refs = [urls[u] for u in inp.get("image_urls", []) if u in urls]
        if refs:
            arguments["image_urls"] = refs
        res = fal_run(images.ENDPOINT, arguments, f"image:{job['id']}")
        url = res["images"][0]["url"]
        download(url, media / "images" / f"{job['id']}.png")
        log(f"image {job['id']} done in {time.time() - t:.0f}s")
        return {"id": job["id"], "url": url, "seconds": round(time.time() - t, 1), "prompt": inp["prompt"]}

    jobs = final.get("image_jobs", [])
    log(f"generating {len(jobs)} reference images on {images.ENDPOINT}")
    with ThreadPoolExecutor(max_workers=4) as pool:
        made = list(pool.map(make_image, jobs))
    for m in made:
        urls[f"<job:{m['id']}>"] = m["url"]
    record["images"] = made
    record["est_usd"] += images.total(jobs)

    # 3. video segments on Seedance (parallel)
    def make_segment(item: tuple[int, dict]) -> dict:
        i, req = item
        t = time.time()
        refs = [urls[u] for u in req["image_urls"] if u in urls]
        missing = [u for u in req["image_urls"] if u not in urls]
        arguments = {"prompt": req["prompt"], "image_urls": refs, "duration": req["duration"],
                     "resolution": args.resolution, "aspect_ratio": req["aspect_ratio"], "generate_audio": True}
        try:
            res = fal_run(req["endpoint"], arguments, f"segment:{i + 1}")
        except RuntimeError as e:
            # Moderation may flag a photo-derived setting image (a faint reflection of the photographer is enough).
            # Fall back once: drop the in-place reference, renumber the @Image tags, keep the identity anchor.
            k = next((n for n, u in enumerate(req["image_urls"]) if u in in_place), None)
            if "content_policy" not in str(e) or k is None:
                raise
            log(f"  segment {i + 1} rejected by moderation; retrying without the in-place reference")
            arguments = {**arguments, "image_urls": [r for n, r in enumerate(refs) if n != k],
                         "prompt": drop_ref(req["prompt"], k + 1)}
            res = fal_run(req["endpoint"], arguments, f"segment:{i + 1}:no_in_place")
        path = download(res["video"]["url"], media / "segments" / f"seg_{i + 1}.mp4")
        log(f"segment {i + 1} done in {time.time() - t:.0f}s ({req['duration']} s)")
        return {"index": i + 1, "url": res["video"]["url"], "seed": res.get("seed"), "path": str(path),
                "missing_refs": missing, "seconds": round(time.time() - t, 1), "prompt": req["prompt"]}

    in_place = {f"<job:{j['id']}>" for j in final.get("image_jobs", []) if j.get("kind") == "in_place"}
    reqs = final["video_requests"]
    log(f"generating {len(reqs)} video segment(s) at {args.resolution}")
    with ThreadPoolExecutor(max_workers=2) as pool:
        segs = list(pool.map(make_segment, enumerate(reqs)))
    record["segments"] = segs
    record["est_usd"] += sum(int(r["duration"]) * (VIDEO_USD_PER_S_25 if "2.5" in r["endpoint"] else VIDEO_USD_PER_S)[args.resolution] for r in reqs)

    # 4. join segments (hard cut) and burn English subtitles
    raw = media / "film_raw.mp4"
    if len(segs) == 1:
        shutil.copy(segs[0]["path"], raw)
    else:
        inputs = sum((["-i", s["path"]] for s in segs), [])
        streams = "".join(f"[{i}:v][{i}:a]" for i in range(len(segs)))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
                        f"{streams}concat=n={len(segs)}:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-crf", "18", "-c:a", "aac", str(raw)], check=True)
    (media / "film.srt").write_text(srt(final["subtitles"]))
    w, h, dur = probe(raw)
    pngs = []
    for k, cue in enumerate(final["subtitles"]):
        p = media / "subs" / f"cue_{k:02d}.png"
        p.parent.mkdir(exist_ok=True)
        subtitle_png(cue["text"], w, p)
        pngs.append((p, cue))
    inputs = ["-i", str(raw)] + sum((["-i", str(p)] for p, _ in pngs), [])
    chain, last = [], "[0:v]"
    for k, (_, cue) in enumerate(pngs, 1):
        out = f"[v{k}]"
        chain.append(f"{last}[{k}:v]overlay=x=(W-w)/2:y=H-h-H/14:enable='between(t,{cue['t_start']},{cue['t_end']})'{out}")
        last = out
    film = media / "film.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-i", str(media / "film.srt")]
    if chain:
        cmd += ["-filter_complex", ";".join(chain), "-map", last]
    else:
        cmd += ["-map", "0:v"]
    cmd += ["-map", "0:a?", "-map", f"{len(pngs) + 1}:s", "-c:v", "libx264", "-crf", "18", "-c:a", "copy",
            "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", str(film)]
    subprocess.run(cmd, check=True)

    record.update({"film": str(film), "film_seconds": round(dur, 2), "frame": f"{w}x{h}",
                   "wall_seconds": round(time.time() - t0, 1), "est_usd": round(record["est_usd"], 2)})
    (media / "generation.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    log(f"done: {film} ({w}x{h}, {dur:.1f}s) · est ${record['est_usd']} · {record['wall_seconds']}s wall")


if __name__ == "__main__":
    main()
