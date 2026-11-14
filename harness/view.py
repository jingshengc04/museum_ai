"""Render a run as a readable conversation: every Claude call with its system prompt, input (images
included), thinking summary and answer.

    uv run python view.py runs/1114-173547-hope-v1.2     # writes <run>/transcript.html
    uv run python view.py latest                         # newest run
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE_NAMES = {
    "s0_identify": "S0 · Identify the exhibit from the photo",
    "s0b_research": "S0b · Web research (search + fetch tools)",
    "s1_digest": "S1 · Digest the knowledge pack",
    "kw_identify": "Keywords (side request, after identify)",
    "kw_research": "Keywords (side request, after research)",
    "s1b_assets": "S1b · Plan reference images",
    "s2_concept": "S2 · Three concepts, choose one",
    "s3_script": "S3 · Write the script",
    "s4_review": "S4 · Review",
}


def known_images() -> dict[str, Path]:
    """sha256(base64)[:16] → file, for every image the agent could have been shown."""
    out = {}
    for p in list((HERE / "photos").glob("*")) + list((HERE / "knowledge").glob("*/assets/*")):
        if p.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg", ".gif"):
            b64 = base64.standard_b64encode(p.read_bytes()).decode()
            out[hashlib.sha256(b64.encode()).hexdigest()[:16]] = p
    return out


def esc(t: str) -> str:
    return html.escape(t)


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "latest"
    if arg == "latest":
        run = max((p for p in (HERE / "runs").iterdir() if p.is_dir() and not p.name.startswith("_")), key=lambda p: p.name)
    else:
        run = Path(arg).resolve()
    images = known_images()
    used: dict[str, Path] = {}
    blocks = []

    for stage_dir in sorted(p for p in run.iterdir() if p.is_dir()):
        req_f = stage_dir / "request.json"
        if not req_f.exists():
            continue
        req = json.loads(req_f.read_text())
        stage = stage_dir.name.split("_", 1)[1]
        meta = json.loads((stage_dir / "meta.json").read_text()) if (stage_dir / "meta.json").exists() else {}
        out_f, think_f, err_f = stage_dir / "output.json", stage_dir / "thinking.md", stage_dir / "error.json"

        user_parts = []
        for b in req["user"]:
            if b.get("type") == "image":
                h = b.get("sha256", "")
                if h in images:
                    used[h] = images[h]
                    user_parts.append(f'<img class="pic" data-img="{h}" alt="{esc(images[h].name)}"><div class="cap">{esc(images[h].name)}</div>')
                else:
                    user_parts.append('<div class="cap">[image]</div>')
            else:
                user_parts.append(f"<pre>{esc(b.get('text', ''))}</pre>")

        extra = ""
        if (stage_dir / "tools.json").exists():
            tj = json.loads((stage_dir / "tools.json").read_text())
            rows = "".join(f"<li><b>{esc(c['tool'])}</b> {esc(json.dumps(c.get('input'), ensure_ascii=False))}</li>" for c in tj["calls"] if c.get("tool"))
            extra += f"<details open><summary>Tool calls ({sum(1 for c in tj['calls'] if c.get('tool'))}) · {len(tj['retrieved_urls'])} URLs returned</summary><ul>{rows}</ul></details>"
        for name in ("checks.json", "feedback.md", "nudged.json"):
            f = stage_dir / name
            if f.exists() and f.read_text().strip() not in ("", "[]"):
                extra += f"<details open><summary>{name}</summary><pre>{esc(f.read_text())}</pre></details>"

        cost = "cached" if meta.get("cached") else f"${meta.get('cost_usd') or 0:.3f}, {meta.get('seconds')}s"
        title = STAGE_NAMES.get(stage, stage)
        blocks.append(f"""
<section>
  <h2>{esc(stage_dir.name[:2])} · {esc(title)}</h2>
  <div class="meta">{esc(req['prompt_file'])} @ {esc(req.get('prompt_sha', ''))} · effort {esc(req['effort'])} · {esc(cost)}</div>
  <details><summary>System prompt</summary><pre>{esc(req['system'])}</pre></details>
  <div class="msg user"><div class="who">Input to Claude</div>{''.join(user_parts)}</div>
  {f'<details class="think"><summary>Thinking summary</summary><pre>{esc(think_f.read_text())}</pre></details>' if think_f.exists() else ''}
  <div class="msg claude"><div class="who">Claude's answer</div><pre>{esc(out_f.read_text()) if out_f.exists() else esc(err_f.read_text() if err_f.exists() else '(no output)')}</pre></div>
  {extra}
