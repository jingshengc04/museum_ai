"""Deterministic timing nudge, applied to every draft before the checks.

A line that starts 0.5 s too early is not a writing problem, so code fixes it instead of spending a revision
round (run 1114-181730-hope-v1.4: the best draft lost only because its first line started at 0.3 s).
Lines move by at most MAX_SHIFT seconds; anything bigger stays for the checks and the writer.
"""
from __future__ import annotations

import schemas
from checks import HEAD_S, TAIL_S, WORDS_PER_SECOND, spoken_words

MAX_SHIFT = 1.0
GAP = 0.1


def nudge(script: schemas.Script) -> tuple[schemas.Script, list[str]]:
    sc = script.model_copy(deep=True)
    changes: list[str] = []
    offset = 0.0
    shifts: list[tuple[float, float, float]] = []  # (film_start_before, film_end_before, delta)
    for i, seg in enumerate(sc.segments, 1):
        lines = sorted(seg.narration, key=lambda l: l.t_start)
        if lines:
            dur = [spoken_words(l.text) / WORDS_PER_SECOND for l in lines]
            orig = [l.t_start for l in lines]
            start = list(orig)
            low = HEAD_S if i == 1 else 0.3
            for k in range(len(lines)):  # forward: respect the opening and no-overlap rules
                floor = low if k == 0 else start[k - 1] + dur[k - 1] + GAP
                start[k] = max(start[k], floor)
            limit = seg.duration_s - TAIL_S + 0.15
            if start[-1] + dur[-1] > limit:  # backward: pull lines earlier into free space
                start[-1] = limit - dur[-1]
                for k in range(len(lines) - 2, -1, -1):
                    start[k] = min(start[k], start[k + 1] - GAP - dur[k])
            ok = all(abs(s - o) <= MAX_SHIFT + 1e-6 for s, o in zip(start, orig)) and start[0] >= low - 1e-6 and \
                all(start[k + 1] >= start[k] + dur[k] + GAP - 1e-6 for k in range(len(lines) - 1))
            if ok:
                for line, o, s, d in zip(lines, orig, start, dur):
                    s = round(s, 2)
                    if abs(s - o) > 0.01:
                        changes.append(f"segment {i}: moved '{line.text[:40]}' from {o:.2f}s to {s:.2f}s")
                        shifts.append((offset + o, offset + o + d + 0.5, s - o))
                        line.t_start = s
        offset += seg.duration_s
    for cue in sc.subtitles:  # subtitles follow the line they belong to
        for a, b, delta in shifts:
            if a - 0.05 <= cue.t_start < b:
                cue.t_start = round(cue.t_start + delta, 2)
                cue.t_end = round(cue.t_end + delta, 2)
                break
    return sc, changes
