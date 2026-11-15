"""Output structure of every stage. The agent's judgement lives in these fields.

Field order matters: structured output is generated in order, so evidence comes before verdicts
(e.g. the reviewer audits claims and lists issues before it scores).
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ---------- progress keywords (a separate side request; the core agent never waits for it) ----------

class Highlight(BaseModel):
    kind: Literal["name", "period", "date", "place", "person", "material", "measure", "species", "theme", "visual", "decision", "check"]
    text: str = Field(description="The keyword itself, 1-5 words, e.g. 'Hope the blue whale', 'Jurassic', 'Wexford Harbour', '25.2 m'.")
    basis: str = Field(description="Where it comes from: the source URL, 'photo' or 'pack'.")


class KeywordBatch(BaseModel):
    keywords: list[Highlight] = Field(description="5-10 keywords, each copied from the material given.")


# ---------- S0 identify (multimodal, open recognition) ----------

class Identification(BaseModel):
    recognized_as: str = Field(description="What the object in the photo is, in your own words, before looking at the list.")
    short_name: str = Field(description="2-6 word name of the object, e.g. 'Hope the blue whale' or 'bronze ritual wine vessel'.")
    museum: str = Field(description="The museum and gallery if you can tell from the photo, else empty.")
    exhibit_id: str = Field(description="Id from the list of prepared exhibits that matches, or empty string if none does.")
    confidence: Literal["high", "medium", "low"]
    what_is_visible: str = Field(description="What the photo actually shows: which part of the object, angle, distance, framing, light, people.")
    visitor_interest: str = Field(description="What the framing suggests the visitor is curious about.")
    reason: str


# ---------- S0b research (web search + fetch) ----------

class Source(BaseModel):
    url: str = Field(description="Exactly as returned by the search or fetch tool.")
    title: str
    publisher: str
    official: bool = Field(description="True for the museum's own pages or the institution that holds the object.")


class Finding(BaseModel):
    quote: str = Field(description="Verbatim sentence or phrase (10-40 words) copied from the page that states the claim.")
    text: str = Field(description="One claim, stated plainly, using the quote's own words and qualifiers.")
    url: str = Field(description="The source URL that states it, exactly as returned by the tools.")
    about: Literal["exhibit", "context"]


class Research(BaseModel):
    queries_summary: str = Field(description="One line: what you searched for and why.")
    sources: list[Source]
    findings: list[Finding]
    agrees_with_pack: list[str] = Field(description="Pack statements the sources confirm.")
    conflicts: list[str] = Field(description="Where sources disagree with each other or with the pack, and which version is safer.")
    not_found: list[str] = Field(description="Visitor questions the sources could not answer.")


# ---------- S1 digest the knowledge pack ----------

class Fact(BaseModel):
    id: str = Field(description="Short snake_case id.")
    text: str = Field(description="The fact, stated plainly, no embellishment.")
    source: str = Field(description="The source URL exactly as written in the knowledge pack.")
    about: Literal["exhibit", "context"] = Field(description="exhibit = this object's own story; context = general background.")


class VisitorQuestion(BaseModel):
    question: str
    answer_fact_ids: list[str] = Field(description="Facts that answer it; empty if the pack cannot.")


class ThroughLine(BaseModel):
    name: str
    beginning: str
    turn: str = Field(description="A change in what the object is or means (animal to specimen, buried to displayed, there to here).")
    end: str
    turn_fact_ids: list[str]
    fact_ids: list[str]
    spine: str = Field(description="Fewest spoken sentences telling the whole story, numbers in words, listed facts only.")
    needs_s: Literal[15, 30]


class ControllingIdea(BaseModel):
    visitor_assumes: str = Field(description="What a visitor in front of it naturally thinks (X).")
    actually: str = Field(description="What is actually true (Y), stated in the pack's own words.")
    actually_fact_ids: list[str] = Field(description="Exhibit facts that state Y directly, not by inference.")
    second_half_fact_ids: list[str] = Field(description="New exhibit facts that would advance the turn in a second 15 s segment; empty if none.")
    last_thought: str = Field(description="The thought the visitor should have when they look back at the real object, in ten words or fewer.")


class MaterialSheet(BaseModel):
    facts: list[Fact]
    conflicts: list[str] = Field(description="Places where sources disagree (e.g. two different counts), and which version is safe to say.")
    visitor_questions: list[VisitorQuestion] = Field(description="The 3-5 questions a person standing in front of this object most likely has.")
    through_lines: list[ThroughLine] = Field(description="One to three stories the object could tell about itself.")
    visual_motifs: list[str] = Field(description="Concrete things a camera could show.")
    emotional_core: str = Field(description="The one thing about this exhibit most likely to move a visitor. Interpretation must be marked as such.")
    controlling_idea: ControllingIdea
    lead_line: int = Field(description="0-based index of the through-line that carries the controlling idea.")
    duration_s: Literal[15, 30]
    duration_reason: str


# ---------- S1b reference-image plan ----------

class PlannedImage(BaseModel):
    id: str = Field(description="Short id, e.g. zun_now, ram_awake, hall_inplace, ritual_hall_plate.")
    kind: Literal["subject_view", "in_place", "living_form", "turnaround", "keyframe", "world_plate", "detail"]
    prompt: str = Field(description="Image-generation prompt. The image model starts from the visitor's photo; describe the full result.")
    must_avoid: str = Field(description="What must not appear (text labels, people, glass, other objects...).")
    purpose: str


class AssetPlan(BaseModel):
    hero_mover_name: str = Field(description="The one part or creature that comes alive, e.g. 'the front ram', 'Hope'.")
    still_parts: str = Field(description="What stays still, e.g. 'the other three rams'; empty if nothing else.")
    subject_name: str = Field(description="2-6 word name of the exhibit as it is now, e.g. 'the whale skeleton'.")
    living_form_name: str = Field(description="2-6 word name of the living/original form, e.g. 'the living blue whale'; empty if none.")
    subject_lock: str = Field(description="One canonical 15-30 word description of the exhibit, reused verbatim everywhere it appears.")
    living_form_lock: str = Field(description="One canonical description of the exhibit as it was alive/new/in use, or empty if not applicable.")
    images: list[PlannedImage]


# ---------- S2 concept ----------

class Concept(BaseModel):
    name: str
    mode: Literal["character", "awaken", "world_returns"]
    engine: str = Field(description="Which story engine drives it (reveal, decisive moment, visitor's view back in time, contrast, direct address, overlooked detail, ...).")
    logline: str = Field(description="The whole film in one sentence.")
    hook_visual: str = Field(description="What is seen in the first 2-3 seconds. Must be filmable; no text or numbers on screen.")
    hook_line: str = Field(description="The first spoken line, written as final.")
    emotional_arc: str
    ending_visual: str = Field(description="The last image: a view of the real exhibit the visitor can match when they look up.")
    ending_line: str = Field(description="The last spoken line, written as final.")
    fact_ids: list[str]
    answers_question: str = Field(description="Which visitor question this film answers.")
    hero_mover: str = Field(description="Exactly one: the part or character that comes alive, or 'the world' in world_returns mode.")
    want: str = Field(description="What the hero wants, at most five words, readable with the sound off.")
    first_sign: str = Field(description="The first visible sign of life, by about 3 s.")
    big_move: str = Field(description="The high-amplitude beat, with a speed or force word and its physical consequence.")
    return_trace: str = Field(description="What is left on the still, whole exhibit in the last shot.")
    spectacle_shot: str = Field(description="The one image a visitor would screen-record, in one sentence.")


class ConceptSet(BaseModel):
    concepts: list[Concept]
    chosen: int = Field(description="0-based index of the chosen concept.")
    choice_reason: str


# ---------- S3 script ----------

class Asset(BaseModel):
    id: str = Field(description="Use the id of an existing reference image when one fits; otherwise a new short id.")
    source: Literal["existing", "generate"]
    depicts: Literal["exhibit_now", "living_form", "environment", "detail", "keyframe"] = Field(description="exhibit_now = the real object (identity anchor); living_form = the awakened hero / character; environment = in-place view or a world plate; detail = close-up of the exhibit; keyframe = the hero at its big pose.")
    view: str = Field(description="Which view or state of the exhibit, e.g. skeleton front, alive side, detail of jaw.")
    prompt: str = Field(description="For 'generate': image-generation prompt (subject alone, neutral even light, plain background, no text). For 'existing': empty.")
    purpose: str


class ShotSpec(BaseModel):
    t_start: float = Field(description="Seconds from the start of the segment.")
    t_end: float
    beat: Literal["still", "stir", "act", "return"]
    transition_in: str = Field(description="How the shot begins: cut, match cut on <feature>, whip pan, through the glass, time-lapse. 'cut' for shot 1.")
    refs: list[str] = Field(description="Asset ids actually visible in this shot.")
    framing: str = Field(description="e.g. extreme close-up, wide, aerial.")
    camera: str = Field(description="One primary camera move with its speed and endpoint (any move, any speed).")
    transformation: str = Field(description="Optional, at most one: start state -> mechanism and speed -> end state. Empty if none.")
    action: str = Field(description="A verb chain with physical consequences, up to about 35 words, speed and force words included.")
    visual: str = Field(description="At most 8 words of light or colour, only if it adds something. No @Image tags.")


class Line(BaseModel):
    t_start: float = Field(description="Seconds from the start of the segment.")
    text: str = Field(description="Spoken English narration, written for the ear (numbers and dates in words).")
    kind: Literal["fact", "visible", "voice"] = Field(description="fact = states something about the exhibit's past/size/meaning; visible = what the visitor sees in the room now; voice = feeling or address, no claims.")
    fact_ids: list[str] = Field(description="Ids of facts this line states; required for kind=fact, empty otherwise.")


class Audio(BaseModel):
    ambience: str
    sfx: list[str] = Field(description="Two or three specific sounds tied to the action.")
    music: str = Field(description="Music cue for this segment: how the film's music_style opens or ends here.")


class Segment(BaseModel):
    duration_s: float = Field(description="At most 15 seconds: one video generation.")
    setting: str = Field(description="The one place this segment happens in (at most one jump to a second place).")
    ref_assets: list[str] = Field(description="Asset ids used as reference images for this generation, in @Image order. At most 4.")
    shots: list[ShotSpec]
    narration: list[Line]
    audio: Audio
    end_frame: str = Field(description="The near-still image this segment ends on, so the next can cut cleanly.")


class Subtitle(BaseModel):
    t_start: float = Field(description="Seconds from the start of the whole film.")
    t_end: float
    text: str


class Script(BaseModel):
    exhibit_id: str
    title: str
    logline: str
    duration_s: Literal[15, 30]
    mode: Literal["character", "awaken", "world_returns"]
    hero_mover: str
    hero_want: str
    still_parts: str
    look: str = Field(description="One concrete look line, e.g. 'stylized 3D animated feature, soft rim light, gallery at night'.")
    return_trace: str
    style: Literal["realistic", "stylized"] = Field(description="Look of the film; must match the reference images used.")
    narrator_presence: Literal["voiceover", "on_screen"] = Field(description="voiceover = the character's voice over its action, no lip-sync (default); on_screen = it visibly speaks in shot, only when a talking mouth suits it.")
    voice: str = Field(description="One fixed narrator voice description (age, gender if any, timbre, accent, pace, warmth), repeated verbatim in every segment.")
    narrator_attitude: str = Field(description="How the exhibit feels about the person standing in front of it.")
    music_style: str = Field(description="One music style for the whole film (instruments, tempo, one texture), or 'no music'.")
    subject_name: str = Field(description="Copied from the asset plan.")
    living_form_name: str = Field(description="Copied from the asset plan; empty if the film never shows it.")
    subject_lock: str = Field(description="Canonical description of the exhibit as displayed now (15-30 words).")
    living_form_lock: str = Field(description="Canonical description of its living/original form, or empty if the film never shows it.")
    assets: list[Asset]
    segments: list[Segment]
    subtitles: list[Subtitle]


# ---------- S4 review ----------

class Claim(BaseModel):
    line: str = Field(description="The narration line, quoted.")
    claim: str = Field(description="What it asserts about the exhibit or its history; 'none' for pure feeling.")
    kind: Literal["fact", "visible", "voice"]
    supporting_fact: str = Field(description="Fact id and the words of that fact that support the claim, or 'none'.")
    supported: bool


class Issue(BaseModel):
    where: str = Field(description="e.g. 'segment 1 shot 2' or 'segment 2 line 3'.")
    severity: Literal["blocking", "polish"] = Field(description="blocking = must be fixed before shipping; polish = would make it better.")
    problem: str
    fix: str = Field(description="A concrete rewrite or instruction, staying inside the chosen concept and the listed facts.")


class Scores(BaseModel):
    hook: int = Field(description="1-5")
    visitor_view: int = Field(description="1-5")
    aliveness: int = Field(description="1-5: the exhibit or its character acts with intent and weight")
    spectacle: int = Field(description="1-5: there is a shot a viewer would screen-record")
    escalation: int = Field(description="1-5: still, stir, act, return with a real high-amplitude beat")
    physicality: int = Field(description="1-5: verb chains with visible consequences and named sounds")
    character: int = Field(description="1-5: personality through behaviour and voice")
    return_shot: int = Field(description="1-5: last shot is the real exhibit, whole, at the visitor's angle, with one trace of life")
    renderability: int = Field(description="1-5: only Seedance's real failure modes count")
    truth: int = Field(description="1-5: spoken claims only")
    sound: int = Field(description="1-5")
    voice_fit: int = Field(description="1-5: lines add what the picture cannot, sound like this character, fit their time")


class Review(BaseModel):
    claims: list[Claim]
    fantasy_legibility: Literal["pass", "fail"] = Field(description="fail if any image could be read as a documentary record of an invented or unsourced event, or shows identifiable people.")
    previous_issues_resolved: list[str] = Field(description="For each issue in the previous review (if any): resolved / not resolved, one line each.")
    issues: list[Issue]
    scores: Scores
    summary: str
