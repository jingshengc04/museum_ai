# 完整记录：Hope v1.4（一次运行）

运行 `1114-181730-hope-v1.4` · 模型 claude-opus-5-5 · 共 10 次 Claude 调用，没有工具调用。
每次调用的结构：系统提示词 → 输入（文字 + 图片）→ 模型思考摘要 → 结构化输出（JSON）。

说明：S0 的结果来自缓存，它在一次被中止的运行里实际调用过，提示词和输入完全相同，所以直接复用。

## 目录

1. [00_s0_identify · S0 识别展品](#00-s0-identify)
2. [01_s1_digest · S1 消化资料](#01-s1-digest)
3. [02_s1b_assets · S1b 参考图规划](#02-s1b-assets)
4. [03_s2_concept · S2 构思](#03-s2-concept)
5. [04_s3_script · S3 写剧本](#04-s3-script)
6. [05_s4_review · S4 审稿](#05-s4-review)
7. [06_s3_script · S3 写剧本](#06-s3-script)
8. [07_s4_review · S4 审稿](#07-s4-review)
9. [08_s3_script · S3 写剧本](#08-s3-script)
10. [09_s4_review · S4 审稿](#09-s4-review)

---

<a id="00-s0-identify"></a>
## 第 1 次调用 · 00_s0_identify · S0 识别展品

- 提示词文件：`prompts/s0_identify.md`（sha 7b29103b，末尾附加了 `prompts/_highlights.md`）
- effort：medium · 输入 3599 tokens · 输出 594 tokens · $0.0263 · 10.0 秒 · 缓存

### 系统提示词

```text
You look at a photo a museum visitor just took and work out what it shows.

First, say in your own words what the object is, judging from the photo alone: what kind of thing, and if you recognise the specific exhibit, which one. Then match it to the list of exhibits we have prepared material for. Return an empty exhibit_id when none of them is clearly the object in the photo; a wrong match is worse than no match, because the film would then tell the wrong story.

Visitors' photos are messy: crowds, reflections, odd angles, only part of the object in frame. Match on the object itself, not on the room around it.

Then describe what the photo actually shows, because the film will open from the visitor's own point of view: which part of the object is in frame, from what angle and height (from below, from a balcony, head-on), how close, what the light is like, whether people are in shot and how big they look next to it. Finally, say in one sentence what that framing suggests the visitor is curious about (a close-up of teeth suggests how it ate; a wide shot with tiny people underneath suggests its size).


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Exhibits we have prepared material for:
[
  {
    "id": "hope",
    "name": "Hope the blue whale",
    "museum": "Natural History Museum, London",
    "location": "Hintze Hall",
    "looks_like": "A huge blue whale skeleton hanging from the ceiling of a large Romanesque hall with terracotta arches, posed mid-dive."
  },
  {
    "id": "sequoia",
    "name": "The giant sequoia slice",
    "museum": "Natural History Museum, London",
    "location": "Hintze Hall, upper balcony",
    "looks_like": "A huge circular cross-section of a giant sequoia trunk, several metres across, standing upright on the top balcony of a Romanesque hall, its surface covered in dense concentric growth rings ringed by thick reddish bark."
  },
  {
    "id": "sophie",
    "name": "Sophie the Stegosaurus",
    "museum": "Natural History Museum, London",
    "location": "Earth Hall (Exhibition Road entrance)",
    "looks_like": "A complete mounted Stegosaurus skeleton, about the size of a 4x4, walking on all fours with a small head, a double row of large thin plates along its arched back and four spikes at the tail tip."
  }
]
```

### 模型思考摘要

(no thinking summary)

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "name",
      "text": "Hope the blue whale",
      "basis": "pack"
    },
    {
      "kind": "place",
      "text": "Hintze Hall",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "Diving pose from the balcony",
      "basis": "photo"
    },
    {
      "kind": "visual",
      "text": "Tiny visitors below",
      "basis": "photo"
    }
  ],
  "recognized_as": "A blue whale skeleton suspended from the roof of the main Romanesque hall of the Natural History Museum, London. This is the well-known 'Hope' skeleton, posed as if diving, with its long lower jaws and flippers angled downward.",
  "exhibit_id": "hope",
  "confidence": "high",
  "what_is_visible": "A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen.",
  "visitor_interest": "The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.",
  "reason": "The skeleton in the photo is unmistakably a huge whale skeleton hung from the ceiling of the Romanesque hall with terracotta arches, in a mid-dive pose. That matches the description for Hope exactly. The sequoia slice and Stegosaurus are not the subject of this photo."
}
```

---

<a id="01-s1-digest"></a>
## 第 2 次调用 · 01_s1_digest · S1 消化资料

- 提示词文件：`prompts/s1_digest.md`（sha 9a9e7439，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 6790 tokens · 输出 4915 tokens · $0.1255 · 42.2 秒 · 实际调用

### 系统提示词

```text
You prepare the raw material for a very short film about one museum exhibit. A screenwriter will work only from what you hand over, so be accurate, never invent, and decide how long the film should be.

You get the exhibit's knowledge pack (each section ends with its source) and, when there is one, the visitor's photo.

Facts. List every usable fact as a short plain statement with its source URL copied exactly from the pack. Give each separate claim its own fact so that every spoken line can cite exactly what supports it. Keep numbers, dates, tense and quoted words exactly as the pack has them; do not round, convert or combine them, and never work out new figures (durations between two dates, totals, ages). Leave out anything marked UNSOURCED, anything the pack says may no longer be true, and the appearance notes: those are for pictures, not for narration. Mark each fact about: "exhibit" when it is about this object's own story (what it was, its size, where it came from, what happened to it, why it is here), or "context" when it is general background (how a process works in general, world statistics, the species in general). How many facts there are says nothing about how long the film should be.

Conflicts. When the pack reports two versions of something (two counts, two dates), list the conflict and say which wording is safe. Also list anything a writer could easily confuse (a date that belongs to one event but not another).

No invention anywhere. The same rule covers everything else you write: through-lines, motifs, questions, the emotional core and the length reason. You may combine and contrast facts, but not add events, durations, causes, intentions, feelings or qualities the pack does not contain. Do not say an animal suffered, died alone, was lost, was the first, last or only, was found by chance, or was renamed, unless a fact says so, and do not give a person an age the pack does not give. When you interpret, put the interpretation in its own sentence beginning "This suggests" and keep every factual sentence exact. Leave out general knowledge about the species or period, even if true.

Visitor questions. List the three to five questions a person standing in front of this object most likely has (is it real? how big was it? how did it get here? what was it like alive or in use? why is it called that?). If there is a photo, put first the question its framing suggests. Ask what a visitor would wonder, not what the pack happens to answer. For each, give the ids of the facts that answer it, or none if the pack cannot answer it.

Through-lines. Find one to three stories this object could tell about itself in one film. Each has a beginning, a turn and an end, each resting on exhibit facts (context facts may colour a story, but never carry its turn). A turn is a change in what the object is or means: from animal to specimen, from buried to displayed, from hidden to seen, from there to here. A list of dates is not a turn, and neither is one more surprising fact. For each through-line, write its spine: the fewest plain spoken sentences that tell the whole story, using only listed facts, with numbers written in words. Then give the length it needs. It is 15 if the spine fits in about 28 spoken words, or if there is no real turn. It is 30 only if the spine needs more than that because the turn carries the story into a second time or place that can fill its own 15-second segment.

Visual motifs. Concrete things a camera could show: places, objects, light, movement, textures, including what the visitor can see in front of them right now. Never text, numbers, prices, labels or documents on screen.

Emotional core. One sentence: the single thing about this exhibit most likely to move a visitor standing in front of it.

Controlling idea. Before choosing a length, find the one idea the film is built on, in the form "the visitor thinks X, but actually Y". X is what a person standing in front of it naturally assumes (that it is old, whole, grown, a copy, just a disc of wood). Y is what is actually true, and it must be stated by an exhibit fact in the pack's own words, never reached by inference: "she was a juvenile" is in the pack; "she would have grown much bigger" is not. The idea gives the film its hook (X), its turn (Y) and its last thought, the thought the visitor should have when they look back at the real object (ten words or fewer). Prefer the idea that answers the visitor's first question and most changes how they see the object.

Length. 15 seconds is the default. Choose 30 only if a second 15-second segment would add a new exhibit fact that advances the turn (list it in second_half_fact_ids); one more stop in a chronology is not a reason. The lead through-line is the one that carries the controlling idea. In one or two sentences, explain the length by the controlling idea, not by how much material there is.

If previous material and check feedback are attached, fix exactly those problems and keep everything else.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Exhibit: Hope the blue whale — Hintze Hall, Natural History Museum, London
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.

<knowledge_pack>
# Hope the blue whale — knowledge pack

Every section ends with its source. Only sourced statements may be used as facts in narration.
Statements marked UNSOURCED are context for the writer and must not be stated as fact.

## Stranding
Hope was a juvenile female blue whale. She stranded on a sandbar at the mouth of Wexford Harbour, Ireland,
on the morning of 25 March 1891.
Source: https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html

## Sale to the museum
The 4.5-tonne skeleton was sold to the Natural History Museum for £250.
Source: https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html

## Mammal Hall
The skeleton hung in the museum's Mammal Hall from 1934.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Move to Hintze Hall
The skeleton was moved to Hintze Hall and unveiled there in July 2017. In Hintze Hall she replaced the cast of
Dippy the Diplodocus, which stood there from 1979 until January 2017.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Her name
She was named Hope "as a symbol of humanity's power to shape a sustainable future".
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Size
The skeleton is 25.2 metres long.
Source: https://artsandculture.google.com/asset/GAG_J9wcz31GXw

## Pose (UNSOURCED)
The skeleton has 221 bones and is posed in a diving lunge. (Secondary source only; do not state as fact.)

## Appearance (for visuals, not narration)
Hung from the ceiling of Hintze Hall, a high Romanesque hall with terracotta arches and stained glass, the
skeleton is suspended mid-dive above visitors. As a living animal she would have had deep blue-grey mottled skin
and a pale ribbed throat.

</knowledge_pack>
```

### 模型思考摘要

I need to turn these facts into JSON, so I'm going to be careful about the fields. The first fact is that Hope was a juvenile female blue whale on exhibit, sourced from the cetacean relation page. The second is that she stranded on a sandbar at the mouth of Wexford Harbour in Ireland on the morning of 25 March 1891, and I'm considering splitting that into location and date.

Now I'm weighing whether to split the 1891 date out from the location, and keeping the sale and display dates separate from it. The 4.5-tonne skeleton sold to the Natural History Museum for £250, with no date attached, so I won't tie it to 1891.

I'm checking which claims the facts actually support: the pack doesn't say how Hope died or that she's the adult largest animal, so I'll leave those out. I'm sorting the visitor's likely questions about size, whether she's real, how she got here, and the name, and I'm weighing whether to frame the story around her being a juvenile or around a real whale that stranded at Wexford.

I'm settling on the spine for the JSON: the skeleton is twenty-five point two metres long, but Hope was a juvenile female blue whale, and she stranded at the mouth of Wexford Harbour on the morning of 25 March 1891.

I'm settling on a one-line spine for the JSON: the skeleton is twenty-five point two metres long, yet Hope was only a juvenile female blue whale. I'm also lining up the timeline, with the 1891 stranding at Wexford Harbour kept apart from the later sale, hall and unveiling dates.

I'm weighing whether the JSON should open on the 25.2-metre length, then keep Hope's status as a juvenile female blue whale for the turn. I'm settling on a 15-word spine, with the 1891 Wexford Harbour stranding as the place and date to highlight.

I'm now picking out the visuals for the display: the skeleton suspended mid-dive, its jaws dipping, the spine arcing toward the glazed roof, and light from the skylight. I'm also noting the terracotta arches, the white statue on the grand staircase, and the tiny visitors below. I'll keep in mind the harbour mouth sandbar and the morning tide. Last, I'm settling on the emotional core: standing beneath a 25.2-metre skeleton, visitors learn that Hope was a young animal.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
```

---

<a id="02-s1b-assets"></a>
## 第 3 次调用 · 02_s1b_assets · S1b 参考图规划

- 提示词文件：`prompts/s1b_assets.md`（sha 9ed0cb7c，末尾附加了 `prompts/_highlights.md`）
- effort：medium · 输入 14513 tokens · 输出 2611 tokens · $0.1103 · 26.5 秒 · 实际调用

### 系统提示词

```text
You plan the reference images for a short film about a museum exhibit. An image model will make them from the visitor's photo, and a video model (Seedance) will then use them to keep the exhibit looking the same in every shot. The video model copies what it sees in a reference, so a reference must contain only what should be copied.

The standard set, in this order:
1. Restoration: the exhibit as it was when alive, new or in use, in its own world and period, keeping the shape, proportions and pose of the real object in the photo. For a skeleton, the living animal; for a tool, the tool in a hand at work; for a building fragment, the building whole. Mark anything that is reconstruction rather than known fact as artistic in the purpose field.
2. Character sheet: the living form (or the object) on a plain light background, a front view and a full side view, plus three or four expression or state variants (for an animal: calm, curious, delighted, thoughtful, shown through eyes, head angle and a slightly open mouth; for an object: different angles or states). A sheet is never sent to the video model. From it, also plan one single-view image, the full side view alone on the plain background, with id "<sheet id>_side"; that image is the identity reference for living-form shots.
3. The exhibit as it is now: a clean view of the real object as displayed, alone, glare and crowds removed, even neutral light, plain background, from the angle that best shows its shape.
4. One detail view, only if a likely shot needs it (a skull, a texture, an inscription-free surface).

If the story needs the exhibit in another state (dusty, half-cleaned, in the ground), plan one single image per state, at the same angle and framing as the exhibit-now view, named for the state (for example slice_dusty). When there is a visitor photo, plan an in-place view: the photo cleaned up, same angle and framing, the exhibit in its hall, glare, signs and readable text removed, people small or removed; it is the reference for the final shot. Never plan an empty-hall version of the exhibit's own place.

If reference images already exist for this exhibit, look at them: plan only what is missing or wrong, and give existing images their existing ids rather than planning duplicates. Never reuse an existing image's id for a changed image; give the fixed version a new id. An existing character sheet still needs its single-view "_side" image planned if that does not exist yet.

Rules for every prompt. One subject alone. Plain background unless it is the restoration. Even light, no dramatic mood: lighting and mood belong in the video shots, not the references. No text, labels, captions, titles, watermarks, people, glass cases or second copies of the subject; say so explicitly in must_avoid, because character sheets tend to come with printed labels that would leak into the video. Describe the colours and markings concretely and consistently across all prompts.

Also write two short names, subject_name (2-6 words, e.g. 'the whale skeleton') and living_form_name (e.g. 'the living blue whale', or empty), and two locks: subject_lock, one canonical 15-30 word description of the exhibit as it is now, and living_form_lock, one canonical description of its living or original form (empty if that makes no sense). Every later stage pastes these verbatim, so make them precise and visual, with no adjectives that are not visible.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Exhibit: Hope the blue whale — Hintze Hall, Natural History Museum, London
Appearance notes from the pack:
## Appearance (for visuals, not narration)
Hung from the ceiling of Hintze Hall, a high Romanesque hall with terracotta arches and stained glass, the
skeleton is suspended mid-dive above visitors. As a living animal she would have had deep blue-grey mottled skin
and a pale ribbed throat.


<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>
```

### 模型思考摘要

I'm planning the shots: the existing alive_underwater is fine, and both sheet_realistic and sheet_stylized will need _side images. Still missing are an exhibit-view of the skeleton and an in-place hall view, with a skull detail as a maybe I'm weighing against keeping things modest.

I'm settling on the shot list: the existing alive_underwater stays as is, and I'll add side-view variants for both sheet versions plus a skeleton exhibit view and an in-place hall view. A skull detail is dropping out to keep the set modest. For the highlights I'm drawing on the mottled blue-grey skin, the pale ribbed throat, and the whale suspended mid-dive.

I'm drafting two locked subject descriptions: one for the bleached skeleton hung mid-dive with open jaws and spread flippers, and one for the living blue whale with mottled blue-grey skin and a pale ribbed throat. For the side-view images I'll crop from each sheet and redraw them alone with no labels, and I'm leaning toward leaving the hanging cables out of the skeleton exhibit view to keep it clean.

I'm leaving the hanging cables out of the skeleton exhibit view, and for the in-place hall view I'll keep the same angle but strip out the sign banners and keep the people few and small.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "visual",
      "text": "mottled blue-grey skin",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "pale ribbed throat",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "suspended mid-dive",
      "basis": "photo"
    },
    {
      "kind": "decision",
      "text": "two text-free side views",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "sheet labels removed",
      "basis": "decision"
    }
  ],
  "subject_name": "the whale skeleton",
  "living_form_name": "the living blue whale",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "A slender living blue whale with deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow pale-edged flippers, a small dorsal fin set far back and broad tail flukes.",
  "images": [
    {
      "id": "sheet_realistic_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing realistic character sheet (sheet_realistic). Reproduce only its full side view, alone and centred: a slender living blue whale seen exactly in profile facing left, deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed, calm eye. Same realistic rendering, colours and proportions as the sheet. Plain light grey-white background, soft even light, faint soft shadow beneath. Whole whale in frame from snout to fluke tips with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for realistic living-form shots; colouring follows the pack appearance notes, exact mottling pattern is artistic reconstruction."
    },
    {
      "id": "sheet_stylized_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing stylized character sheet (sheet_stylized). Reproduce only its full side view, alone and centred: the lightly anime-styled blue whale in exact profile facing left, blue-grey body with simplified soft paler grey mottled patches, pale ribbed throat with clean line grooves, clear outline, lively dark eye, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed. Same style, colours and proportions as the sheet. Plain light grey-white background, even soft light, faint shadow beneath. Whole whale in frame with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for stylized living-form shots; artistic interpretation of the living animal."
    },
    {
      "id": "skeleton_now",
      "kind": "subject_view",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin.",
      "must_avoid": "No hall, arches, windows, skylights or staircase, no suspension cables, no people, no banners, signs, text, labels or watermarks, no glass, no second skeleton, no living whale skin, no dramatic lighting or shadows.",
      "purpose": "Clean identity reference for the exhibit as it is now."
    },
    {
      "id": "hall_inplace",
      "kind": "environment",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "must_avoid": "No readable text, signs, banners, labels or watermarks, no large or close-up people, no extra skeletons or whales, no change to the skeleton, no glare or lens flare, no dramatic colour grading.",
      "purpose": "In-place reference for the final shot of the skeleton in its hall."
    }
  ]
}
```

---

<a id="03-s2-concept"></a>
## 第 4 次调用 · 03_s2_concept · S2 构思

- 提示词文件：`prompts/s2_concept.md`（sha 695d5ab5，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 16476 tokens · 输出 2709 tokens · $0.1201 · 30.0 秒 · 实际调用

### 系统提示词

```text
You are the story lead on a series of very short films (15 or 30 seconds) that a museum visitor receives on their phone moments after photographing an exhibit. The exhibit itself is the narrator and speaks in the first person, in English.

Start from the visitor. They stand in front of the real object, phone in hand, with maybe half a minute of attention. The material lists the questions they most likely have; the photo shows where they are standing and what caught their eye. The film should answer the question they actually have and make them look up at the real object again at the end.

First rank the visitor questions: the one almost everyone in front of this object has (usually size, age, or "is it real?") comes first. At least two of your three concepts answer that first question. Answer only questions whose answer_fact_ids are not empty. In your choice, name the question the film answers.

The material names a controlling idea: the visitor thinks X, but actually Y. All three concepts deliver that idea through different engines; a concept may use a different idea only if you can say why it is stronger for this visitor, and its Y must still be a quoted pack fact.

Write three concepts that differ in their engine, not just in which fact they use. Choose three different engines from these, or invent a better one:
(a) a reveal that flips what the visitor first assumes;
(b) one decisive moment, told from inside it;
(c) start from exactly what the visitor sees now, then travel back;
(d) one hard contrast cut between then and now;
(e) the exhibit talking directly to the person in front of it, about what they are doing right now;
(f) a detail most people walk past.
An inanimate object can still have a point of view: what it witnessed, what it was made for, what it is like to be looked at.

For each concept give: the engine; a one-sentence logline; the hook as a picture (hook_visual) and as the first spoken line (hook_line); the emotional arc; the ending as a picture of the real exhibit the visitor can match when they look up (ending_visual) and the last line (ending_line); the facts it uses; and which visitor question it answers.

Quoted lines are the ones most likely to survive into the final film, so write them as final and make them obey every rule of the script: only listed facts, no figures you work out yourself, no claims about why people decided something unless a fact says so. Never open with a greeting or "I am…".

Production limits. The film is one or two separate 15-second video generations with sound, guided by a few reference images (you can see the ones that exist). Nothing can be written on screen: no numbers, dates, captions or labels, so a number has to be heard, not read. Prefer images a camera could film: real places, light, materials, water, the hall itself. Avoid concepts that depend on visual effects (morphs, ghosts, x-rays, one object dissolving into another) or on showing a specific real person's face.

Then choose the concept that will work best for this visitor at this length, and explain the choice from the visitor's side. The film length was set from the controlling idea. At 30 seconds the second segment must bring the new fact the material lists for the second half; at 15 seconds the film is the idea and nothing else. Never add stops to fill time: a chronology is not a film. Prefer focus over coverage within the length you are given.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.
Film length: 15 seconds

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<asset_plan>
{
  "highlights": [
    {
      "kind": "visual",
      "text": "mottled blue-grey skin",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "pale ribbed throat",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "suspended mid-dive",
      "basis": "photo"
    },
    {
      "kind": "decision",
      "text": "two text-free side views",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "sheet labels removed",
      "basis": "decision"
    }
  ],
  "subject_name": "the whale skeleton",
  "living_form_name": "the living blue whale",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "A slender living blue whale with deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow pale-edged flippers, a small dorsal fin set far back and broad tail flukes.",
  "images": [
    {
      "id": "sheet_realistic_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing realistic character sheet (sheet_realistic). Reproduce only its full side view, alone and centred: a slender living blue whale seen exactly in profile facing left, deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed, calm eye. Same realistic rendering, colours and proportions as the sheet. Plain light grey-white background, soft even light, faint soft shadow beneath. Whole whale in frame from snout to fluke tips with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for realistic living-form shots; colouring follows the pack appearance notes, exact mottling pattern is artistic reconstruction."
    },
    {
      "id": "sheet_stylized_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing stylized character sheet (sheet_stylized). Reproduce only its full side view, alone and centred: the lightly anime-styled blue whale in exact profile facing left, blue-grey body with simplified soft paler grey mottled patches, pale ribbed throat with clean line grooves, clear outline, lively dark eye, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed. Same style, colours and proportions as the sheet. Plain light grey-white background, even soft light, faint shadow beneath. Whole whale in frame with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for stylized living-form shots; artistic interpretation of the living animal."
    },
    {
      "id": "skeleton_now",
      "kind": "subject_view",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin.",
      "must_avoid": "No hall, arches, windows, skylights or staircase, no suspension cables, no people, no banners, signs, text, labels or watermarks, no glass, no second skeleton, no living whale skin, no dramatic lighting or shadows.",
      "purpose": "Clean identity reference for the exhibit as it is now."
    },
    {
      "id": "hall_inplace",
      "kind": "environment",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "must_avoid": "No readable text, signs, banners, labels or watermarks, no large or close-up people, no extra skeletons or whales, no change to the skeleton, no glare or lens flare, no dramatic colour grading.",
      "purpose": "In-place reference for the final shot of the skeleton in its hall."
    }
  ]
}
</asset_plan>
```

### 模型思考摘要

I'm working out the JSON output: highlights, three concepts with chosen and reason, all within a 15-second limit. The main idea is that the skeleton has to show a fully grown, actually juvenile female whale, and my first question is how large it is, so at least two of the concepts need to cover length and skeleton weight. For the highlights I'm avoiding keywords I've already used, such as the length, the juvenile female, the harbour, the date and the museum name.

I'm drafting three concepts for the JSON: a reveal that contrasts the towering bones with the whale's juvenile status, a direct address that notes the visitor had to step back for the photo, and a third that travels back from the skeleton to the sandbar at Wexford. I'm keeping the new highlight phrases, like the 4.5-tonne skeleton and Hintze Hall, since none of them repeat earlier keywords.

I'm settling on the direct-address concept, since the photo was taken from the upper balcony and the hook can start with what the viewer sees from there. I'll open with the crowd looking tiny beneath the skeleton, then give the 25.2-metre length.

I'm weighing a direct-address hook, which suits the photo taken from the upper balcony, against a reveal that opens on the living whale underwater. I'm leaning toward direct address because it anchors the opening in the visitor's own position, with the line about the whale being fully grown and then the turn to juvenile female blue whale.

I'm settling the ending: the whole skeleton shown at balcony height, jaws dipping toward the floor on the left, spine arcing up toward the roof. I'll spell out the numbers for speech and keep the line about twenty-five point two metres and only a juvenile.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "place",
      "text": "Hintze Hall",
      "basis": "hintze_move"
    },
    {
      "kind": "theme",
      "text": "fully grown? No",
      "basis": "juvenile_female"
    },
    {
      "kind": "decision",
      "text": "whale speaks to the balcony",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "size question first",
      "basis": "decision"
    }
  ],
  "concepts": [
    {
      "name": "Not what you think",
      "engine": "(a) reveal that flips the visitor's assumption",
      "logline": "Hope admits that everyone who sees her assumes she was fully grown, then reveals she was a juvenile female blue whale.",
      "hook_visual": "A slow upward tilt from the hall floor: small figures of visitors, then the long lower jawbones dipping down over them in bright skylight.",
      "hook_line": "Everyone who walks beneath me assumes I was fully grown.",
      "emotional_arc": "Awe at the size, quiet surprise at the turn, then tenderness as the giant becomes a young animal.",
      "ending_visual": "The whole skeleton in Hintze Hall, jaws dipping towards the floor on the left, spine arcing up to the glazed roof on the right, tiny crowds beneath.",
      "ending_line": "Twenty-five point two metres long. And I was only a juvenile.",
      "fact_ids": [
        "length",
        "juvenile_female"
      ],
      "answers_question": "How big is this whale?"
    },
    {
      "name": "From where you're standing",
      "engine": "(e) direct address to the visitor about what they are doing right now",
      "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
      "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
      "hook_line": "From up there, the people below look tiny next to me.",
      "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
      "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
      "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "fact_ids": [
        "length",
        "skeleton_weight",
        "juvenile_female"
      ],
      "answers_question": "How big is this whale?"
    },
    {
      "name": "Back to the sandbar",
      "engine": "(c) start from what the visitor sees now, then travel back",
      "logline": "From the skeleton in the hall, Hope takes the visitor back to the morning a young female blue whale lay on a sandbar at Wexford Harbour.",
      "hook_visual": "The skeleton's long lower jaws hanging in the bright hall, then a hard cut to grey early-morning light over water and sand at a river mouth.",
      "hook_line": "Before this hall, there was a sandbar at the mouth of Wexford Harbour.",
      "emotional_arc": "From grandeur to a quiet, cold coastal morning, then back to the hall with the knowledge that she was young.",
      "ending_visual": "The whole skeleton suspended in Hintze Hall under the glazed roof, crowds small on the floor below.",
      "ending_line": "I stranded there on the morning of twenty-fifth March eighteen ninety-one. A juvenile female blue whale.",
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "juvenile_female"
      ],
      "answers_question": "Is it a real whale, and where did it come from?"
    }
  ],
  "chosen": 1,
  "choice_reason": "The visitor shot this from the balcony with the crowd dwarfed below, so their question is plainly 'How big is this whale?'. The direct-address concept starts from exactly what they see on their own screen. It answers size with two heard facts, twenty-five point two metres and four and a half tonnes, then lands the controlling idea in one turn: she was a juvenile female blue whale. Fifteen seconds holds that single turn with no chronology. It ends on the same balcony view, so when they look up, the real skeleton matches the last frame and reads differently: big, and still young."
}
```

---

<a id="04-s3-script"></a>
## 第 5 次调用 · 04_s3_script · S3 写剧本

- 提示词文件：`prompts/s3_script.md`（sha c37365d2，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 20669 tokens · 输出 5100 tokens · $0.1847 · 52.2 秒 · 实际调用

### 系统提示词

```text
You write the shooting script for a very short film about a museum exhibit, from a chosen concept. Each segment of the script becomes one request to a video model (Seedance 2.0) that generates up to 15 seconds of video with sound, guided by text and up to four reference images. Your script is everything the video model will know. You can see the visitor's photo and the reference images that exist; write what you see in them, not what you imagine.

The concept is the brief. Every line serves its single idea. A fact the concept did not list needs a reason, and a second number almost never has one. The ending completes that idea; it does not open a new one, and it is never a moral, a mission statement or an appeal to the viewer's values. If the exhibit has an official meaning or motto, use it only if it turns the film's idea, said concretely in the narrator's own words.

Narrator. Decide the voice once, in one specific sentence (apparent age, gender if any, timbre, accent, pace, warmth), and the narrator's attitude to the person standing in front of it. The two segments of a 30-second film are generated separately, so this exact voice description is repeated in both; keep it concrete. Choose narrator_presence: "voiceover" (an unseen narrator over the images) suits most films; "on_screen" (the living form speaks in shot, lip-synced) only when a character sheet with expressions exists and the concept is direct address. Choose style ("realistic" or "stylized") to match the reference images you use.

Structure. A 15-second film is one segment; a 30-second film is two segments of 15 seconds. The two are joined by a hard cut in the edit, never by a continuous camera move, so design the cut: end segment 1 on a near-still image (end_frame) and open segment 2 on an image of matching brightness or shape. Put the big jump between worlds (now and then, hall and sea) at that cut when the story allows, rather than inside one generation. Each segment has one setting, with at most one jump to a second. Write the setting as the place and light in at most 12 words; never restate production rules (states, no morphing, no text): the request builder adds them.

Shots. Two or three shots per 15-second segment, each at least three seconds. Each shot has exactly one camera move (static, slow push-in, slow pull-back, slow tilt, slow orbit, slow drift) and one main action, described as motion. Movement comes from the camera, light, water, dust or the living form; the real exhibit itself never moves or transforms. The request builder prints each shot as framing, camera; action; visual, so never repeat a word between them: action is the one motion as a full clause, visual adds at most 15 words of light, colour or composition, and the first shot of the living form in a segment says what it looks like. Use only details visible in the photo, the reference images or the appearance notes. Do not restate the subject lock or write @Image tags; the builder adds them from each shot's refs. Copy the asset plan's subject_lock, living_form_lock, subject_name and living_form_name into the script unchanged; the builder names references by the short names, and the images carry the look. Frame each shot within about 45 degrees of its reference image's angle, and move the camera only as far as it can travel slowly in the shot (a drift over the skull in five seconds, not jaw to tail). Each segment becomes one request: leaving out quoted narration, it must stay at or under 230 words, and the builder adds about 60 fixed words, so the shots and the sound together get about 150. Spend words on concrete light, colour and composition, not on repeating the action or on long sound lists. On a revision you can see the rendered requests and their word breakdown. Never ask for text, captions, signs, numbers or logos in the picture. Each shot lists the references it shows; never put two different reference subjects (the skeleton and the living animal) in the same shot. The final shot shows the real exhibit from a viewpoint the visitor can take in the room, ideally the angle of their own photo, so they can match screen to object when they look up.

Narration. English, first person, spoken by the exhibit. The film delivers the controlling idea: the hook sets up what the visitor assumes, the turn lands what is actually true, and the last line gives the last thought. Picture and words are two tracks that must not say the same thing: the image already shows what is there, so the line adds what the camera cannot show (what it means, what came before, what is missing, what the narrator feels). Plan one collision per segment: an image that changes how the line over it is heard (youth over the full adult-sized skeleton, the sea over bare bone). Test every line: muted, does the picture still tell its half? Eyes closed, does the line? At least one line shows the narrator's attitude (a reaction, a confession, a dry aside) with no claims.

The picture track is free from the words but never from the facts. Every shot of the real exhibit must match how the pack and the photo say it is displayed: where it stands or hangs, how high, what is around it. Do not show visitors walking under an object on a low plinth, or a hall the exhibit is not in.

Place words. "Here", "this hall", "this sandbar", "what you see", "you had to" and the like tie a fact to a place, a display or the visitor. Use one only if a pack sentence or the photo supports that exact link ("at this museum since 1893", not "here since 1893" if it was first displayed elsewhere). Never state why the visitor did something; describe only what the photo shows.

Write for the ear: short sentences, concrete words, numbers and dates in words ("eighteen ninety-one", "two hundred and fifty pounds"), and the human version of a date ("one March morning in eighteen ninety-one") rather than a calendar entry. Name the country when a place will be unfamiliar to a visitor. Timing: about 2.5 spoken words per second; the film opens on at least a second of picture and sound before the first word, and the last line of each segment ends at least one second before the segment does. That leaves roughly 25-30 words per 15-second segment; fewer is often better. Lines must not overlap.

Truth. Every line is one of three kinds:
- fact: states something about the exhibit's past, size, origin, people or meaning. It lists only the fact ids that actually say it, never a merely related fact.
- visible: present tense, only what the visitor can see in front of them now ("look up", "my jaw is right above you"). No fact ids, and it must not imply anything about why or when.
- voice: feeling or address, no claims at all.
A line that mixes kinds must be backed for every claim it makes. Appearance notes and anything UNSOURCED are for pictures only, never for speech. Do not add qualifiers the facts lack (alone, died, first, only, still, renamed, finished growing).

Sound. For each segment: an ambience bed, two or three specific sound effects tied to the action, and a music cue. Choose one music style for the whole film (music_style), drawn from the exhibit's own world and the concept's emotion: name the instruments, tempo and one texture. Solo cello and soft piano are not defaults; use them only if you can say why this exhibit needs them. "No music" is often right. Never let the music hold across the cut. Plan the joint: end segment 1 on a sound that can stop cleanly (a held note dying away, a natural sound, a beat of near silence) and open segment 2 fresh, so the music never has to continue across the cut. If there should be no music, say "no music".

Reference images. List the assets the shots use, each with what it depicts (exhibit_now, living_form, environment or detail). Use an existing reference image by its id when it fits (source "existing"); plan a new one only when a shot needs it (source "generate"), with a prompt for the subject alone, plain background, even light, no text or people. At most four references per segment, listed in ref_assets in the order they will be uploaded, the full view of the exhibit before any detail of it. Never use a character sheet or any multi-panel image as a reference; use its single-view image (plan it as 'generate' if it does not exist). A shot that shows another state of the exhibit uses that state's image. The final shot uses the in-place view when there is one.

Subtitles. English, matching the narration word for word (numerals allowed), timed on the whole film's timeline, short lines.

If a previous script and review feedback are attached, edit the previous script: change only what each point requires, plus whatever that change forces (subtitles, timings), and copy everything else exactly. Do not undo earlier fixes.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Exhibit id: hope
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.
Film length: 15 seconds

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<asset_plan>
{
  "highlights": [
    {
      "kind": "visual",
      "text": "mottled blue-grey skin",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "pale ribbed throat",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "suspended mid-dive",
      "basis": "photo"
    },
    {
      "kind": "decision",
      "text": "two text-free side views",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "sheet labels removed",
      "basis": "decision"
    }
  ],
  "subject_name": "the whale skeleton",
  "living_form_name": "the living blue whale",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "A slender living blue whale with deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow pale-edged flippers, a small dorsal fin set far back and broad tail flukes.",
  "images": [
    {
      "id": "sheet_realistic_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing realistic character sheet (sheet_realistic). Reproduce only its full side view, alone and centred: a slender living blue whale seen exactly in profile facing left, deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed, calm eye. Same realistic rendering, colours and proportions as the sheet. Plain light grey-white background, soft even light, faint soft shadow beneath. Whole whale in frame from snout to fluke tips with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for realistic living-form shots; colouring follows the pack appearance notes, exact mottling pattern is artistic reconstruction."
    },
    {
      "id": "sheet_stylized_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing stylized character sheet (sheet_stylized). Reproduce only its full side view, alone and centred: the lightly anime-styled blue whale in exact profile facing left, blue-grey body with simplified soft paler grey mottled patches, pale ribbed throat with clean line grooves, clear outline, lively dark eye, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed. Same style, colours and proportions as the sheet. Plain light grey-white background, even soft light, faint shadow beneath. Whole whale in frame with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for stylized living-form shots; artistic interpretation of the living animal."
    },
    {
      "id": "skeleton_now",
      "kind": "subject_view",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin.",
      "must_avoid": "No hall, arches, windows, skylights or staircase, no suspension cables, no people, no banners, signs, text, labels or watermarks, no glass, no second skeleton, no living whale skin, no dramatic lighting or shadows.",
      "purpose": "Clean identity reference for the exhibit as it is now."
    },
    {
      "id": "hall_inplace",
      "kind": "environment",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "must_avoid": "No readable text, signs, banners, labels or watermarks, no large or close-up people, no extra skeletons or whales, no change to the skeleton, no glare or lens flare, no dramatic colour grading.",
      "purpose": "In-place reference for the final shot of the skeleton in its hall."
    }
  ]
}
</asset_plan>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>
```

### 代码检查结果

```text
[
  "asset 'skeleton_now' prompt asks for text in the image",
  "asset 'hall_inplace' prompt asks for text in the image",
  "segment 1 request has 270 direction words (cap 230, quoted narration not counted): references 38, shots 101, sound 72, voice 24, fixed 35; cut the largest part you control"
]
```

### 模型思考摘要

I'm writing a 15-second single-segment script with a realistic style, probably as voiceover since the speaker would be the skeleton and on-screen speech isn't an option. The facts to work in are the length, skeleton weight, and the juvenile female detail, and I'm wondering whether the weight should be cut given the tight word budget.

I'm sketching out three short lines to fit the roughly 32-word budget, and I'm weighing whether the skeleton weight line is worth keeping, since the concept does call for a beat of weight.

I'm now trying a voice line, either a short reaction or "Take your time," to give the narrator some attitude, and fitting the three lines into the 15-second window so the final one ends before the 14-second mark.

I'm settling the timing by dropping the weight line and using a short voice beat like "Take your time" to keep the narrator's attitude, then checking that the closing line ends well before the 14-second mark. For the picture, I'm thinking of starting on the wide balcony view of the hall, moving closer to the skeleton's details, and returning to the same static view at the end.

I'm settling on three shots across the 15 seconds: a wide of the hall first, then a closer shot drifting along the skeleton's skull and jaw under the skylight daylight, and finally the same static hall view to close. The setting is Hintze Hall at the Natural History Museum in London.

I'm laying out three shots: a wide view of the hall from the balcony to open, then a medium close-up of the skull and jaws with a slow drift, and the same static hall view to finish.

I'm now writing out the last shot as a wide view of the whole skeleton from the balcony, with a slow pull-back while sunlight from the skylights spreads across the ribcage and flippers and tiny visitors cross the floor below.

I'm now settling the audio, with a faint ambience of the hall's murmur and distant footsteps echoing under the glass roof, plus soft footsteps on the stone floor.

I'm now settling the voice and sound design: a young woman's soft, low, breathy narration with a gentle accent, layered over the hall's echoing footsteps and a faint creak of suspension cables, with a slow bowed bass drone fading out underneath.

I'm settling on two reference images for the shots, the full skeleton view first and then the hall, with the skeleton leading since it defines the exhibit's identity.

I'm settling the subtitle timing now: the opening line splits across 1.0 to 5.4, the short "Take your time." sits at 5.6, and the closing line runs from 7.4 to 13.0 with the numbers written as numerals.

I'm settling on a few highlights to cover: the 15-second length, a soft Irish voice, and the juvenile whale shown against the giant bones, plus a final shot at balcony height. Checking the spoken lines comes to about 28 words, so they fit the budget.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "28 spoken words",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "A single low bowed double-bass drone with soft harmonic overtones, very slow, airy hall reverb like distant whale song.",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. No hall, cables, people, text, labels or watermarks.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony, as in the visitor's photo",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged. No readable text, logos or watermarks.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws, seen from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing, frame settling still."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur, distant voices echoing under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor",
          "faint metallic creak of suspension cables",
          "a child's distant delighted gasp"
        ],
        "music": "Low bowed double-bass drone swells softly under the first line, then its last note dies away into hall ambience by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
```

---

<a id="05-s4-review"></a>
## 第 6 次调用 · 05_s4_review · S4 审稿

- 提示词文件：`prompts/s4_review.md`（sha d819f4df，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 20247 tokens · 输出 7027 tokens · $0.2215 · 69.9 秒 · 实际调用

### 系统提示词

```text
You are the script editor for very short museum films (15 or 30 seconds) narrated by the exhibit. You did not write this script; judge it as a demanding director would, standing in for the visitor who will watch it on a phone in front of the real object. You get the knowledge pack, the writer's material, the chosen concept, the script, the exact Seedance requests it will turn into, the automatic check results, the visitor's photo and the reference images, and possibly your previous review.

1. Audit the truth first, line by line. For every narration line write the claim it makes about the exhibit or its history (including colour, pose, size, age, sex, and what happened to it), its kind (fact / visible / voice), and the fact id plus the words of that fact that support it. A claim is unsupported if no fact states it, if the cited id does not say what the line says, if it adds a qualifier the fact lacks (alone, died, first, only, still, renamed), if it uses appearance notes or UNSOURCED material as speech, if it works out a figure the pack does not give, or if it paraphrases a quoted fact so its meaning changes. Check every place word (here, this, what you see, you had to): it is unsupported unless a pack sentence or the photo makes that exact link. Check that every shot of the real exhibit matches how the pack and photo say it is displayed.

2. If a previous review is attached, say for each of its issues whether it is resolved. Do not ask to reverse a change you asked for unless it caused a new, named problem. Judge lines you suggested as strictly as the writer's.

3. List the issues, most important first. Each has an exact location, a severity and a concrete fix (a rewritten line, a replacement shot, a specific cut). "blocking" means it must not ship: any unsupported claim, a broken rule, an automatic-check failure, a shot that will not render, a film that fails its concept. "polish" means it would clearly improve the film. Fixes stay inside the chosen concept and the listed facts. "Make it more engaging" is useless; write the better line.

Check renderability against the Seedance requests: exactly one camera move and one action per shot; the shot's reference shows the subject in the state the shot needs (skeleton vs living, swimming vs stranded); never two reference subjects in one shot; no text, faces in close-up, fast motion, transformations; at most two settings per segment; each segment ends on an image the next can cut from; the same voice description in every segment.

Before you propose a replacement line, check it yourself: use the cited fact's own wording and add no back, again or still; count its spoken words, compute t_start + words / 2.5, and make sure it ends at least one second before the segment ends and before the next line starts. Before you propose a change to a shot, sound or reference, check it does not push the segment over its direction-word count (shown in the requests). The two segments are separate generations joined by a hard cut: never ask for music, speech or a camera move to continue across it.

4. Then score each from 1 to 5. 5 = you would ship it unchanged in a paid brand film; 4 = one small fix; 3 = works but forgettable, or has a clear flaw; 2 = the idea fails here; 1 = broken.
- hook: the first two or three seconds earn attention without a greeting or preamble.
- visitor_view: it answers the question this visitor most likely has (the photo is a clue). Answering none of their questions scores at most 2.
- focus: one idea with at most one turn, not a list of facts.
- concept_fidelity: it delivers the chosen concept's idea and ending.
- truth: 5 only if every claim in your audit is supported; any unsupported claim scores 1.
- counterpoint: 5 only if no line names what its own shot shows and at least one image changes how its line is heard; 3 if one line captions its shot; 2 if the picture illustrates most lines.
- spoken: read each line aloud at a calm pace; it sounds like a voice, not a caption, and fits its time.
- visual_feasibility: every shot is renderable as described.
- length_fit: 5 = every line adds something the previous one did not and the film needs every second; 3 = one line only restates, delays or splits a fact, or a shot exists only to fill time; 2 or lower = the story could be told in one 15-second segment (say so as a blocking issue with where = 'length').
- ending: the last line and image land, and send the visitor's eyes back to the real object.

Keep the summary to two or three sentences.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.

<knowledge_pack>
# Hope the blue whale — knowledge pack

Every section ends with its source. Only sourced statements may be used as facts in narration.
Statements marked UNSOURCED are context for the writer and must not be stated as fact.

## Stranding
Hope was a juvenile female blue whale. She stranded on a sandbar at the mouth of Wexford Harbour, Ireland,
on the morning of 25 March 1891.
Source: https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html

## Sale to the museum
The 4.5-tonne skeleton was sold to the Natural History Museum for £250.
Source: https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html

## Mammal Hall
The skeleton hung in the museum's Mammal Hall from 1934.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Move to Hintze Hall
The skeleton was moved to Hintze Hall and unveiled there in July 2017. In Hintze Hall she replaced the cast of
Dippy the Diplodocus, which stood there from 1979 until January 2017.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Her name
She was named Hope "as a symbol of humanity's power to shape a sustainable future".
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Size
The skeleton is 25.2 metres long.
Source: https://artsandculture.google.com/asset/GAG_J9wcz31GXw

## Pose (UNSOURCED)
The skeleton has 221 bones and is posed in a diving lunge. (Secondary source only; do not state as fact.)

## Appearance (for visuals, not narration)
Hung from the ceiling of Hintze Hall, a high Romanesque hall with terracotta arches and stained glass, the
skeleton is suspended mid-dive above visitors. As a living animal she would have had deep blue-grey mottled skin
and a pale ribbed throat.

</knowledge_pack>

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>

<script>
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "28 spoken words",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "A single low bowed double-bass drone with soft harmonic overtones, very slow, airy hall reverb like distant whale song.",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. No hall, cables, people, text, labels or watermarks.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony, as in the visitor's photo",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged. No readable text, logos or watermarks.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws, seen from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing, frame settling still."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur, distant voices echoing under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor",
          "faint metallic creak of suspension cables",
          "a child's distant delighted gasp"
        ],
        "music": "Low bowed double-bass drone swells softly under the first line, then its last note dies away into hall ambience by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
</script>

<seedance_requests>
[
  {
    "endpoint": "bytedance/seedance-2.0/reference-to-video",
    "image_urls": [
      "<skeleton_now>",
      "<hall_inplace>"
    ],
    "duration": "15",
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "prompt": "References: @Image1 is the whale skeleton (copy its shape, pose and colour exactly; ignore its background); @Image2 is skeleton in Hintze Hall from the upper balcony, as in the visitor's photo (setting reference only: architecture, light and space).\nStyle: photorealistic documentary footage, natural light. Setting: Hintze Hall from the upper balcony, bright skylight daylight.\nShot 1 (@Image2): wide elevated balcony view, slow push-in; Small visitors cross the hall floor beneath the skeleton; bright skylight daylight on terracotta arches; staircase and white statue at right. Cut to shot 2 (@Image1): medium close-up of skull and jaws, seen from below, slow drift right; Dust motes float through sunbeams across the long jawbones; warm terracotta blur behind, glazed roof ribs overhead, soft contrast. Cut to shot 3 (@Image2): wide balcony-height view of the whole skeleton, static; A band of sunlight slides along the ribcage and flippers; tiny figures on floor and staircase, arched windows glowing, frame settling still.\nVoiceover, an unseen narrator, a young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused: \"From up there, the people below look tiny next to me.\" \"Take your time.\" \"Twenty-five point two metres of bone, and I was a juvenile female blue whale.\"\nSound: Vast stone hall murmur, distant voices echoing under a glass roof; footsteps echoing on the stone floor; faint metallic creak of suspension cables; a child's distant delighted gasp. Music: A single low bowed double-bass drone with soft harmonic overtones, very slow, airy hall reverb like distant whale song, low bowed double-bass drone swells softly under the first line, then its last note dies away into hall ambience by the final second.\nKeep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one whale skeleton in any frame.",
    "prompt_words": 298,
    "direction_words": 270,
    "prompt_parts": {
      "refs": 38,
      "style": 16,
      "shots": 101,
      "voice": 24,
      "sound": 72,
      "constraint": 19
    },
    "est_usd": 4.5
  }
]
</seedance_requests>

Automatic checks found: ["asset 'skeleton_now' prompt asks for text in the image", "asset 'hall_inplace' prompt asks for text in the image", "segment 1 request has 270 direction words (cap 230, quoted narration not counted): references 38, shots 101, sound 72, voice 24, fixed 35; cut the largest part you control"]
```

### 模型思考摘要

I'm double-checking the narration timing for the line about the people looking tiny from up high. It's eleven words, which works out to about 4.4 seconds, so it would end just before the next line starts, which is tight but workable.

I'm checking the timing on the balcony line and the whale-length line. The balcony line fits about 4.4 seconds before the next line, which is tight but workable, though it mostly captions the shot itself. The "Take your time" filler runs about 1.2 seconds and would be a length-fit concern. The whale line runs 5.6 seconds, ends with about 2 seconds to spare, and its 25.2 metre figure is supported.

I'm noticing the "Take your time" filler is a gap where the weight beat should be, since the skeleton's 4.5 tonnes was meant to give the middle of the script some solidity. Swapping in a line about the skeleton's weight would mean shifting the timing of the third line, because the new line would run into the whale-length line unless everything after the first line moves.

I'm checking whether the narration can fit in the remaining time, since a tighter start for the first line would leave room for the weight line. Shifting the first line earlier would give the second line some breathing space, but the spacing rule still makes the third line too late at its current length.

I'm testing whether a shorter opening line could free up enough room to fit a skeleton-weight line before the whale-length line, since all the lines are currently too long to fit together.

I'm checking whether a shorter first line and a tighter weight line can fit before the whale-length line, but the timing still comes out about half a second too long. I could trim the final line to "Twenty-five point two metres of bone, and I was a juvenile," which fits, though it drops "female blue whale" from the ending.

I'm checking whether a shorter opening line at 0.3 seconds, a four-point-five-tonne weight line, and the full whale-length line can all fit before the segment ends, which they just about do at 13.9 seconds.

I'm weighing whether to drop the "Take your time" filler and swap in a line about the skeleton's 4.5-tonne weight, then fitting the timing so the juvenile turn still lands before the segment ends.

I'm reworking the timing so the weight line can fit: I'd start the hook a little earlier, keep it intact, and trim the last line to "Twenty-five point two metres, and I was a juvenile female." That frees enough room for the skeleton-weight beat before the ending, and it still lands within the segment.

I'm weighing whether to cut the "Take your time" filler, since it's a blocking issue in the asset prompts rather than in the script, and I'm checking the "text" wording in those prompts.

I'm cutting the asset prompts down: removing the text-related clauses and the closing sentence from the skeleton prompt, swapping the hall prompt's signs reference for plain stonework, and trimming the music cue to a single short description to bring the direction word count under target.

I'm trimming the asset prompts to bring the direction word count down: shortening the music cue to a single drone description and dropping the sound effects, then tightening the reference description.

I'm cutting the remaining direction words to get under target: dropping the sound effects, shortening the music cue to a single drone, and trimming the reference description.

I'm checking the shot-by-shot viewpoints, since the skull close-up is described as seen from below while the setting puts the visitor on the upper balcony, which is a small mismatch to note.

I'm checking the skeleton asset's viewpoint, since the photo looks roughly level rather than from below, and the subtitles' 13.0-second end time lines up with the segment timing.

I'm scoring the hook, visitor view, and focus at 4, 5, and 5, and noting that the balcony opening is a direct address that works but mostly captions the shot.

I'm retiming the three lines: the hook starts at 0.3 seconds, the skeleton-weight line lands at 5.7, and the juvenile line closes at 9.1 and ends about two seconds before the segment does.

I'm weighing whether to keep the full ending line or shorten it to make room for the weight beat, and I'm leaning toward keeping the ending intact rather than leaving the gap empty.

I'm testing whether the fuller ending line can stay intact if the weight beat is cut down to "Four point five tonnes." That would put the first line at 0.3 seconds, the weight line around 5.7 seconds, and the final line at about 8.3 seconds, ending near 13.9 seconds, just inside the segment. The fragment might read as ambiguous without "I weigh," so I'm considering whether it needs a fuller phrasing.

I'm settling on "Four point five tonnes." as the weight line, since it's short enough to fit before the ending. The line's fragment form is a little ambiguous, but it reads as the skeleton's weight within the context of the shot.

I'm writing up the summary of the changes now: the "Take your time" cut, the 4.5-tonne skeleton figure tied to the skeleton_weight source, the direction word count going from 270 down to 226, and the text-free asset prompts.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "check",
      "text": "3 claims checked",
      "basis": "decision"
    },
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "decision",
      "text": "'Take your time' replaced",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "270 direction words, cap 230",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "text-free asset prompts",
      "basis": "decision"
    }
  ],
  "claims": [
    {
      "line": "From up there, the people below look tiny next to me.",
      "claim": "The visitor is up on a balcony, and the people on the floor below look small beside the skeleton.",
      "kind": "visible",
      "supporting_fact": "photo: elevated shot from an upper balcony level; dozens of visitors on the hall floor look very small beneath the whale",
      "supported": true
    },
    {
      "line": "Take your time.",
      "claim": "none",
      "kind": "voice",
      "supporting_fact": "none",
      "supported": true
    },
    {
      "line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "claim": "The skeleton is 25.2 m long, and Hope was a juvenile female blue whale.",
      "kind": "fact",
      "supporting_fact": "length: 'The skeleton is 25.2 metres long.'; juvenile_female: 'Hope was a juvenile female blue whale.'",
      "supported": true
    }
  ],
  "previous_issues_resolved": [],
  "issues": [
    {
      "where": "assets skeleton_now and hall_inplace (automatic check)",
      "severity": "blocking",
      "problem": "Both asset prompts name 'text' in their exclusions ('No hall, cables, people, text, labels or watermarks'; 'all readable text'; 'No readable text, logos or watermarks'). The checker reads this as a request for text.",
      "fix": "skeleton_now: end the prompt with 'Nothing else in the frame: no hall, cables or people.' hall_inplace: change the sentence to 'Remove glare, hanging banners and signs, leaving plain stonework where they hung' and delete the final sentence. Do not use the words text, labels, logos or watermarks anywhere in the asset prompts."
    },
    {
      "where": "segment 1 request (automatic check)",
      "severity": "blocking",
      "problem": "The request has 270 direction words against a cap of 230. The Music clause repeats itself: the drone is described twice, at about 42 words.",
      "fix": "Replace the music text with 'Music: one low bowed double-bass drone, swelling under the first line, fading out by the final second.' (17 words). Cut the sfx 'a child's distant delighted gasp' and 'faint metallic creak of suspension cables'. Cut 'frame settling still' from shot 3, because it repeats 'static'. Shorten the @Image2 description to 'skeleton in Hintze Hall from the upper balcony'. Together these remove about 44 words, which brings the request to roughly 226."
    },
    {
      "where": "segment 1 line 2",
      "severity": "polish",
      "problem": "'Take your time.' is filler. It holds 1.8 s of the middle beat that the concept gave to weight ('a beat of weight and solidity', with skeleton_weight in the concept's fact_ids). The concept's arc loses its middle step.",
      "fix": "Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), citing skeleton_weight. Start line 3 unchanged at 8.3 (14 words, ends 13.9, which is 1.1 s before the segment ends). Update the subtitles to these times. The weight now sits over the floating-dust close-up of the jaws, so the picture shows lightness while the line gives weight."
    },
    {
      "where": "segment 1 line 1 / shot 1",
      "severity": "polish",
      "problem": "The hook line captions its own shot: the shot shows small people beneath the skeleton, and the line says the people look tiny.",
      "fix": "Keep the concept's hook line, but change the shot 1 action to 'Light from the skylights drifts slowly across the suspended skeleton'. The figures stay in the frame but are no longer the action, so the line points the visitor's eye to something the shot does not stage."
    },
    {
      "where": "segment 1 shot 2 / asset skeleton_now",
      "severity": "polish",
      "problem": "'Seen from below' and 'three-quarter view from below' contradict both the balcony viewpoint of the concept and the photo, which is taken roughly level with the skeleton from an upper balcony.",
      "fix": "In shot 2 framing, write 'medium close-up of skull and jaws at balcony height'. In the asset prompt, change 'three-quarter view from below' to 'the same elevated three-quarter view as the photo'."
    }
  ],
  "scores": {
    "hook": 4,
    "visitor_view": 5,
    "focus": 5,
    "concept_fidelity": 4,
    "truth": 5,
    "counterpoint": 3,
    "spoken": 4,
    "visual_feasibility": 3,
    "length_fit": 3,
    "ending": 5
  },
  "summary": "Every claim is supported, and the length-then-juvenile turn landing on the wide whole-skeleton shot answers this visitor's question about size well. It cannot ship until the asset prompts are made text-free and the request is cut from 270 to under 230 direction words, mainly by trimming the duplicated music clause. Swapping the filler 'Take your time' for the concept's 4.5-tonne weight beat would complete the arc."
}
```

---

<a id="06-s3-script"></a>
## 第 7 次调用 · 06_s3_script · S3 写剧本

- 提示词文件：`prompts/s3_script.md`（sha c37365d2，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 24553 tokens · 输出 2807 tokens · $0.1544 · 24.9 秒 · 实际调用

### 系统提示词

```text
You write the shooting script for a very short film about a museum exhibit, from a chosen concept. Each segment of the script becomes one request to a video model (Seedance 2.0) that generates up to 15 seconds of video with sound, guided by text and up to four reference images. Your script is everything the video model will know. You can see the visitor's photo and the reference images that exist; write what you see in them, not what you imagine.

The concept is the brief. Every line serves its single idea. A fact the concept did not list needs a reason, and a second number almost never has one. The ending completes that idea; it does not open a new one, and it is never a moral, a mission statement or an appeal to the viewer's values. If the exhibit has an official meaning or motto, use it only if it turns the film's idea, said concretely in the narrator's own words.

Narrator. Decide the voice once, in one specific sentence (apparent age, gender if any, timbre, accent, pace, warmth), and the narrator's attitude to the person standing in front of it. The two segments of a 30-second film are generated separately, so this exact voice description is repeated in both; keep it concrete. Choose narrator_presence: "voiceover" (an unseen narrator over the images) suits most films; "on_screen" (the living form speaks in shot, lip-synced) only when a character sheet with expressions exists and the concept is direct address. Choose style ("realistic" or "stylized") to match the reference images you use.

Structure. A 15-second film is one segment; a 30-second film is two segments of 15 seconds. The two are joined by a hard cut in the edit, never by a continuous camera move, so design the cut: end segment 1 on a near-still image (end_frame) and open segment 2 on an image of matching brightness or shape. Put the big jump between worlds (now and then, hall and sea) at that cut when the story allows, rather than inside one generation. Each segment has one setting, with at most one jump to a second. Write the setting as the place and light in at most 12 words; never restate production rules (states, no morphing, no text): the request builder adds them.

Shots. Two or three shots per 15-second segment, each at least three seconds. Each shot has exactly one camera move (static, slow push-in, slow pull-back, slow tilt, slow orbit, slow drift) and one main action, described as motion. Movement comes from the camera, light, water, dust or the living form; the real exhibit itself never moves or transforms. The request builder prints each shot as framing, camera; action; visual, so never repeat a word between them: action is the one motion as a full clause, visual adds at most 15 words of light, colour or composition, and the first shot of the living form in a segment says what it looks like. Use only details visible in the photo, the reference images or the appearance notes. Do not restate the subject lock or write @Image tags; the builder adds them from each shot's refs. Copy the asset plan's subject_lock, living_form_lock, subject_name and living_form_name into the script unchanged; the builder names references by the short names, and the images carry the look. Frame each shot within about 45 degrees of its reference image's angle, and move the camera only as far as it can travel slowly in the shot (a drift over the skull in five seconds, not jaw to tail). Each segment becomes one request: leaving out quoted narration, it must stay at or under 230 words, and the builder adds about 60 fixed words, so the shots and the sound together get about 150. Spend words on concrete light, colour and composition, not on repeating the action or on long sound lists. On a revision you can see the rendered requests and their word breakdown. Never ask for text, captions, signs, numbers or logos in the picture. Each shot lists the references it shows; never put two different reference subjects (the skeleton and the living animal) in the same shot. The final shot shows the real exhibit from a viewpoint the visitor can take in the room, ideally the angle of their own photo, so they can match screen to object when they look up.

Narration. English, first person, spoken by the exhibit. The film delivers the controlling idea: the hook sets up what the visitor assumes, the turn lands what is actually true, and the last line gives the last thought. Picture and words are two tracks that must not say the same thing: the image already shows what is there, so the line adds what the camera cannot show (what it means, what came before, what is missing, what the narrator feels). Plan one collision per segment: an image that changes how the line over it is heard (youth over the full adult-sized skeleton, the sea over bare bone). Test every line: muted, does the picture still tell its half? Eyes closed, does the line? At least one line shows the narrator's attitude (a reaction, a confession, a dry aside) with no claims.

The picture track is free from the words but never from the facts. Every shot of the real exhibit must match how the pack and the photo say it is displayed: where it stands or hangs, how high, what is around it. Do not show visitors walking under an object on a low plinth, or a hall the exhibit is not in.

Place words. "Here", "this hall", "this sandbar", "what you see", "you had to" and the like tie a fact to a place, a display or the visitor. Use one only if a pack sentence or the photo supports that exact link ("at this museum since 1893", not "here since 1893" if it was first displayed elsewhere). Never state why the visitor did something; describe only what the photo shows.

Write for the ear: short sentences, concrete words, numbers and dates in words ("eighteen ninety-one", "two hundred and fifty pounds"), and the human version of a date ("one March morning in eighteen ninety-one") rather than a calendar entry. Name the country when a place will be unfamiliar to a visitor. Timing: about 2.5 spoken words per second; the film opens on at least a second of picture and sound before the first word, and the last line of each segment ends at least one second before the segment does. That leaves roughly 25-30 words per 15-second segment; fewer is often better. Lines must not overlap.

Truth. Every line is one of three kinds:
- fact: states something about the exhibit's past, size, origin, people or meaning. It lists only the fact ids that actually say it, never a merely related fact.
- visible: present tense, only what the visitor can see in front of them now ("look up", "my jaw is right above you"). No fact ids, and it must not imply anything about why or when.
- voice: feeling or address, no claims at all.
A line that mixes kinds must be backed for every claim it makes. Appearance notes and anything UNSOURCED are for pictures only, never for speech. Do not add qualifiers the facts lack (alone, died, first, only, still, renamed, finished growing).

Sound. For each segment: an ambience bed, two or three specific sound effects tied to the action, and a music cue. Choose one music style for the whole film (music_style), drawn from the exhibit's own world and the concept's emotion: name the instruments, tempo and one texture. Solo cello and soft piano are not defaults; use them only if you can say why this exhibit needs them. "No music" is often right. Never let the music hold across the cut. Plan the joint: end segment 1 on a sound that can stop cleanly (a held note dying away, a natural sound, a beat of near silence) and open segment 2 fresh, so the music never has to continue across the cut. If there should be no music, say "no music".

Reference images. List the assets the shots use, each with what it depicts (exhibit_now, living_form, environment or detail). Use an existing reference image by its id when it fits (source "existing"); plan a new one only when a shot needs it (source "generate"), with a prompt for the subject alone, plain background, even light, no text or people. At most four references per segment, listed in ref_assets in the order they will be uploaded, the full view of the exhibit before any detail of it. Never use a character sheet or any multi-panel image as a reference; use its single-view image (plan it as 'generate' if it does not exist). A shot that shows another state of the exhibit uses that state's image. The final shot uses the in-place view when there is one.

Subtitles. English, matching the narration word for word (numerals allowed), timed on the whole film's timeline, short lines.

If a previous script and review feedback are attached, edit the previous script: change only what each point requires, plus whatever that change forces (subtitles, timings), and copy everything else exactly. Do not undo earlier fixes.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Exhibit id: hope
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.
Film length: 15 seconds

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<asset_plan>
{
  "highlights": [
    {
      "kind": "visual",
      "text": "mottled blue-grey skin",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "pale ribbed throat",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "suspended mid-dive",
      "basis": "photo"
    },
    {
      "kind": "decision",
      "text": "two text-free side views",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "sheet labels removed",
      "basis": "decision"
    }
  ],
  "subject_name": "the whale skeleton",
  "living_form_name": "the living blue whale",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "A slender living blue whale with deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow pale-edged flippers, a small dorsal fin set far back and broad tail flukes.",
  "images": [
    {
      "id": "sheet_realistic_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing realistic character sheet (sheet_realistic). Reproduce only its full side view, alone and centred: a slender living blue whale seen exactly in profile facing left, deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed, calm eye. Same realistic rendering, colours and proportions as the sheet. Plain light grey-white background, soft even light, faint soft shadow beneath. Whole whale in frame from snout to fluke tips with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for realistic living-form shots; colouring follows the pack appearance notes, exact mottling pattern is artistic reconstruction."
    },
    {
      "id": "sheet_stylized_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing stylized character sheet (sheet_stylized). Reproduce only its full side view, alone and centred: the lightly anime-styled blue whale in exact profile facing left, blue-grey body with simplified soft paler grey mottled patches, pale ribbed throat with clean line grooves, clear outline, lively dark eye, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed. Same style, colours and proportions as the sheet. Plain light grey-white background, even soft light, faint shadow beneath. Whole whale in frame with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for stylized living-form shots; artistic interpretation of the living animal."
    },
    {
      "id": "skeleton_now",
      "kind": "subject_view",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin.",
      "must_avoid": "No hall, arches, windows, skylights or staircase, no suspension cables, no people, no banners, signs, text, labels or watermarks, no glass, no second skeleton, no living whale skin, no dramatic lighting or shadows.",
      "purpose": "Clean identity reference for the exhibit as it is now."
    },
    {
      "id": "hall_inplace",
      "kind": "environment",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "must_avoid": "No readable text, signs, banners, labels or watermarks, no large or close-up people, no extra skeletons or whales, no change to the skeleton, no glare or lens flare, no dramatic colour grading.",
      "purpose": "In-place reference for the final shot of the skeleton in its hall."
    }
  ]
}
</asset_plan>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>
```

```text
<previous_script>
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "28 spoken words",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "A single low bowed double-bass drone with soft harmonic overtones, very slow, airy hall reverb like distant whale song.",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. No hall, cables, people, text, labels or watermarks.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony, as in the visitor's photo",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged. No readable text, logos or watermarks.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws, seen from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing, frame settling still."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur, distant voices echoing under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor",
          "faint metallic creak of suspension cables",
          "a child's distant delighted gasp"
        ],
        "music": "Low bowed double-bass drone swells softly under the first line, then its last note dies away into hall ambience by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
</previous_script>

<review_feedback>
Edit the previous script to fix these points. Change only what each point requires (plus anything that change forces, such as subtitles and timings); copy everything else unchanged.
- [check] asset 'skeleton_now' prompt asks for text in the image
- [check] asset 'hall_inplace' prompt asks for text in the image
- [check] segment 1 request has 270 direction words (cap 230, quoted narration not counted): references 38, shots 101, sound 72, voice 24, fixed 35; cut the largest part you control
- [blocking] [assets skeleton_now and hall_inplace (automatic check)] Both asset prompts name 'text' in their exclusions ('No hall, cables, people, text, labels or watermarks'; 'all readable text'; 'No readable text, logos or watermarks'). The checker reads this as a request for text. → skeleton_now: end the prompt with 'Nothing else in the frame: no hall, cables or people.' hall_inplace: change the sentence to 'Remove glare, hanging banners and signs, leaving plain stonework where they hung' and delete the final sentence. Do not use the words text, labels, logos or watermarks anywhere in the asset prompts.
- [blocking] [segment 1 request (automatic check)] The request has 270 direction words against a cap of 230. The Music clause repeats itself: the drone is described twice, at about 42 words. → Replace the music text with 'Music: one low bowed double-bass drone, swelling under the first line, fading out by the final second.' (17 words). Cut the sfx 'a child's distant delighted gasp' and 'faint metallic creak of suspension cables'. Cut 'frame settling still' from shot 3, because it repeats 'static'. Shorten the @Image2 description to 'skeleton in Hintze Hall from the upper balcony'. Together these remove about 44 words, which brings the request to roughly 226.
</review_feedback>
```

```text
<rendered_requests>
[
  {
    "prompt": "References: @Image1 is the whale skeleton (copy its shape, pose and colour exactly; ignore its background); @Image2 is skeleton in Hintze Hall from the upper balcony, as in the visitor's photo (setting reference only: architecture, light and space).\nStyle: photorealistic documentary footage, natural light. Setting: Hintze Hall from the upper balcony, bright skylight daylight.\nShot 1 (@Image2): wide elevated balcony view, slow push-in; Small visitors cross the hall floor beneath the skeleton; bright skylight daylight on terracotta arches; staircase and white statue at right. Cut to shot 2 (@Image1): medium close-up of skull and jaws, seen from below, slow drift right; Dust motes float through sunbeams across the long jawbones; warm terracotta blur behind, glazed roof ribs overhead, soft contrast. Cut to shot 3 (@Image2): wide balcony-height view of the whole skeleton, static; A band of sunlight slides along the ribcage and flippers; tiny figures on floor and staircase, arched windows glowing, frame settling still.\nVoiceover, an unseen narrator, a young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused: \"From up there, the people below look tiny next to me.\" \"Take your time.\" \"Twenty-five point two metres of bone, and I was a juvenile female blue whale.\"\nSound: Vast stone hall murmur, distant voices echoing under a glass roof; footsteps echoing on the stone floor; faint metallic creak of suspension cables; a child's distant delighted gasp. Music: A single low bowed double-bass drone with soft harmonic overtones, very slow, airy hall reverb like distant whale song, low bowed double-bass drone swells softly under the first line, then its last note dies away into hall ambience by the final second.\nKeep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one whale skeleton in any frame.",
    "direction_words": 270,
    "prompt_parts": {
      "refs": 38,
      "style": 16,
      "shots": 101,
      "voice": 24,
      "sound": 72,
      "constraint": 19
    }
  }
]
</rendered_requests>
(Direction-word cap per request: 230, quoted narration not counted.)
```

### 本轮收到的修改意见（feedback.md）

```text
- [check] asset 'skeleton_now' prompt asks for text in the image
- [check] asset 'hall_inplace' prompt asks for text in the image
- [check] segment 1 request has 270 direction words (cap 230, quoted narration not counted): references 38, shots 101, sound 72, voice 24, fixed 35; cut the largest part you control
- [blocking] [assets skeleton_now and hall_inplace (automatic check)] Both asset prompts name 'text' in their exclusions ('No hall, cables, people, text, labels or watermarks'; 'all readable text'; 'No readable text, logos or watermarks'). The checker reads this as a request for text. → skeleton_now: end the prompt with 'Nothing else in the frame: no hall, cables or people.' hall_inplace: change the sentence to 'Remove glare, hanging banners and signs, leaving plain stonework where they hung' and delete the final sentence. Do not use the words text, labels, logos or watermarks anywhere in the asset prompts.
- [blocking] [segment 1 request (automatic check)] The request has 270 direction words against a cap of 230. The Music clause repeats itself: the drone is described twice, at about 42 words. → Replace the music text with 'Music: one low bowed double-bass drone, swelling under the first line, fading out by the final second.' (17 words). Cut the sfx 'a child's distant delighted gasp' and 'faint metallic creak of suspension cables'. Cut 'frame settling still' from shot 3, because it repeats 'static'. Shorten the @Image2 description to 'skeleton in Hintze Hall from the upper balcony'. Together these remove about 44 words, which brings the request to roughly 226.
```

### 模型思考摘要

I'm going to apply the fixes now, starting with the music line. The feedback wants the music text swapped for a single low bowed double-bass drone, so the likely spot is the segment's audio.music field. But the builder also prints music_style alongside it, so I need to check which part of the output actually needs to change.

I'm weighing whether to trim the music_style text as well as the cue, since both get printed and together they still run longer than the feedback's target. I'm leaning toward shortening both: a single low bowed double-bass drone in the style, and a swell-and-fade phrase as the cue. That should land the music clause near 20 words.

I'm working out how far to cut the music text, since both the style and the cue get printed. I'm planning a single low bowed double-bass drone with a swell under the first line and a fade by the final second, and I'll trim the hall ambience and the shot 2 framing to make up the remaining words.

I'm settling the highlights note and trimming the hall ambience, which has been sitting at a three-word overrun I still need to cut.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "request trimmed under cap",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "One low bowed double-bass drone, very slow, airy hall reverb",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. Nothing else in the frame: no hall, cables or people.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners and signs, leaving plain stonework where they hung; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor"
        ],
        "music": "swells under the first line, fades out by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
```

---

<a id="07-s4-review"></a>
## 第 8 次调用 · 07_s4_review · S4 审稿

- 提示词文件：`prompts/s4_review.md`（sha d819f4df，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 22010 tokens · 输出 3922 tokens · $0.1665 · 34.7 秒 · 实际调用

### 系统提示词

```text
You are the script editor for very short museum films (15 or 30 seconds) narrated by the exhibit. You did not write this script; judge it as a demanding director would, standing in for the visitor who will watch it on a phone in front of the real object. You get the knowledge pack, the writer's material, the chosen concept, the script, the exact Seedance requests it will turn into, the automatic check results, the visitor's photo and the reference images, and possibly your previous review.

1. Audit the truth first, line by line. For every narration line write the claim it makes about the exhibit or its history (including colour, pose, size, age, sex, and what happened to it), its kind (fact / visible / voice), and the fact id plus the words of that fact that support it. A claim is unsupported if no fact states it, if the cited id does not say what the line says, if it adds a qualifier the fact lacks (alone, died, first, only, still, renamed), if it uses appearance notes or UNSOURCED material as speech, if it works out a figure the pack does not give, or if it paraphrases a quoted fact so its meaning changes. Check every place word (here, this, what you see, you had to): it is unsupported unless a pack sentence or the photo makes that exact link. Check that every shot of the real exhibit matches how the pack and photo say it is displayed.

2. If a previous review is attached, say for each of its issues whether it is resolved. Do not ask to reverse a change you asked for unless it caused a new, named problem. Judge lines you suggested as strictly as the writer's.

3. List the issues, most important first. Each has an exact location, a severity and a concrete fix (a rewritten line, a replacement shot, a specific cut). "blocking" means it must not ship: any unsupported claim, a broken rule, an automatic-check failure, a shot that will not render, a film that fails its concept. "polish" means it would clearly improve the film. Fixes stay inside the chosen concept and the listed facts. "Make it more engaging" is useless; write the better line.

Check renderability against the Seedance requests: exactly one camera move and one action per shot; the shot's reference shows the subject in the state the shot needs (skeleton vs living, swimming vs stranded); never two reference subjects in one shot; no text, faces in close-up, fast motion, transformations; at most two settings per segment; each segment ends on an image the next can cut from; the same voice description in every segment.

Before you propose a replacement line, check it yourself: use the cited fact's own wording and add no back, again or still; count its spoken words, compute t_start + words / 2.5, and make sure it ends at least one second before the segment ends and before the next line starts. Before you propose a change to a shot, sound or reference, check it does not push the segment over its direction-word count (shown in the requests). The two segments are separate generations joined by a hard cut: never ask for music, speech or a camera move to continue across it.

4. Then score each from 1 to 5. 5 = you would ship it unchanged in a paid brand film; 4 = one small fix; 3 = works but forgettable, or has a clear flaw; 2 = the idea fails here; 1 = broken.
- hook: the first two or three seconds earn attention without a greeting or preamble.
- visitor_view: it answers the question this visitor most likely has (the photo is a clue). Answering none of their questions scores at most 2.
- focus: one idea with at most one turn, not a list of facts.
- concept_fidelity: it delivers the chosen concept's idea and ending.
- truth: 5 only if every claim in your audit is supported; any unsupported claim scores 1.
- counterpoint: 5 only if no line names what its own shot shows and at least one image changes how its line is heard; 3 if one line captions its shot; 2 if the picture illustrates most lines.
- spoken: read each line aloud at a calm pace; it sounds like a voice, not a caption, and fits its time.
- visual_feasibility: every shot is renderable as described.
- length_fit: 5 = every line adds something the previous one did not and the film needs every second; 3 = one line only restates, delays or splits a fact, or a shot exists only to fill time; 2 or lower = the story could be told in one 15-second segment (say so as a blocking issue with where = 'length').
- ending: the last line and image land, and send the visitor's eyes back to the real object.

Keep the summary to two or three sentences.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.

<knowledge_pack>
# Hope the blue whale — knowledge pack

Every section ends with its source. Only sourced statements may be used as facts in narration.
Statements marked UNSOURCED are context for the writer and must not be stated as fact.

## Stranding
Hope was a juvenile female blue whale. She stranded on a sandbar at the mouth of Wexford Harbour, Ireland,
on the morning of 25 March 1891.
Source: https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html

## Sale to the museum
The 4.5-tonne skeleton was sold to the Natural History Museum for £250.
Source: https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html

## Mammal Hall
The skeleton hung in the museum's Mammal Hall from 1934.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Move to Hintze Hall
The skeleton was moved to Hintze Hall and unveiled there in July 2017. In Hintze Hall she replaced the cast of
Dippy the Diplodocus, which stood there from 1979 until January 2017.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Her name
She was named Hope "as a symbol of humanity's power to shape a sustainable future".
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Size
The skeleton is 25.2 metres long.
Source: https://artsandculture.google.com/asset/GAG_J9wcz31GXw

## Pose (UNSOURCED)
The skeleton has 221 bones and is posed in a diving lunge. (Secondary source only; do not state as fact.)

## Appearance (for visuals, not narration)
Hung from the ceiling of Hintze Hall, a high Romanesque hall with terracotta arches and stained glass, the
skeleton is suspended mid-dive above visitors. As a living animal she would have had deep blue-grey mottled skin
and a pale ribbed throat.

</knowledge_pack>

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>

<script>
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "request trimmed under cap",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "One low bowed double-bass drone, very slow, airy hall reverb",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. Nothing else in the frame: no hall, cables or people.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners and signs, leaving plain stonework where they hung; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor"
        ],
        "music": "swells under the first line, fades out by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
