"""Bridge to the script agent in harness/ (maintained separately: nothing in harness/ is edited from here).

The agent is run as its own process, `python run.py ...` inside harness/, so its module-level state never
mixes between two visitors. Its documented hand-off is files in harness/runs/<run>/:

  events.jsonl   live progress (stage_start / stage_end, search, source, keywords_batch, ...), read as it grows
  final.json     image jobs, Seedance requests, timed subtitles, status
  script.json    the chosen script (which lines state which facts)
  NN_s1_digest/output.json   the facts it worked from, each with its source URL

Every stage the agent runs is cached by the agent itself, so the same photo and pack cost nothing the second time.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import config

Emit = Callable[..., None]

# What the visitor reads while each agent stage runs, and how far the progress bar has got by then.
STAGES = {
    "s0_identify": (18, "Looking closely at the photo"),
    "s0b_research": (20, "Searching the archives"),
    "s1_digest": (23, "Reading the sources"),
    "s1b_assets": (26, "Planning the pictures"),
    "s2_concept": (29, "Finding the story"),
    "s3_script": (31, "Writing the script"),
    "s4_review": (34, "Checking every line against the sources"),
}


@dataclass
class AgentRun:
    dir: Path
    final: dict
    script: dict
    facts: list[dict] = field(default_factory=list)
    cost_usd: float = 0.0

    @property
    def status(self) -> str:
        return self.final.get("status") or ""

    @property
    def passed(self) -> bool:
        return self.status.startswith("PASS") and "REGRESSION" not in self.status

    def photo(self) -> Path | None:
        """The photo the agent worked from (a visitor's, or the pack's test photo)."""
        name = self.final.get("photo")
        if not name:
            return None
        path = Path(name)
        path = path if path.is_absolute() else config.HARNESS_DIR / path
        return path if path.exists() else None

    def identity(self) -> dict:
        """What the agent recognised in the photo (name, museum), when it ran its own recognition."""
        found = sorted(self.dir.glob("*_s0_identify/output.json"))
        return json.loads(found[-1].read_text()) if found else {}

    def existing_image(self, asset_id: str) -> Path | None:
        registry = config.HARNESS_DIR / "knowledge" / self.final["exhibit_id"] / "assets" / "assets.json"
        if not registry.exists():
            return None
        for item in json.loads(registry.read_text()):
            if item["id"] == asset_id:
                return registry.parent / item["file"]
        return None


def load(run_dir: Path) -> AgentRun:
    """Read a finished agent run."""
    final = json.loads((run_dir / "final.json").read_text())
    script = json.loads((run_dir / "script.json").read_text()) if (run_dir / "script.json").exists() else {}
    facts: list[dict] = []
    digests = sorted(run_dir.glob("*_s1_digest/output.json"))
    if digests:  # the last digest is the one that passed the agent's own checks
        facts = [f for f in json.loads(digests[-1].read_text()).get("facts", []) if f.get("source")]
    cost = 0.0
    for meta in run_dir.glob("*/meta.json"):
        data = json.loads(meta.read_text())
        if not data.get("cached"):
            cost += data.get("cost_usd") or 0
    return AgentRun(dir=run_dir, final=final, script=script, facts=facts, cost_usd=round(cost, 2))


def _relay(event: dict, emit: Emit, seen_keywords: set[str]) -> None:
    """Turn one agent event into what the visitor sees while waiting."""
    kind, stage = event.get("type"), event.get("stage", "")
    if kind == "stage_start" and stage in STAGES:
        percent, text = STAGES[stage]
        emit("progress", percent=percent, text=text)
        emit("thought", text=f"{text}…")
    elif kind == "search" and event.get("text"):
        emit("thought", text=f"Searching: {event['text']}")
    elif kind == "source" and event.get("text"):
        emit("thought", text=f"Reading {event['text']}")
    elif kind == "keywords_batch":
        words = [k["text"] for k in event.get("keywords", []) if k.get("text") and k["text"] not in seen_keywords]
        seen_keywords.update(words)
        if words:
            emit("keywords", words=words)
    elif kind == "retry" and event.get("text"):
        emit("thought", text=f"{stage}: {event['text']}", level="warn")


def run(emit: Emit, exhibit_id: str | None = None, photo: Path | None = None) -> AgentRun:
    """Run the agent on a photo and/or a prepared exhibit, relaying its progress. Blocks until it is done."""
    command = [sys.executable, "run.py"]
    if exhibit_id:
        command.append(exhibit_id)
    if photo:
        command += ["--photo", str(Path(photo).resolve())]
    if not exhibit_id and not photo:
        raise ValueError("the script agent needs a photo or an exhibit id")

    process = subprocess.Popen(command, cwd=config.HARNESS_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1)
    output: list[str] = []
    run_name: list[str] = []

    def read_output() -> None:
        for line in process.stdout:
            output.append(line.rstrip())
            match = re.match(r"^\[[^\]]*\] (\S+)", line)
            if match and not run_name:
                run_name.append(match.group(1))

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()

    started, position, seen = time.time(), 0, set()
    events_file = None
    while True:
        finished = process.poll() is not None
        if run_name and events_file is None:
            events_file = config.HARNESS_DIR / "runs" / run_name[0] / "events.jsonl"
        if events_file and events_file.exists():
            with events_file.open() as fh:
                fh.seek(position)
                for line in fh:
                    if not line.endswith("\n"):
                        break  # half-written; read it next time
                    position += len(line.encode())
                    if line.strip():
                        _relay(json.loads(line), emit, seen)
        if finished:
            break
        if time.time() - started > config.HARNESS_TIMEOUT:
            process.kill()
            raise TimeoutError(f"The script agent took longer than {config.HARNESS_TIMEOUT} s and was stopped.")
        time.sleep(0.3)
    reader.join(timeout=5)

    if not run_name:
        raise RuntimeError("The script agent did not start: " + " / ".join(output[-5:]))
    run_dir = config.HARNESS_DIR / "runs" / run_name[0]
    if not (run_dir / "final.json").exists():
        report = run_dir / "report.md"
        reason = ""
        if report.exists():
            text = report.read_text()
            if "## Error" in text:
                lines = [line.strip() for line in text.split("## Error", 1)[1].splitlines()]
                reason = next((line for line in lines if line and not line.startswith("```")), "")
        reason = reason or next((line.strip() for line in reversed(output) if "ERROR" in line), "") or " / ".join(output[-3:])
        raise RuntimeError(f"The script agent could not write a script: {reason}")
    return load(run_dir)
