# Too Young for the Shallows

*Cartoon Hope slips out of her skeleton, measures herself against the whole hall and reveals she wasn't yet fully grown, then lunges back into the only diving pose of its kind.*

**Status: NEEDS_HUMAN** · chosen attempt #1

Run `1114-211146-hope-alive` · exhibit `hope` · photo `hope_hintze_hall.webp` · model `claude-opus-5-5` · new spend $1.65

Prompts: keywords.md@bc94ebc2, s0_identify.md@025d7a76, s0b_research.md@63222915, s1_digest.md@7733405d, s1b_assets.md@a71685f9, s2_concept.md@2a800085, s3_script.md@8ad7080f, s4_review.md@6ce755ad

User input: (none)

## Attempts

| # | checks | blocking | polish | truth | min score | sum | words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 8 | 6 | 3 | 1 | 1 | 41 | 38 |
| 1 ✅ | 3 | 3 | 5 | 5 | 2 | 48 | 32 |
| 2 | 3 | 4 | 3 | 5 | 2 | 47 | 32 |

## S0 What the photo shows

- **Recognised as:** The blue whale skeleton suspended from the ceiling of Hintze Hall at the Natural History Museum, London, posed in a diving lunge. This is 'Hope'. → `hope` (high)
- **Visible:** A wide, elevated shot taken from a first-floor balcony looking across and slightly down into Hintze Hall. The whole whale skeleton fills the upper centre of the frame, seen from the side as it dives. The long lower jaws and skull angle down toward the left, and the spine and ribs arc up and away toward the skylights at the top right. Its hanging cables are visible. Soft daylight comes through the glazed roof and the arched windows, lighting the pale bones and the terracotta Romanesque arches. Below, dozens of visitors walk across the hall floor and climb the grand staircase, which has a white marble statue at its landing. The people look tiny next to the jaws alone. A small glass case with a coral-like specimen sits in a side alcove at the bottom left.
- **Visitor interest:** The wide balcony view, with tiny people below and the skeleton spanning the whole hall, suggests the visitor is struck by the whale's sheer size and its dramatic diving pose in the grand hall.

## Progress keywords (separate side requests)

**identify** (at 0.0s): Hope · blue whale skeleton · Hintze Hall · Natural History Museum, London · diving lunge · long lower jaws · terracotta Romanesque arches · hanging cables
**research** (at 0.0s): Hope the blue whale · 25 March 1891 · mouth of Wexford Harbour · 25.2 metres long · Hintze Hall · diving lunge feeding position · Swantons Bank · Ned Wickham · £250 · royal fish

## S0b Web research

I fetched the Natural History Museum's own Hope pages (the 2017 unveiling URL, which now redirects to the 'Hope the whale at the Natural History Museum' page, and the 2018 'secret history' page). I also ran one search to check where the pack's naming quote, the Dippy dates and the diving-lunge pose actually come from. Questions covered: her size, height above the floor, number of bones, pose, stranding, sale, arrival in London and name.

Tool calls:
- code_execution: `{"code": "import json\nr = await web_fetch({\"url\":\"https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html\"})\nc = r[0]['content'] if isinstance(r,list) else str(r)\nprint(c[:6000])"}`
- web_fetch: `{"url": "https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html"}`
- code_execution: `{"code": "d=r[0]['content']['source']['data'] if isinstance(r[0]['content'],dict) else c\ni=d.find('Choosing a new star')\nprint(d[i:i+9000])"}`
- code_execution: `{"code": "print(type(r)); d=c\ni=d.find('Choosing a new star')\nprint(d[i:i+9000])"}`
- code_execution: `{"code": "i=d.find('left them')\nprint(d[i:i+7000])"}`
- code_execution: `{"code": "r2 = await web_fetch({\"url\":\"https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html\"})\nd2=str(r2)\ni=d2.find('# ')\nimport re\nfor k in ['250','fully grown','15 years','calf','Wexford','sandbar','harpoon','Harbour','auction','Ball']:\n    for m in re.finditer(k,d2):\n        print(k,':',d2[max(0,m.start()-300):m.start()+300].replace('\\\\n',' '));print('---');break"}`
- web_fetch: `{"url": "https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html"}`
- code_execution: `{"code": "print(d2[:300])\nfor k in ['bought','female','Dippy','symbol','auctioned for','Gallagher','oil']:\n    for m in re.finditer(k,d2):\n        print(k,':',d2[max(0,m.start()-300):m.start()+300].replace('\\\\n',' '));print('---');break"}`
- code_execution: `{"code": "i=d2.find('Around half of this sum')\nprint(d2[i-1200:i+50].replace('\\\\n',' '))"}`
- code_execution: `{"code": "s = await web_search({\"query\":\"Hope blue whale named \\\"symbol of humanity's power to shape a sustainable future\\\" Natural History Museum\"})\nfor x in s[:6]:\n    print(x['url'],x['title']);cc=x['content']\n    j=cc.find('symbol');print(cc[max(0,j-300):j+200] if j>=0 else cc[:200]);print('==')"}`
- web_search: `{"query": "Hope blue whale named \"symbol of humanity's power to shape a sustainable future\" Natural History Museum"}`
- code_execution: `{"code": "if isinstance(s,str): s=json.loads(s)\nprint(type(s), str(s)[:300])"}`
- code_execution: `{"code": "for x in s[:6]:\n    print(x.get('url'),x.get('title'));cc=x.get('content','')\n    j=cc.find('symbol');print(cc[max(0,j-300):j+250] if j>=0 else cc[:200]);print('==')"}`
- code_execution: `{"code": "for x in s[3:6]:\n    cc=x.get('content','')\n    for k in ['Dippy','1979','2017','221','dive','lunge','female']:\n        j=cc.find(k)\n        if j>=0: print(x['url'][:40],k,':',cc[max(0,j-200):j+200].replace('\\n',' '));print('-')"}`

