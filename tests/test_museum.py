import json

import pytest
from fastapi.testclient import TestClient

from museum import config, edit, exhibits, pipeline, storyboard, video, voice


def test_everything_is_mock_by_default(monkeypatch):
    assert not any(m["live"] for m in config.modes().values())
    monkeypatch.setenv("LIVE", "video")
    monkeypatch.delenv("FAL_KEY", raising=False)
    assert not config.is_live("video"), "naming a service in LIVE is not enough without its key"
    monkeypatch.setenv("FAL_KEY", "x")
    assert config.is_live("video") and not config.is_live("voice")


# ---------- fitting clips to narration ----------

@pytest.mark.parametrize("source, target, how, speed, freeze", [
    (8.0, 5.0, "trim", 1.0, 0.0),
    (5.0, 6.0, "slow", 1.2, 0.0),
    (5.0, 8.0, "slow+freeze", 1.25, 1.75),
])
def test_fit_plan(source, target, how, speed, freeze):
    plan = edit.fit_plan(source, target)
    assert (plan["how"], plan["speed"], plan["freeze"]) == (how, speed, freeze)


def test_crossfades_do_not_eat_narration_time():
    slots = edit.timeline([4.0, 6.0, 5.0])
    assert slots[1]["start"] == pytest.approx(slots[0]["length"])
    assert edit.clip_length(slots[0], is_last=False) == pytest.approx(slots[0]["length"] + config.XFADE)
    assert edit.clip_length(slots[2], is_last=True) == slots[2]["length"]
    assert video.request_seconds(40) == config.VIDEO_MAX_SECONDS and video.request_seconds(0.5) == config.VIDEO_MIN_SECONDS


# ---------- word timings ----------

def test_alignment_drops_tags_and_keeps_punctuation():
    text = "[softly] Look up. Yes!"
    times = [i * 0.1 for i in range(len(text))]
    words = voice.words_from_alignment(list(text), times, [t + 0.1 for t in times])
    assert [w["w"] for w in words] == ["Look", "up.", "Yes!"]
    assert words[0]["t0"] == pytest.approx(0.9)


def test_alignment_splits_chinese_per_character():
    words = voice.estimated_words("[softly] 1891年，我搁浅了。", 4.0)
    assert [w["w"] for w in words] == ["1891", "年，", "我", "搁", "浅", "了。"]
    cues = pipeline.captions_for(words, 10.0, "zh")
    assert cues[0]["text"] == "1891年，我搁浅了。" and cues[0]["start"] >= 10.0


def test_captions_break_on_sentences_and_do_not_overlap():
    words = voice.estimated_words("Look up. Yes, me. I am Hope, and I have a story for you, a long one.", 6.0)
    cues = pipeline.captions_for(words, 0.0, "en")
    assert cues[0]["text"] == "Look up."
    assert all(a["end"] <= b["start"] for a, b in zip(cues, cues[1:]))
    assert all(len(c["text"]) <= 40 for c in cues)


# ---------- facts ----------

@pytest.mark.parametrize("path", sorted((config.ROOT / "exhibits").glob("*/storyboards/*.json")), ids=lambda p: p.stem)
def test_hand_written_storyboards_only_cite_sourced_facts(path):
    exhibit = exhibits.load(path.parent.parent.name)
    language, _, style = path.stem.partition("-")
    board = storyboard.build(exhibit, language, style, lambda *a, **k: None)
    assert 1 <= len(board.shots) <= 10
    assert all(f["source"].startswith("https://") for f in exhibit.facts)
    for shot in board.shots:
        assert storyboard.narration_units(shot.narration, language) <= storyboard.unit_budget(language, shot.seconds), shot.narration


def test_unsourced_fact_is_refused():
    exhibit = exhibits.load("hope")
    assert "bones_pose" not in {f["id"] for f in exhibit.facts}
    board = storyboard.Storyboard(title="t", language="en", shots=[
        storyboard.Shot(id=1, narration="I have 221 bones.", action="a", camera="c", location="l", mood="m", fact_ids=["bones_pose"]),
    ])
    with pytest.raises(ValueError, match="without a source"):
        storyboard.validate(board, exhibit)


def test_video_prompt_puts_action_first_and_adds_style():
    exhibit = exhibits.load("hope")
    shot = storyboard.Shot(id=1, narration="n", action="The whale rolls.", camera="Wide.", location="Ocean.", mood="Joy.")
    prompt = storyboard.video_prompt(shot, exhibit)
    assert prompt.startswith("Action: The whale rolls. Camera: Wide. Location: Ocean. Mood: Joy.")
    assert "deep blue mottled" in prompt and prompt.endswith(exhibit.data["style_suffix"])