</script>

<seedance_requests>
[
  {
    "endpoint": "bytedance/seedance-2.0/reference-to-video",
    "image_urls": [
      "<skeleton_now>",
      "<hall_inplace>"
    ],
    "duration": "15",
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "prompt": "References: @Image1 is the whale skeleton (copy its shape, pose and colour exactly; ignore its background); @Image2 is skeleton in Hintze Hall from the upper balcony (setting reference only: architecture, light and space).\nStyle: photorealistic documentary footage, natural light. Setting: Hintze Hall from the upper balcony, bright skylight daylight.\nShot 1 (@Image2): wide elevated balcony view, slow push-in; Small visitors cross the hall floor beneath the skeleton; bright skylight daylight on terracotta arches; staircase and white statue at right. Cut to shot 2 (@Image1): medium close-up of skull and jaws from below, slow drift right; Dust motes float through sunbeams across the long jawbones; warm terracotta blur behind, glazed roof ribs overhead, soft contrast. Cut to shot 3 (@Image2): wide balcony-height view of the whole skeleton, static; A band of sunlight slides along the ribcage and flippers; tiny figures on floor and staircase, arched windows glowing.\nVoiceover, an unseen narrator, a young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused: \"From up there, the people below look tiny next to me.\" \"Take your time.\" \"Twenty-five point two metres of bone, and I was a juvenile female blue whale.\"\nSound: Vast stone hall murmur under a glass roof; footsteps echoing on the stone floor. Music: One low bowed double-bass drone, very slow, airy hall reverb, swells under the first line, fades out by the final second.\nKeep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one whale skeleton in any frame.",
    "prompt_words": 254,
    "direction_words": 226,
    "prompt_parts": {
      "refs": 33,
      "style": 16,
      "shots": 97,
      "voice": 24,
      "sound": 37,
      "constraint": 19
    },
    "est_usd": 4.5
  }
]
</seedance_requests>

