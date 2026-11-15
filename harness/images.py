"""Turn the S1b reference-image plan into image-generation jobs: one initial image + one text prompt each.

Everything about generation is fixed here in code (endpoint, price, initial image = the visitor photo); the LLM only
writes the prompt, which states the view, the angle and what to avoid. Jobs can start as soon as S1b finishes, in
parallel with concept and script writing (S2-S4). Not executed here; `image_jobs.json` is the hand-off.
"""
from __future__ import annotations

import os

import schemas

ENDPOINT = os.environ.get("IMAGE_ENDPOINT", "fal-ai/nano-banana-pro/edit")
USD_PER_IMAGE = 0.15  # nano-banana-pro/edit, research/round1
# Seedance's partner moderation rejects any reference image that may show a real person's likeness
# ("content_policy_violation: partner_validation_failed"), and a visitor photo is usually full of people.
NO_PEOPLE = ("No people anywhere in the image: the space is empty, every visitor and figure removed, including any "
             "reflection, shadow or silhouette of a person on glass, metal or polished surfaces.")


def jobs(plan: schemas.AssetPlan, existing: list[dict], photo: bool) -> list[dict]:
    have = {a["id"] for a in existing}
    initial = ["<visitor_photo>"] if photo else []  # fixed in code: the LLM never configures generation
    out = []
    for im in plan.images:
        if im.id in have:
            continue
        out.append({
            "id": im.id,
            "kind": im.kind,
            "endpoint": ENDPOINT,
            "input": {
                "image_urls": initial,
                "prompt": f"{im.prompt.strip()} {NO_PEOPLE} Avoid: {im.must_avoid.strip()}",
            },
            "purpose": im.purpose,
            "est_usd": USD_PER_IMAGE,
            **({} if initial else {"note": "no initial image: run as text-to-image"}),
        })
    return out


def total(job_list: list[dict]) -> float:
    return round(sum(j.get("est_usd", 0) for j in job_list), 2)
