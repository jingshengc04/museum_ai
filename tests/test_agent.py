"""The script agent bridge and the agent path through the pipeline. No paid calls: the agent is faked or replayed."""
import json
import shutil
import sys
import textwrap

import pytest

from museum import config, edit, exhibits, pipeline, script_agent, video

EXAMPLE = config.HARNESS_DIR / "examples" / "four_ram_zun_e2e"
pytestmark = pytest.mark.skipif(not EXAMPLE.exists(), reason="harness/ is not checked out")


def agent_output(tmp_path, status="NEEDS_HUMAN", exhibit_id=None):
    """A finished agent run built from the harness's own end-to-end example."""
    run = tmp_path / "1114-000000-hope"
    run.mkdir(parents=True)
    final = json.loads((EXAMPLE / "final.json").read_text())
    final["status"] = status
    final["exhibit_id"] = exhibit_id or final["exhibit_id"]
    (run / "final.json").write_text(json.dumps(final))
    shutil.copyfile(EXAMPLE / "script.json", run / "script.json")
    (run / "02_s1_digest").mkdir()
    (run / "02_s1_digest" / "output.json").write_text(json.dumps({"facts": [
        {"id": "unearthed_1938_ningxiang", "text": "Unearthed in 1938 in Ningxiang, Hunan.", "source": "https://example.org/zun", "about": "exhibit"},
        {"id": "unsourced", "text": "No source.", "source": "", "about": "exhibit"}]}))
    (run / "02_s1_digest" / "meta.json").write_text(json.dumps({"cost_usd": 0.4, "cached": False}))
    return run


# ---------- the bridge: run.py as its own process, progress read from events.jsonl ----------

FAKE_RUN = textwrap.dedent('''
    import json, os, shutil, sys, time
    from pathlib import Path
    name = "1114-000000-hope"
    print(f"[hope] {name}  photo=none", flush=True)
    run = Path("runs") / name
    run.mkdir(parents=True, exist_ok=True)
    events = [{"type": "stage_start", "stage": "s0b_research"}, {"type": "search", "stage": "s0b_research", "text": "Hope blue whale 1891"},
              {"type": "keywords_batch", "stage": "kw_research", "keywords": [{"text": "Wexford Harbour"}, {"text": "1891"}]},
              {"type": "stage_start", "stage": "s3_script"}]
    with (run / "events.jsonl").open("w") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\\n"); fh.flush(); time.sleep(0.15)
    if os.environ.get("FAKE_FAIL"):
        (run / "report.md").write_text("# x\\n\\n## Error\\n\\n```\\nRuntimeError: the pack is empty\\n```\\n")
        sys.exit(0)
    for f in Path(os.environ["FAKE_OUT"]).iterdir():
        (shutil.copytree if f.is_dir() else shutil.copyfile)(f, run / f.name)
''')


@pytest.fixture
def fake_harness(tmp_path, monkeypatch):
    home = tmp_path / "harness"
    home.mkdir()
    (home / "run.py").write_text(FAKE_RUN)
    monkeypatch.setattr(config, "HARNESS_DIR", home)
    monkeypatch.setattr(config, "AGENT_PIPELINE", "staged")
    monkeypatch.setenv("FAKE_OUT", str(agent_output(tmp_path / "out")))
    return home


def test_bridge_relays_progress_and_reads_the_hand_off(fake_harness):
    seen = []
    run = script_agent.run(lambda kind, **data: seen.append((kind, data)), exhibit_id="hope")
    assert run.final["video_requests"] and run.status == "NEEDS_HUMAN" and not run.passed
    assert [f["id"] for f in run.facts] == ["unearthed_1938_ningxiang"], "facts without a source are dropped"
    assert run.cost_usd == 0.4
    assert ("progress", {"percent": script_agent.STAGES["s0b_research"][0], "text": "Searching the archives"}) in seen
    assert ("thought", {"text": "Searching: Hope blue whale 1891"}) in seen
    assert ("keywords", {"words": ["Wexford Harbour", "1891"]}) in seen