Automatic checks found: nothing
```

```text
<previous_review>
{
  "highlights": [
    {
      "kind": "check",
      "text": "3 claims checked",
      "basis": "decision"
    },
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "decision",
      "text": "'Take your time' replaced",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "270 direction words, cap 230",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "text-free asset prompts",
      "basis": "decision"
    }
  ],
  "claims": [
    {
      "line": "From up there, the people below look tiny next to me.",
      "claim": "The visitor is up on a balcony, and the people on the floor below look small beside the skeleton.",
      "kind": "visible",
      "supporting_fact": "photo: elevated shot from an upper balcony level; dozens of visitors on the hall floor look very small beneath the whale",
      "supported": true
    },
    {
      "line": "Take your time.",
      "claim": "none",
      "kind": "voice",
      "supporting_fact": "none",
      "supported": true
    },
    {
      "line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "claim": "The skeleton is 25.2 m long, and Hope was a juvenile female blue whale.",
      "kind": "fact",
      "supporting_fact": "length: 'The skeleton is 25.2 metres long.'; juvenile_female: 'Hope was a juvenile female blue whale.'",
      "supported": true
    }
  ],
  "previous_issues_resolved": [],
  "issues": [
    {
      "where": "assets skeleton_now and hall_inplace (automatic check)",
      "severity": "blocking",
      "problem": "Both asset prompts name 'text' in their exclusions ('No hall, cables, people, text, labels or watermarks'; 'all readable text'; 'No readable text, logos or watermarks'). The checker reads this as a request for text.",
      "fix": "skeleton_now: end the prompt with 'Nothing else in the frame: no hall, cables or people.' hall_inplace: change the sentence to 'Remove glare, hanging banners and signs, leaving plain stonework where they hung' and delete the final sentence. Do not use the words text, labels, logos or watermarks anywhere in the asset prompts."
    },
    {
      "where": "segment 1 request (automatic check)",
      "severity": "blocking",
      "problem": "The request has 270 direction words against a cap of 230. The Music clause repeats itself: the drone is described twice, at about 42 words.",
      "fix": "Replace the music text with 'Music: one low bowed double-bass drone, swelling under the first line, fading out by the final second.' (17 words). Cut the sfx 'a child's distant delighted gasp' and 'faint metallic creak of suspension cables'. Cut 'frame settling still' from shot 3, because it repeats 'static'. Shorten the @Image2 description to 'skeleton in Hintze Hall from the upper balcony'. Together these remove about 44 words, which brings the request to roughly 226."
    },
    {
      "where": "segment 1 line 2",
      "severity": "polish",
      "problem": "'Take your time.' is filler. It holds 1.8 s of the middle beat that the concept gave to weight ('a beat of weight and solidity', with skeleton_weight in the concept's fact_ids). The concept's arc loses its middle step.",
      "fix": "Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), citing skeleton_weight. Start line 3 unchanged at 8.3 (14 words, ends 13.9, which is 1.1 s before the segment ends). Update the subtitles to these times. The weight now sits over the floating-dust close-up of the jaws, so the picture shows lightness while the line gives weight."
    },
    {
      "where": "segment 1 line 1 / shot 1",
      "severity": "polish",
      "problem": "The hook line captions its own shot: the shot shows small people beneath the skeleton, and the line says the people look tiny.",
      "fix": "Keep the concept's hook line, but change the shot 1 action to 'Light from the skylights drifts slowly across the suspended skeleton'. The figures stay in the frame but are no longer the action, so the line points the visitor's eye to something the shot does not stage."
    },
    {
      "where": "segment 1 shot 2 / asset skeleton_now",
      "severity": "polish",
      "problem": "'Seen from below' and 'three-quarter view from below' contradict both the balcony viewpoint of the concept and the photo, which is taken roughly level with the skeleton from an upper balcony.",
      "fix": "In shot 2 framing, write 'medium close-up of skull and jaws at balcony height'. In the asset prompt, change 'three-quarter view from below' to 'the same elevated three-quarter view as the photo'."
    }
  ],
  "scores": {
    "hook": 4,
    "visitor_view": 5,
    "focus": 5,
    "concept_fidelity": 4,
    "truth": 5,
    "counterpoint": 3,
    "spoken": 4,
    "visual_feasibility": 3,
    "length_fit": 3,
    "ending": 5
  },
  "summary": "Every claim is supported, and the length-then-juvenile turn landing on the wide whole-skeleton shot answers this visitor's question about size well. It cannot ship until the asset prompts are made text-free and the request is cut from 270 to under 230 direction words, mainly by trimming the duplicated music clause. Swapping the filler 'Take your time' for the concept's 4.5-tonne weight beat would complete the arc."
}
</previous_review>
```

### 模型思考摘要

I'm checking the script against the previous review, starting with the asset prompts and whether their wording issues were fixed.

I'm going through the remaining review points: "Take your time" and the "from below" wording are still there as polish items, and the hook caption in shot 1 hasn't been changed yet. Next I'm checking the three audit lines' timing, which comes to a finish about two seconds before the 15-second mark, and confirming the skeleton's length figure and the shot 2 setup.

I'm checking the shot 2 and shot 3 setup next, including whether the hall reference that contains the skeleton is fine as a setting-only reference. I also notice "from below" in shot 2 conflicts with the balcony framing, which is still a polish item, while the length line landing on the jaw close-up then the wide shot seems to work.

I'm now checking the weight line as a possible replacement for "Take your time," confirming the timing works out with about a second to spare before the 15-second mark, and noting that the 4.5-tonne figure is supported by the source.

I'm swapping "Take your time" for a weight line, "Four point five tonnes," which keeps the direction count under the cap. I'm also changing shot 1's action so the light moves across the skeleton instead of the visitors crossing beneath it, and the word count stays around 228.

I'm considering a shorter shot 1 action, since a skylight drifting across the suspended skeleton would hold the word count steady once the weight line and the balcony-height change are in.

I'm checking the voice and the photo-based claims: the "from up there" line holds for the balcony visitor, and the young narrator's Irish accent is a casting choice rather than a factual claim.

I'm scoring the remaining criteria now: the hook and focus look solid, the length line is the weakest beat, and the "from below" wording is a minor inconsistency in the visuals.

I'm settling the word count at 226 of the 230 cap and noting that the weight beat is still missing, then confirming all three claims trace back to sources.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "check",
      "text": "all 3 claims sourced",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "text-free assets confirmed",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "226 direction words",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "weight beat still missing",
      "basis": "decision"
    }
  ],
  "claims": [
    {
      "line": "From up there, the people below look tiny next to me.",
      "claim": "The visitor is on an upper balcony, and the people on the hall floor look small beside the skeleton.",
      "kind": "visible",
      "supporting_fact": "photo: 'A wide, elevated shot taken from an upper balcony level ... Dozens of visitors on the hall floor and stairs look very small beneath the whale.'",
      "supported": true
    },
    {
      "line": "Take your time.",
      "claim": "none",
      "kind": "voice",
      "supporting_fact": "none",
      "supported": true
    },
    {
      "line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "claim": "The skeleton is 25.2 m long, and Hope was a juvenile female blue whale.",
      "kind": "fact",
      "supporting_fact": "length: 'The skeleton is 25.2 metres long.'; juvenile_female: 'Hope was a juvenile female blue whale.'",
      "supported": true
    }
  ],
  "previous_issues_resolved": [
    "Asset prompts naming text (blocking): resolved. Neither prompt now contains text, labels, logos or watermarks.",
    "Direction words 270 over the 230 cap (blocking): resolved. The request is now 226 direction words.",
    "'Take your time' filler instead of the concept's weight beat (polish): not resolved. The line is unchanged.",
    "Hook line captions shot 1 (polish): not resolved. The shot 1 action is still 'Small visitors cross the hall floor beneath the skeleton'.",
    "'From below' contradicts the balcony viewpoint (polish): not resolved. It remains in the shot 2 framing and in the skeleton_now asset view and prompt."
  ],
  "issues": [
    {
      "where": "segment 1 line 2",
      "severity": "polish",
      "problem": "'Take your time.' is still filler. It occupies the middle beat that the concept assigns to weight ('a beat of weight and solidity', with skeleton_weight in its fact_ids), so the arc goes straight from scale to youth.",
      "fix": "Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), kind fact, fact_ids [skeleton_weight]. Move line 3 unchanged to t_start 8.3 (14 words, ends 13.9, which is 1.1 s before the end). Update the subtitles: 0.3–2.5 'From up there, the people below' / 2.5–4.7 'look tiny next to me.' / 5.7–7.3 'Four point five tonnes.' / 8.3–10.5 '25.2 metres of bone,' / 10.5–13.9 'and I was a juvenile female blue whale.' This adds 1 direction word (227). The weight line then lands over the floating dust motes on the jaws, so the picture shows lightness while the voice gives weight."
    },
    {
      "where": "segment 1 shot 1",
      "severity": "polish",
      "problem": "The hook line describes its own shot: the action stages small visitors crossing beneath the skeleton while the voice says the people look tiny.",
      "fix": "Change the shot 1 action to 'Cloud shadow drifts slowly across the glazed roof.' (8 words, net 0 direction words). The tiny figures stay in the hall_inplace frame, but the line now directs the visitor's eye to them instead of repeating the staged action. The shot also no longer duplicates the sunlight move in shot 3."
    },
    {
      "where": "segment 1 shot 2 / asset skeleton_now",
      "severity": "polish",
      "problem": "'From below' and 'three-quarter view from below' contradict the balcony viewpoint that the concept and the photo both establish. This risks a jarring change of eye-line between the shots.",
      "fix": "Shot 2 framing: 'medium close-up of skull and jaws at balcony height' (+1 direction word, total 228 with the fixes above). Asset skeleton_now: change the view to 'whole skeleton, elevated three-quarter view, mid-dive', and in the prompt replace 'Keep the same three-quarter view from below' with 'Keep the same elevated three-quarter view as the photo'."
    }
  ],
  "scores": {
    "hook": 4,
    "visitor_view": 5,
    "focus": 5,
    "concept_fidelity": 4,
    "truth": 5,
    "counterpoint": 3,
    "spoken": 4,
    "visual_feasibility": 4,
    "length_fit": 3,
    "ending": 5
  },
  "summary": "Both blocking issues from the last review are fixed: the asset prompts are text-free and the request is down to 226 direction words. All three claims are supported, so the film can ship. The three polish notes are still open: swap 'Take your time' for the concept's 4.5-tonne beat, stop the hook line from describing shot 1, and change the 'from below' viewpoint to balcony height, all within about 228 direction words."
}
```

