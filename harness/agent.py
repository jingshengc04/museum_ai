"""The script-writing agent, one stage at a time, with every call archived.

Stages (each = one structured-output Claude call):
    S0  identify     photo → what is it, which prepared exhibit, what does the visitor see
    S1  digest       knowledge pack (+ photo) → material sheet, length decision
    S1b assets       material + photo → reference-image plan (restoration, character sheet, views)
    S2  concept      material + photo + reference images → 3 concepts, choose one
    S3  script       … → structured shooting script (edits its previous draft on revision)
    S4  review       script + concept + pack + rendered Seedance requests → claim audit, issues, scores

System prompt = prompts/<stage>[.<variant>].md. Every call writes runs/<run>/<NN_stage>/ with the request,
raw text, thinking summary, output, usage and prompt hash, and is cached by a hash of its full input
(images included), so re-running an unchanged stage is free. `sample` gives independent draws for A/B tests.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import time
import traceback
from pathlib import Path

from pydantic import BaseModel

import schemas
import seedance

HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "prompts"
KNOWLEDGE = HERE / "knowledge"
RUNS = HERE / "runs"
CACHE = HERE / "runs" / "_cache"

MODEL = os.environ.get("HARNESS_MODEL", "claude-opus-5-5")
PRICE_PER_MTOK = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50)}
FRESH: set[str] = set()   # stages that must skip the cache this run ("all" = every stage)
SAMPLE = 0                # independent draw number; part of the cache key
EMIT = None               # callable(event: dict) for the live progress feed (set by run.py)
KEYWORD_MODEL = os.environ.get("KEYWORD_MODEL", MODEL)  # the side keyword request; can be a cheaper model
USER_INPUT = ""           # free text from the user (e.g. "选15s"), appended as "User input: ..." to the stages below
USER_INPUT_STAGES = {"s1_digest", "s1b_assets", "s2_concept", "s3_script", "s4_review"}
MEDIA = {".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif"}


def emit(stage: str, **event) -> None:
    if EMIT:
        EMIT({"stage": stage, **event})


def _load_env() -> None:
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            key, _, value = line.strip().partition("=")
            if key and not key.startswith("#"):
                os.environ.setdefault(key, value)


_load_env()


# ---------- exhibits, packs, images ----------

NO_PACK = False           # --no-pack: ignore every prepared exhibit (search-only test)
ADHOC: dict[str, dict] = {}  # exhibits recognised from the photo that have no prepared pack
NO_PACK_TEXT = ("(No prepared knowledge pack for this exhibit. The web research findings are the only allowed "
                "sources; every fact must cite the URL of a finding.)")


def exhibits() -> list[dict]:
    if NO_PACK:
        return []
    return [json.loads(p.read_text()) for p in sorted(KNOWLEDGE.glob("*/meta.json"))]


def meta(exhibit_id: str) -> dict:
    if exhibit_id in ADHOC:
        return ADHOC[exhibit_id]
    return json.loads((KNOWLEDGE / exhibit_id / "meta.json").read_text())


def pack(exhibit_id: str) -> str:
    if exhibit_id in ADHOC:
        return NO_PACK_TEXT
    return (KNOWLEDGE / exhibit_id / "pack.md").read_text()


def register_adhoc(ident: schemas.Identification) -> str:
    """An exhibit known only from the photo: its name and museum come from S0, its facts only from research."""
    slug = re.sub(r"[^a-z0-9]+", "-", ident.short_name.lower()).strip("-")[:30] or "exhibit"
    exhibit_id = f"adhoc-{slug}"
    museum, _, location = (ident.museum or "").partition(",")
    ADHOC[exhibit_id] = {"id": exhibit_id, "name": ident.short_name, "museum": museum.strip() or "unknown museum",
                         "location": location.strip() or "unknown gallery", "looks_like": ident.recognized_as}
    return exhibit_id


def existing_assets(exhibit_id: str) -> list[dict]:
    """Reference images already made for this exhibit (knowledge/<id>/assets/assets.json)."""
    if exhibit_id in ADHOC:
        return []
    reg = KNOWLEDGE / exhibit_id / "assets" / "assets.json"
    if not reg.exists():
        return []
    items = json.loads(reg.read_text())
    for item in items:
        item["path"] = str(reg.parent / item["file"])
    return items


def image_block(path: Path | str) -> dict:
    path = Path(path)
    return {"type": "image", "source": {"type": "base64", "media_type": MEDIA.get(path.suffix.lower(), "image/jpeg"),
                                        "data": base64.standard_b64encode(path.read_bytes()).decode()}}


def _text(t: str) -> dict:
    return {"type": "text", "text": t}


def photo_blocks(photo: Path | None) -> list[dict]:
    if not photo:
        return [_text("(No visitor photo for this run.)")]
    return [_text("The visitor's photo:"), image_block(photo)]


def asset_blocks(exhibit_id: str) -> list[dict]:
    items = existing_assets(exhibit_id)
    if not items:
        return [_text("(No reference images exist yet for this exhibit; any you need must be planned as 'generate'.)")]
    blocks = [_text("Reference images that already exist for this exhibit:")]
    for a in items:
        info = {k: a[k] for k in ("id", "kind", "style", "has_text_labels", "description")}
        blocks += [_text(json.dumps(info, ensure_ascii=False)), image_block(a["path"])]
    return blocks


# ---------- one stage call ----------

def prompt_file(stage: str, variant: str = "") -> Path:
    return PROMPTS / (f"{stage}.{variant}.md" if variant else f"{stage}.md")


def _client():
    import anthropic

    return anthropic.Anthropic()


def _content_for_key(content) -> object:
    """User content with image bytes replaced by their hash (for the cache key and the log)."""
    if isinstance(content, str):
        return content
    out = []
    for b in content:
        if b.get("type") == "image":
            out.append({"type": "image", "sha256": hashlib.sha256(b["source"]["data"].encode()).hexdigest()[:16]})
        else:
            out.append(b)
    return out


def call(stage: str, content, schema: type[BaseModel], run_dir: Path, index: int,
         effort: str = "high", variant: str = "", tools: list[dict] | None = None, model: str | None = None,
         prompt_stage: str | None = None) -> BaseModel:
    pf = prompt_file(prompt_stage or stage, variant)
    system = pf.read_text()
    out_dir = run_dir / f"{index:02d}_{stage}"
    out_dir.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        content = [_text(content)]
    if USER_INPUT and stage in USER_INPUT_STAGES:
        content = content + [_text(f"User input: {USER_INPUT}")]

    logged = _content_for_key(content)
    request = {"model": model or MODEL, "effort": effort, "prompt_file": str(pf.relative_to(HERE)),
               "prompt_sha": hashlib.sha256(system.encode()).hexdigest()[:8], "sample": SAMPLE,
               "system": system, "user": logged, "schema": schema.__name__, "tools": tools or []}
    key = hashlib.sha256(json.dumps([request, schema.model_json_schema()], sort_keys=True, default=str).encode()).hexdigest()[:20]
    (out_dir / "request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2))
    (out_dir / "user.md").write_text("\n\n".join(b["text"] if b.get("type") == "text" else f"[image {b.get('sha256')}]" for b in logged))

    cached = CACHE / f"{stage}-{key}.json"
    emit(stage, type="stage_start")
    if cached.exists() and not (FRESH & {stage, "all"}):
        record = json.loads(cached.read_text())
        record["cached"] = True
        for e in record.get("events", []):
            emit(stage, replay=True, **e)
    else:
        try:
            record = _with_retries(lambda: _live_call(system, content, schema, effort, out_dir, stage, tools, model), stage)
        except Exception as e:
            (out_dir / "error.json").write_text(json.dumps(
                {"type": type(e).__name__, "message": str(e), "traceback": traceback.format_exc()}, indent=2))
            raise
        CACHE.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps(record, ensure_ascii=False, indent=2))
        record["cached"] = False

    emit(stage, type="stage_end", cached=record["cached"])
    (out_dir / "output.json").write_text(json.dumps(record["output"], ensure_ascii=False, indent=2))
    (out_dir / "thinking.md").write_text(record.get("thinking") or "(no thinking summary)")
    (out_dir / "events.json").write_text(json.dumps(record.get("events", []), ensure_ascii=False, indent=2))
    if record.get("tool_log"):
        (out_dir / "tools.json").write_text(json.dumps({"retrieved_urls": record.get("retrieved_urls", []),
                                                        "calls": record["tool_log"]}, ensure_ascii=False, indent=2))
    (out_dir / "meta.json").write_text(json.dumps(
        {"prompt_file": request["prompt_file"], "prompt_sha": request["prompt_sha"], "sample": SAMPLE,
         **{k: record.get(k) for k in ("usage", "cost_usd", "seconds", "stop_reason", "cached", "request_id")}}, indent=2))
    return schema.model_validate(record["output"])


def _transient(e: Exception) -> bool:
    import anthropic
    if isinstance(e, (anthropic.APITimeoutError, anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.InternalServerError)):
        return True
    if isinstance(e, anthropic.APIStatusError) and e.status_code in (429, 500, 502, 503, 504, 529):
        return True
    return type(e).__name__ in ("ReadTimeout", "RemoteProtocolError", "ConnectError")


def _with_retries(fn, stage: str, tries: int = 3):
    for attempt in range(tries):
        try:
            return fn()
        except Exception as e:
            if attempt + 1 == tries or not _transient(e):
                raise
            wait = 10 * (attempt + 1)
            emit(stage, type="retry", text=f"{type(e).__name__}, retrying in {wait}s")
            print(f"  ↻ {stage}: {type(e).__name__}, retrying in {wait}s")
            time.sleep(wait)


def _block_dict(b) -> dict:
    return b.model_dump() if hasattr(b, "model_dump") else dict(b)


def _live_call(system: str, content: list, schema: type[BaseModel], effort: str, out_dir: Path, stage: str,
               tools: list[dict] | None = None, model: str | None = None) -> dict:
    model = model or MODEL
    started = time.time()
    events: list[dict] = []
    buf, thinking_seen = "", False
    messages = [{"role": "user", "content": content}]
    tool_log: list[dict] = []
    retrieved: list[str] = []
    usage_in = usage_out = 0

    def push(event: dict) -> None:
        event = {"t": round(time.time() - started, 2), **event}
        events.append(event)
        emit(stage, **event)

    def on_block(b: dict) -> None:
        kind = b.get("type")
        if kind == "server_tool_use":
            tool_log.append({"tool": b.get("name"), "input": b.get("input")})
            q = (b.get("input") or {}).get("query") or (b.get("input") or {}).get("url")
            push({"type": "search" if b.get("name") == "web_search" else "fetch", "text": q})
        elif kind in ("web_search_tool_result", "web_fetch_tool_result"):
            c = b.get("content")
            items = c if isinstance(c, list) else [c] if isinstance(c, dict) else []
            found = []
            for it in items:
                if isinstance(it, dict) and it.get("url"):
                    found.append({"url": it["url"], "title": it.get("title", "")})
                    retrieved.append(it["url"])
                elif isinstance(it, dict) and it.get("error_code"):
                    found.append({"error": it["error_code"]})
            tool_log.append({"result": kind, "items": found})
            for f in found[:3]:
                if f.get("url"):
                    push({"type": "source", "text": f.get("title") or f["url"], "url": f["url"]})

    response = None
    for _round in range(6):  # pause_turn continuations
        kwargs = dict(
            model=model, max_tokens=64000, system=system, messages=messages,
            thinking={"type": "adaptive", "display": "summarized"},
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": strict_schema(schema)}},
        )
        if tools:
            kwargs["tools"] = tools
        with _client().messages.stream(**kwargs) as stream:
            for ev in stream:
                et = getattr(ev, "type", "")
                if et == "content_block_stop" and tools:
                    try:
                        on_block(_block_dict(stream.current_message_snapshot.content[ev.index]))
                    except Exception:
                        pass
                if et != "content_block_delta":
                    continue
                kind = getattr(ev.delta, "type", "")
                if kind == "thinking_delta" and not thinking_seen:
                    thinking_seen = True
                    push({"type": "thinking"})
                elif kind == "text_delta" and not buf:
                    buf = "started"
                    push({"type": "writing"})
            response = stream.get_final_message()
        usage_in += response.usage.input_tokens
        usage_out += response.usage.output_tokens
        if response.stop_reason != "pause_turn":
            break
        messages = messages + [{"role": "assistant", "content": response.content}]

    blocks = response.content
    last_tool = max([i for i, b in enumerate(blocks) if b.type.endswith("_tool_result")], default=-1)
    text = "".join(b.text for b in blocks[last_tool + 1:] if b.type == "text")
    (out_dir / "raw.txt").write_text(text)
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined this request: {response.stop_details}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Output hit max_tokens before finishing")
    thinking = "\n\n".join(b.thinking for b in blocks if b.type == "thinking" and b.thinking)
    output = schema.model_validate_json(text).model_dump()

    price_in, price_out = PRICE_PER_MTOK.get(model, (0, 0))
    searches = sum(1 for t in tool_log if t.get("tool") == "web_search")
    return {
        "output": output,
        "events": events,
        "thinking": thinking,
        "tool_log": tool_log,
        "retrieved_urls": sorted(set(retrieved)) if tools else None,
        "usage": {"input_tokens": usage_in, "output_tokens": usage_out, "web_searches": searches},
        "cost_usd": round((usage_in * price_in + usage_out * price_out) / 1e6 + searches * 0.01, 4),
        "seconds": round(time.time() - started, 1),
        "stop_reason": response.stop_reason,
        "request_id": getattr(response, "_request_id", None) or getattr(response, "id", None),
    }


def strict_schema(schema: type[BaseModel]) -> dict:
    """Pydantic JSON schema → structured-outputs schema (every object closed, every field required)."""
    raw = schema.model_json_schema()
    defs = raw.pop("$defs", {})

    def fix(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return fix(defs[node["$ref"].split("/")[-1]])
            props = node.get("properties")
            node = {k: fix(v) for k, v in node.items() if k not in ("title", "default", "properties")}
            if props is not None:  # property names are data, never strip them
                node["properties"] = {name: fix(sub) for name, sub in props.items()}
            if node.get("type") == "object":
                node["additionalProperties"] = False
                node["required"] = list(node.get("properties", {}))
            return node
        if isinstance(node, list):
            return [fix(n) for n in node]
        return node

    return fix(raw)


def _j(model: BaseModel) -> str:
    return model.model_dump_json(indent=2)


# ---------- the stages ----------

def s0_identify(photo: Path, run_dir: Path, variant: str = "") -> schemas.Identification:
    listing = [{k: e[k] for k in ("id", "name", "museum", "location", "looks_like")} for e in exhibits()]
    content = photo_blocks(photo) + [_text(f"Exhibits we have prepared material for:\n{json.dumps(listing, ensure_ascii=False, indent=2)}")]
    return call("s0_identify", content, schemas.Identification, run_dir, 0, effort="medium", variant=variant)


def keyword_batch(label: str, material: str, run_dir: Path) -> schemas.KeywordBatch:
    """Side request: 5-10 keywords for the progress display, copied from the material given. Runs in a
    background thread; the core agent never waits for it."""
    return call(f"kw_{label}", [_text(material)], schemas.KeywordBatch, run_dir, 90, effort="low",
                variant="", model=KEYWORD_MODEL, prompt_stage="keywords")


SEARCH_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 5},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 4, "max_content_tokens": 6000},
]


def s0b_research(exhibit_id: str, ident: schemas.Identification | None, photo: Path | None, run_dir: Path,
                 variant: str = "") -> schemas.Research:
    m = meta(exhibit_id)
    seen = (f"What the photo shows: {ident.recognized_as} {ident.what_is_visible}\nVisitor interest: {ident.visitor_interest}"
            if ident else "No photo for this run.")
    content = photo_blocks(photo) + [_text(
        f"Exhibit: {m['name']} — {m['location']}, {m['museum']}\n{seen}\n\n"
        f"Our prepared knowledge pack (verify it and find what it lacks; it may be empty or incomplete):\n"
        f"<knowledge_pack>\n{pack(exhibit_id)}\n</knowledge_pack>")]
    return call("s0b_research", content, schemas.Research, run_dir, 0, effort="medium", variant=variant, tools=SEARCH_TOOLS)


def s1_digest(exhibit_id: str, photo: Path | None, photo_notes: str, run_dir: Path, variant: str = "",
              previous: schemas.MaterialSheet | None = None, feedback: str = "",
              research: schemas.Research | None = None) -> schemas.MaterialSheet:
    m = meta(exhibit_id)
    found = ""
    if research is not None:
        found = ("\n\n<web_research>\n" + json.dumps({k: research.model_dump()[k] for k in
                 ("sources", "findings", "agrees_with_pack", "conflicts", "not_found")}, ensure_ascii=False, indent=2)
                 + "\n</web_research>")
    content = photo_blocks(photo) + [_text(
        f"Exhibit: {m['name']} — {m['location']}, {m['museum']}\n"
        f"Notes on the visitor's photo: {photo_notes or 'none'}\n\n"
        f"<knowledge_pack>\n{pack(exhibit_id)}\n</knowledge_pack>{found}")]
    if previous is not None:
        content.append(_text(f"<previous_material>\n{_j(previous)}\n</previous_material>\n\n"
                             f"<check_feedback>\nFix these problems in the previous material, keep the rest:\n{feedback}\n</check_feedback>"))
    return call("s1_digest", content, schemas.MaterialSheet, run_dir, 11 if previous is not None else 1, variant=variant)


def s1b_assets(exhibit_id: str, sheet: schemas.MaterialSheet, photo: Path | None, run_dir: Path,
               variant: str = "") -> schemas.AssetPlan:
    m = meta(exhibit_id)
    content = photo_blocks(photo) + asset_blocks(exhibit_id) + [_text(
        f"Exhibit: {m['name']} — {m['location']}, {m['museum']}\n"
        f"Appearance notes from the pack:\n{_appearance(exhibit_id)}\n\n<material>\n{_j(sheet)}\n</material>")]
    return call("s1b_assets", content, schemas.AssetPlan, run_dir, 2, effort="medium", variant=variant)


def s2_concept(exhibit_id: str, sheet: schemas.MaterialSheet, plan: schemas.AssetPlan, photo: Path | None,
               photo_notes: str, run_dir: Path, variant: str = "") -> schemas.ConceptSet:
    content = photo_blocks(photo) + asset_blocks(exhibit_id) + [_text(
        f"Notes on the visitor's photo: {photo_notes or 'none'}\nFilm length: {sheet.duration_s} seconds\n\n"
        f"<material>\n{_j(sheet)}\n</material>\n\n<asset_plan>\n{_j(plan)}\n</asset_plan>")]
    return call("s2_concept", content, schemas.ConceptSet, run_dir, 3, variant=variant)


def s3_script(exhibit_id: str, sheet: schemas.MaterialSheet, plan: schemas.AssetPlan, concept: schemas.Concept,
              photo: Path | None, photo_notes: str, run_dir: Path, attempt: int = 0,
              previous: schemas.Script | None = None, feedback: str = "", variant: str = "") -> schemas.Script:
    content = photo_blocks(photo) + asset_blocks(exhibit_id) + [_text(
        f"Exhibit id: {exhibit_id}\nNotes on the visitor's photo: {photo_notes or 'none'}\n"
        f"Film length: {sheet.duration_s} seconds\n\n"
        f"<material>\n{_j(sheet)}\n</material>\n\n<asset_plan>\n{_j(plan)}\n</asset_plan>\n\n"
        f"<concept>\n{_j(concept)}\n</concept>")]
    if previous is not None:
        content.append(_text(
            f"<previous_script>\n{_j(previous)}\n</previous_script>\n\n"
            f"<review_feedback>\nEdit the previous script to fix these points. Change only what each point requires "
            f"(plus anything that change forces, such as subtitles and timings); copy everything else unchanged.\n"
            f"{feedback}\n</review_feedback>"))
        rendered = [seedance.render(previous, i) for i in range(len(previous.segments))]
        content.append(_text("<rendered_requests>\n" + json.dumps(
            [{k: r[k] for k in ("prompt", "direction_words", "prompt_parts")} for r in rendered], ensure_ascii=False, indent=2)
            + f"\n</rendered_requests>\n(Direction-word cap per request: {seedance.MAX_DIRECTION_WORDS}, quoted narration not counted.)"))
    return call("s3_script", content, schemas.Script, run_dir, 4 + attempt * 2, variant=variant)


def s4_review(exhibit_id: str, script: schemas.Script, sheet: schemas.MaterialSheet, concept: schemas.Concept,
              photo: Path | None, photo_notes: str, check_problems: list[str], run_dir: Path, attempt: int = 0,
              previous: schemas.Review | None = None, variant: str = "") -> schemas.Review:
    requests = [seedance.render(script, i) for i in range(len(script.segments))]
    content = photo_blocks(photo) + asset_blocks(exhibit_id) + [_text(
        f"Notes on the visitor's photo: {photo_notes or 'none'}\n\n"
        f"<knowledge_pack>\n{pack(exhibit_id)}\n</knowledge_pack>\n\n"
        f"<material>\n{_j(sheet)}\n</material>\n\n<concept>\n{_j(concept)}\n</concept>\n\n"
        f"<script>\n{_j(script)}\n</script>\n\n"
        f"<seedance_requests>\n{json.dumps(requests, ensure_ascii=False, indent=2)}\n</seedance_requests>\n\n"
        f"Automatic checks found: {json.dumps(check_problems, ensure_ascii=False) if check_problems else 'nothing'}")]
    if previous is not None:
        content.append(_text(f"<previous_review>\n{_j(previous)}\n</previous_review>"))
    return call("s4_review", content, schemas.Review, run_dir, 5 + attempt * 2, variant=variant)


def _appearance(exhibit_id: str) -> str:
    text = pack(exhibit_id)
    i = text.find("## Appearance")
    return text[i:].split("\n## ")[0] if i >= 0 else "(none)"
