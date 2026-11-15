"""Web app: upload a photo, watch the film get made, play it with live sources."""
from __future__ import annotations

import asyncio
import json
import threading
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config, exhibits, outline, pipeline, video

MAX_PHOTO_BYTES = 15 * 1024 * 1024
# How far a job has got when each step starts, and what it says meanwhile (the page shows the same).
STEP_PROGRESS = {"identify": (8, "Reading the artifact"), "story": (18, "Searching the archives"), "voice": (30, "Recovering its voice"),
                 "video": (36, "Restoring the moment"), "edit": (92, "Cutting the film")}
PHOTO_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

app = FastAPI(title="Museum AI")
config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")
app.mount("/exhibits", StaticFiles(directory=config.EXHIBITS_DIR), name="exhibits")
app.mount("/assets", StaticFiles(directory=config.WEB_DIR / "assets"), name="assets")


class Job:
    def __init__(self, language: str, style: str, exhibit_id: str | None, fresh: bool = False):
        self.id = time.strftime("%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        self.dir = config.OUTPUT_DIR / self.id
        self.language, self.style, self.exhibit_id, self.fresh = language, style, exhibit_id, fresh
        self.events: list[dict] = []
        self.finished = False
        self.started = time.time()
        self.photo_url: str | None = None
        self.summary = {"state": "running", "percent": 0, "text": "Starting", "name": "", "title": "", "photo": None,
                        "manifest": None, "error": None, "fallback": None}
        self._shots = self._drawn = 0

    def emit(self, kind: str, **data) -> None:
        self.events.append({"type": kind, **data})
        s = self.summary
        if kind == "step" and data.get("status") == "start" and data.get("step") in STEP_PROGRESS:
            percent, s["text"] = STEP_PROGRESS[data["step"]]
            s["percent"] = max(s["percent"], percent)
        elif kind == "progress":
            s["percent"], s["text"] = max(s["percent"], data["percent"]), data["text"]
        elif kind == "exhibit":
            s["name"] = data["exhibit"]["name"]
            s["photo"] = self.photo_url or data["exhibit"].get("photo")
        elif kind == "storyboard":
            s["title"], self._shots = data["title"], len(data["shots"])
        elif kind == "shot" and data.get("stage") == "video" and data.get("status") == "done" and self._shots:
            self._drawn += 1
            s["percent"] = max(s["percent"], 36 + round(56 * self._drawn / self._shots))
        elif kind == "done":
            s.update(state="done", percent=100, text="Ready", manifest=data["manifest"])
        elif kind == "error":
            s.update(state="error", text="Could not be made", error=data["message"], fallback=data.get("fallback"))

    def status(self) -> dict:
        return {"id": self.id, "started": self.started, **self.summary}

    def _fallback(self) -> str | None:
        """A saved film to show if this job fails: same language and style if there is one."""
        found = [d for e in exhibits.all_exhibits() if self.exhibit_id in (None, e.id) for d in e.demos()]
        exact = [d for d in found if (d["language"], d["style"]) == (self.language, self.style)]
        same_language = [d for d in found if d["language"] == self.language]
        best = exact or same_language or found
        return best[0]["manifest"] if best else None

    def run(self, photo: Path | None) -> None:
        try:
            _, folder = pipeline.make_film(self.dir, self.language, self.style, self.emit, photo=photo,
                                           exhibit_id=self.exhibit_id, fresh=self.fresh)
            self.emit("done", manifest=config.url_for(folder / "manifest.json"))
        except Exception as error:  # any failure must reach the visitor as a message, never a hang
            self.emit("error", message=str(error), fallback=self._fallback())
        finally:
            self.finished = True


JOBS: dict[str, Job] = {}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(config.WEB_DIR / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/state")
def state() -> dict:
    found = exhibits.all_exhibits()
    shots = 9
    return {
        "modes": config.modes(),
        "languages": config.LANGUAGES,
        "styles": config.STYLES,
        # Offered on the first screen: exhibits with a film ready to play, and our own prepared ones. Any other
        # exhibit (agent packs, objects learned from photos) is still recognised from a photo.
        "exhibits": [e.public() for e in sorted(found, key=lambda e: bool(e.data.get("learned")))  # prepared ones first
                     if pipeline.library_hit(e, "en", "first_person") or not (e.data.get("from_pack") or e.data.get("learned"))],
        "video": {
            "model": config.VIDEO_MODEL,
            "resolution": config.VIDEO_RESOLUTION,
            "worst_case_usd": video.worst_case_usd(shots) if config.is_live("video") else 0,
            "budget_usd": config.MAX_FAL_USD,
        },
    }


@app.post("/api/outline")
def outline_photo(photo: UploadFile = File(...)) -> Response:
    """Outline of the exhibit in a photo, as a transparent PNG. 204 when there is nothing to draw."""
    if photo.content_type not in PHOTO_TYPES:
        raise HTTPException(400, "The photo must be a JPEG, PNG or WebP image.")
    blob = photo.file.read(MAX_PHOTO_BYTES + 1)
    if len(blob) > MAX_PHOTO_BYTES:
        raise HTTPException(400, "The photo is larger than 15 MB.")
    try:
        png = outline.outline_png(blob)
    except Exception:  # the outline is decoration: without it the scan still runs
        png = None
    if png is None:
        return Response(status_code=204)
    return Response(png, media_type="image/png")


@app.get("/api/stories")
def stories() -> list[dict]:
    """Every film made so far, newest first: the film library plus the runs still in output/."""
    folders = [m.parent for e in exhibits.all_exhibits() for m in sorted(e.dir.glob("demo/*/manifest.json"))]
    folders += [m.parent for m in config.OUTPUT_DIR.glob("*/manifest.json")]
    found, seen = [], set()
    for folder in folders:
        film = folder / "final.mp4"
        if not film.exists():
            continue
        manifest = json.loads((folder / "manifest.json").read_text())
        # A film saved to the library also sits in output/; show it once.
        identity = (manifest.get("fingerprint"), manifest["title"], manifest.get("seconds_to_make"))
        if identity in seen or manifest["language"] != "en":
            continue
        seen.add(identity)
        found.append({
            "manifest": config.url_for(folder / "manifest.json"),
            "title": manifest["title"],
            "exhibit": manifest["exhibit"]["name"],
            "museum": manifest["exhibit"].get("museum", ""),
            "duration": manifest["duration"],
            "thumb": config.url_for(folder / manifest["shots"][0]["thumb"]),
            "made": film.stat().st_mtime,
        })
    return sorted(found, key=lambda story: story["made"], reverse=True)


@app.post("/api/jobs")
async def create_job(
    language: str = Form("en"),
    style: str = Form("first_person"),
    exhibit_id: str | None = Form(None),
    fresh: bool = Form(False),
    photo: UploadFile | None = File(None),
) -> dict:
    if language not in config.LANGUAGES or style not in config.STYLES:
        raise HTTPException(400, "Unknown language or style.")
    if exhibit_id and exhibit_id not in {e.id for e in exhibits.all_exhibits()}:
        raise HTTPException(400, "Unknown exhibit.")
    job = Job(language, style, exhibit_id or None, fresh)
    saved = None
    if photo is not None and photo.filename:
        if photo.content_type not in PHOTO_TYPES:
            raise HTTPException(400, "The photo must be a JPEG, PNG or WebP image.")
        blob = await photo.read(MAX_PHOTO_BYTES + 1)
        if len(blob) > MAX_PHOTO_BYTES:
            raise HTTPException(400, "The photo is larger than 15 MB.")
        job.dir.mkdir(parents=True, exist_ok=True)
        saved = job.dir / f"photo{PHOTO_TYPES[photo.content_type]}"
        saved.write_bytes(blob)
        job.photo_url = job.summary["photo"] = config.url_for(saved)
    JOBS[job.id] = job
    threading.Thread(target=job.run, args=(saved,), daemon=True).start()
    return {"job_id": job.id}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    """Where a job has got: for the list of this visitor's films, while it runs in the background."""
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "No such job.")
    return job.status()


@app.get("/api/jobs/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "No such job.")

    async def stream():
        sent = 0
        while True:
            while sent < len(job.events):
                yield f"data: {json.dumps(job.events[sent], ensure_ascii=False)}\n\n"
                sent += 1
            if job.finished and sent >= len(job.events):
                return
            await asyncio.sleep(0.15)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-store"})