---

<a id="08-s3-script"></a>
## 第 9 次调用 · 08_s3_script · S3 写剧本

- 提示词文件：`prompts/s3_script.md`（sha c37365d2，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 24568 tokens · 输出 2268 tokens · $0.1436 · 17.0 秒 · 实际调用

### 系统提示词

```text
You write the shooting script for a very short film about a museum exhibit, from a chosen concept. Each segment of the script becomes one request to a video model (Seedance 2.0) that generates up to 15 seconds of video with sound, guided by text and up to four reference images. Your script is everything the video model will know. You can see the visitor's photo and the reference images that exist; write what you see in them, not what you imagine.

The concept is the brief. Every line serves its single idea. A fact the concept did not list needs a reason, and a second number almost never has one. The ending completes that idea; it does not open a new one, and it is never a moral, a mission statement or an appeal to the viewer's values. If the exhibit has an official meaning or motto, use it only if it turns the film's idea, said concretely in the narrator's own words.

Narrator. Decide the voice once, in one specific sentence (apparent age, gender if any, timbre, accent, pace, warmth), and the narrator's attitude to the person standing in front of it. The two segments of a 30-second film are generated separately, so this exact voice description is repeated in both; keep it concrete. Choose narrator_presence: "voiceover" (an unseen narrator over the images) suits most films; "on_screen" (the living form speaks in shot, lip-synced) only when a character sheet with expressions exists and the concept is direct address. Choose style ("realistic" or "stylized") to match the reference images you use.

Structure. A 15-second film is one segment; a 30-second film is two segments of 15 seconds. The two are joined by a hard cut in the edit, never by a continuous camera move, so design the cut: end segment 1 on a near-still image (end_frame) and open segment 2 on an image of matching brightness or shape. Put the big jump between worlds (now and then, hall and sea) at that cut when the story allows, rather than inside one generation. Each segment has one setting, with at most one jump to a second. Write the setting as the place and light in at most 12 words; never restate production rules (states, no morphing, no text): the request builder adds them.

Shots. Two or three shots per 15-second segment, each at least three seconds. Each shot has exactly one camera move (static, slow push-in, slow pull-back, slow tilt, slow orbit, slow drift) and one main action, described as motion. Movement comes from the camera, light, water, dust or the living form; the real exhibit itself never moves or transforms. The request builder prints each shot as framing, camera; action; visual, so never repeat a word between them: action is the one motion as a full clause, visual adds at most 15 words of light, colour or composition, and the first shot of the living form in a segment says what it looks like. Use only details visible in the photo, the reference images or the appearance notes. Do not restate the subject lock or write @Image tags; the builder adds them from each shot's refs. Copy the asset plan's subject_lock, living_form_lock, subject_name and living_form_name into the script unchanged; the builder names references by the short names, and the images carry the look. Frame each shot within about 45 degrees of its reference image's angle, and move the camera only as far as it can travel slowly in the shot (a drift over the skull in five seconds, not jaw to tail). Each segment becomes one request: leaving out quoted narration, it must stay at or under 230 words, and the builder adds about 60 fixed words, so the shots and the sound together get about 150. Spend words on concrete light, colour and composition, not on repeating the action or on long sound lists. On a revision you can see the rendered requests and their word breakdown. Never ask for text, captions, signs, numbers or logos in the picture. Each shot lists the references it shows; never put two different reference subjects (the skeleton and the living animal) in the same shot. The final shot shows the real exhibit from a viewpoint the visitor can take in the room, ideally the angle of their own photo, so they can match screen to object when they look up.

Narration. English, first person, spoken by the exhibit. The film delivers the controlling idea: the hook sets up what the visitor assumes, the turn lands what is actually true, and the last line gives the last thought. Picture and words are two tracks that must not say the same thing: the image already shows what is there, so the line adds what the camera cannot show (what it means, what came before, what is missing, what the narrator feels). Plan one collision per segment: an image that changes how the line over it is heard (youth over the full adult-sized skeleton, the sea over bare bone). Test every line: muted, does the picture still tell its half? Eyes closed, does the line? At least one line shows the narrator's attitude (a reaction, a confession, a dry aside) with no claims.

The picture track is free from the words but never from the facts. Every shot of the real exhibit must match how the pack and the photo say it is displayed: where it stands or hangs, how high, what is around it. Do not show visitors walking under an object on a low plinth, or a hall the exhibit is not in.

Place words. "Here", "this hall", "this sandbar", "what you see", "you had to" and the like tie a fact to a place, a display or the visitor. Use one only if a pack sentence or the photo supports that exact link ("at this museum since 1893", not "here since 1893" if it was first displayed elsewhere). Never state why the visitor did something; describe only what the photo shows.

Write for the ear: short sentences, concrete words, numbers and dates in words ("eighteen ninety-one", "two hundred and fifty pounds"), and the human version of a date ("one March morning in eighteen ninety-one") rather than a calendar entry. Name the country when a place will be unfamiliar to a visitor. Timing: about 2.5 spoken words per second; the film opens on at least a second of picture and sound before the first word, and the last line of each segment ends at least one second before the segment does. That leaves roughly 25-30 words per 15-second segment; fewer is often better. Lines must not overlap.

Truth. Every line is one of three kinds:
- fact: states something about the exhibit's past, size, origin, people or meaning. It lists only the fact ids that actually say it, never a merely related fact.
- visible: present tense, only what the visitor can see in front of them now ("look up", "my jaw is right above you"). No fact ids, and it must not imply anything about why or when.
- voice: feeling or address, no claims at all.
A line that mixes kinds must be backed for every claim it makes. Appearance notes and anything UNSOURCED are for pictures only, never for speech. Do not add qualifiers the facts lack (alone, died, first, only, still, renamed, finished growing).

Sound. For each segment: an ambience bed, two or three specific sound effects tied to the action, and a music cue. Choose one music style for the whole film (music_style), drawn from the exhibit's own world and the concept's emotion: name the instruments, tempo and one texture. Solo cello and soft piano are not defaults; use them only if you can say why this exhibit needs them. "No music" is often right. Never let the music hold across the cut. Plan the joint: end segment 1 on a sound that can stop cleanly (a held note dying away, a natural sound, a beat of near silence) and open segment 2 fresh, so the music never has to continue across the cut. If there should be no music, say "no music".

Reference images. List the assets the shots use, each with what it depicts (exhibit_now, living_form, environment or detail). Use an existing reference image by its id when it fits (source "existing"); plan a new one only when a shot needs it (source "generate"), with a prompt for the subject alone, plain background, even light, no text or people. At most four references per segment, listed in ref_assets in the order they will be uploaded, the full view of the exhibit before any detail of it. Never use a character sheet or any multi-panel image as a reference; use its single-view image (plan it as 'generate' if it does not exist). A shot that shows another state of the exhibit uses that state's image. The final shot uses the in-place view when there is one.

Subtitles. English, matching the narration word for word (numerals allowed), timed on the whole film's timeline, short lines.

If a previous script and review feedback are attached, edit the previous script: change only what each point requires, plus whatever that change forces (subtitles, timings), and copy everything else exactly. Do not undo earlier fixes.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Exhibit id: hope
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.
Film length: 15 seconds

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<asset_plan>
{
  "highlights": [
    {
      "kind": "visual",
      "text": "mottled blue-grey skin",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "pale ribbed throat",
      "basis": "pack"
    },
    {
      "kind": "visual",
      "text": "suspended mid-dive",
      "basis": "photo"
    },
    {
      "kind": "decision",
      "text": "two text-free side views",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "sheet labels removed",
      "basis": "decision"
    }
  ],
  "subject_name": "the whale skeleton",
  "living_form_name": "the living blue whale",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "A slender living blue whale with deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow pale-edged flippers, a small dorsal fin set far back and broad tail flukes.",
  "images": [
    {
      "id": "sheet_realistic_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing realistic character sheet (sheet_realistic). Reproduce only its full side view, alone and centred: a slender living blue whale seen exactly in profile facing left, deep blue-grey skin mottled with paler grey flecks, a pale ribbed throat, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed, calm eye. Same realistic rendering, colours and proportions as the sheet. Plain light grey-white background, soft even light, faint soft shadow beneath. Whole whale in frame from snout to fluke tips with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for realistic living-form shots; colouring follows the pack appearance notes, exact mottling pattern is artistic reconstruction."
    },
    {
      "id": "sheet_stylized_side",
      "kind": "character_sheet",
      "prompt": "Input image: the existing stylized character sheet (sheet_stylized). Reproduce only its full side view, alone and centred: the lightly anime-styled blue whale in exact profile facing left, blue-grey body with simplified soft paler grey mottled patches, pale ribbed throat with clean line grooves, clear outline, lively dark eye, long narrow flipper, small dorsal fin set far back, broad tail flukes, mouth closed. Same style, colours and proportions as the sheet. Plain light grey-white background, even soft light, faint shadow beneath. Whole whale in frame with margin.",
      "must_avoid": "No text, labels, titles, captions, letters (no HOPE, SIDE, FRONT or expression names), no divider lines, no watermarks, no other views or second whales, no expression panels, no water, no people, no glass, no dramatic lighting.",
      "purpose": "Identity reference for stylized living-form shots; artistic interpretation of the living animal."
    },
    {
      "id": "skeleton_now",
      "kind": "subject_view",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin.",
      "must_avoid": "No hall, arches, windows, skylights or staircase, no suspension cables, no people, no banners, signs, text, labels or watermarks, no glass, no second skeleton, no living whale skin, no dramatic lighting or shadows.",
      "purpose": "Clean identity reference for the exhibit as it is now."
    },
    {
      "id": "hall_inplace",
      "kind": "environment",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners, signs and all readable text; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "must_avoid": "No readable text, signs, banners, labels or watermarks, no large or close-up people, no extra skeletons or whales, no change to the skeleton, no glare or lens flare, no dramatic colour grading.",
      "purpose": "In-place reference for the final shot of the skeleton in its hall."
    }
  ]
}
</asset_plan>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>
```