Sources:
- 🏛 [Hope the whale at the Natural History Museum | Natural History Museum](https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html) — Natural History Museum, London
- 🏛 [Secret history of Hope the blue whale (NHM history page)](https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html) — Natural History Museum, London
- 🏛 [Blue whale - the largest creature on Earth (1:20 scale) — Google Arts & Culture](https://artsandculture.google.com/asset/blue-whale-the-largest-creature-on-earth-1-20-scale/GAG_J9wcz31GXw?hl=en) — Google Arts & Culture / Natural History Museum
- [Hope (whale)](https://en.wikipedia.org/wiki/Hope_(whale)) — Wikipedia
- [Kate Middleton helps unveil a whale skeleton called Hope at Natural History Museum](https://www.ibtimes.co.uk/kate-middleton-helps-unveil-whale-skeleton-called-hope-natural-history-museum-1630275) — International Business Times UK
- [Natural History Museum blue whale: See time-lapse video...](https://www.getsurrey.co.uk/whats-on/arts-culture-news/natural-history-museum-blue-whale-13326321) — Get Surrey

Findings (verified URLs only):
- (exhibit) According to Lorraine Cornish, the museum's Head of Conservation, Hope is the only blue whale skeleton in the world hung in the diving lunge feeding position. — <https://artsandculture.google.com/asset/blue-whale-the-largest-creature-on-earth-1-20-scale/GAG_J9wcz31GXw?hl=en>
- (exhibit) The museum named the female blue whale Hope as a symbol of humanity's power to shape a sustainable future. — <https://artsandculture.google.com/asset/blue-whale-the-largest-creature-on-earth-1-20-scale/GAG_J9wcz31GXw?hl=en>
- (exhibit) On the morning of 25 March 1891, Hope stranded on a sandy ridge called Swantons Bank at the mouth of Wexford Harbour. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) Nobody knows for sure why she stranded. Bad weather might have made her lose her bearings, or she may still have been weak from raising a calf. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) Hope is thought to have been around 15 years old when she died, and was likely born sometime around 1876. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) The whale wasn't yet fully grown, and its youth wasn't enough to help it escape the shallows. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) Ned Wickham, a lifeboat pilot, eventually killed Hope to spare her further suffering by plunging an improvised harpoon under one of her flippers. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) The Receiver of Wreck auctioned off Hope's carcass, and the auction raised £111. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) Her buyer, William Armstrong, extracted almost 3,000 litres of oil from Hope. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (exhibit) William Armstrong sold the skeleton to the museum for £250, which the museum says equals over £28,000 today. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (context) Under UK law, whales have counted as 'royal fish' since 1324. As Ireland was under British rule at the time, Hope's body became the property of the state. — <https://nhm.ac.uk/discover/news/2018/september/secret-history-of-hope-the-blue-whale-finally-revealed.html>
- (context) Hope replaced a Diplodocus cast known as Dippy, which had been displayed in the main hall from 1979 until January 2017. — <https://en.wikipedia.org/wiki/Hope_(whale)>

Conflicts:
- The 2017 NHM URL cited by the pack now redirects to a newer page. That page does not contain the 'symbol of humanity's power' quote or the Dippy dates of 1979 to January 2017. Instead, it says she is called Hope 'in recognition of the recovery of her species following decades of commercial hunting'. For the naming quote, cite the Google Arts & Culture asset. For the Dippy dates, use Wikipedia (secondary). Both reasons for the name are compatible.
- The pack's Google Arts & Culture URL is the asset for a 1:20 scale 3D model of Hope. The page still states that the original skeleton is 25.2 m long.
- Get Surrey's headline gives the whale as 26.2 metres. The NHM says 25.2 metres, so use the NHM figure.
- Get Surrey says she stranded 'in Wexford Harbour'. The NHM says on Swantons Bank 'at the mouth of Wexford Harbour', and that wording is safer.
- The pack says she hung in the Mammal Hall 'from 1934'. The NHM agrees and adds that she stayed there 81 years. Note that she arrived in London in 1892 and spent more than 40 years in storage before going on display.

Not found:
- The NHM sources I checked do not give her estimated weight or skin colour as a living animal. The pack's 'Appearance' description of her skin remains unsourced.
- I did not verify the pack's March 2018 'a-cetacean-relation' page, because I did not fetch it.
- How much of the skeleton is original bone versus restoration was not covered, beyond the replacement spacers between the vertebrae.

## Final package (final.json)

- Image jobs (visitor photo + prompt): 3 (~$0.45): hope_skeleton_now, hall_inplace, hope_awake
- Existing images used: none
- Missing images: none
- Video requests: 2 (~$4.2), image_urls: <job:hope_skeleton_now>, <job:hall_inplace>, <job:hope_awake> | <job:hope_skeleton_now>, <job:hall_inplace>, <job:hope_awake>

## S1 Material

**Emotional core:** The whale that fills the whole hall wasn't yet fully grown when she stranded, and her youth wasn't enough to help her escape the shallows. This suggests that the giant above the visitors' heads was, in her own life, still young.

**Length:** 30s — The controlling idea — this vast whale was not yet fully grown and could not escape the shallows — sets up a turn that only lands in a second place: in Hintze Hall she is the only blue whale skeleton hung in a diving lunge, so a second fifteen seconds moves her from stranded in shallow water to diving above the visitor.

