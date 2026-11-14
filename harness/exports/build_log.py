"""Build the review log: every Claude call the harness made, every workflow agent (prompt + tool calls),
and every prompt version's full text.

    uv run python exports/build_log.py      # writes exports/CALL_LOG.md and exports/stats.json
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RUNS = HERE / "runs"
OUT = HERE / "exports"
SESSION = Path("/Users/liangkaicheng.1/.claude/projects/-Users-liangkaicheng-1-Documents-Imperial-AI-Hackathon-2026/ef02991d-9b2f-4d51-94c5-e0811a7cd51b")
WORKFLOWS = {
    "wf_9afd28b2-ff4": "Round 1: research, critique, test packs",
    "wf_84a4fb3f-e05": "Round 2: diagnose v1.2, blind v0 vs v1, synthesise",
    "wf_24f28f18-99b": "Round 3 (first launch): failed at start, wrong args, 0 agents",
    "wf_ff62ae98-9f1": "Round 3: blind four-way ranking, decide",
}
KEY = re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}")


def redact(t: str) -> str:
    return KEY.sub("sk-ant-…REDACTED", t)


def runs() -> list[dict]:
    out = []
    for run in sorted(p for p in RUNS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        calls = []
        for stage_dir in sorted(p for p in run.iterdir() if p.is_dir()):
            if not (stage_dir / "request.json").exists():
                continue
            req = json.loads((stage_dir / "request.json").read_text())
            meta = json.loads((stage_dir / "meta.json").read_text()) if (stage_dir / "meta.json").exists() else {}
            imgs = sum(1 for b in req["user"] if isinstance(b, dict) and b.get("type") == "image") if isinstance(req["user"], list) else 0
            u = meta.get("usage") or {}
            calls.append({
                "folder": stage_dir.name, "stage": stage_dir.name.split("_", 1)[1],
                "prompt": req["prompt_file"], "sha": req.get("prompt_sha", "-"), "effort": req["effort"], "model": req["model"],
                "images": imgs, "cached": meta.get("cached"), "in": u.get("input_tokens"), "out": u.get("output_tokens"),
                "usd": meta.get("cost_usd") or 0, "s": meta.get("seconds"), "error": (stage_dir / "error.json").exists(),
            })
        report = (run / "report.md").read_text() if (run / "report.md").exists() else ""
        m = re.search(r"\*\*Status: ([^*]+)\*\*", report)
        title = report.splitlines()[0].lstrip("# ") if report else "(no report: early run or killed)"
        out.append({"run": run.name, "title": title, "status": m.group(1) if m else ("v0 (pass/revise in model)" if "v0" in run.name else "-"),
                    "calls": calls, "live": sum(1 for c in calls if c["cached"] is False),
                    "usd": round(sum(c["usd"] for c in calls if c["cached"] is False), 2)})
    return out


def workflow_agents() -> list[dict]:
    out = []
    for wf, name in WORKFLOWS.items():
        d = SESSION / "subagents" / "workflows" / wf
        labels = {}
        for line in (d / "journal.jsonl").read_text().splitlines() if (d / "journal.jsonl").exists() else []:
            e = json.loads(line)
            if e.get("type") == "started":
                labels[e["agentId"]] = (e.get("label"), e.get("phase"))
        agents = []
        for f in sorted(d.glob("agent-*.jsonl")):
            aid = f.stem.removeprefix("agent-")
            tools, turns, task, final = collections.Counter(), 0, "", ""
            parts, started = [], False
            for line in f.read_text().splitlines():
                e = json.loads(line)
                msg = e.get("message") or {}
                content = msg.get("content")
                if e.get("type") == "user" and turns == 0:
                    texts = [content] if isinstance(content, str) else [b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]
                    for t in texts:
                        if "computed task" in t:
                            started = True
                        if started and t:
                            parts.append(t)
                    task = "\n\n".join(parts)
                if e.get("type") == "assistant":
                    turns += 1
                    for b in content if isinstance(content, list) else []:
                        if b.get("type") == "tool_use":
                            tools[b.get("name")] += 1
                        if b.get("type") == "text" and b.get("text"):
                            final = b["text"]
            label, phase = labels.get(aid, (aid, ""))
            agents.append({"id": aid, "label": label, "phase": phase, "turns": turns, "tools": dict(tools),
                           "tool_calls": sum(tools.values()), "task": redact(task)})
        out.append({"workflow": wf, "name": name, "agents": agents})
    return out


def main_session_tools() -> dict:
    tools = collections.Counter()
    turns = 0
    f = SESSION.with_suffix(".jsonl")
    if not f.exists():
        return {}
    for line in f.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant" and not e.get("isSidechain"):
            turns += 1
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    name = b.get("name", "")
                    tools[name] += 1
    return {"assistant_messages": turns, "tool_calls": sum(tools.values()), "by_tool": dict(tools.most_common())}


def prompt_versions() -> dict[str, str]:
    """prompt_file@sha -> full system text, from every request ever logged."""
    seen = {}
    for req in sorted(RUNS.glob("*/*/request.json")):
        r = json.loads(req.read_text())
        k = f"{r['prompt_file']}@{r.get('prompt_sha', '-')}"
        seen.setdefault(k, (req.parent.parent.name, r["system"]))
    return seen


def main() -> None:
    R, W, S, P = runs(), workflow_agents(), main_session_tools(), prompt_versions()
    stats = {
        "runs": len(R), "harness_calls_total": sum(len(r["calls"]) for r in R),
        "harness_calls_live": sum(r["live"] for r in R), "harness_usd": round(sum(r["usd"] for r in R), 2),
        "workflow_agents": sum(len(w["agents"]) for w in W),
        "workflow_tool_calls": sum(a["tool_calls"] for w in W for a in w["agents"]),
        "main_session": S, "prompt_versions": len(P),
    }
    (OUT / "stats.json").write_text(json.dumps({"stats": stats, "runs": [{k: v for k, v in r.items() if k != "calls"} for r in R]}, indent=2, ensure_ascii=False))

    L = ["# Call log (raw)", "",
         "Everything the debugging session called, generated from the archives by `exports/build_log.py`. "
         "The readable summary is `SUMMARY.md`; the full conversation export is the zip in ~/Downloads.", "",
         "## A. Harness agent: every Claude call", "",
         "Each call is one structured-output request to the Claude API (no tools; images attached where noted). "
         "`cached` = served from the content-hash cache, no tokens spent. Full request: `runs/<run>/<folder>/request.json`; "
         "answer: `output.json`; thinking summary: `thinking.md`.", ""]
    for r in R:
        L += [f"### {r['run']}", f"*{r['title']}* · status **{r['status']}** · {len(r['calls'])} calls ({r['live']} live) · ${r['usd']}", "",
              "| folder | prompt@sha | model / effort | images | cached | in tok | out tok | $ | s |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for c in r["calls"]:
            L.append(f"| {c['folder']}{' ⚠️error' if c['error'] else ''} | {c['prompt'].split('/')[-1]}@{c['sha']} | {c['model']} / {c['effort']} | {c['images']} | "
                     f"{'yes' if c['cached'] else 'no' if c['cached'] is False else '-'} | {c['in'] or ''} | {c['out'] or ''} | {c['usd'] or ''} | {c['s'] or ''} |")
        L.append("")

    L += ["## B. Workflow agents: task prompt and tool calls", ""]
    for w in W:
        L += [f"### {w['name']} (`{w['workflow']}`)", f"{len(w['agents'])} agents, {sum(a['tool_calls'] for a in w['agents'])} tool calls", ""]
        for a in w["agents"]:
            tools = ", ".join(f"{k}×{v}" for k, v in sorted(a["tools"].items(), key=lambda kv: -kv[1])) or "none"
            L += [f"#### {a['label']} ({a['phase']})", f"{a['turns']} model turns · tool calls: {tools}", "",
                  "<details><summary>Task prompt</summary>", "", "```", a["task"].strip(), "```", "", "</details>", ""]

    L += ["## C. Main session tool calls (this Claude Code conversation)", ""]
    if S:
        L += [f"{S['assistant_messages']} assistant messages, {S['tool_calls']} tool calls:", ""]
        L += [f"- {k}: {v}" for k, v in S["by_tool"].items()]
    L += ["", "## D. Every prompt version (full text)", "",
          "Keyed by file and sha8 of the exact system text sent (the shared keyword rule is included from v1.4 on). "
          "First run that used it in brackets.", ""]
    for k, (first, text) in P.items():
        L += [f"### {k}  [{first}]", "", "<details><summary>Show</summary>", "", "```", text.strip(), "```", "", "</details>", ""]
    (OUT / "CALL_LOG.md").write_text(redact("\n".join(L)) + "\n")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