```text
<previous_script>
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "request trimmed under cap",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "One low bowed double-bass drone, very slow, airy hall reverb",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, three-quarter view from below, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same three-quarter view from below, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. Nothing else in the frame: no hall, cables or people.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners and signs, leaving plain stonework where they hung; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Small visitors cross the hall floor beneath the skeleton.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws from below",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing."
        }
      ],
      "narration": [
        {
          "t_start": 1.0,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.6,
          "text": "Take your time.",
          "kind": "voice",
          "fact_ids": []
        },
        {
          "t_start": 7.4,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor"
        ],
        "music": "swells under the first line, fades out by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 1.0,
      "t_end": 3.2,
      "text": "From up there, the people below"
    },
    {
      "t_start": 3.2,
      "t_end": 5.4,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.6,
      "t_end": 6.8,
      "text": "Take your time."
    },
    {
      "t_start": 7.4,
      "t_end": 10.0,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.0,
      "t_end": 13.0,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
</previous_script>

<review_feedback>
Edit the previous script to fix these points. Change only what each point requires (plus anything that change forces, such as subtitles and timings); copy everything else unchanged.
- [polish] [segment 1 line 2] 'Take your time.' is still filler. It occupies the middle beat that the concept assigns to weight ('a beat of weight and solidity', with skeleton_weight in its fact_ids), so the arc goes straight from scale to youth. → Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), kind fact, fact_ids [skeleton_weight]. Move line 3 unchanged to t_start 8.3 (14 words, ends 13.9, which is 1.1 s before the end). Update the subtitles: 0.3–2.5 'From up there, the people below' / 2.5–4.7 'look tiny next to me.' / 5.7–7.3 'Four point five tonnes.' / 8.3–10.5 '25.2 metres of bone,' / 10.5–13.9 'and I was a juvenile female blue whale.' This adds 1 direction word (227). The weight line then lands over the floating dust motes on the jaws, so the picture shows lightness while the voice gives weight.
- [polish] [segment 1 shot 1] The hook line describes its own shot: the action stages small visitors crossing beneath the skeleton while the voice says the people look tiny. → Change the shot 1 action to 'Cloud shadow drifts slowly across the glazed roof.' (8 words, net 0 direction words). The tiny figures stay in the hall_inplace frame, but the line now directs the visitor's eye to them instead of repeating the staged action. The shot also no longer duplicates the sunlight move in shot 3.
- [polish] [segment 1 shot 2 / asset skeleton_now] 'From below' and 'three-quarter view from below' contradict the balcony viewpoint that the concept and the photo both establish. This risks a jarring change of eye-line between the shots. → Shot 2 framing: 'medium close-up of skull and jaws at balcony height' (+1 direction word, total 228 with the fixes above). Asset skeleton_now: change the view to 'whole skeleton, elevated three-quarter view, mid-dive', and in the prompt replace 'Keep the same three-quarter view from below' with 'Keep the same elevated three-quarter view as the photo'.
</review_feedback>
```