Facts:
- `female_blue_whale` (exhibit) Hope was a female blue whale.
- `stranding_1891` (exhibit) She stranded on a sandbar at the mouth of Wexford Harbour, Ireland, on the morning of 25 March 1891.
- `swantons_bank` (exhibit) The sandy ridge where she stranded is called Swantons Bank, at the mouth of Wexford Harbour.
- `stranding_cause_possible` (exhibit) Bad weather might have caused her to lose her bearings, or she may still have been weak from the effort of raising a calf.
- `not_fully_grown` (exhibit) The whale wasn't yet fully grown when she stranded.
- `youth_not_enough` (exhibit) Her youth wasn't enough to help her escape the shallows.
- `age_around_15` (exhibit) Hope is thought to have been around 15 years old at the time of her death.
- `born_around_1876` (exhibit) Hope was likely born sometime around 1876.
- `ned_harpoon` (exhibit) Ned eventually killed Hope to save her from further suffering by plunging an improvised harpoon under one of her flippers.
- `carcass_auction` (exhibit) Hope's carcass was auctioned off by the Receiver of Wreck, a role normally associated with salvaging shipwrecks.
- `auction_111` (exhibit) The auction raised £111.
- `oil_3000_litres` (exhibit) Her buyer, William Armstrong, extracted almost 3,000 litres of oil from Hope.
- `skeleton_4_5_tonnes` (exhibit) The skeleton weighs 4.5 tonnes.
- `sold_250` (exhibit) The skeleton was sold to the Natural History Museum for £250.
- `equivalent_28000` (exhibit) The museum says £250 was the equivalent of over £28,000 today.
- `mammal_hall_1934` (exhibit) The skeleton hung in the museum's Mammal Hall from 1934.
- `hintze_unveiled_2017` (exhibit) The skeleton was moved to Hintze Hall and unveiled there in July 2017.
- `replaced_dippy` (exhibit) In Hintze Hall she replaced a Diplodocus cast known as Dippy, which had been displayed in the main hall from 1979 until January 2017.
- `named_hope_future` (exhibit) The museum named the female blue whale Hope as a symbol of humanity's power to shape a sustainable future.
- `named_hope_recovery` (exhibit) She is called Hope in recognition of the recovery of her species following decades of commercial hunting.
- `length_25_2` (exhibit) The skeleton is 25.2 metres long.
- `diving_lunge_only` (exhibit) According to Lorraine Cornish, the museum's Head of Conservation, Hope is the only blue whale skeleton in the world to be hung in the diving lunge feeding position.
- `royal_fish_1324` (context) Whales have been deemed 'royal fish' under UK law since 1324.

Visitor questions:
- How big is she really, compared with all these people below her? → length_25_2, skeleton_4_5_tonnes, not_fully_grown
- Why is she hanging in that diving pose? → diving_lunge_only
- Where did this whale come from, and how did she end up here? → female_blue_whale, stranding_1891, swantons_bank, ned_harpoon, carcass_auction, sold_250, mammal_hall_1934, hintze_unveiled_2017
- Is this a real whale skeleton or a model? → stranding_1891, sold_250, skeleton_4_5_tonnes
- Why is she called Hope? → named_hope_future, named_hope_recovery

Conflicts:
- Length: Get Surrey's headline gives 26.2 metres; the NHM gives 25.2 metres. Say twenty-five point two metres.
- Place: Get Surrey says she stranded 'in Wexford Harbour'; the NHM says on Swantons Bank 'at the mouth of Wexford Harbour'. Say 'at the mouth of Wexford Harbour'.
- Naming: the 2017 NHM URL cited by the pack now redirects to a page without the 'symbol of humanity's power to shape a sustainable future' quote; that quote is cited to the NHM's Google Arts & Culture asset. The newer NHM page gives a second, compatible reason: 'in recognition of the recovery of her species following decades of commercial hunting'. Either is safe if attributed to its own source.
- Dippy dates (1979 until January 2017) are no longer on the NHM page the pack cites; they are cited to Wikipedia (secondary). January 2017 is when Dippy left the hall, not when Hope arrived; Hope was unveiled in July 2017.
- Age: do not call her a juvenile or a calf. Safe wording: 'not yet fully grown' and 'thought to have been around fifteen years old'. The calf is only a possibility ('she may still have been weak from the effort of raising a calf'); do not say she definitely had a calf.
- Cause of stranding is uncertain: the NHM says bad weather 'might have' and she 'may' have been weak; do not state a cause as fact.
- Two different sums: £111 was what the auction of the carcass raised; £250 was what the skeleton was sold to the museum for. Do not mix them up, and do not compute a profit.
- 4.5 tonnes is the weight of the skeleton, not of the living whale; 25.2 metres is the skeleton's length.
- Dates belong to different events: 1891 is the stranding, 1934 is when she began hanging in the Mammal Hall, July 2017 is the Hintze Hall unveiling. Research notes she arrived in London in 1892, spent over 40 years in storage and hung 81 years in the Mammal Hall, but these are not tied to a specific cited page; do not narrate them.
- The bone count (221) is marked UNSOURCED in the pack and the research gives no specific URL for it; leave it out. The diving lunge pose may be stated via the Head of Conservation quote.
- The pack's Google Arts & Culture page is for a 1:20 scale model of Hope; it still states the original skeleton is 25.2 m long.
- Ned is named only as 'Ned' in the quoted NHM text; the research summary calls him Ned Wickham, a lifeboat pilot. 'Ned' alone is safest.

**Controlling idea:** the visitor thinks *A skeleton this enormous, spanning the whole hall above tiny people, must have been a fully grown giant at the end of a long life.*, but actually *The whale wasn't yet fully grown when she stranded, and her youth wasn't enough to help her escape the shallows.* [not_fully_grown, youth_not_enough] · second half: [diving_lunge_only, hintze_unveiled_2017] · last thought: "Twenty-five metres long, and still not fully grown."

Through-lines:
- **Stuck in the shallows, diving forever** ✅ lead (30s): A female blue whale, not yet fully grown, strands on a sandbar at the mouth of Wexford Harbour on the morning of 25 March 1891, and her youth isn't enough to help her escape the shallows. → *From an animal trapped in shallow water to a skeleton hung in a dive: she becomes the only blue whale skeleton in the world hung in the diving lunge feeding position.* → Unveiled in Hintze Hall in July 2017, she dives above the visitors.
  > spine (65 words): She is twenty-five point two metres long, and she wasn't yet fully grown. On the morning of twenty-five March eighteen ninety-one she stranded at the mouth of Wexford Harbour, and her youth wasn't enough to help her escape the shallows. Since July twenty seventeen she has hung in Hintze Hall, the only blue whale skeleton in the world hung in the diving lunge feeding position.
- **From royal fish to museum bones** (30s): After she strands, Ned kills her with an improvised harpoon to save her from further suffering. → *Her carcass is auctioned by the Receiver of Wreck for £111 and her buyer extracts almost 3,000 litres of oil, then the 4.5-tonne skeleton is sold to the museum for £250: from carcass to specimen.* → From 1934 the skeleton hangs in the museum's Mammal Hall.
  > spine (50 words): The Receiver of Wreck auctioned her carcass for one hundred and eleven pounds. Her buyer took almost three thousand litres of oil from her, then sold the four point five tonne skeleton to the museum for two hundred and fifty pounds. From nineteen thirty-four she hung in the Mammal Hall.