# ---------- budget ----------

def test_budget_guard_stops_an_expensive_film(monkeypatch, tiny_exhibit):
    monkeypatch.setenv("LIVE", "video")
    monkeypatch.setenv("FAL_KEY", "x")
    monkeypatch.setattr(config, "MAX_FAL_USD", 0.15)
    exhibit = exhibits.load("hope")
    shot = storyboard.Shot(id=1, narration="n", action="a", camera="c", location="l", mood="m", refs=["side"])
    plans = [video.plan(shot.model_copy(update={"id": i}), exhibit, 5.0) for i in (1, 3, 4)]
    assert [p.source for p in plans] == ["generate"] * 3
    with pytest.raises(RuntimeError, match="MAX_FAL_USD"):
        video.check_budget(plans)
    assert video.plan(shot.model_copy(update={"id": 2}), exhibit, 5.0).source == "override"


def test_seedance_request_and_price(monkeypatch, tiny_exhibit):
    monkeypatch.setenv("LIVE", "video")
    monkeypatch.setenv("FAL_KEY", "x")
    exhibit = exhibits.load("hope")
    shot = storyboard.Shot(id=1, narration="[softly] I am Hope.", action="a", camera="c", location="l", mood="m", refs=["side"], seconds=15)
    p = video.plan(shot, exhibit, 15, photo=tiny_exhibit / "photo.jpg")
    assert [r.name for r in p.refs] == ["photo.jpg", "side.png"], "the visitor's photo leads the references"
    assert "@Image1 is the visitor's photo" in p.prompt and "[softly]" not in p.prompt
    request = video.request_arguments(p, ["u1", "u2"])
    assert request == {"prompt": p.prompt, "duration": "15", "resolution": "720p", "aspect_ratio": "16:9", "generate_audio": True, "image_urls": ["u1", "u2"]}
    assert video.estimate_usd([p, p]) == pytest.approx(7.26, abs=0.01), "two 15 s scenes at 720p"
    assert video.check_budget([p, p]) <= config.MAX_FAL_USD


# ---------- the whole thing, mock ----------

def test_mock_film_uses_drop_in_material(tiny_exhibit, tmp_path):
    events = []
    job = config.OUTPUT_DIR / tmp_path.name / "job"
    manifest, folder = pipeline.make_film(job, "en", "kids", lambda kind, **data: events.append((kind, data)))
    assert folder == job

    assert manifest["storyboard_origin"] == "fallback"  # no kids script and the LLM is mock
    assert [s["video_source"] for s in manifest["shots"]] == ["mock", "override"]
    assert manifest["shots"][0]["refs"] == ["side", "curious"]
    assert manifest["fal_cost_usd"] == 0
    assert edit.duration(job / "final.mp4") == pytest.approx(manifest["duration"], abs=0.15)
    assert manifest["captions"][-1]["end"] <= manifest["duration"] + 0.3
    assert all((job / s["thumb"]).exists() for s in manifest["shots"])
    assert {f["id"] for f in manifest["facts"] if f["used"]} == {"name", "stranding", "sale", "hintze"}
    assert edit.has_audio(job / "final.mp4"), "the clips carry their own voice track"
    assert [s["voice_source"] for s in manifest["shots"]] == ["mock", "override"]
    assert 'saying exactly these words and nothing else: "I am Hope.' in manifest["shots"][0]["prompt"]
    assert "WEBVTT" in (job / "captions.vtt").read_text()
    assert [d["step"] for k, d in events if k == "step" and d["status"] == "done"] == ["identify", "story", "video", "edit"]

    demo = tiny_exhibit / "demo" / "en-kids"  # a finished film goes into the library by itself
    assert exhibits.load("hope").demos()[0]["manifest"] == "/exhibits/hope/demo/en-kids/manifest.json"
    stored = json.loads((demo / "manifest.json").read_text())
    stored["modes"]["video"] = True
    (demo / "manifest.json").write_text(json.dumps(stored))
    with pytest.raises(RuntimeError, match="--force"):
        pipeline.promote(job)