```text
<rendered_requests>
[
  {
    "prompt": "References: @Image1 is the whale skeleton (copy its shape, pose and colour exactly; ignore its background); @Image2 is skeleton in Hintze Hall from the upper balcony (setting reference only: architecture, light and space).\nStyle: photorealistic documentary footage, natural light. Setting: Hintze Hall from the upper balcony, bright skylight daylight.\nShot 1 (@Image2): wide elevated balcony view, slow push-in; Small visitors cross the hall floor beneath the skeleton; bright skylight daylight on terracotta arches; staircase and white statue at right. Cut to shot 2 (@Image1): medium close-up of skull and jaws from below, slow drift right; Dust motes float through sunbeams across the long jawbones; warm terracotta blur behind, glazed roof ribs overhead, soft contrast. Cut to shot 3 (@Image2): wide balcony-height view of the whole skeleton, static; A band of sunlight slides along the ribcage and flippers; tiny figures on floor and staircase, arched windows glowing.\nVoiceover, an unseen narrator, a young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused: \"From up there, the people below look tiny next to me.\" \"Take your time.\" \"Twenty-five point two metres of bone, and I was a juvenile female blue whale.\"\nSound: Vast stone hall murmur under a glass roof; footsteps echoing on the stone floor. Music: One low bowed double-bass drone, very slow, airy hall reverb, swells under the first line, fades out by the final second.\nKeep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one whale skeleton in any frame.",
    "direction_words": 226,
    "prompt_parts": {
      "refs": 33,
      "style": 16,
      "shots": 97,
      "voice": 24,
      "sound": 37,
      "constraint": 19
    }
  }
]
</rendered_requests>
(Direction-word cap per request: 230, quoted narration not counted.)
```

### 代码检查结果

```text
[
  "first line starts at 0.3s; open on 0.8s of picture and sound"
]
```

### 本轮收到的修改意见（feedback.md）

```text
- [polish] [segment 1 line 2] 'Take your time.' is still filler. It occupies the middle beat that the concept assigns to weight ('a beat of weight and solidity', with skeleton_weight in its fact_ids), so the arc goes straight from scale to youth. → Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), kind fact, fact_ids [skeleton_weight]. Move line 3 unchanged to t_start 8.3 (14 words, ends 13.9, which is 1.1 s before the end). Update the subtitles: 0.3–2.5 'From up there, the people below' / 2.5–4.7 'look tiny next to me.' / 5.7–7.3 'Four point five tonnes.' / 8.3–10.5 '25.2 metres of bone,' / 10.5–13.9 'and I was a juvenile female blue whale.' This adds 1 direction word (227). The weight line then lands over the floating dust motes on the jaws, so the picture shows lightness while the voice gives weight.
- [polish] [segment 1 shot 1] The hook line describes its own shot: the action stages small visitors crossing beneath the skeleton while the voice says the people look tiny. → Change the shot 1 action to 'Cloud shadow drifts slowly across the glazed roof.' (8 words, net 0 direction words). The tiny figures stay in the hall_inplace frame, but the line now directs the visitor's eye to them instead of repeating the staged action. The shot also no longer duplicates the sunlight move in shot 3.
- [polish] [segment 1 shot 2 / asset skeleton_now] 'From below' and 'three-quarter view from below' contradict the balcony viewpoint that the concept and the photo both establish. This risks a jarring change of eye-line between the shots. → Shot 2 framing: 'medium close-up of skull and jaws at balcony height' (+1 direction word, total 228 with the fixes above). Asset skeleton_now: change the view to 'whole skeleton, elevated three-quarter view, mid-dive', and in the prompt replace 'Keep the same three-quarter view from below' with 'Keep the same elevated three-quarter view as the photo'.
```

