"""Web app: upload a photo, watch the film get made, play it with live sources."""
from __future__ import annotations

import asyncio
import json
import threading
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import config, exhibits, pipeline, video

MAX_PHOTO_BYTES = 15 * 1024 * 1024
PHOTO_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

app = FastAPI(title="Museum AI")
config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=config.OUTPUT_DIR), name="output")
app.mount("/exhibits", StaticFiles(directory=config.EXHIBITS_DIR), name="exhibits")


class Job:
    def __init__(self, language: str, style: str, exhibit_id: str | None):
        self.id = time.strftime("%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        self.dir = config.OUTPUT_DIR / self.id
        self.language, self.style, self.exhibit_id = language, style, exhibit_id
        self.events: list[dict] = []
        self.finished = False

    def emit(self, kind: str, **data) -> None:
        self.events.append({"type": kind, **data})

    def _fallback(self) -> str | None:
        """A saved film to show if this job fails: same language and style if there is one."""
        found = [d for e in exhibits.all_exhibits() if self.exhibit_id in (None, e.id) for d in e.demos()]
        exact = [d for d in found if (d["language"], d["style"]) == (self.language, self.style)]
        same_language = [d for d in found if d["language"] == self.language]
        best = exact or same_language or found
        return best[0]["manifest"] if best else None

    def run(self, photo: Path | None) -> None:
        try:
            pipeline.make_film(self.dir, self.language, self.style, self.emit, photo=photo, exhibit_id=self.exhibit_id)
            self.emit("done", manifest=f"/output/{self.id}/manifest.json")
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
        "exhibits": [e.public() for e in found],
        "video": {
            "model": config.VIDEO_MODEL,
            "resolution": config.VIDEO_RESOLUTION,
            "worst_case_usd": video.worst_case_usd(shots) if config.is_live("video") else 0,
            "budget_usd": config.MAX_FAL_USD,
        },
    }


@app.post("/api/jobs")
async def create_job(
    language: str = Form("en"),
    style: str = Form("first_person"),
    exhibit_id: str | None = Form(None),
    photo: UploadFile | None = File(None),
) -> dict:
    if language not in config.LANGUAGES or style not in config.STYLES:
        raise HTTPException(400, "Unknown language or style.")
    if exhibit_id and exhibit_id not in {e.id for e in exhibits.all_exhibits()}:
        raise HTTPException(400, "Unknown exhibit.")
    job = Job(language, style, exhibit_id or None)
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
    JOBS[job.id] = job
    threading.Thread(target=job.run, args=(saved,), daemon=True).start()
    return {"job_id": job.id}


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
