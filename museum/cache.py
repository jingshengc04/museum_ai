"""Content-hash cache for paid results: same inputs never get billed twice."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Callable

from . import config


def file_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def key(*parts) -> str:
    blob = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:24]


def path(kind: str, cache_key: str, ext: str) -> Path:
    folder = config.CACHE_DIR / kind
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{cache_key}{ext}"


def cached_file(kind: str, cache_key: str, ext: str, produce: Callable[[Path], None]) -> tuple[Path, bool]:
    """Return (file, was_cached). `produce(tmp)` writes the file on a miss."""
    target = path(kind, cache_key, ext)
    if target.exists() and target.stat().st_size > 0:
        return target, True
    tmp = target.with_name(f"{target.stem}.{os.getpid()}.tmp{ext}")
    try:
        produce(tmp)
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)
    return target, False


def cached_json(kind: str, cache_key: str, produce: Callable[[], dict]) -> tuple[dict, bool]:
    target = path(kind, cache_key, ".json")
    if target.exists():
        return json.loads(target.read_text()), True
    data = produce()
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data, False
