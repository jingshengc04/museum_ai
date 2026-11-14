"""Tests never make paid calls: LIVE is forced empty before anything reads .env."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

os.environ["LIVE"] = ""
_tmp = Path(tempfile.mkdtemp(prefix="museum-test-"))
os.environ["MUSEUM_CACHE_DIR"] = str(_tmp / "cache")
os.environ["MUSEUM_OUTPUT_DIR"] = str(_tmp / "output")

import pytest  # noqa: E402
from PIL import Image  # noqa: E402

from museum import config  # noqa: E402

REAL_HOPE = config.ROOT / "exhibits" / "hope"


@pytest.fixture
def tiny_exhibit(tmp_path, monkeypatch):
    """A copy of Hope with a two-shot storyboard and every drop-in slot filled."""
    root = tmp_path / "exhibits"
    folder = root / "hope"
    (folder / "storyboards").mkdir(parents=True)
    (folder / "refs").mkdir()
    (folder / "overrides").mkdir()
    shutil.copyfile(REAL_HOPE / "exhibit.json", folder / "exhibit.json")

    board = json.loads((REAL_HOPE / "storyboards" / "en-first_person.json").read_text())
    board["shots"] = board["shots"][:2]
    (folder / "storyboards" / "en-first_person.json").write_text(json.dumps(board))

    Image.new("RGB", (640, 480), (20, 60, 110)).save(folder / "photo.jpg")
    for name in ("side", "curious", "delighted"):
        Image.new("RGB", (300, 200), (30, 80, 160)).save(folder / "refs" / f"{name}.png")
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=30:duration=2",
         "-pix_fmt", "yuv420p", str(folder / "overrides" / "shot_02.mp4")],
        check=True,
    )
    monkeypatch.setattr(config, "EXHIBITS_DIR", root)
    return folder