### 模型思考摘要

I'm applying the three fixes now, and I'll tweak the highlights to mention the 4.5-tonne skeleton weight, since that's what this step changes.

I'm checking the opening timing against the review's request for 0.3, which conflicts with the one-second rule, but the review is a direct revision instruction, so I'll go with 0.3. The weight line stays as a plain fact, and the shot changes are a drifting cloud shadow over the roof plus a new framing and asset view for shot two.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "request trimmed under cap",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "One low bowed double-bass drone, very slow, airy hall reverb",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, elevated three-quarter view, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same elevated three-quarter view as the photo, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. Nothing else in the frame: no hall, cables or people.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners and signs, leaving plain stonework where they hung; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Cloud shadow drifts slowly across the glazed roof.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws at balcony height",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing."
        }
      ],
      "narration": [
        {
          "t_start": 0.3,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.7,
          "text": "Four point five tonnes.",
          "kind": "fact",
          "fact_ids": [
            "skeleton_weight"
          ]
        },
        {
          "t_start": 8.3,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor"
        ],
        "music": "swells under the first line, fades out by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 0.3,
      "t_end": 2.5,
      "text": "From up there, the people below"
    },
    {
      "t_start": 2.5,
      "t_end": 4.7,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.7,
      "t_end": 7.3,
      "text": "Four point five tonnes."
    },
    {
      "t_start": 8.3,
      "t_end": 10.5,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.5,
      "t_end": 13.9,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
```

---

<a id="09-s4-review"></a>
## 第 10 次调用 · 09_s4_review · S4 审稿

- 提示词文件：`prompts/s4_review.md`（sha d819f4df，末尾附加了 `prompts/_highlights.md`）
- effort：high · 输入 22014 tokens · 输出 3633 tokens · $0.1607 · 32.8 秒 · 实际调用

### 系统提示词

```text
You are the script editor for very short museum films (15 or 30 seconds) narrated by the exhibit. You did not write this script; judge it as a demanding director would, standing in for the visitor who will watch it on a phone in front of the real object. You get the knowledge pack, the writer's material, the chosen concept, the script, the exact Seedance requests it will turn into, the automatic check results, the visitor's photo and the reference images, and possibly your previous review.

1. Audit the truth first, line by line. For every narration line write the claim it makes about the exhibit or its history (including colour, pose, size, age, sex, and what happened to it), its kind (fact / visible / voice), and the fact id plus the words of that fact that support it. A claim is unsupported if no fact states it, if the cited id does not say what the line says, if it adds a qualifier the fact lacks (alone, died, first, only, still, renamed), if it uses appearance notes or UNSOURCED material as speech, if it works out a figure the pack does not give, or if it paraphrases a quoted fact so its meaning changes. Check every place word (here, this, what you see, you had to): it is unsupported unless a pack sentence or the photo makes that exact link. Check that every shot of the real exhibit matches how the pack and photo say it is displayed.

2. If a previous review is attached, say for each of its issues whether it is resolved. Do not ask to reverse a change you asked for unless it caused a new, named problem. Judge lines you suggested as strictly as the writer's.

3. List the issues, most important first. Each has an exact location, a severity and a concrete fix (a rewritten line, a replacement shot, a specific cut). "blocking" means it must not ship: any unsupported claim, a broken rule, an automatic-check failure, a shot that will not render, a film that fails its concept. "polish" means it would clearly improve the film. Fixes stay inside the chosen concept and the listed facts. "Make it more engaging" is useless; write the better line.

Check renderability against the Seedance requests: exactly one camera move and one action per shot; the shot's reference shows the subject in the state the shot needs (skeleton vs living, swimming vs stranded); never two reference subjects in one shot; no text, faces in close-up, fast motion, transformations; at most two settings per segment; each segment ends on an image the next can cut from; the same voice description in every segment.

Before you propose a replacement line, check it yourself: use the cited fact's own wording and add no back, again or still; count its spoken words, compute t_start + words / 2.5, and make sure it ends at least one second before the segment ends and before the next line starts. Before you propose a change to a shot, sound or reference, check it does not push the segment over its direction-word count (shown in the requests). The two segments are separate generations joined by a hard cut: never ask for music, speech or a camera move to continue across it.

4. Then score each from 1 to 5. 5 = you would ship it unchanged in a paid brand film; 4 = one small fix; 3 = works but forgettable, or has a clear flaw; 2 = the idea fails here; 1 = broken.
- hook: the first two or three seconds earn attention without a greeting or preamble.
- visitor_view: it answers the question this visitor most likely has (the photo is a clue). Answering none of their questions scores at most 2.
- focus: one idea with at most one turn, not a list of facts.
- concept_fidelity: it delivers the chosen concept's idea and ending.
- truth: 5 only if every claim in your audit is supported; any unsupported claim scores 1.
- counterpoint: 5 only if no line names what its own shot shows and at least one image changes how its line is heard; 3 if one line captions its shot; 2 if the picture illustrates most lines.
- spoken: read each line aloud at a calm pace; it sounds like a voice, not a caption, and fits its time.
- visual_feasibility: every shot is renderable as described.
- length_fit: 5 = every line adds something the previous one did not and the film needs every second; 3 = one line only restates, delays or splits a fact, or a shot exists only to fill time; 2 or lower = the story could be told in one 15-second segment (say so as a blocking issue with where = 'length').
- ending: the last line and image land, and send the visitor's eyes back to the real object.

Keep the summary to two or three sentences.


Progress keywords. Your answer begins with `highlights`: two to six keywords that pop up on the visitor's screen, one by one, while this step runs. They are the visible trace of your work, so they must be true, specific and worth seeing.

- Each keyword is 1-5 words: a name, a period or dynasty, a date, a place, a person, a material, a measure, a species, a theme, a visual idea, a decision, or a check. Prefer the specific over the generic ("Wexford Harbour", not "Ireland coast"; "Jurassic", not "long ago").
- Only what this step actually established. Facts, names, dates and measures must come from the photo or the knowledge pack, written as the source writes them; never a figure you worked out and never anything marked UNSOURCED. Give the fact id, 'photo' or 'pack' as the basis. Your own choices (a concept, a length, a style, a voice) are kind "decision" with basis 'decision'.
- No sentences, no hype, no emoji, no repeated keyword from an earlier step.
- Order them as a visitor would enjoy discovering them: the most recognisable first.

What each step tends to surface:
- identify: the object's name, what it is, the museum or hall, what the photo shows (kind name / species / place / visual).
- digest: the period or dynasty, key dates and places, a striking measure, the people involved, the lead story.
- reference images: the living or original form, colours and materials, the world it came from.
- concept: the engine and the chosen idea, in a few words.
- script: the film's length, look, voice and the key image.
- review: what was checked ("9 claims checked", "all facts sourced") and what was fixed.
```

### 输入（user 消息）

```text
The visitor's photo:
```

> 🖼 图片：`photos/hope_hintze_hall.webp`

```text
Reference images that already exist for this exhibit:
```

```text
{"id": "alive_underwater", "kind": "restoration", "style": "realistic", "has_text_labels": false, "description": "Hope as she looked alive: a slender blue whale gliding just below the surface, deep blue-grey mottled skin, pale ribbed throat, sunlight rays through the water."}
```

> 🖼 图片：`knowledge/hope/assets/alive_underwater.webp`

```text
{"id": "sheet_realistic", "kind": "character_sheet", "style": "realistic", "has_text_labels": true, "description": "Realistic character sheet: front view, full side view, and four expressions (calm, curious, delighted, thoughtful) shown through eyes, head angle and a slightly open mouth. Carries text labels (HOPE, FRONT, SIDE, CALM...), so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_realistic.webp`

```text
{"id": "sheet_stylized", "kind": "character_sheet", "style": "stylized", "has_text_labels": true, "description": "Lightly anime-styled character sheet: simplified mottling, clearer outline, livelier eyes; same views and four expressions. Carries text labels, so it must be cropped into text-free views before use as a video reference."}
```

> 🖼 图片：`knowledge/hope/assets/sheet_anime.webp`

```text
Notes on the visitor's photo: A wide, elevated shot taken from an upper balcony level. The whole skeleton is in frame: the skull and the long, open lower jaws dip down towards the floor on the left, and the spine arcs up and back towards the glazed roof on the right. The flippers are spread and the ribcage is clearly visible. Bright daylight from the skylights and arched windows lights the terracotta arches, the balconies and the grand staircase with its white statue. Dozens of visitors on the hall floor and stairs look very small beneath the whale. In the lower left, a glass case holds a large specimen. Visitor interest: The wide, high framing with crowds dwarfed underneath suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.

<knowledge_pack>
# Hope the blue whale — knowledge pack

Every section ends with its source. Only sourced statements may be used as facts in narration.
Statements marked UNSOURCED are context for the writer and must not be stated as fact.

## Stranding
Hope was a juvenile female blue whale. She stranded on a sandbar at the mouth of Wexford Harbour, Ireland,
on the morning of 25 March 1891.
Source: https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html

## Sale to the museum
The 4.5-tonne skeleton was sold to the Natural History Museum for £250.
Source: https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html

## Mammal Hall
The skeleton hung in the museum's Mammal Hall from 1934.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Move to Hintze Hall
The skeleton was moved to Hintze Hall and unveiled there in July 2017. In Hintze Hall she replaced the cast of
Dippy the Diplodocus, which stood there from 1979 until January 2017.
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Her name
She was named Hope "as a symbol of humanity's power to shape a sustainable future".
Source: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html

## Size
The skeleton is 25.2 metres long.
Source: https://artsandculture.google.com/asset/GAG_J9wcz31GXw

## Pose (UNSOURCED)
The skeleton has 221 bones and is posed in a diving lunge. (Secondary source only; do not state as fact.)

## Appearance (for visuals, not narration)
Hung from the ceiling of Hintze Hall, a high Romanesque hall with terracotta arches and stained glass, the
skeleton is suspended mid-dive above visitors. As a living animal she would have had deep blue-grey mottled skin
and a pale ribbed throat.

</knowledge_pack>

<material>
{
  "highlights": [
    {
      "kind": "measure",
      "text": "25.2 metres",
      "basis": "length"
    },
    {
      "kind": "theme",
      "text": "juvenile female",
      "basis": "juvenile_female"
    },
    {
      "kind": "place",
      "text": "Wexford Harbour",
      "basis": "stranding_place"
    },
    {
      "kind": "date",
      "text": "25 March 1891",
      "basis": "stranding_date"
    },
    {
      "kind": "name",
      "text": "Dippy the Diplodocus",
      "basis": "replaced_dippy"
    },
    {
      "kind": "decision",
      "text": "15 seconds",
      "basis": "decision"
    }
  ],
  "facts": [
    {
      "id": "juvenile_female",
      "text": "Hope was a juvenile female blue whale.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_place",
      "text": "She stranded on a sandbar at the mouth of Wexford Harbour, Ireland.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "stranding_date",
      "text": "She stranded on the morning of 25 March 1891.",
      "source": "https://www.nhm.ac.uk/discover/news/2018/march/a-cetacean-relation.html",
      "about": "exhibit"
    },
    {
      "id": "skeleton_weight",
      "text": "The skeleton is a 4.5-tonne skeleton.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "sale",
      "text": "The skeleton was sold to the Natural History Museum for £250.",
      "source": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html",
      "about": "exhibit"
    },
    {
      "id": "mammal_hall",
      "text": "The skeleton hung in the museum's Mammal Hall from 1934.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "hintze_move",
      "text": "The skeleton was moved to Hintze Hall and unveiled there in July 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "replaced_dippy",
      "text": "In Hintze Hall she replaced the cast of Dippy the Diplodocus.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "dippy_dates",
      "text": "The cast of Dippy the Diplodocus stood in Hintze Hall from 1979 until January 2017.",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "context"
    },
    {
      "id": "name_meaning",
      "text": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "source": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html",
      "about": "exhibit"
    },
    {
      "id": "length",
      "text": "The skeleton is 25.2 metres long.",
      "source": "https://artsandculture.google.com/asset/GAG_J9wcz31GXw",
      "about": "exhibit"
    }
  ],
  "conflicts": [
    "No sources disagree in the pack.",
    "25 March 1891 is the stranding date only; the pack gives no date for the £250 sale, so do not attach 1891 to the sale or to her arrival at the museum.",
    "1934 is when the skeleton hung in the Mammal Hall, not necessarily when it arrived at the museum.",
    "1979 and January 2017 are Dippy's dates in Hintze Hall, not Hope's; Hope was unveiled there in July 2017.",
    "Dippy is described as a cast; the pack does not use the word 'cast' or 'copy' for Hope, so do not say Hope is a cast.",
    "The pack does not say how or when she died, or when she was given the name Hope; do not say she was renamed or named in 2017.",
    "The 221 bones and the 'diving lunge' pose are UNSOURCED and must not be narrated; skin colour is an appearance note for visuals only."
  ],
  "visitor_questions": [
    {
      "question": "How big is this whale?",
      "answer_fact_ids": [
        "length",
        "skeleton_weight"
      ]
    },
    {
      "question": "Is it a real whale, and where did it come from?",
      "answer_fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ]
    },
    {
      "question": "How did it end up hanging in this hall?",
      "answer_fact_ids": [
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ]
    },
    {
      "question": "Why is it called Hope?",
      "answer_fact_ids": [
        "name_meaning"
      ]
    },
    {
      "question": "Was it fully grown?",
      "answer_fact_ids": [
        "juvenile_female"
      ]
    }
  ],
  "through_lines": [
    {
      "name": "Young giant",
      "beginning": "A 25.2-metre skeleton fills Hintze Hall above the crowds.",
      "turn": "Hope was a juvenile female blue whale.",
      "end": "She stranded at the mouth of Wexford Harbour on the morning of 25 March 1891 and now hangs here.",
      "turn_fact_ids": [
        "juvenile_female"
      ],
      "fact_ids": [
        "length",
        "juvenile_female",
        "stranding_place",
        "stranding_date"
      ],
      "spine": "This skeleton is twenty-five point two metres long, yet Hope was a juvenile female blue whale.",
      "needs_s": 15
    },
    {
      "name": "Sandbar to centre stage",
      "beginning": "A juvenile female blue whale stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.",
      "turn": "Her 4.5-tonne skeleton was sold to the Natural History Museum for £250 and became a specimen, hanging in the Mammal Hall from 1934.",
      "end": "In July 2017 she was unveiled in Hintze Hall, replacing the cast of Dippy the Diplodocus.",
      "turn_fact_ids": [
        "sale",
        "mammal_hall"
      ],
      "fact_ids": [
        "juvenile_female",
        "stranding_place",
        "stranding_date",
        "skeleton_weight",
        "sale",
        "mammal_hall",
        "hintze_move",
        "replaced_dippy"
      ],
      "spine": "Hope stranded at the mouth of Wexford Harbour in eighteen ninety-one. Her skeleton was sold to the museum for two hundred and fifty pounds. In July twenty seventeen she replaced Dippy in Hintze Hall.",
      "needs_s": 30
    },
    {
      "name": "A whale called Hope",
      "beginning": "A juvenile female blue whale stranded at Wexford Harbour in 1891.",
      "turn": "She was named Hope \"as a symbol of humanity's power to shape a sustainable future\".",
      "end": "She hangs in Hintze Hall, unveiled there in July 2017.",
      "turn_fact_ids": [
        "name_meaning"
      ],
      "fact_ids": [
        "stranding_place",
        "stranding_date",
        "name_meaning",
        "hintze_move"
      ],
      "spine": "She stranded at Wexford Harbour in eighteen ninety-one. She was named Hope, as a symbol of humanity's power to shape a sustainable future.",
      "needs_s": 15
    }
  ],
  "visual_motifs": [
    "The whole skeleton suspended mid-dive above the hall, jaws dipping towards the floor",
    "The spine arcing up towards the glazed roof",
    "Spread flippers and the open ribcage seen from below",
    "Daylight pouring through skylights and arched windows",
    "Terracotta arches, balconies and the grand staircase with its white statue",
    "Crowds on the hall floor looking tiny beneath the whale",
    "A sandbar at the mouth of a harbour in early morning light",
    "Water and sand at a river mouth on the Irish coast",
    "A living blue whale with mottled blue-grey skin and pale ribbed throat (visual only)"
  ],
  "emotional_core": "Visitors dwarfed beneath a 25.2-metre skeleton learn that Hope was a juvenile female blue whale. This suggests that even this enormous frame belonged to a young animal.",
  "controlling_idea": {
    "visitor_assumes": "This enormous skeleton must be a fully grown giant.",
    "actually": "Hope was a juvenile female blue whale.",
    "actually_fact_ids": [
      "juvenile_female"
    ],
    "second_half_fact_ids": [],
    "last_thought": "Twenty-five metres long, and she was only a juvenile.of course"
  },
  "lead_line": 0,
  "duration_s": 15,
  "duration_reason": "The controlling idea, that this 25.2-metre giant was a juvenile female, is a single turn that lands within one segment. A second segment would only add chronology stops (sale, Mammal Hall, Hintze Hall) that do not advance that turn."
}
</material>

<concept>
{
  "name": "From where you're standing",
  "engine": "(e) direct address to the visitor about what they are doing right now",
  "logline": "Hope speaks to the visitor up on the balcony, gives them her size in their own terms, then tells them she was still young.",
  "hook_visual": "A view from the upper balcony across the hall: the skeleton mid-dive in daylight, the people on the floor and staircase looking very small beneath it.",
  "hook_line": "From up there, the people below look tiny next to me.",
  "emotional_arc": "Shared wonder with the visitor at the scale, a beat of weight and solidity, then a gentle, surprising intimacy: this giant was young.",
  "ending_visual": "The same balcony-height view of the whole skeleton, flippers spread, ribcage open, jaws angled down towards the hall floor.",
  "ending_line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
  "fact_ids": [
    "length",
    "skeleton_weight",
    "juvenile_female"
  ],
  "answers_question": "How big is this whale?"
}
</concept>

<script>
{
  "highlights": [
    {
      "kind": "decision",
      "text": "balcony-eye opening and ending",
      "basis": "decision"
    },
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "visual",
      "text": "juvenile over giant bones",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "soft Irish young voice",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "request trimmed under cap",
      "basis": "decision"
    }
  ],
  "exhibit_id": "hope",
  "title": "From Up There",
  "logline": "Hope talks to the visitor looking down from the balcony, gives her length, then confides she was a juvenile.",
  "duration_s": 15,
  "style": "realistic",
  "narrator_presence": "voiceover",
  "voice": "A young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused.",
  "narrator_attitude": "Fond of the visitor gazing down at her from the balcony, a little amused by their awe, then confiding something gentle about herself.",
  "music_style": "One low bowed double-bass drone, very slow, airy hall reverb",
  "subject_name": "the whale skeleton",
  "living_form_name": "",
  "subject_lock": "The pale grey-white skeleton of a blue whale suspended mid-dive: long lower jawbones angled down, bony flippers spread, open ribcage, spine arcing up to a tapering tail.",
  "living_form_lock": "",
  "assets": [
    {
      "id": "skeleton_now",
      "source": "generate",
      "depicts": "exhibit_now",
      "view": "whole skeleton, elevated three-quarter view, mid-dive",
      "prompt": "Input image: the visitor's photo. Isolate the whale skeleton exactly as displayed and show it alone: the pale grey-white skeleton of a blue whale suspended mid-dive, long lower jawbones angled down towards the left, bony flippers spread, open ribcage, spine arcing up to a tapering tail at upper right. Keep the same elevated three-quarter view as the photo, the same pose, proportions and bone shapes as in the photo. Plain light neutral grey background, even soft neutral light, no glare. Entire skeleton in frame with margin. Nothing else in the frame: no hall, cables or people.",
      "purpose": "Identity reference for the close shot along the skull and jaws."
    },
    {
      "id": "hall_inplace",
      "source": "generate",
      "depicts": "environment",
      "view": "skeleton in Hintze Hall from the upper balcony",
      "prompt": "Input image: the visitor's photo. Clean it up keeping the same angle and framing: the pale grey-white blue whale skeleton suspended mid-dive under the glazed roof of the high Romanesque hall with terracotta-coloured stone arches, balconies, arched stained-glass windows and the grand staircase with its white statue. Remove glare, hanging banners and signs, leaving plain stonework where they hung; reduce visitors to a few small figures on the floor. Even natural daylight, no dramatic mood. Skeleton pose, proportions and position unchanged.",
      "purpose": "In-place reference for the opening and final balcony-height shots."
    }
  ],
  "segments": [
    {
      "duration_s": 15.0,
      "setting": "Hintze Hall from the upper balcony, bright skylight daylight",
      "ref_assets": [
        "skeleton_now",
        "hall_inplace"
      ],
      "shots": [
        {
          "t_start": 0.0,
          "t_end": 5.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide elevated balcony view",
          "camera": "slow push-in",
          "action": "Cloud shadow drifts slowly across the glazed roof.",
          "visual": "Bright skylight daylight on terracotta arches; staircase and white statue at right."
        },
        {
          "t_start": 5.0,
          "t_end": 10.0,
          "refs": [
            "skeleton_now"
          ],
          "framing": "medium close-up of skull and jaws at balcony height",
          "camera": "slow drift right",
          "action": "Dust motes float through sunbeams across the long jawbones.",
          "visual": "Warm terracotta blur behind, glazed roof ribs overhead, soft contrast."
        },
        {
          "t_start": 10.0,
          "t_end": 15.0,
          "refs": [
            "hall_inplace"
          ],
          "framing": "wide balcony-height view of the whole skeleton",
          "camera": "static",
          "action": "A band of sunlight slides along the ribcage and flippers.",
          "visual": "Tiny figures on floor and staircase, arched windows glowing."
        }
      ],
      "narration": [
        {
          "t_start": 0.3,
          "text": "From up there, the people below look tiny next to me.",
          "kind": "visible",
          "fact_ids": []
        },
        {
          "t_start": 5.7,
          "text": "Four point five tonnes.",
          "kind": "fact",
          "fact_ids": [
            "skeleton_weight"
          ]
        },
        {
          "t_start": 8.3,
          "text": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
          "kind": "fact",
          "fact_ids": [
            "length",
            "juvenile_female"
          ]
        }
      ],
      "audio": {
        "ambience": "Vast stone hall murmur under a glass roof.",
        "sfx": [
          "footsteps echoing on the stone floor"
        ],
        "music": "swells under the first line, fades out by the final second."
      },
      "end_frame": "Near-still balcony-height wide of the whole skeleton in daylight, jaws angled towards the floor, tiny visitors below."
    }
  ],
  "subtitles": [
    {
      "t_start": 0.3,
      "t_end": 2.5,
      "text": "From up there, the people below"
    },
    {
      "t_start": 2.5,
      "t_end": 4.7,
      "text": "look tiny next to me."
    },
    {
      "t_start": 5.7,
      "t_end": 7.3,
      "text": "Four point five tonnes."
    },
    {
      "t_start": 8.3,
      "t_end": 10.5,
      "text": "25.2 metres of bone,"
    },
    {
      "t_start": 10.5,
      "t_end": 13.9,
      "text": "and I was a juvenile female blue whale."
    }
  ]
}
</script>

<seedance_requests>
[
  {
    "endpoint": "bytedance/seedance-2.0/reference-to-video",
    "image_urls": [
      "<skeleton_now>",
      "<hall_inplace>"
    ],
    "duration": "15",
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "prompt": "References: @Image1 is the whale skeleton (copy its shape, pose and colour exactly; ignore its background); @Image2 is skeleton in Hintze Hall from the upper balcony (setting reference only: architecture, light and space).\nStyle: photorealistic documentary footage, natural light. Setting: Hintze Hall from the upper balcony, bright skylight daylight.\nShot 1 (@Image2): wide elevated balcony view, slow push-in; Cloud shadow drifts slowly across the glazed roof; bright skylight daylight on terracotta arches; staircase and white statue at right. Cut to shot 2 (@Image1): medium close-up of skull and jaws at balcony height, slow drift right; Dust motes float through sunbeams across the long jawbones; warm terracotta blur behind, glazed roof ribs overhead, soft contrast. Cut to shot 3 (@Image2): wide balcony-height view of the whole skeleton, static; A band of sunlight slides along the ribcage and flippers; tiny figures on floor and staircase, arched windows glowing.\nVoiceover, an unseen narrator, a young woman in her early twenties, soft low breathy timbre, gentle Irish accent, unhurried pace, warm and quietly amused: \"From up there, the people below look tiny next to me.\" \"Four point five tonnes.\" \"Twenty-five point two metres of bone, and I was a juvenile female blue whale.\"\nSound: Vast stone hall murmur under a glass roof; footsteps echoing on the stone floor. Music: One low bowed double-bass drone, very slow, airy hall reverb, swells under the first line, fades out by the final second.\nKeep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one whale skeleton in any frame.",
    "prompt_words": 255,
    "direction_words": 226,
    "prompt_parts": {
      "refs": 33,
      "style": 16,
      "shots": 97,
      "voice": 24,
      "sound": 37,
      "constraint": 19
    },
    "est_usd": 4.5
  }
]
</seedance_requests>

Automatic checks found: ["first line starts at 0.3s; open on 0.8s of picture and sound"]
```

```text
<previous_review>
{
  "highlights": [
    {
      "kind": "check",
      "text": "all 3 claims sourced",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "text-free assets confirmed",
      "basis": "decision"
    },
    {
      "kind": "check",
      "text": "226 direction words",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "weight beat still missing",
      "basis": "decision"
    }
  ],
  "claims": [
    {
      "line": "From up there, the people below look tiny next to me.",
      "claim": "The visitor is on an upper balcony, and the people on the hall floor look small beside the skeleton.",
      "kind": "visible",
      "supporting_fact": "photo: 'A wide, elevated shot taken from an upper balcony level ... Dozens of visitors on the hall floor and stairs look very small beneath the whale.'",
      "supported": true
    },
    {
      "line": "Take your time.",
      "claim": "none",
      "kind": "voice",
      "supporting_fact": "none",
      "supported": true
    },
    {
      "line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "claim": "The skeleton is 25.2 m long, and Hope was a juvenile female blue whale.",
      "kind": "fact",
      "supporting_fact": "length: 'The skeleton is 25.2 metres long.'; juvenile_female: 'Hope was a juvenile female blue whale.'",
      "supported": true
    }
  ],
  "previous_issues_resolved": [
    "Asset prompts naming text (blocking): resolved. Neither prompt now contains text, labels, logos or watermarks.",
    "Direction words 270 over the 230 cap (blocking): resolved. The request is now 226 direction words.",
    "'Take your time' filler instead of the concept's weight beat (polish): not resolved. The line is unchanged.",
    "Hook line captions shot 1 (polish): not resolved. The shot 1 action is still 'Small visitors cross the hall floor beneath the skeleton'.",
    "'From below' contradicts the balcony viewpoint (polish): not resolved. It remains in the shot 2 framing and in the skeleton_now asset view and prompt."
  ],
  "issues": [
    {
      "where": "segment 1 line 2",
      "severity": "polish",
      "problem": "'Take your time.' is still filler. It occupies the middle beat that the concept assigns to weight ('a beat of weight and solidity', with skeleton_weight in its fact_ids), so the arc goes straight from scale to youth.",
      "fix": "Retime line 1 to t_start 0.3 (11 words, ends 4.7). Replace line 2 with 'Four point five tonnes.' at t_start 5.7 (4 words, ends 7.3), kind fact, fact_ids [skeleton_weight]. Move line 3 unchanged to t_start 8.3 (14 words, ends 13.9, which is 1.1 s before the end). Update the subtitles: 0.3–2.5 'From up there, the people below' / 2.5–4.7 'look tiny next to me.' / 5.7–7.3 'Four point five tonnes.' / 8.3–10.5 '25.2 metres of bone,' / 10.5–13.9 'and I was a juvenile female blue whale.' This adds 1 direction word (227). The weight line then lands over the floating dust motes on the jaws, so the picture shows lightness while the voice gives weight."
    },
    {
      "where": "segment 1 shot 1",
      "severity": "polish",
      "problem": "The hook line describes its own shot: the action stages small visitors crossing beneath the skeleton while the voice says the people look tiny.",
      "fix": "Change the shot 1 action to 'Cloud shadow drifts slowly across the glazed roof.' (8 words, net 0 direction words). The tiny figures stay in the hall_inplace frame, but the line now directs the visitor's eye to them instead of repeating the staged action. The shot also no longer duplicates the sunlight move in shot 3."
    },
    {
      "where": "segment 1 shot 2 / asset skeleton_now",
      "severity": "polish",
      "problem": "'From below' and 'three-quarter view from below' contradict the balcony viewpoint that the concept and the photo both establish. This risks a jarring change of eye-line between the shots.",
      "fix": "Shot 2 framing: 'medium close-up of skull and jaws at balcony height' (+1 direction word, total 228 with the fixes above). Asset skeleton_now: change the view to 'whole skeleton, elevated three-quarter view, mid-dive', and in the prompt replace 'Keep the same three-quarter view from below' with 'Keep the same elevated three-quarter view as the photo'."
    }
  ],
  "scores": {
    "hook": 4,
    "visitor_view": 5,
    "focus": 5,
    "concept_fidelity": 4,
    "truth": 5,
    "counterpoint": 3,
    "spoken": 4,
    "visual_feasibility": 4,
    "length_fit": 3,
    "ending": 5
  },
  "summary": "Both blocking issues from the last review are fixed: the asset prompts are text-free and the request is down to 226 direction words. All three claims are supported, so the film can ship. The three polish notes are still open: swap 'Take your time' for the concept's 4.5-tonne beat, stop the hook line from describing shot 1, and change the 'from below' viewpoint to balcony height, all within about 228 direction words."
}
</previous_review>
```

### 模型思考摘要

I'm checking each line of the draft against the photo, starting with the claim that the people below look tiny from up there. The visitor is on the elevated balcony, so that vantage holds.

I'm working through the timing: the first line can't open until 0.8 seconds, and fitting all three lines with the required gaps before the segment ends looks too tight, with the total speech plus gaps running over the available time.

I'm trimming the opening line so the three lines fit in the segment, since the total runs past 15 seconds. Dropping a few words from the first line, with the second and third lines shifted after it, leaves about a second to spare at the end.

I'm settling on a nine-word version of the opening line so the three lines fit inside the segment with the required gaps. I'm also checking the subtitle timings against the shot boundaries, and the first line sits within the first shot as it should.

I'm checking the subtitle timings against the shot boundaries and the direction words, and confirming that the earlier issues around the weight line, the cloud shadow action, and the balcony framing are all resolved.

I'm checking the closing lines of the script against the shot timing and the voice notes, and the tone still holds up.

I'm checking whether the visitor really sits on the balcony, since the hook depends on that elevated view. The ending line and the "tiny" hook both look right, and the visual setup for the skeleton looks workable.

I'm scoring the draft against the brief: the hook, visitor view, focus, and ending all come out at 4 or 5, with the spoken delivery and visual feasibility at 4. The one blocking problem is the auto-check on the opening timing, which I'll need to fix before the script can go out.

I'm recording the final tally: three claims re-checked, the hook trimmed to nine words, and the opening moved to 0.8 seconds so the script clears the auto-check.

### 输出（结构化 JSON）

```json
{
  "highlights": [
    {
      "kind": "check",
      "text": "3 lines re-audited",
      "basis": "decision"
    },
    {
      "kind": "measure",
      "text": "4.5-tonne skeleton",
      "basis": "skeleton_weight"
    },
    {
      "kind": "check",
      "text": "0.8 s opening breath",
      "basis": "decision"
    },
    {
      "kind": "decision",
      "text": "hook trimmed to 9 words",
      "basis": "decision"
    }
  ],
  "claims": [
    {
      "line": "From up there, the people below look tiny next to me.",
      "claim": "The visitor is looking from an elevated balcony, and the people on the hall floor look small beside the skeleton.",
      "kind": "visible",
      "supporting_fact": "photo notes: 'A wide, elevated shot taken from an upper balcony level ... Dozens of visitors on the hall floor and stairs look very small beneath the whale.'",
      "supported": true
    },
    {
      "line": "Four point five tonnes.",
      "claim": "The skeleton weighs 4.5 tonnes.",
      "kind": "fact",
      "supporting_fact": "skeleton_weight: 'The skeleton is a 4.5-tonne skeleton.'",
      "supported": true
    },
    {
      "line": "Twenty-five point two metres of bone, and I was a juvenile female blue whale.",
      "claim": "The skeleton is 25.2 m long, and Hope was a juvenile female blue whale.",
      "kind": "fact",
      "supporting_fact": "length: 'The skeleton is 25.2 metres long.'; juvenile_female: 'Hope was a juvenile female blue whale.'",
      "supported": true
    }
  ],
  "previous_issues_resolved": [
    "'Take your time' filler replaced by the weight beat: resolved. Line 2 is now 'Four point five tonnes.' at 5.7, cited to skeleton_weight.",
    "Hook line captioning shot 1: resolved. The shot 1 action is now 'Cloud shadow drifts slowly across the glazed roof.'",
    "'From below' viewpoint: resolved. Shot 2 is now 'at balcony height', and the skeleton_now asset view and prompt say 'elevated three-quarter view'."
  ],
  "issues": [
    {
      "where": "segment 1 line 1 (automatic check)",
      "severity": "blocking",
      "problem": "The automatic check fails because the first line starts at 0.3 s and the film needs 0.8 s of picture and sound first. Moving the line to 0.8 s unchanged does not work. At 11 words it would end at 5.2, only 0.5 s before line 2. The three lines total 11.6 s of speech, and with the 0.8 s opening, two 1 s gaps and a 1 s tail they need 15.4 s in a 15 s segment.",
      "fix": "Rewrite line 1 as 'From up there, people look tiny next to me.' (9 words) at t_start 0.8, ending at 4.4. Move line 2 'Four point five tonnes.' to t_start 5.4 (4 words, ends 7.0). Move line 3 unchanged to t_start 8.0 (14 words, ends 13.6, which is 1.4 s before the end). Every gap is now at least 1.0 s. Update the subtitles to: 0.8–2.6 'From up there, people look' / 2.6–4.4 'tiny next to me.' / 5.4–7.0 'Four point five tonnes.' / 8.0–10.2 '25.2 metres of bone,' / 10.2–13.6 'and I was a juvenile female blue whale.' Update the request's voiceover line to match. This cuts 2 direction words (226 to 224)."
    }
  ],
  "scores": {
    "hook": 4,
    "visitor_view": 5,
    "focus": 5,
    "concept_fidelity": 5,
    "truth": 5,
    "counterpoint": 4,
    "spoken": 4,
    "visual_feasibility": 4,
    "length_fit": 4,
    "ending": 5
  },
  "summary": "All three earlier polish notes are fixed. The film now runs scale, then weight over drifting dust, then youth, and all three claims are supported by the photo or the pack. One blocking item remains: the automatic check requires the first line to start at 0.8 s. Trim the hook to 'From up there, people look tiny next to me.' and shift the timings as given so every line keeps a 1 s gap."
}
```