def test_second_visitor_gets_the_library_film_through_the_same_steps(tiny_exhibit, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPLAY_SECONDS", 0.2)
    quiet = lambda *a, **k: None  # noqa: E731
    first, seen = [], []
    out = config.OUTPUT_DIR / tmp_path.name
    made, _ = pipeline.make_film(out / "a", "en", "first_person", lambda kind, **data: first.append((kind, data)))

    reused, folder = pipeline.make_film(out / "b", "en", "first_person", lambda kind, **data: seen.append((kind, data)))
    assert folder == tiny_exhibit / "demo" / "en-first_person" and reused == made
    assert not (out / "b" / "final.mp4").exists(), "nothing was rendered again"
    shape = lambda log: [(k, d.get("step"), d.get("status"), d.get("id"), d.get("stage")) for k, d in log]  # noqa: E731
    assert sorted(shape(seen), key=str) == sorted(shape(first), key=str), "the visitor sees the same events"
    thumbs = [d["thumb"] for k, d in seen if "thumb" in d]
    assert thumbs and all(t.startswith("/exhibits/hope/demo/en-first_person/thumbs/") for t in thumbs)

    exhibit = exhibits.load("hope")
    assert pipeline.make_film(out / "c", "en", "first_person", quiet, fresh=True)[1] == out / "c"
    assert pipeline.library_hit(exhibit, "zh", "first_person") is None, "other languages are other films"
    monkeypatch.setenv("LIVE", "video")
    monkeypatch.setenv("FAL_KEY", "x")
    assert pipeline.library_hit(exhibit, "en", "first_person") is None, "a mock film is not served once video is live"
    monkeypatch.setenv("LIVE", "")
    (tiny_exhibit / "refs" / "side.png").write_bytes((tiny_exhibit / "photo.jpg").read_bytes())
    assert pipeline.library_hit(exhibits.load("hope"), "en", "first_person") is None, "new material means a new film"


def test_server_runs_a_job_and_falls_back_to_a_saved_film(tiny_exhibit, monkeypatch):
    from museum import server

    monkeypatch.setattr(config, "REPLAY_SECONDS", 0.2)

    client = TestClient(server.app)
    state = client.get("/api/state").json()
    assert state["exhibits"][0]["refs"] == ["curious", "delighted", "side"]
    assert state["video"]["worst_case_usd"] == 0
    assert client.post("/api/jobs", data={"style": "nope"}).status_code == 400
    assert client.post("/api/jobs", data={"exhibit_id": "hope"}, files={"photo": ("x.txt", b"hi", "text/plain")}).status_code == 400

    photo = {"photo": ("x.jpg", (tiny_exhibit / "photo.jpg").read_bytes(), "image/jpeg")}
    monkeypatch.setattr(server.outline, "outline_png", lambda blob: b"\x89PNG fake")
    found = client.post("/api/outline", files=photo)
    assert found.status_code == 200 and found.headers["content-type"] == "image/png"
    monkeypatch.setattr(server.outline, "outline_png", lambda blob: None)
    assert client.post("/api/outline", files=photo).status_code == 204, "nothing stands out: the page scans without an outline"
    monkeypatch.setattr(server.outline, "outline_png", lambda blob: 1 / 0)
    assert client.post("/api/outline", files=photo).status_code == 204, "a broken model must not break the scan"
    assert client.post("/api/outline", files={"photo": ("x.txt", b"hi", "text/plain")}).status_code == 400

    def run(data):
        job_id = client.post("/api/jobs", data=data).json()["job_id"]
        stream = client.get(f"/api/jobs/{job_id}/events").text
        return job_id, [json.loads(line[6:]) for line in stream.splitlines() if line.startswith("data: ")]

    job_id, events = run({"exhibit_id": "hope", "language": "en", "style": "first_person"})
    assert events[-1] == {"type": "done", "manifest": f"/output/{job_id}/manifest.json"}
    assert client.get(events[-1]["manifest"]).json()["video"] == "final.mp4"
    assert client.get(f"/output/{job_id}/final.mp4", headers={"Range": "bytes=0-99"}).status_code == 206

    shelf = client.get("/api/stories").json()
    assert [s["title"] for s in shelf] == ["Hope: the whale who came ashore"], "library copy and output copy show once"
    assert shelf[0]["manifest"] == "/exhibits/hope/demo/en-first_person/manifest.json" and shelf[0]["thumb"].endswith("thumbs/shot_01.jpg")

    _, events = run({"exhibit_id": "hope", "language": "en", "style": "first_person"})
    assert events[-1] == {"type": "done", "manifest": "/exhibits/hope/demo/en-first_person/manifest.json"}
    job_id, events = run({"exhibit_id": "hope", "language": "en", "style": "first_person", "fresh": "true"})
    assert events[-1]["manifest"] == f"/output/{job_id}/manifest.json"

    monkeypatch.setattr(edit, "join", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("ffmpeg exploded")))
    _, events = run({"exhibit_id": "hope", "language": "en", "style": "funny"})
    assert events[-1]["type"] == "error" and "ffmpeg exploded" in events[-1]["message"]
    assert events[-1]["fallback"] == "/exhibits/hope/demo/en-first_person/manifest.json"
