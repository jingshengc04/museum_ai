"""Check keys and endpoints with free, read-only calls: nothing here generates anything or spends credits."""
from __future__ import annotations

import os
import uuid

import httpx

from . import config, video


def elevenlabs() -> list[str]:
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        return ["FAIL  ELEVENLABS_API_KEY is not set"]
    headers, api, out = {"xi-api-key": key}, "https://api.elevenlabs.io/v1", []
    plan = httpx.get(f"{api}/user/subscription", headers=headers, timeout=20)
    if plan.status_code != 200:
        return [f"FAIL  key rejected (HTTP {plan.status_code}): {plan.text[:160]}"]
    data = plan.json()
    left = data["character_limit"] - data["character_count"]
    out.append(f"ok    key accepted: {data['tier']} plan, {left:,} of {data['character_limit']:,} credits left")
    models = {m["model_id"] for m in httpx.get(f"{api}/models", headers=headers, timeout=20).json() if m.get("can_do_text_to_speech")}
    out.append(f"{'ok  ' if config.ELEVEN_MODEL in models else 'FAIL'}  model {config.ELEVEN_MODEL} {'is' if config.ELEVEN_MODEL in models else 'is NOT'} available for speech")
    voice = httpx.get(f"{api}/voices/{config.ELEVEN_VOICE_ID}", headers=headers, timeout=20)
    name = voice.json().get("name") if voice.status_code == 200 else None
    out.append(f"ok    default voice exists: {name}" if name else f"FAIL  default voice {config.ELEVEN_VOICE_ID} not found (HTTP {voice.status_code})")
    return out


def fal() -> list[str]:
    key = os.environ.get("FAL_KEY", "")
    if not key:
        return ["FAIL  FAL_KEY is not set"]
    out = []
    # Asking for the status of a request that does not exist costs nothing: a bad key gets 401, a good one 404.
    app = "/".join(config.VIDEO_MODEL.split("/")[:2])
    probe = httpx.get(f"https://queue.fal.run/{app}/requests/{uuid.uuid4()}/status", headers={"Authorization": f"Key {key}"}, timeout=20)
    if probe.status_code == 401:
        out.append(f"FAIL  key rejected: {probe.text[:160]}")
    else:
        out.append(f"ok    key accepted (HTTP {probe.status_code} for an unknown request, as expected). Balance cannot be read without spending.")
    schema = httpx.get("https://fal.ai/api/openapi/queue/openapi.json", params={"endpoint_id": config.VIDEO_MODEL}, timeout=30)
    if schema.status_code != 200:
        out.append(f"FAIL  model {config.VIDEO_MODEL} not found (HTTP {schema.status_code})")
        return out
    schemas = schema.json()["components"]["schemas"]
    fields = next(v["properties"] for k, v in schemas.items() if k.lower().endswith("input") and "properties" in v)
    request = video.request_arguments(video.ShotPlan(_probe_shot(), config.VIDEO_MAX_SECONDS, "x", [], "generate"), ["https://example.com/x.png"])
    missing = sorted(set(request) - set(fields))
    out.append(f"FAIL  model no longer takes: {missing}" if missing else f"ok    model {config.VIDEO_MODEL} exists and takes every field we send")
    for field, value in request.items():
        allowed = fields.get(field, {}).get("enum")
        if allowed and value not in allowed:
            out.append(f"FAIL  {field}={value!r} is not one of {allowed}")
    film = video.worst_case_usd(2) if config.NATIVE_AUDIO else video.worst_case_usd(9)
    limit = f"${config.MAX_FAL_USD:.2f}" if config.MAX_FAL_USD > 0 else "off"
    out.append(f"note  one film costs about ${film:.2f} at {config.VIDEO_RESOLUTION}; the per-film limit MAX_FAL_USD is {limit}")
    return out


def _probe_shot():
    from .storyboard import Shot

    return Shot(id=1, narration="x", action="x", camera="x", location="x", mood="x")


def anthropic() -> list[str]:
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        return ["FAIL  ANTHROPIC_API_KEY is not set (story writing and photo recognition stay in mock mode)"]
    import anthropic as sdk

    try:
        model = sdk.Anthropic().models.retrieve(config.STORY_MODEL)  # reading a model's details is not billed
    except sdk.AuthenticationError:
        return ["FAIL  key rejected"]
    except sdk.NotFoundError:
        return [f"FAIL  key accepted, but model {config.STORY_MODEL} is not available to it"]
    except sdk.APIError as error:
        return [f"FAIL  {error}"]
    return [f"ok    key accepted, model {model.id} is available"]


def run() -> bool:
    good = True
    services = [("fal (video and sound)" if config.NATIVE_AUDIO else "fal (video)", fal), ("Anthropic (story)", anthropic)]
    if not config.NATIVE_AUDIO:  # ElevenLabs is only used with a silent video model
        services.insert(0, ("ElevenLabs (voice)", elevenlabs))
    for name, check in services:
        try:
            lines = check()
        except httpx.HTTPError as error:
            lines = [f"FAIL  could not reach the service: {error}"]
        print(name)
        for line in lines:
            print(f"  {line}")
        good = good and not any(line.startswith("FAIL") for line in lines)
    return good