def test_bridge_reports_why_the_agent_failed(fake_harness, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")
    with pytest.raises(RuntimeError, match="the pack is empty"):
        script_agent.run(lambda *a, **k: None, exhibit_id="hope")


# lean.py names its folder runs/<stamp>-lean-<label> and prints no run name first.
FAKE_LEAN = textwrap.dedent('''
    import argparse, json, shutil, time
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo"); ap.add_argument("--label"); ap.add_argument("--resolution")
    args = ap.parse_args()
    run = Path("runs") / f"1115-000000-lean-{args.label}"
    run.mkdir(parents=True)
    with (run / "events.jsonl").open("w") as fh:
        for e in [{"type": "stage_start", "stage": "s0_identify"}, {"type": "fetch", "stage": "s0b_research", "text": "https://example.org/zun"},
                  {"type": "stage_start", "stage": "lean_write"}]:
            fh.write(json.dumps(e) + "\\n"); fh.flush(); time.sleep(0.15)
    final = json.loads(Path(LEAN).joinpath("final.json").read_text())
    final["video_requests"][0]["resolution"] = args.resolution
    (run / "final.json").write_text(json.dumps(final))
''')
LEAN = config.HARNESS_DIR / "examples" / "four_ram_zun_lean"


def lean_harness(fake_harness, monkeypatch):
    (fake_harness / "lean.py").write_text(f"LEAN = {str(LEAN)!r}\n" + FAKE_LEAN)
    monkeypatch.setattr(config, "AGENT_PIPELINE", "lean")


@pytest.mark.skipif(not LEAN.exists(), reason="no lean example")
def test_bridge_runs_the_lean_pipeline(fake_harness, monkeypatch, tmp_path):
    lean_harness(fake_harness, monkeypatch)
    seen = []
    with pytest.raises(ValueError, match="needs a photo"):
        script_agent.run(lambda *a, **k: None, exhibit_id="hope")
    run = script_agent.run(lambda kind, **data: seen.append((kind, data)), photo=tmp_path / "p.jpg")
    assert run.dir.name.startswith("1115-000000-lean-web") and run.passed
    assert run.final["video_requests"][0]["resolution"] == config.AGENT_VIDEO_RESOLUTION
    assert ("progress", {"percent": 30, "text": "Writing the script"}) in seen
    assert ("thought", {"text": "Reading https://example.org/zun"}) in seen
    # no digest in a lean run: the facts are the ones its lines cite, each with its URL
    assert run.facts and all(f["source"].startswith("http") for f in run.facts)
    assert {f for line in run.final["lines"] for f in line["fact_ids"]} == {f["id"] for f in run.facts}


@pytest.mark.skipif(not LEAN.exists(), reason="no lean example")
def test_lean_film_is_one_30_s_take_on_seedance_25(fake_harness, tiny_exhibit, tmp_path, monkeypatch):
    lean_harness(fake_harness, monkeypatch)
    monkeypatch.setattr(config, "use_agent", lambda: True)
    run = script_agent.run(lambda *a, **k: None, photo=tiny_exhibit / "photo.jpg")
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: run)
    planned = []
    plan_request = video.plan_request
    monkeypatch.setattr(video, "plan_request", lambda *a: planned.append(plan_request(*a)) or planned[-1])
    job = config.OUTPUT_DIR / tmp_path.name / "job"
    manifest, _ = pipeline.make_film(job, "en", "first_person", lambda *a, **k: None, exhibit_id="hope", save=False)

    p = planned[-1]
    assert (p.model, p.resolution, p.seconds) == (config.SEEDANCE_25, "480p", 30), "the agent's endpoint, not cut to 15 s"
    assert video.request_arguments(p, ["u"])["resolution"] == "480p"
    assert config.clip_price_usd(p.seconds, p.model, p.resolution) == pytest.approx(6.62, abs=0.01)
    assert edit.duration(job / "final.mp4") == pytest.approx(30, abs=0.3)
    assert len(manifest["captions"]) == len(run.final["subtitles"])
    assert any(f["used"] for f in manifest["facts"]), "the lines' citations reach the sources panel"
    assert manifest["exhibit"]["id"] == "hope", "lean's own adhoc id does not replace an exhibit we recognised"


# ---------- the agent path through the pipeline ----------

@pytest.fixture
def agent_on(monkeypatch):
    monkeypatch.setattr(config, "use_agent", lambda: True)
    monkeypatch.setattr(config, "AGENT_PIPELINE", "staged")  # these runs come from the staged example
    monkeypatch.setattr(config, "REPLAY_SECONDS", 0.2)


def test_agent_film_mock(tiny_exhibit, tmp_path, agent_on, monkeypatch):
    calls = []
    run = script_agent.load(agent_output(tmp_path))
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: calls.append(kw) or run)
    job = config.OUTPUT_DIR / tmp_path.name / "job"
    manifest, folder = pipeline.make_film(job, "en", "first_person", lambda *a, **k: None, exhibit_id="hope")

    assert calls == [{"exhibit_id": "hope", "photo": tiny_exhibit / "photo.jpg"}], "no visitor photo: the exhibit's own"
    assert folder == job and manifest["storyboard_origin"] == "agent"
    assert manifest["agent"]["status"] == "NEEDS_HUMAN"
    assert edit.has_audio(job / "final.mp4") and edit.duration(job / "final.mp4") == pytest.approx(15, abs=0.2)
    assert [c["text"] for c in manifest["captions"]] == [s["text"] for s in run.final["subtitles"]]
    assert manifest["captions"][0]["start"] == pytest.approx(1.0)
    assert manifest["shots"][0]["prompt"] == run.final["video_requests"][0]["prompt"], "the agent's prompt is used as written"
    assert manifest["facts"] == [{"id": "unearthed_1938_ningxiang", "text": "Unearthed in 1938 in Ningxiang, Hunan.",
                                  "source": "https://example.org/zun", "used": True}]
    learned = config.EXHIBITS_DIR / "adhoc-four-ram-square-zun"
    saved = json.loads((learned / "demo" / "en-first_person" / "manifest.json").read_text())
    assert saved["agent"]["status"] == "NEEDS_HUMAN", "kept for other visitors, with its review status recorded"