</section>""")

    feed = []
    if (run / "events.jsonl").exists():
        for line in (run / "events.jsonl").read_text().splitlines():
            e = json.loads(line)
            if e.get("type") == "keywords_batch":
                for k in e.get("keywords", []):
                    feed.append({"t_run": e["t_run"], "stage": e["stage"], "type": "highlight", "kind": k.get("kind"), "text": k.get("text")})
                continue
            if e.get("type") in ("highlight", "stage_start", "search", "source", "image_jobs_ready"):
                if e.get("type") == "search":
                    e = {**e, "kind": "search", "text": f"searching: {e.get('text')}"}
                elif e.get("type") == "source":
                    e = {**e, "kind": "source"}
                elif e.get("type") == "image_jobs_ready":
                    e = {**e, "kind": "images", "text": f"{e.get('count')} images can start (~${e.get('est_usd')})"}
                feed.append({k: e.get(k) for k in ("t_run", "stage", "type", "kind", "text")})
    feed_html = ""
    if feed:
        feed_html = """<section><h2>Progress feed</h2><div class="meta">Keywords as they popped up during the run. Replay uses the recorded timings.</div>
<button id="replay">Replay</button> <span id="clock" class="meta"></span><div id="feed"></div></section>"""
    img_js = json.dumps({h: f"data:image/{p.suffix.lstrip('.').replace('jpg', 'jpeg')};base64,{base64.standard_b64encode(p.read_bytes()).decode()}" for h, p in used.items()})
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent transcript</title>
<style>
:root {{ --bg:#f7f6f2; --fg:#1d1d1b; --muted:#6b6a65; --card:#fff; --line:#e3e1da; --user:#eef3fb; --claude:#f3efe6; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#16161a; --fg:#e8e6e1; --muted:#9a988f; --card:#1f1f24; --line:#33333a; --user:#1c2433; --claude:#2a2620; }} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.5 -apple-system, system-ui, sans-serif; margin:0; padding:24px 16px; }}
main {{ max-width:980px; margin:auto; }}
h1 {{ font-size:22px; margin:0 0 4px; }} h2 {{ font-size:17px; margin:0 0 4px; }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; margin:16px 0; }}
.meta, .cap {{ color:var(--muted); font-size:12px; }}
pre {{ white-space:pre-wrap; word-break:break-word; font:12.5px/1.45 ui-monospace, Menlo, monospace; margin:6px 0; }}
.msg {{ border-radius:8px; padding:10px 12px; margin:10px 0; }} .user {{ background:var(--user); }} .claude {{ background:var(--claude); }}
.who {{ font-weight:600; font-size:13px; }}
#feed {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; min-height:40px; }}
.chip {{ border:1px solid var(--line); border-radius:999px; padding:4px 10px; font-size:13px; background:var(--user); animation:pop .35s ease-out; }}
.chip b {{ font-weight:600; }} .chip i {{ color:var(--muted); font-style:normal; font-size:11px; margin-right:6px; }}
.stagechip {{ flex-basis:100%; color:var(--muted); font-size:12px; margin-top:4px; }}
@keyframes pop {{ from {{ transform:scale(.6); opacity:0; }} to {{ transform:scale(1); opacity:1; }} }}
button {{ font:inherit; padding:4px 12px; border-radius:6px; border:1px solid var(--line); background:var(--card); color:var(--fg); cursor:pointer; }}
.pic {{ max-width:100%; max-height:260px; border-radius:6px; margin-top:6px; }}
details {{ margin:6px 0; }} summary {{ cursor:pointer; color:var(--muted); font-size:13px; }}
</style></head><body><main>
<h1>Agent transcript</h1><div class="meta">{esc(run.name)} · model calls in order · images are what the model actually saw</div>
{feed_html}
{''.join(blocks)}
</main>
<script>const FEED={json.dumps(feed, ensure_ascii=False)};
const NAMES={json.dumps(STAGE_NAMES)};
function chip(e){{const d=document.createElement('div');
 if(e.type==='stage_start'){{d.className='stagechip';d.textContent=NAMES[e.stage]||e.stage;}}
 else{{d.className='chip';d.innerHTML='<i>'+e.kind+'</i><b></b>';d.querySelector('b').textContent=e.text;}}
 document.getElementById('feed').appendChild(d);}}
function showAll(){{const f=document.getElementById('feed');if(!f)return;f.innerHTML='';FEED.forEach(chip);}}
let timers=[];
function replay(){{timers.forEach(clearTimeout);timers=[];document.getElementById('feed').innerHTML='';
 const speed=Math.max(1,(FEED.length?FEED[FEED.length-1].t_run:1)/40);
 FEED.forEach(e=>timers.push(setTimeout(()=>{{chip(e);document.getElementById('clock').textContent=e.t_run.toFixed(1)+'s (x'+speed.toFixed(0)+')';}},e.t_run*1000/speed)));}}
if(FEED.length){{showAll();document.getElementById('replay').onclick=replay;}}
const IMG={img_js};document.querySelectorAll('img[data-img]').forEach(i=>{{i.src=IMG[i.dataset.img]||''}});</script>
</body></html>"""
    target = run / "transcript.html"
    target.write_text(page)
    print(target)


if __name__ == "__main__":
    main()