- **A name for the future** (30s): From 1934 the skeleton hangs in the museum's Mammal Hall. → *In July 2017 she is moved into Hintze Hall, replacing Dippy the Diplodocus cast, and named Hope: from a specimen to a symbol.* → She is named as a symbol of humanity's power to shape a sustainable future, in recognition of the recovery of her species.
  > spine (37 words): From nineteen thirty-four she hung in the Mammal Hall. In July twenty seventeen she was unveiled in Hintze Hall, in place of Dippy, and named Hope, as a symbol of humanity's power to shape a sustainable future.

## S1b Reference-image plan

**Names:** the whale skeleton / Hope the cartoon whale

**Subject lock:** A 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind.

**Living form lock:** A stylized cartoon blue whale, slender body, deep blue-grey mottled skin with soft lighter patches, pale ribbed throat, large expressive dark eyes, gentle smiling mouth, long slim flippers.

- **hope_skeleton_now** (subject_view) — Identity anchor for the exhibit as it is now: exact bone shape, colour and dive pose.
  > From this photo, show only the whale skeleton, isolated on a plain light grey background, at the same three-quarter angle as the photo: a 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind. Show the full skeleton from jaw tips to tail vertebrae, with flipper bones visible, every vertebra and rib curve crisp. Even, soft neutral studio light, no glare, no harsh shadows, no reflections. Remove the hall, the architecture, the windows and all people. Photorealistic bone texture.
  > avoid: text, labels, captions, watermarks, people, visitors, glass cases, banners, hall architecture, windows, skylights, second skeleton, flesh or skin, cartoon styling
- **hall_inplace** (in_place) — Reference for the final return shot of the skeleton in its hall.
  > From this photo, keep the exact same angle and framing of the Romanesque hall with its terracotta arches, carved stonework, glazed roof, stained-glass arched windows, grand staircase and white marble statue, with the whale skeleton hanging in the centre: a 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind. Remove all visitors from the floor, staircase and balconies, leaving the polished floor empty. Remove the hanging banners, signs, display text and any readable lettering. Remove glare and lens reflections. Soft natural daylight from the skylights, photorealistic.
  > avoid: people, visitors, faces, readable text, signs, banners, labels, watermarks, glare, reflections, extra whale, cartoon whale, living whale
- **hope_awake** (living_form) — Clean single-view character reference for Hope, derived from the labelled stylized sheet.
  > From this photo, design the whale skeleton as a living character: Hope, a stylized cartoon blue whale shown alone in three-quarter view on a plain light grey-blue background. Slender, streamlined body, deep blue-grey mottled skin with soft lighter patches, pale ribbed throat with fine parallel grooves, large expressive dark eyes with a soft highlight, a long gently smiling mouth that can open to talk, long slim pale-edged flippers, small dorsal fin, broad tail flukes. Friendly, curious, young personality. Clean outline, lightly anime-styled with simplified mottling, as in the stylized design guide. Whole body visible from snout to tail flukes. Even soft light, no water, no hall.
  > avoid: text, labels, captions, watermarks, people, glass cases, skeleton bones, multiple views, expression variants, second whale, water surface, sun rays, hall architecture
- **hope_dive_keyframe** (keyframe) — Keyframe for the diving lunge, linking the character's motion to the skeleton's hung pose.
  > From this photo, show Hope alone on a plain light grey-blue background in her big pose, a diving lunge: a stylized cartoon blue whale, slender body, deep blue-grey mottled skin with soft lighter patches, pale ribbed throat with fine parallel grooves, large expressive dark eyes, gentle smiling mouth, long slim flippers. Her head angles steeply downward with the jaw slightly open and throat grooves gently stretched, body arcing up behind her and tail flukes raised, matching the downward dive angle of the skeleton in the photo. Seen in three-quarter view, eyes bright and determined. Even soft light, lightly anime-styled clean outline.
  > avoid: text, labels, watermarks, people, glass cases, skeleton bones, second whale, water, hall architecture, multiple views
- **shallows_plate** (world_plate) — Artistic world plate for the stranding shallows sequence, no character in it.
  > From this photo, keep only its soft colour mood and create an artistic, painterly world plate: grey early-morning water at the mouth of a wide harbour, a long low sandy ridge just breaking the surface, thin shallow water lapping over the sandbar, pale overcast sky with a faint dawn glow, distant low dark coastline. Lightly anime-styled painted backdrop matching a cartoon film. Empty scene with room in the middle for a character to be added later.
  > avoid: whale, skeleton, animals, people, faces, boats with names, buildings, landmarks, text, signs, watermarks, dated objects
- **open_ocean_plate** (world_plate) — Artistic world plate for Hope swimming free before the dive returns to the hall.
  > From this photo, keep only its soft colour mood and create an artistic, painterly world plate: deep open blue ocean seen underwater, rippling surface above with gentle sun rays slanting down into blue-green depths, a few drifting particles, darker blue fading below. Lightly anime-styled painted backdrop matching a cartoon film. Empty scene with open space for a diving character to be added later.
  > avoid: whale, skeleton, fish, animals, people, faces, boats, land, text, watermarks

## S2 Concepts

### 0. Too Young for the Shallows ✅ chosen — character / ESCAPE AND RETURN (lines ordered as a reveal): Hope swims out of her bones, stretches the length of the hall above the tiny people, then dives back into her pose
- **Logline:** Cartoon Hope slips out of her skeleton, measures herself against the whole hall and reveals she wasn't yet fully grown, then lunges back into the only diving pose of its kind.
- **Hero:** Hope the cartoon whale wants To show how big she is · first sign: By 2 s the skull's eye socket blinks into a living cartoon eye and blue skin ripples down the jaw. · big move: In segment two she shoots up to the skylights, then plunges at full speed in a diving lunge, jaw thrown open and throat pleats ballooning. The rush of air sweeps across the empty hall and sends the hanging cables swinging, until she slams back into her bones and they lock into the dive pose.
- **Spectacle shot:** Hope, now a full blue whale, glides nose to tail along the whole length of Hintze Hall, her flipper passing just over the tiny people on the grand staircase.  · return trace: One hanging cable still trembles and a last faint shimmer of blue fades along the lower jaw of the still skeleton.
- **Hook:** The balcony view of the still skeleton. The skull's empty eye socket blinks open into a large, bright cartoon eye, and a ripple of blue-grey skin shivers down the long jaws. — "From up here, those people look tiny, don't they?"
- **Arc:** Awe at her size turns to surprise (she was still young), then tenderness (the shallows), then a rush of joy as she dives, and ends in quiet wonder at the real bones.
- **Ending:** The real skeleton, whole and still in Hintze Hall at the visitor's balcony angle: jaws angled down, spine and ribs arcing toward the skylights, cables taut. — "Twenty-five point two metres, and still not fully grown."
- **Answers:** How big is she really, compared with all these people below her?

