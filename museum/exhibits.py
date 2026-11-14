"""Exhibit folders: facts, character and every drop-in slot for existing material.

exhibits/<id>/
  exhibit.json            facts + sources, character, style suffix
  photo.jpg|png           the exhibit as a visitor sees it (sample photo in the UI)
  refs/<name>.png         character reference crops; a shot uses them by <name>
  storyboards/<lang>-<style>.json   hand-written storyboard, skips the LLM
  overrides/shot_03.mp4   ready-made clip for shot 3, skips video generation
  overrides/shot_03.mp3   ready-made narration for shot 3 (+ optional shot_03.words.json)
  overrides/ambient.mp3   ready-made sound bed
  demo/<lang>-<style>/    known-good film (final.mp4 + manifest.json), see `promote`
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import config

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass
class Exhibit:
    id: str
    dir: Path
    data: dict
    refs: dict[str, Path] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def facts(self) -> list[dict]:
        """Only facts with a source may be narrated."""
        return [f for f in self.data.get("facts", []) if f.get("source")]

    @property
    def unsourced_facts(self) -> list[dict]:
        return [f for f in self.data.get("facts", []) if not f.get("source")]

    @property
    def photo(self) -> Path | None:
        for ext in sorted(IMAGE_EXT):
            p = self.dir / f"photo{ext}"
            if p.exists():
                return p
        return None

    def storyboard_file(self, language: str, style: str) -> Path:
        return self.dir / "storyboards" / f"{language}-{style}.json"

    def override(self, shot_id: int, ext: str) -> Path | None:
        p = self.dir / "overrides" / f"shot_{shot_id:02d}{ext}"
        return p if p.exists() else None

    def ambient_override(self) -> Path | None:
        for ext in (".mp3", ".wav", ".m4a"):
            p = self.dir / "overrides" / f"ambient{ext}"
            if p.exists():
                return p
        return None

    def demo_dir(self, language: str, style: str) -> Path:
        return self.dir / "demo" / f"{language}-{style}"

    def demos(self) -> list[dict]:
        out = []
        for manifest in sorted(self.dir.glob("demo/*/manifest.json")):
            if (manifest.parent / "final.mp4").exists():
                language, _, style = manifest.parent.name.partition("-")
                out.append({"language": language, "style": style, "manifest": self.url(manifest)})
        return out

    def url(self, path: Path) -> str:
        return f"/exhibits/{self.id}/{path.relative_to(self.dir).as_posix()}"

    def voice_id(self, language: str) -> str:
        voices = self.data.get("character", {}).get("voice", {})
        return voices.get(language) or config.ELEVEN_VOICE_ID

    def public(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "museum": self.data.get("museum", ""),
            "location": self.data.get("location", ""),
            "character": self.data.get("character", {}).get("name", ""),
            "photo": self.url(self.photo) if self.photo else None,
            "refs": sorted(self.refs),
            "facts": self.facts,
            "unsourced_facts": self.unsourced_facts,
            "demos": self.demos(),
        }


def load(exhibit_id: str) -> Exhibit:
    folder = config.EXHIBITS_DIR / exhibit_id
    data = json.loads((folder / "exhibit.json").read_text())
    refs = {
        p.stem.lower(): p
        for p in sorted((folder / "refs").glob("*"))
        if p.suffix.lower() in IMAGE_EXT
    }
    return Exhibit(id=exhibit_id, dir=folder, data=data, refs=refs)


def all_exhibits() -> list[Exhibit]:
    return [load(p.parent.name) for p in sorted(config.EXHIBITS_DIR.glob("*/exhibit.json"))]