def test_passing_agent_film_is_reused_without_running_the_agent_again(tiny_exhibit, tmp_path, agent_on, monkeypatch):
    run = script_agent.load(agent_output(tmp_path, status="PASS", exhibit_id="hope"))
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: run)
    out = config.OUTPUT_DIR / tmp_path.name
    first, _ = pipeline.make_film(out / "a", "en", "first_person", lambda *a, **k: None, exhibit_id="hope")

    def no_agent(emit, **kw):
        raise AssertionError("a library hit must not run the agent")
    monkeypatch.setattr(script_agent, "run", no_agent)
    seen = []
    again, folder = pipeline.make_film(out / "b", "en", "first_person", lambda kind, **d: seen.append(kind), exhibit_id="hope")
    assert folder == tiny_exhibit / "demo" / "en-first_person" and again == first
    assert {"storyboard", "shot"} <= set(seen) and seen.count("step") >= 6, "the visitor still sees the making-of"
    assert not (out / "b" / "final.mp4").exists()


def test_agent_budget_counts_pictures_and_stops_before_paying(tiny_exhibit, tmp_path, agent_on, monkeypatch):
    monkeypatch.setenv("LIVE", "video")
    monkeypatch.setenv("FAL_KEY", "x")
    monkeypatch.setattr(config, "MAX_FAL_USD", 1.0)
    run = script_agent.load(agent_output(tmp_path, status="PASS"))
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: run)
    monkeypatch.setattr(video, "reference_image", lambda *a: pytest.fail("nothing may be paid for over budget"))
    with pytest.raises(RuntimeError, match=r"about \$4\.08 .*MAX_FAL_USD"):  # 3 pictures x $0.15 + 15 s x $0.2419
        pipeline.make_film(config.OUTPUT_DIR / tmp_path.name / "c", "en", "first_person", lambda *a, **k: None, exhibit_id="hope")


def test_agent_only_exhibits_are_recognisable_but_not_offered(tiny_exhibit):
    ids = [e.id for e in exhibits.all_exhibits()]
    assert ids[0] == "hope" and "sophie" in ids
    sophie = exhibits.load("sophie")
    assert sophie.data["from_pack"] and sophie.pack and sophie.demo_dir("en", "first_person").parts[-3] == "sophie"


def test_object_learned_from_a_photo_is_kept_and_found_again(tiny_exhibit, tmp_path, agent_on, monkeypatch):
    from museum import storyboard

    out = agent_output(tmp_path)
    (out / "00_s0_identify").mkdir()
    (out / "00_s0_identify" / "output.json").write_text(json.dumps(
        {"short_name": "Four-Ram Square Zun", "museum": "National Museum of China, Beijing", "recognized_as": "a square bronze zun with four rams"}))
    run = script_agent.load(out)
    calls = []
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: calls.append(kw) or run)

    def unknown(photo, candidates, emit):
        raise LookupError("not one of ours")
    monkeypatch.setattr(storyboard, "identify", unknown)
    photo = tiny_exhibit / "photo.jpg"
    first, _ = pipeline.make_film(config.OUTPUT_DIR / tmp_path.name / "a", "en", "first_person", lambda *a, **k: None, photo=photo)
    assert calls == [{"exhibit_id": None, "photo": photo}]

    learned = exhibits.load("adhoc-four-ram-square-zun")
    assert learned.data["learned"] and learned.name == "Four-Ram Square Zun" and learned.facts[0]["source"] == "https://example.org/zun"
    assert learned.demos(), "its film is in the library"

    # A later visitor's photo is recognised as the learned exhibit: the saved film plays, the agent does not run.
    monkeypatch.setattr(storyboard, "identify", lambda photo, candidates, emit: next(e for e in candidates if e.id == learned.id))
    again, folder = pipeline.make_film(config.OUTPUT_DIR / tmp_path.name / "b", "en", "first_person", lambda *a, **k: None, photo=photo)
    assert folder == learned.demo_dir("en", "first_person") and again == first and len(calls) == 1


def test_the_agent_may_correct_our_recognition(tiny_exhibit, tmp_path, agent_on, monkeypatch):
    run = script_agent.load(agent_output(tmp_path))  # the agent settles on the zun although we passed hope
    monkeypatch.setattr(script_agent, "run", lambda emit, **kw: run)
    manifest, _ = pipeline.make_film(config.OUTPUT_DIR / tmp_path.name / "a", "en", "first_person", lambda *a, **k: None, exhibit_id="hope")
    assert manifest["exhibit"]["id"] == "adhoc-four-ram-square-zun"
    assert not (tiny_exhibit / "demo" / "en-first_person").exists(), "the zun's film is not filed under Hope"
