"""Vercel entry point: the hosted demo (see vercel.json and "Hosted demo" in README.md).

It recognises a visitor's photo with Claude and plays films already in the library. Making a new film needs
minutes of background work, ffmpeg and a writable disk, so it runs on our own server, never here.
Set ANTHROPIC_API_KEY in the Vercel project; everything else is decided below.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("MUSEUM_HOSTED", "1")
os.environ.setdefault("LIVE", "llm")  # photo recognition only: no fal, no ElevenLabs
os.environ.setdefault("SCRIPT_AGENT", "builtin")
os.environ.setdefault("MUSEUM_OUTPUT_DIR", "/tmp/museum/output")  # the only writable place in a function
os.environ.setdefault("MUSEUM_CACHE_DIR", "/tmp/museum/cache")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from museum.server import app  # noqa: E402,F401