### 1. Caught in the Flash — character / IT NOTICES YOU: the visitor's photo flash wakes her; she swims straight up to the balcony and talks into the lens
- **Logline:** The visitor's flash wakes Hope, who swims up to the balcony to stare into the phone, tells them she was still young, then dives back into her pose.
- **Hero:** Hope the cartoon whale wants To fill your whole screen · first sign: At 1 s the flash fires and the skull swings toward the camera, an eye opening in the socket. · big move: She surges up to the balcony so fast that her eye fills the entire phone frame and her breath fogs the lens. Then she spins away and drops in a steep diving lunge, her tail flukes whipping past the camera and making the frame shake.
- **Spectacle shot:** A single huge, friendly whale eye fills the phone screen from the balcony and blinks at the visitor. · return trace: A thin mist on the lens clears to reveal the still skeleton, one cable gently swaying.
- **Hook:** A white camera flash bursts across the hall. The skeleton's skull jerks toward the balcony, blue skin flooding over the bone from the jaw back. — "You can't fit all of me in, can you?"
- **Arc:** Startled delight at being seen turns to playful closeness at the lens, then a softer, younger truth, then pride as she shows off her dive.
- **Ending:** The real skeleton, whole and still, framed exactly as in the visitor's balcony photo, diving across the hall under the skylights. — "Look again. I was still growing."
- **Answers:** How big is she really, compared with all these people below her?

### 2. Bone to Blue — awaken / MATERIAL MAGIC: the skeleton fills out into living skin in place, performs one feeding lunge without leaving her cables, and drains back to bone
- **Logline:** Without leaving her cables, Hope's bones flood with living blue skin from jaw to tail, her throat swells in one great lunge, and the skin ebbs back to pale bone.
- **Hero:** Hope's skin flowing over her bones wants To feel whole again · first sign: By 2 s blue skin spreads up the lower jaw and throat pleats appear on the bone. · big move: Fully fleshed, she gapes in one powerful feeding lunge in place. Her throat balloons hugely and the cables strain and groan under the sudden weight.
- **Spectacle shot:** The whole hanging skeleton fully clothed in living blue skin, throat ballooned open, suspended over the tiny crowd. · return trace: The skin ebbs back tail-first and leaves a faint wet gleam on the jaw tips of the pale skeleton.
- **Hook:** Close on the pale lower jaw. A wash of deep blue-grey spreads over the bone like rising water, and fine throat pleats draw themselves across it. — "You think these are the bones of an old giant."
- **Arc:** Mystery gives way to the thrill of seeing her whole and alive, then a tender reveal, then the calm of watching her settle back into bone.
- **Ending:** The real skeleton, pale and whole, mid-dive at the visitor's balcony angle with the skylights above. — "The only blue whale skeleton in the world hung like this, still diving."
- **Answers:** How big is she really, compared with all these people below her?

**Why this one:** The visitor took this photo because the whale dwarfs everyone in the hall, so the film answers size first. In concept 0, Hope herself becomes the ruler: she glides the full length of the hall over the tiny people, gives her length in metres, and then delivers the surprise that she wasn't yet fully grown. She is a true character with eyes, expression and voice. Her escape and her full-speed dive back into the pose give the strongest aliveness and spectacle, and the second segment carries the diving-lunge fact as the turn from the shallows to diving forever. It renders as one character moving at a time, one transformation per shot and short lines, with no reconstruction of the stranding. When the visitor looks up from the phone, the jaws and arching spine read as a young whale caught mid-dive, and the trembling cable makes it feel as if she only just got back.

## S3 Script (chosen attempt)

```
{
  "duration_s": 30,
  "mode": "character",
  "hero_mover": "Hope the cartoon whale",
  "act_shots": [
    "1.3",
    "2.2"
  ],
  "force_words": 11,
  "style": "stylized",
  "narrator": "on_screen",
  "segments": 2,
  "shots": 6,
  "spoken_words": 32,
  "words_per_second": 1.07,
  "lines_by_kind": {
    "fact": 4,
    "visible": 0,
    "voice": 0
  },
  "assets": {
    "existing": 0,
    "generate": 3
  }
}
```

- **Mode / hero:** character / Hope the cartoon whale (wants To show how big she is); still: —
- **Look:** stylized 3D animated feature, light anime outlines, soft skylight daylight, grand Romanesque hall · style stylized · narrator on_screen
- **Voice:** A young woman's voice, bright and warm, soft British accent, unhurried pace, playful with a hint of shyness.
- **Attitude:** Delighted to be noticed, eager to impress the visitor with her size, then tender and a little wistful about how young she was.
- **Music:** no music
- **Subject lock:** A 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind.

### Segment 1 (15.0s · Hintze Hall, seen from the first-floor balcony · refs: hope_skeleton_now, hall_inplace, hope_awake)

