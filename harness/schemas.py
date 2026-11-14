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
    id: str = Field(description="Short id, e.g. alive_restoration, sheet_realistic, detail_skull.")
    kind: Literal["restoration", "character_sheet", "subject_view", "detail", "environment"]
    prompt: str = Field(description="Image-generation prompt. The image model starts from the visitor's photo; describe the full result.")
    must_avoid: str = Field(description="What must not appear (text labels, people, glass, other objects...).")
    purpose: str


class AssetPlan(BaseModel):
    subject_name: str = Field(description="2-6 word name of the exhibit as it is now, e.g. 'the whale skeleton'.")
    living_form_name: str = Field(description="2-6 word name of the living/original form, e.g. 'the living blue whale'; empty if none.")
    subject_lock: str = Field(description="One canonical 15-30 word description of the exhibit, reused verbatim everywhere it appears.")
    living_form_lock: str = Field(description="One canonical description of the exhibit as it was alive/new/in use, or empty if not applicable.")
    images: list[PlannedImage]


# ---------- S2 concept ----------

class Concept(BaseModel):
    name: str
    engine: str = Field(description="Which story engine drives it (reveal, decisive moment, visitor's view back in time, contrast, direct address, overlooked detail, ...).")
    logline: str = Field(description="The whole film in one sentence.")
    hook_visual: str = Field(description="What is seen in the first 2-3 seconds. Must be filmable; no text or numbers on screen.")
    hook_line: str = Field(description="The first spoken line, written as final.")
    emotional_arc: str
    ending_visual: str = Field(description="The last image: a view of the real exhibit the visitor can match when they look up.")
    ending_line: str = Field(description="The last spoken line, written as final.")
    fact_ids: list[str]
    answers_question: str = Field(description="Which visitor question this film answers.")


class ConceptSet(BaseModel):
    concepts: list[Concept]
    chosen: int = Field(description="0-based index of the chosen concept.")
    choice_reason: str


# ---------- S3 script ----------

class Asset(BaseModel):
    id: str = Field(description="Use the id of an existing reference image when one fits; otherwise a new short id.")
    source: Literal["existing", "generate"]
    depicts: Literal["exhibit_now", "living_form", "environment", "detail"] = Field(description="exhibit_now = the real object as displayed; living_form = as it was alive/new/in use; environment = a place; detail = close-up of the exhibit.")
    view: str = Field(description="Which view or state of the exhibit, e.g. skeleton front, alive side, detail of jaw.")
    prompt: str = Field(description="For 'generate': image-generation prompt (subject alone, neutral even light, plain background, no text). For 'existing': empty.")
    purpose: str


class ShotSpec(BaseModel):
    t_start: float = Field(description="Seconds from the start of the segment.")
    t_end: float
    refs: list[str] = Field(description="Asset ids actually visible in this shot.")
    framing: str = Field(description="e.g. extreme close-up, wide, aerial.")
    camera: str = Field(description="Exactly one camera move, e.g. slow push-in, static, slow tilt up.")
    action: str = Field(description="The one motion in the shot as a full clause: subject + verb + direction, 4-12 words.")
    visual: str = Field(description="At most 15 words: light, colour, texture or composition the action does not already say. No motion verbs, never repeat the action, never describe the exhibit's own shape or colour (the reference shows it); describe a living form's look the first time it appears in a segment. No @Image tags.")


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
    style: Literal["realistic", "stylized"] = Field(description="Look of the film; must match the reference images used.")
    narrator_presence: Literal["voiceover", "on_screen"] = Field(description="voiceover = unseen narrator over the images; on_screen = the exhibit's living form speaks in shot.")
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
    focus: int = Field(description="1-5")
    concept_fidelity: int = Field(description="1-5")
    truth: int = Field(description="1-5")
    counterpoint: int = Field(description="1-5: lines add what the picture cannot show instead of describing it")
    spoken: int = Field(description="1-5: lines sound like a voice, fit their time")
    visual_feasibility: int = Field(description="1-5")
    length_fit: int = Field(description="1-5")
    ending: int = Field(description="1-5")


class Review(BaseModel):
    claims: list[Claim]
    previous_issues_resolved: list[str] = Field(description="For each issue in the previous review (if any): resolved / not resolved, one line each.")
    issues: list[Issue]
    scores: Scores
    summary: str
