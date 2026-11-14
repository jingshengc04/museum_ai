"""Find the exhibit in a visitor's photo and return its outline, for the scan effect.

Uses U2-Net salient-object segmentation through onnxruntime, on the CPU, locally: no API, no cost.
The model file is fetched once into cache/models/ (u2netp is 4.6 MB; u2net is 176 MB and sharper,
choose with OUTLINE_MODEL=u2net).
"""
from __future__ import annotations

import io
import os
import threading
from pathlib import Path

from . import config

MODEL = os.environ.get("OUTLINE_MODEL", "").strip() or "u2netp"
MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/{name}.onnx"
MAX_SIDE = 900  # the outline is drawn at this size at most; the browser scales it over the photo

_session = None
_lock = threading.Lock()


def _model_file() -> Path:
    target = config.CACHE_DIR / "models" / f"{MODEL}.onnx"
    if not target.exists():
        import httpx

        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(".part")
        with httpx.stream("GET", MODEL_URL.format(name=MODEL), follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            with partial.open("wb") as fh:
                for chunk in response.iter_bytes():
                    fh.write(chunk)
        partial.replace(target)
    return target


def _load():
    global _session
    with _lock:
        if _session is None:
            import onnxruntime

            _session = onnxruntime.InferenceSession(str(_model_file()), providers=["CPUExecutionProvider"])
    return _session


def subject_mask(image):
    """Greyscale PIL image, white where the main object is, same size as `image`."""
    import numpy as np
    from PIL import Image

    session = _load()
    pixels = np.asarray(image.convert("RGB").resize((320, 320), Image.LANCZOS), dtype=np.float32)
    pixels /= max(float(pixels.max()), 1e-6)
    pixels = (pixels - (0.485, 0.456, 0.406)) / (0.229, 0.224, 0.225)
    batch = pixels.transpose(2, 0, 1)[None].astype(np.float32)
    saliency = session.run(None, {session.get_inputs()[0].name: batch})[0][0, 0]
    low, high = float(saliency.min()), float(saliency.max())
    saliency = (saliency - low) / max(high - low, 1e-6)
    return Image.fromarray((saliency * 255).astype("uint8"), "L").resize(image.size, Image.LANCZOS)


def outline_png(photo: bytes) -> bytes | None:
    """Transparent PNG with a white line around the exhibit, or None when nothing stands out."""
    from PIL import Image, ImageChops, ImageFilter, ImageOps

    image = ImageOps.exif_transpose(Image.open(io.BytesIO(photo)))
    image.thumbnail((MAX_SIDE, MAX_SIDE))
    solid = subject_mask(image).filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 128 else 0)
    covered = sum(solid.histogram()[128:]) / (solid.width * solid.height)
    if not 0.01 < covered < 0.95:
        return None
    # The line is the band between a slightly grown and a slightly shrunk copy of the shape.
    width = max(3, round(max(image.size) / 450) * 2 + 1)
    edge = ImageChops.subtract(solid.filter(ImageFilter.MaxFilter(width)), solid.filter(ImageFilter.MinFilter(width)))
    edge = edge.filter(ImageFilter.GaussianBlur(0.8))
    line = Image.new("RGBA", image.size, (255, 255, 255, 0))
    line.putalpha(edge)
    out = io.BytesIO()
    line.save(out, "PNG", optimize=True)
    return out.getvalue()