| t | refs | framing / camera | action | visual |
| --- | --- | --- | --- | --- |
| 0.0–3.5 **still** | hope_skeleton_now, hall_inplace | cut → wide elevated balcony view / locked off | Tiny visitors stand frozen on staircase and floor, looking up; at 1.5s the skull's empty eye socket blinks open into a bright cartoon eye that swivels to camera. |  |
| 3.5–8.5 **stir** | hope_skeleton_now, hope_awake | cut → close-up on skull and jaws / slow push-in to her eye | She shakes her head hard, cables twanging, and grins at camera, talking. ⟶ pale bone -> blue-grey skin ripples fast from the jaw tips back over four seconds -> Hope's living head fills the frame |  |
| 8.5–15.0 **act** | hall_inplace, hope_skeleton_now, hope_awake | whip pan → wide full hall / fast lateral tracking alongside her, then hold | Hope, free of the bare skeleton behind, surges the hall's length, tail beating hard, flipper skimming over frozen visitors on the staircase; cables swing in her wake; she brakes hard and hovers, looking back. |  |

Narration:
- `1.8s` *fact* "My skeleton is twenty-five point two metres long." [length_25_2]
- `5.6s` *fact* "And I wasn't yet fully grown." [not_fully_grown]

Audio: Echoing stone hall; sfx: bone creak, cables twanging, deep whale call; music: No music.
End frame: Hope hovering near-still above the grand staircase, looking back at camera, the bare skeleton hanging behind her.

### Segment 2 (15.0s · Hintze Hall, seen from the first-floor balcony · refs: hope_skeleton_now, hall_inplace, hope_awake)

| t | refs | framing / camera | action | visual |
| --- | --- | --- | --- | --- |
| 15.0–19.5 **stir** | hope_awake, hall_inplace | cut → medium close-up / slow push-in to her eyes | Hope hovers above the staircase, looks down at frozen tiny visitors, eyes softening, flippers drooping as she speaks, then her tail snaps once, hard. |  |
| 19.5–24.5 **act** | hope_awake, hope_skeleton_now, hall_inplace | cut → wide at balcony height / 4.5-5.5s fast tilt up, 5.5-9.5s hold wide | Hope rockets to the glazed roof, flips, plunges full speed into the hanging bones, jaw thrown open, throat pleats ballooning; cables swing hard; a deep thud as it locks. ⟶ blue skin -> streams off into the hanging bones snout to tail over four seconds -> skeleton locked in dive pose |  |
| 24.5–30.0 **return** | hall_inplace, hope_skeleton_now | cut → wide elevated balcony view, visitor's photo angle / locked off | The skeleton hangs whole and still, jaws angled down; one cable still trembles and a last shimmer of blue fades along the lower jaw. |  |

Narration:
- `15.8s` *fact* "My youth wasn't enough to escape the shallows." [youth_not_enough]
- `24.7s` *fact* "I'm the only blue whale skeleton in a diving lunge." [diving_lunge_only]

Audio: Echoing stone hall hush; sfx: air whoosh, bones locking thud, cable twang; music: No music.
End frame: The real skeleton whole and still in Hintze Hall at the visitor's balcony angle, one cable barely trembling.

### Assets

- **hope_skeleton_now** (generate, skeleton, three-quarter side view in dive pose, isolated) — Identity anchor for the exhibit as it is now: exact bone shape, colour and dive pose.
  > From this photo, show only the whale skeleton, isolated on a plain light grey background, at the same three-quarter angle as the photo: a 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind. Show the full skeleton from jaw tips to tail vertebrae, with flipper bones visible, every vertebra and rib curve crisp. Even, soft neutral studio light, no glare, no harsh shadows, no reflections. Remove the hall, the architecture, the windows and all people. Photorealistic bone texture. No text, labels or watermarks.
- **hall_inplace** (generate, skeleton in Hintze Hall from the first-floor balcony, visitor's photo angle) — In-place view for the opening still shot, the hall-scale action and the final return shot; its few tiny still figures carry the scale gag.
  > From this photo, keep the exact same angle and framing of the Romanesque hall with its terracotta arches, carved stonework, glazed roof, stained-glass arched windows, grand staircase and white marble statue, with the whale skeleton hanging in the centre: a 25-metre blue whale skeleton of pale cream-grey bone suspended mid-dive by thin cables, long lower jaws and skull angled downward, spine and ribs arcing up behind. Keep only a few small, still, unidentifiable figures standing on the staircase and floor, seen from far away with no visible faces; remove all other visitors. Remove the hanging banners, signs, display text and any readable lettering. Remove glare and lens reflections. Soft natural daylight from the skylights, photorealistic.
- **hope_awake** (generate, cartoon Hope alive, three-quarter view, whole body) — Clean single-view character reference for Hope, derived from the labelled stylized sheet; keeps her design identical in every shot.
  > From this photo, design the whale skeleton as a living character: Hope, a stylized cartoon blue whale shown alone in three-quarter view on a plain light grey-blue background. Slender, streamlined body, deep blue-grey mottled skin with soft lighter patches, pale ribbed throat with fine parallel grooves, large expressive dark eyes with a soft highlight, a long gently smiling mouth that can open to talk, long slim pale-edged flippers, small dorsal fin, broad tail flukes. Friendly, curious, young personality. Clean outline, lightly anime-styled with simplified mottling, as in the stylized design guide. Whole body visible from snout to tail flukes. Even soft light, no water, no hall, no text.

## Seedance requests

Segment 1: `bytedance/seedance-2.0/reference-to-video` · duration 15 · 480p 16:9 · refs ['<hope_skeleton_now>', '<hall_inplace>', '<hope_awake>'] · 335 direction words {'refs': 52, 'lock': 14, 'style': 13, 'shots': 190, 'voice': 28, 'sound': 13, 'constraint': 25} · 349 total · ~$2.1

```
References: @Image1 = the whale skeleton, identity anchor: shape, decoration and colours exactly as shown; ignore its background; @Image2 = skeleton in Hintze Hall from the first-floor balcony, visitor's photo angle (setting only); @Image3 = Hope the cartoon whale, the character: same design, colours and markings in every shot; ignore its background.
Only Hope the cartoon whale comes alive. The whale skeleton ends whole and unchanged.
Stylized 3D animated feature, light anime outlines, soft skylight daylight, grand Romanesque hall.
Shot 1 (0-3.5s) [the whale skeleton from @Image1, the setting from @Image2]: wide elevated balcony view, locked off. Tiny visitors stand frozen on staircase and floor, looking up; at 1.5s the skull's empty eye socket blinks open into a bright cartoon eye that swivels to camera. Shot 2 (3.5-8.5s) [the whale skeleton from @Image1, Hope the cartoon whale from @Image3]: close-up on skull and jaws, slow push-in to her eye. She shakes her head hard, cables twanging, and grins at camera, talking; pale bone -> blue-grey skin ripples fast from the jaw tips back over four seconds -> Hope's living head fills the frame. Shot 3 (8.5-15s) [the setting from @Image2, the whale skeleton from @Image1, Hope the cartoon whale from @Image3]: Whip pan: wide full hall, fast lateral tracking alongside her, then hold. Hope, free of the bare skeleton behind, surges the hall's length, tail beating hard, flipper skimming over frozen visitors on the staircase; cables swing in her wake; she brakes hard and hovers, looking back. End on a near-still image: hope hovering near-still above the grand staircase, looking back at camera, the bare skeleton hanging behind her.
Hope the cartoon whale speaks on screen, lips in sync, a young woman's voice, bright and warm, soft British accent, unhurried pace, playful with a hint of shyness: "My skeleton is twenty-five point two metres long." "And I wasn't yet fully grown."
Sound: Echoing stone hall; bone creak; cables twanging; deep whale call. No music.
Clean picture: no subtitles, captions, lettering, logos or watermark. Never two copies of the whale skeleton or of Hope the cartoon whale in one frame.
```

Segment 2: `bytedance/seedance-2.0/reference-to-video` · duration 15 · 480p 16:9 · refs ['<hope_skeleton_now>', '<hall_inplace>', '<hope_awake>'] · 314 direction words {'refs': 52, 'lock': 14, 'style': 13, 'shots': 168, 'voice': 28, 'sound': 14, 'constraint': 25} · 332 total · ~$2.1

```
References: @Image1 = the whale skeleton, identity anchor: shape, decoration and colours exactly as shown; ignore its background; @Image2 = skeleton in Hintze Hall from the first-floor balcony, visitor's photo angle (setting only); @Image3 = Hope the cartoon whale, the character: same design, colours and markings in every shot; ignore its background.
Only Hope the cartoon whale comes alive. The whale skeleton ends whole and unchanged.
Stylized 3D animated feature, light anime outlines, soft skylight daylight, grand Romanesque hall.
Shot 1 (0-4.5s) [Hope the cartoon whale from @Image3, the setting from @Image2]: medium close-up, slow push-in to her eyes. Hope hovers above the staircase, looks down at frozen tiny visitors, eyes softening, flippers drooping as she speaks, then her tail snaps once, hard. Shot 2 (4.5-9.5s) [Hope the cartoon whale from @Image3, the whale skeleton from @Image1, the setting from @Image2]: wide at balcony height, 4.5-5.5s fast tilt up, 5.5-9.5s hold wide. Hope rockets to the glazed roof, flips, plunges full speed into the hanging bones, jaw thrown open, throat pleats ballooning; cables swing hard; a deep thud as it locks; blue skin -> streams off into the hanging bones snout to tail over four seconds -> skeleton locked in dive pose. Shot 3 (9.5-15s) [the setting from @Image2, the whale skeleton from @Image1]: wide elevated balcony view, visitor's photo angle, locked off. The skeleton hangs whole and still, jaws angled down; one cable still trembles and a last shimmer of blue fades along the lower jaw.
Hope the cartoon whale speaks on screen, lips in sync, a young woman's voice, bright and warm, soft British accent, unhurried pace, playful with a hint of shyness: "My youth wasn't enough to escape the shallows." "I'm the only blue whale skeleton in a diving lunge."
Sound: Echoing stone hall hush; air whoosh; bones locking thud; cable twang. No music.
Clean picture: no subtitles, captions, lettering, logos or watermark. Never two copies of the whale skeleton or of Hope the cartoon whale in one frame.
```

## S4 Review of chosen attempt

Fantasy legibility: **pass**

```
{"hook": 4, "visitor_view": 5, "aliveness": 4, "spectacle": 4, "escalation": 4, "physicality": 4, "character": 4, "return_shot": 4, "renderability": 2, "truth": 5, "sound": 4, "voice_fit": 4}
```

The truth is now clean, both act beats are silent, and the spectacle shot is clear: Hope surges nose to tail the length of Hintze Hall, her flipper skimming over the frozen tiny visitors on the staircase. It cannot ship yet. Both requests are still about 100 words over the cap, the plunge shot is 61 words with the transformation placed after the lock, and the stir shot shakes the skull before the skin grows.

Claim audit:
- ✅ *fact* "My skeleton is twenty-five point two metres long." — The skeleton is 25.2 m long. — length_25_2: 'The skeleton is 25.2 metres long.'
- ✅ *fact* "And I wasn't yet fully grown." — Hope was not yet fully grown (when she stranded). — not_fully_grown: 'The whale wasn't yet fully grown when she stranded.'
- ✅ *fact* "My youth wasn't enough to escape the shallows." — Being young did not let her get out of the shallow water. — youth_not_enough: 'Her youth wasn't enough to help her escape the shallows.'
- ✅ *fact* "I'm the only blue whale skeleton in a diving lunge." — She is the only blue whale skeleton displayed in the diving lunge pose. — diving_lunge_only: 'Hope is the only blue whale skeleton in the world to be hung in the diving lunge feeding position.' The line keeps the specific pose and the 'only' qualifier, so it was accepted in the last review.

Issues:
- **blocking** [both requests] Automatic-check failure: 335 and 314 direction words against a cap of 240. The reference block (52 words), the voice block (28) and the constraint block (25) are all boilerplate-heavy, and '@Image1 ... decoration and colours' describes a skeleton that has no decoration. → Use these blocks in both requests. References: '@Image1 skeleton identity and pose; @Image2 hall, balcony angle, setting; @Image3 Hope's design.' Voice: 'Hope speaks, a young British woman, bright, warm, unhurried, a little shy:' Constraint: 'No text or watermark. One skeleton and one Hope per frame.' Style: 'Stylized 3D feature, light anime outlines, skylight daylight.' Keep the four sound nouns. With the shots below this lands near 190 direction words, and every speed, force and consequence word stays.
- **blocking** [segment 2 shot 2 (act)] Automatic-check failure: the shot runs 61 words. The actions are not bound to the timed camera beats, and the transformation sentence comes after 'a deep thud as it locks', so Seedance may lock the bones first and then stream skin. That would leave skin on the skeleton or give two whale forms. → Rewrite as: '(4.5–5.5s) fast tilt up as Hope rockets to the glazed roof and flips; (5.5–9.5s) hold wide as she plunges full speed into the hanging bones, jaw thrown open, throat pleats ballooning, her blue skin streaming off snout to tail over four seconds; cables swing hard; deep thud as the bones lock in the dive.' That is about 50 words, the transformation gets four full seconds, and the order is plunge, stream, lock.
- **blocking** [segment 1 shot 2 (stir)] The prompt puts 'She shakes her head hard ... grins' before the skin transformation. The bare skull is asked to shake and grin first, and then the skin grows, which reverses the cause and effect. It also pushes the shot past 40 words. → 'Close-up on skull and jaws, slow push-in. Blue-grey skin ripples from the jaw tips back over four seconds until Hope's living head fills the frame; then she shakes her head hard, cables twanging, and grins at camera, talking.' That is about 38 words.
- **polish** [segment 2 shot 3 (return) and voice block] The voice block says 'Hope speaks on screen, lips in sync', but the closing line falls in the return shot, where only the skeleton is present. Seedance may make the real jaws move to match the speech or bring cartoon Hope back into frame, and either would alter the return shot. → In the seg 2 voice block write: 'Line 1 spoken on screen by Hope; line 2 heard off-screen over the still skeleton, its jaws unmoving.' In shot 3 add 'jaws closed and still'.
- **polish** [segment 1 shot 3 camera] 'Whip pan: fast lateral tracking alongside her, then hold' gives Seedance no timing for when the track ends. → '(8.5–13.5s) camera tracks fast alongside Hope as she surges nose to tail down the hall, tail beating hard, flipper skimming over the frozen visitors on the staircase, cables swinging in her wake; (13.5–15s) hold as she brakes hard and hovers, looking back. Bare skeleton hangs still behind.'
- **polish** [segment 2 shot 3 (return)] There are still two traces of life, a trembling cable and a blue shimmer, which split attention on the final image. → 'The skeleton hangs whole and still, jaws angled down, cables still; a last faint shimmer of blue fades along the lower jaw.' Drop 'cable twang' from the seg 2 sound list and use 'skylight hush' as the final sound.
- **polish** [segment 1 shot 1 (still)] A small transformation is triggered at the instant of 1.5 s, which gives the eye little room to grow and risks a pop. → 'Locked off. From 1.0s a large cartoon eye slowly blinks open inside the skull's eye socket and swivels to camera; tiny visitors stand frozen; everything else still.'
- **polish** [segment 1 sound] 'Deep whale call' is not tied to any event, so Seedance will place it at random. → Tie it to an event: 'deep whale call as she brakes and hovers'. Keep 'bone creak' for the eye opening and 'cables twanging' for the head shake.

## Checks and production notes

- ❌ segment 1 request has 335 direction words (cap 240, quoted narration not counted): references 52, shots 190, sound 13, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- ❌ segment 2 shot 2 is 61 words; keep each shot to about 40 (one tight sentence, verbs first)
- ❌ segment 2 request has 314 direction words (cap 240, quoted narration not counted): references 52, shots 168, sound 14, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- 📝 segment 1 request has 335 direction words (soft limit 200)
- 📝 segment 1 request is 349 words including narration
- 📝 segment 2 request has 314 direction words (soft limit 200)
- 📝 segment 2 request is 332 words including narration

Problems along the way:
- s0b: finding says 2015, which is not in its own quote: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html ('Museum staff inspected the skeleton's 221 bones wh')
- s0b: finding says 1930, which is not in its own quote: https://nhm.ac.uk/discover/news/2017/july/museum-unveils-hope-the-blue-whale-skeleton.html ('In the 1930s, wooden blocks, plaster of Paris and ')
- s3#0: segment 1 shot 2 is 55 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#0: segment 1 shot 3 is 47 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#0: segment 1 request has 387 direction words (cap 240, quoted narration not counted): references 52, shots 215, sound 40, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- s3#0: segment 1 line 'My skeleton is twenty-five point two met' talks over the act beat; leave the big move without speech
- s3#0: segment 2 shot 2 camera stacks moves ('fast tilt up to the skylights, then crash-down tracking her dive'); cut, or write timed beats
- s3#0: segment 2 shot 2 is 64 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#0: segment 2 request has 357 direction words (cap 240, quoted narration not counted): references 52, shots 187, sound 38, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- s3#0: segment 2 line 'My youth wasn't enough to escape the sha' talks over the act beat; leave the big move without speech
- s3#1: segment 1 request has 335 direction words (cap 240, quoted narration not counted): references 52, shots 190, sound 13, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- s3#1: segment 2 shot 2 is 61 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#1: segment 2 request has 314 direction words (cap 240, quoted narration not counted): references 52, shots 168, sound 14, voice 28, fixed 52; cut sound and light words first, never speed, force or consequence words
- s3#2: segment 1 request has 303 direction words (cap 240, quoted narration not counted): references 45, shots 178, sound 13, voice 20, fixed 47; cut sound and light words first, never speed, force or consequence words
- s3#2: segment 2 shot 2 is 57 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#2: segment 2 request has 290 direction words (cap 240, quoted narration not counted): references 45, shots 164, sound 14, voice 20, fixed 47; cut sound and light words first, never speed, force or consequence words

## Narration across attempts

**#0:** From up here, those people look tiny, don't they? / My skeleton is twenty-five point two metres long. / I wasn't yet fully grown. / My youth wasn't enough to escape the shallows. / I'm the only blue whale skeleton hung diving.

**#1:** My skeleton is twenty-five point two metres long. / And I wasn't yet fully grown. / My youth wasn't enough to escape the shallows. / I'm the only blue whale skeleton in a diving lunge.

**#2:** My skeleton is twenty-five point two metres long. / And I wasn't yet fully grown. / My youth wasn't enough to escape the shallows. / I'm the only blue whale skeleton in a diving lunge.

