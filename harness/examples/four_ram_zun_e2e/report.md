# You Framed My Rams

*The zun notices the visitor photographing its flawless-looking ram head and tells them that this same vessel was destroyed by bomb attacks during the war.*

**Status: NEEDS_HUMAN** · chosen attempt #2

Run `1114-200829-photo-e2e` · exhibit `adhoc-four-ram-square-zun` · photo `four_ram_zun.webp` · model `claude-opus-5-5` · new spend $2.08

Prompts: keywords.md@bc94ebc2, s0_identify.md@025d7a76, s0b_research.md@63222915, s1_digest.md@7733405d, s1b_assets.md@31f0df76, s2_concept.md@6ab0de52, s3_script.md@becae034, s4_review.md@58db8f8d

User input: (none)

## Attempts

| # | checks | blocking | polish | truth | min score | sum | words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2 | 2 | 5 | 3 | 43 | 29 |
| 1 | 1 | 1 | 2 | 5 | 3 | 44 | 24 |
| 2 ✅ | 0 | 0 | 2 | 5 | 3 | 44 | 24 |

## S0 What the photo shows

- **Recognised as:** The Four-Ram Square Zun, a Late Shang dynasty bronze ritual wine vessel with four curled-horn ram foreparts projecting from its corners, a flaring square mouth and a flanged square foot. The label at the bottom reads 四羊青铜方尊, and it is displayed in the National Museum of China, Beijing. → `` (high)
- **Visible:** The whole vessel fills the frame from the flared mouth down to the base on its white plinth. It is shot from slightly below eye level, angled onto one corner, so a ram head with curled horns faces the camera at the centre and two other rams jut out in profile to the left and right. It is close up through the display-case glass under warm, dim gallery light, with spotlights dotting the dark ceiling above. The glass reflects other visitors, including a woman holding up a phone and a figure on the left; they appear life-size behind the vessel, which is roughly half a metre tall. The corner of the Chinese label is visible at the bottom left.
- **Visitor interest:** The visitor framed the ram heads head-on, which suggests they are fascinated by how the sculpted rams with their curling horns are fused into the vessel and how such intricate bronze was made.

## Progress keywords (separate side requests)

**identify** (at 5.1s): Four-Ram Square Zun · 四羊青铜方尊 · Late Shang dynasty · bronze · ritual wine vessel · curled-horn ram foreparts · flaring square mouth · flanged square foot · National Museum of China, Beijing
**research** (at 87.1s): Four-goat Square Zun · late Shang Dynasty · Ningxiang County, Hunan Province · April 1938 · largest bronze fang zun · Jiang Jingshu · Tanheli site · 400 silver dollars · sacrificial ceremonies

## S0b Web research

I ran three searches: the English object name with the National Museum of China, the Chinese name with size, weight and find-place terms, and the 1938 Ningxiang discovery with casting terms. I then fetched the museum's own feature page, the China Daily article and English Wikipedia to check how big it is, how old, where it was found, why it has its name, what it was used for, how it was made and how it reached Beijing.

Tool calls:
- code_execution: `{"code": "import json\nqs=[\"Four-Ram Square Zun National Museum of China\",\"四羊方尊 中国国家博物馆 高 重 出土\",\"Siyang fangzun Ningxiang Hunan discovered 1938 casting\"]\nfor q in qs:\n    r=await web_search({\"query\":q})\n    for x in r[:6]:\n        print(x.get('url'),'|',x.get('title'))\n        print(x.get('content','')[:600].replace('\\n',' '))\n        print('--')\n    print('=====')"}`
- web_search: `{"query": "Four-Ram Square Zun National Museum of China"}`
- code_execution: `{"code": "r=await web_search({\"query\":qs[0]})\nprint(type(r), str(r)[:500])"}`
- web_search: `{"query": "Four-Ram Square Zun National Museum of China"}`
- code_execution: `{"code": "R={}\ndef show(q,r):\n    r=json.loads(r) if isinstance(r,str) else r\n    R[q]=r\n    for x in r[:6]:\n        if x.get('type')!='web_search_result': print(x);continue\n        print(x.get('url'),'|',x.get('title'))\n        print(x.get('content','')[:700].replace('\\n',' '))\n        print('--')\n    print('=====')\nshow(qs[0],r)\nfor q in qs[1:]:\n    show(q,await web_search({\"query\":q}))"}`
- web_search: `{"query": "四羊方尊 中国国家博物馆 高 重 出土"}`
- web_search: `{"query": "Siyang fangzun Ningxiang Hunan discovered 1938 casting"}`
- code_execution: `{"code": "f=await web_fetch({\"url\":\"https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html\"})\nf=json.loads(f) if isinstance(f,str) else f\nc=f[0]['content'] if isinstance(f,list) else str(f)\nprint(len(c)); print(c[:5000])"}`
- web_fetch: `{"url": "https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html"}`
- code_execution: `{"code": "for u in [\"https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html\",\"https://en.wikipedia.org/wiki/Four-goat_Square_Zun\"]:\n    f=await web_fetch({\"url\":u})\n    f=json.loads(f) if isinstance(f,str) else f\n    s=str(f)\n    i=s.find(\"'data'\")\n    print(s[i:i+5000]); print(\"=======\")"}`
- web_fetch: `{"url": "https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html"}`
- web_fetch: `{"url": "https://en.wikipedia.org/wiki/Four-goat_Square_Zun"}`
- code_execution: `{"code": "f=await web_fetch({\"url\":\"https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html\"})\ns=str(f); i=s.find(\"The *zun* vessel used in sacr\"); print(s[i:i+1500])"}`
- web_fetch: `{"url": "https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html"}`

Sources:
- 🏛 [百年国博 - 进国博，看国宝 (青铜美器——四羊方尊)](https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html) — National Museum of China
- [Bronze vessel with ram-head sculptures: masterpiece from the Shang Dynasty](https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html) — govt.chinadaily.com.cn (China Daily)
- [Four-goat Square Zun](https://en.wikipedia.org/wiki/Four-goat_Square_Zun) — Wikipedia
- [The Four-Ram Square Zun (商四羊方尊)](https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369) — Springer, Contextual Dictionary of Chinese Cultural Knowledge
- [Shang Siyang Bronze Square Zun](https://baike.baidu.com/en/item/Shang%20Siyang%20Bronze%20Square%20Zun/941638) — Baidu Baike
- [National Treasure – Bronze Zun with Four Rams (Shang Dynasty)](https://live2makan.com/2025/06/11/treasures-bronze-zun-with-four-rams-shang-dynasty/) — live2makan (blog)

Findings (verified URLs only):
- (exhibit) The zun was used in sacrificial ceremonies. It was unearthed in Ningxiang, Hunan, in 1938 and destroyed by bomb attacks during the war. — <https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html>
- (exhibit) China Daily says its patterns are a testimony to the superb bronze-casting technology of 3,000 years ago. — <https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html>
- (exhibit) Wikipedia says it was found in April 1938 by Jiang Jingshu and his brothers Jiang Jingqiao and Jiang Xiqiao of Yueshanpu, Huangcai Town, while they were digging to plant sweet potatoes on the mountain. — <https://en.wikipedia.org/wiki/Four-goat_Square_Zun>
- (exhibit) Wikipedia says the owner of the Wanlishan Shop in Huangcai Town bought it with 400 silver dollars and took it to his home. — <https://en.wikipedia.org/wiki/Four-goat_Square_Zun>
- (exhibit) Springer's reference work calls it the largest bronze fang zun (squared wine vessel) of the Shang Dynasty. — <https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369>
- (exhibit) It is generally considered a ritual sacrificial vessel of the late Shang Dynasty. — <https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369>
- (exhibit) It was excavated in 1938 on the hillside of Zhuanerlun, Yueshanpu Village, Huangcai Town, Ningxiang County, Hunan, which is now part of the Tanheli site. — <https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369>

Conflicts:
- Weight: the museum's own page says it weighs close to 34.5 kg (重量接近34.5公斤). Wikipedia gives a flat 34.5 kg, and the zh.wikipedia snippet says about 34.5 kg. The museum's wording, 'close to 34.5 kg', is safer.
- Restoration time: the museum's page says the restoration took more than two months. The live2makan blog speaks of a 'year-long restoration'. Use the museum's version: more than two months.
- Casting method: the museum's page says it was made by join-casting, with the horns and dragon heads cast first and then joined to the vessel. The Baidu Baike snippet says the whole vessel was cast in a single pour. Use the museum's account of separately cast parts.
- Date: the museum's page does not give a precise date; it says only 'three thousand years later'. China Daily gives the Shang Dynasty as c. 16th–11th century BC. Springer says 'late Shang Dynasty'. Wikipedia says '11th – 10th century BC' and 'c. 1000 BC', and the live2makan blog says 14th–11th centuries BC. It is safest to say 'late Shang dynasty, more than 3,000 years ago' and not give exact centuries.
- Who found it, and the sales to dealers (400 silver dollars, and so on), come only from Wikipedia. The museum's page says only that it was unearthed in spring 1938 and passed through several hands, so treat the named finders and sale prices as secondary-source detail.

Not found:
- What exact alloy the bronze is made of, and how much tin and lead it contains.
- Whether it was found alone or with other objects, and who buried it and why, in the archaeological context of the Tanheli site.
- Whether people today can tell where the old breaks were mended, or exactly how the 20-plus fragments were joined back together, beyond the museum's mention of more than two months of restoration.
- Whether it has an inscription identifying its owner. None of the sources found mention one.

## Final package (final.json)

- Image jobs (visitor photo + prompt): 3 (~$0.45): zun_now, detail_ram_head, zun_in_place
- Existing images used: none
- Missing images: none
- Video requests: 1 (~$1.95), image_urls: <job:zun_now>, <job:zun_in_place>, <job:detail_ram_head>

## S1 Material

**Emotional core:** The vessel in front of the visitor was destroyed by bomb attacks during the war. This suggests that an object that looks untouched by three thousand years was broken in modern times.

**Length:** 15s — The controlling idea is a single reversal: the vessel that looks intact was destroyed by bomb attacks during the war. Its spine fits in about twenty-five spoken words, and no verified exhibit fact would advance that turn in a second segment.

Facts:
- `sacrificial_use` (exhibit) The zun was used in sacrificial ceremonies.
- `unearthed_1938_ningxiang` (exhibit) It was unearthed in Ningxiang, Hunan, in 1938.
- `destroyed_bombs` (exhibit) It was destroyed by bomb attacks during the war.
- `casting_3000_years` (exhibit) China Daily says its exquisite patterns are a testimony to the superb bronze-casting technology of 3,000 years ago.
- `found_sweet_potatoes` (exhibit) According to Wikipedia, it was found in April 1938 by Jiang Jingshu and his brothers Jiang Jingqiao and Jiang Xiqiao of Yueshanpu, Huangcai Town, Ningxiang County, while they were digging to plant sweet potatoes on the mountain.
- `bought_400_silver` (exhibit) According to Wikipedia, the owner of the Wanlishan Shop in Huangcai Town bought it with 400 silver dollars and took it to his home.
- `largest_fang_zun` (exhibit) Springer's reference work calls it the largest bronze fang zun (squared wine vessel) of the Shang Dynasty.
- `late_shang_ritual` (exhibit) It is generally considered a ritual sacrificial vessel of the late Shang Dynasty.
- `hillside_tanheli` (exhibit) It was excavated in 1938 on the hillside of Zhuanerlun, Yueshanpu Village, Huangcai Town, Ningxiang County, Hunan, which is now part of the Tanheli site.

Visitor questions:
- How were these ram heads with curling horns made and joined to the vessel? → casting_3000_years
- Is it real, and has it always been in one piece like this? → destroyed_bombs
- How old is it and what was it used for? → late_shang_ritual, sacrificial_use, casting_3000_years, largest_fang_zun
- Where was it found and how did it get here? → unearthed_1938_ningxiang, hillside_tanheli, found_sweet_potatoes, bought_400_silver
- How heavy is it? → (pack cannot answer)

Conflicts:
- Weight, restoration time, casting method and the museum's account of where and how it passed through hands appear only in the research conflict notes, not in verified findings; none of them may be narrated or cited.
- Casting method: sources disagree on whether it was cast in parts or in one pour, and neither version is a verified finding. Safe wording: say nothing about how it was cast beyond China Daily's 'testimony to the superb bronze-casting technology of 3,000 years ago'.
- Date: sources range from c. 16th–11th century BC to 11th–10th century BC. Safe wording: 'late Shang Dynasty' and '3,000 years ago' (as China Daily phrases it); give no exact centuries.
- Finders' names, sweet-potato digging and the 400 silver dollars come only from Wikipedia; attribute these details as secondary.
- 1938 is the year it was unearthed, not the year it was destroyed. The sources give no year for the bombing and do not name the war; do not supply either.
- No verified finding says when, how, by whom or how long it was restored, or when or how it came to the museum; do not invent these.

**Controlling idea:** the visitor thinks *This ancient bronze has come down intact and unbroken from the Shang Dynasty.*, but actually *It was unearthed in Ningxiang, Hunan, in 1938 and destroyed by bomb attacks during the war.* [destroyed_bombs] · second half: [none] · last thought: "This vessel was once destroyed by bombs."

Through-lines:
- **Unearthed, then destroyed** ✅ lead (15s): A ritual sacrificial vessel of the late Shang Dynasty is unearthed in Ningxiang, Hunan, in 1938. → *It was destroyed by bomb attacks during the war: from a vessel that came out of the ground to a destroyed object.* → The same zun now stands in front of the visitor. This suggests that it was put back together, though no listed fact says how.
  > spine (23 words): This ritual vessel of the late Shang Dynasty was unearthed in Ningxiang in nineteen thirty-eight. Then, during the war, bomb attacks destroyed it.
- **From sacrifice to hillside** (15s): It was a ritual sacrificial vessel of the late Shang Dynasty, used in sacrificial ceremonies. → *It was excavated in 1938 on the hillside of Zhuanerlun, now part of the Tanheli site: from buried to unearthed.* → Its patterns are called a testimony to the superb bronze-casting technology of 3,000 years ago.
  > spine (22 words): It was used in sacrificial ceremonies in the late Shang Dynasty. In nineteen thirty-eight it was excavated on a hillside in Hunan.
- **From hillside to market** (15s): Brothers digging to plant sweet potatoes on the mountain found it in April 1938. → *Buried ritual vessel becomes a thing bought and sold: a shop owner bought it with 400 silver dollars.* → The shop owner took it to his home.
  > spine (26 words): In April nineteen thirty-eight, brothers digging to plant sweet potatoes found it. A shop owner bought it with four hundred silver dollars and took it home.

## S1b Reference-image plan

**Names:** the Four-Ram Square Zun / the newly cast bronze zun

**Subject lock:** Dark grey-green bronze square zun, flared square mouth with tall hooked flanges, four ram foreparts with spiralling curled horns at the corners, fine scale and spiral patterns, high square foot.

**Living form lock:** The same square zun freshly cast: polished golden-brown bronze, flared square mouth with tall hooked flanges, four ram foreparts with spiralling curled horns at the corners, crisp scale and spiral patterns, high square foot.

- **alive_restoration** (restoration) — Opening image of the vessel in its own world and period. Artistic reconstruction: the golden-brown polished colour, the timber hall and the altar setting are imagined, not known fact.
  > From this photo, show the same square bronze zun as it looked when newly cast in the late Shang Dynasty, keeping exactly its shape, proportions and corner-on viewing angle: a wide flared square mouth with tall hooked ridged flanges rising at the corners and mid-sides, a narrower neck, a bulging shoulder where four ram foreparts project from the four corners, each ram head with large horns spiralling forward and down, ram chests and bodies covered in fine scale and spiral patterns, the rams' legs merging into a high square foot with flanges. The bronze is freshly polished golden-brown with crisp sharp relief, no green corrosion. It stands alone on a low rammed-earth altar in a dim timber ritual hall with wooden posts and a reed mat floor, soft even daylight from a doorway, the vessel filling most of the frame, a faint gleam of wine at the rim.
  > avoid: No text, labels, captions, titles, watermarks, people, hands, glass cases, museum plinth, spotlights, second vessels or extra copies of the zun, no modern objects, no dramatic lighting or smoke.
- **sheet_new** (character_sheet) — Design consistency reference for the newly cast form; never sent to the video model. Golden-brown colour is artistic reconstruction.
  > From this photo, create a clean object reference sheet of the same square bronze zun as newly cast, polished golden-brown bronze with crisp relief, on a plain light grey background with even soft light. Show five views arranged in a neat grid: a straight front view of one face, a full side view, a corner-on three-quarter view with one ram head facing the viewer, a top-down view of the flared square mouth, and a low view looking up at a ram head with its spiralling curled horns. In every view keep identical proportions: wide flared square mouth with tall hooked ridged flanges, narrower neck, shoulder with four ram foreparts at the corners, fine scale and spiral patterns over the ram bodies, high square flanged foot.
  > avoid: No text, labels, numbers, captions, titles, arrows, watermarks, people, hands, glass cases, plinths, shadows of other objects, green corrosion.
- **sheet_new_side** (character_sheet) — Identity reference for shots of the newly cast vessel. Golden-brown colour is artistic reconstruction.
  > From this photo, show only a single full side view of the same square bronze zun as newly cast, standing upright and centred on a plain light grey background, even soft light, whole vessel in frame with margin. Polished golden-brown bronze with crisp relief: wide flared square mouth with tall hooked ridged flanges along the edges, narrower neck, shoulder with two ram foreparts seen in profile at the left and right corners, their horns spiralling forward and down, a third ram head facing out from the centre corner, fine scale and spiral patterns on the ram bodies, high square flanged foot below.
  > avoid: No text, labels, captions, titles, watermarks, people, hands, glass cases, plinths, other vessels, second copies of the zun, green corrosion, dramatic shadows.
- **zun_now** (subject_view) — Identity reference for the exhibit as it is now.
  > From this photo, show the same square bronze zun exactly as it is now, from the same corner-on angle with one ram head facing the camera, alone and centred on a plain light grey background, even neutral light, no glare or reflections. Dark grey-green bronze with lighter grey highlights on raised edges: wide flared square mouth with tall hooked ridged flanges, narrower neck, four ram foreparts at the shoulder corners with large horns spiralling forward and down, fine scale and spiral patterns over the ram bodies, high square flanged foot. Whole vessel in frame with margin.
  > avoid: No text, labels, captions, watermarks, people, reflections of visitors, glass case, plinth, museum ceiling lights, other objects, second copies of the zun.
- **detail_ram_head** (detail) — Detail for a close shot on the ram head and its curled horns.
  > From this photo, show a close-up of the front ram head of the same square bronze zun, filling the frame, on a plain dark-neutral background, even soft light. Dark grey-green bronze: long narrow ram face with small eyes, large ridged horns curling in spirals around each side of the head, fine scale and spiral patterns on the neck and chest below, part of the flared flanged neck visible above.
  > avoid: No text, labels, watermarks, people, reflections, glass, plinth, other objects, glare.
- **zun_in_ground** (subject_view) — State reference for the 1938 unearthing on a Hunan hillside. Artistic reconstruction of how it lay in the ground.
  > From this photo, show the same square bronze zun at the same corner-on angle and framing as the clean exhibit view, partly emerging from reddish-brown hillside earth: the lower foot buried, clumps of soil caked in the patterns and horns, dark grey-green bronze showing through dirt, the flared square mouth with tall hooked flanges and the four ram heads with spiralling horns clearly recognisable. Even overcast daylight, plain soil around it.
  > avoid: No text, labels, watermarks, people, hands, tools, glass, plinth, other objects, second copies of the zun, dramatic lighting.
- **zun_shattered** (subject_view) — State reference for the destruction by bomb attacks during the war. Artistic: how it broke and the fragment layout are not documented.
  > From this photo, show the same square bronze zun at the same corner-on angle and framing as the clean exhibit view, but broken: the dark grey-green bronze vessel cracked and split into large jagged fragments lying close together on a plain light grey ground, pieces of the flared flanged mouth, ram heads with spiralling horns and scale-patterned body sections still recognisable, the overall square layout of the vessel still readable. Even neutral light.
  > avoid: No text, labels, watermarks, people, fire, smoke, explosions, glass, plinth, other objects, dramatic lighting.
- **zun_in_place** (environment) — Reference for the final shot of the exhibit in its hall.
  > From this photo, keep the same angle and framing: the same dark grey-green square bronze zun with its flared flanged mouth and four ram heads with spiralling horns, standing on its white plinth in the dim warm gallery with small spotlights dotting the dark ceiling. Remove the glare, the reflections of visitors in the glass and the label card; the background stays softly lit and calm.
  > avoid: No readable text, label cards, signs, watermarks, visible people or reflected people, phones, glare, second copies of the zun.

## S2 Concepts

### 0. You framed my rams ✅ chosen — (e) direct address: the exhibit speaks to the visitor about the photo they just took
- **Logline:** The zun notices the visitor photographing its flawless-looking ram head and tells them that this same vessel was destroyed by bomb attacks during the war.
- **Hook:** Corner-on close view through the case glass of the front ram head with its spiralling horns. The warm gallery is dim, and the faint reflection of a visitor holding up a phone sits beside the horns. — "You photographed my ram head as if nothing had ever touched it."
- **Arc:** Admiration of a perfect ancient object, then a jolt (it came out of a Hunan hillside and was later destroyed by bombs), then a second, changed look at the same rams.
- **Ending:** The exhibit in its hall, as the visitor sees it: corner-on, the front ram head with curled horns facing the camera, two rams in profile at left and right, flared flanged mouth above, dark bronze on the white plinth under ceiling spotlights. The camera slowly settles at the visitor's own eye level. — "Look up. The rams you just photographed were once destroyed by bombs."
- **Answers:** Is it real, and has it always been in one piece like this?

### 1. Pieces, then whole — (d) one hard contrast cut between then and now
- **Logline:** The film opens on the zun as broken bronze fragments and hard-cuts to the intact vessel in the gallery, letting the visitor feel the gap between what was destroyed and what they are looking at.
- **Hook:** Large jagged fragments of dark grey-green bronze lie close together on bare grey ground: part of a flanged mouth, a ram head with a spiralling horn, a slab of scale pattern. A low, distant rumble plays, with no fire or smoke shown. — "This is what bomb attacks during the war left of me."
- **Arc:** Unease at a ruin the visitor half recognises, then a sharp cut to the whole vessel and the realisation that the ruin is the object in front of them.
- **Ending:** Hard cut to the intact zun on its white plinth in the dim gallery, corner-on with the front ram head and its curled horns facing the camera and two rams in profile at the sides. The camera holds still. — "Now look up. Same rams. Same horns."
- **Answers:** Is it real, and has it always been in one piece like this?

### 2. From the horn back — (c) start from exactly what the visitor sees now, then travel back
- **Logline:** Starting on the curled horn the visitor is looking at, the zun travels back to its ritual purpose and its hillside unearthing, then lands on the fact that bombs later destroyed it.
- **Hook:** Extreme close view of the front ram's ridged horn spiralling around its head, with dark bronze catching a thin line of gallery light. — "These horns were made for sacrificial ceremonies in the late Shang Dynasty."
- **Arc:** Curiosity about age and purpose, then the reverent world of the ritual hall, then the quiet of a turned Hunan hillside, then the shock of its destruction, then a return to the object in the case.
- **Ending:** The full vessel in its case, corner-on: flared square mouth with tall hooked flanges, the front ram head facing out, rams in profile at both corners, on the white plinth under spotlights. — "Dug from a Hunan hillside in nineteen thirty-eight, then destroyed by bombs in the war. Look again."
- **Answers:** How old is it and what was it used for?

**Why this one:** The question almost everyone in front of this vessel has is whether it really came down to us whole. Ranked first is 'Is it real, and has it always been in one piece like this?', answered by destroyed_bombs. Second is 'How old is it and what was it used for?'. The question about how the ram heads were made is only weakly answered by the facts. This visitor framed the front ram head through the glass, and a woman holding up a phone is reflected right beside it. Direct address starts from exactly that act, 'You photographed my ram head as if nothing had ever touched it.', so the opening line lands on what they just did. It then flips their assumption with one quoted fact: bomb attacks during the war destroyed it. The film ends on the same corner-on ram view they can match the moment they look up. At 15 seconds this carries the single reversal in about thirty spoken words with only one brief stop (the hillside) before the turn. The contrast cut is more striking but asks the visitor to decode a ruin cold. The travel-back concept spends too much of 15 seconds on age and purpose before reaching the idea.

## S3 Script (chosen attempt)

```
{
  "duration_s": 15,
  "style": "realistic",
  "narrator": "voiceover",
  "segments": 1,
  "shots": 3,
  "spoken_words": 24,
  "words_per_second": 1.6,
  "lines_by_kind": {
    "fact": 2,
    "visible": 0,
    "voice": 1
  },
  "assets": {
    "existing": 0,
    "generate": 3
  }
}
```

- **Style / narrator:** realistic / voiceover
- **Voice:** A man in his sixties, low grainy baritone, neutral English, slow, quietly amused.
- **Attitude:** Fond and a little wry toward the visitor who just photographed its rams. It is pleased to be admired, but it gently corrects the idea that it was never broken.
- **Music:** Sparse slow struck bronze bells, long metallic decay.
- **Subject lock:** Dark grey-green bronze square zun, flared square mouth with tall hooked flanges, four ram foreparts with spiralling curled horns at the corners, fine scale and spiral patterns, high square foot.

### Segment 1 (15.0s · Dim warm museum gallery, glass case, spotlights in dark ceiling. · refs: zun_now, zun_in_place, detail_ram_head)

| t | refs | framing / camera | action | visual |
| --- | --- | --- | --- | --- |
| 0.0–5.0 | detail_ram_head | extreme close-up through case glass, corner-on / slow push-in | A visitor's faint reflection raises a phone beside the horns. | Warm amber spotlight from above, dark blurred gallery behind. |
| 5.0–10.0 | zun_now | close-up, corner-on, slightly below eye level / slow tilt up | A thin band of spotlight glides up the bronze edges. | Deep shadow between flanges. |
| 10.0–15.0 | zun_in_place | medium wide, corner-on, visitor eye level / slow pull-back settling to stillness | Ceiling spotlights glow softly brighter above the white plinth. | Front ram facing lens, rams in profile either side. |

Narration:
- `1.0s` *voice* "You photographed my rams as if untouched." 
- `5.0s` *fact* "In nineteen thirty-eight, a Hunan hillside gave me up." [hillside_tanheli, unearthed_1938_ningxiang]
- `10.0s` *fact* "Look up. During the war, bombs destroyed me." [destroyed_bombs]

Audio: Hushed gallery room tone; sfx: one soft shutter click before the voice; music: Fading to silence by the end.
End frame: Near-still corner-on view of the zun on its white plinth at visitor eye level, ceiling spotlights steady above.

### Assets

- **zun_now** (generate, full vessel, corner-on, one ram head facing camera) — Identity reference for the middle shot rising over the bronze patterns and flanges.
  > From this photo, show the same square bronze zun exactly as it is now, from the same corner-on angle with one ram head facing the camera, alone and centred on a plain light grey background, even neutral light, no glare or reflections. Dark grey-green bronze with lighter grey highlights on raised edges: wide flared square mouth with tall hooked ridged flanges, narrower neck, four ram foreparts at the shoulder corners with large horns spiralling forward and down, fine scale and spiral patterns over the ram bodies, high square flanged foot. Whole vessel in frame with margin. No text, labels, captions, watermarks, people, reflections, glass case, plinth, other objects.
- **zun_in_place** (generate, @Image1 on its white plinth in the gallery, visitor's corner-on view) — Final shot of the exhibit in its hall from the visitor's own viewpoint.
  > From this photo, keep the same angle and framing: the same dark grey-green square bronze zun with its flared flanged mouth and four ram heads with spiralling horns, standing on its white plinth in the dim warm gallery with small spotlights dotting the dark ceiling. Remove the glare, the reflections of visitors in the glass and the label card; the background stays softly lit and calm. No readable text, label cards, signs, watermarks, people, phones, second copies of the zun.
- **detail_ram_head** (generate, front ram head and curled horns) — Hook shot: the ram head the visitor photographed, seen through the case glass.
  > From this photo, show a close-up of the front ram head of the same square bronze zun, filling the frame, on a plain dark-neutral background, even soft light. Dark grey-green bronze: long narrow ram face with small eyes, large ridged horns curling in spirals around each side of the head, fine scale and spiral patterns on the neck and chest below, part of the flared flanged neck visible above. No text, labels, watermarks, people, reflections, glass, plinth, other objects, glare.

## Seedance requests

Segment 1: `bytedance/seedance-2.0/reference-to-video` · duration 15 · 480p 16:9 · refs ['<zun_now>', '<zun_in_place>', '<detail_ram_head>'] · 228 direction words {'refs': 55, 'style': 17, 'shots': 92, 'voice': 17, 'sound': 27, 'constraint': 20} · 252 total · ~$1.95

```
References: @Image1 is the Four-Ram Square Zun (copy its shape, pose and colour exactly; ignore its background); @Image2 is @Image1 on its white plinth in the gallery, visitor's corner-on view (setting reference only: architecture, light and space); @Image3 is a close-up of front ram head and curled horns, part of the Four-Ram Square Zun (@Image1).
Style: photorealistic documentary footage, natural light. Setting: Dim warm museum gallery, glass case, spotlights in dark ceiling.
Shot 1 (@Image3): extreme close-up through case glass, corner-on, slow push-in; A visitor's faint reflection raises a phone beside the horns; warm amber spotlight from above, dark blurred gallery behind. Cut to shot 2 (@Image1): close-up, corner-on, slightly below eye level, slow tilt up; A thin band of spotlight glides up the bronze edges; deep shadow between flanges. Cut to shot 3 (@Image2): medium wide, corner-on, visitor eye level, slow pull-back settling to stillness; Ceiling spotlights glow softly brighter above the white plinth; front ram facing lens, rams in profile either side.
Voiceover, an unseen narrator, a man in his sixties, low grainy baritone, neutral English, slow, quietly amused: "You photographed my rams as if untouched." "In nineteen thirty-eight, a Hunan hillside gave me up." "Look up. During the war, bombs destroyed me."
Sound: Hushed gallery room tone; one soft shutter click before the voice. Music: Sparse slow struck bronze bells, long metallic decay, fading to silence by the end.
Keep it subtitle-free: no subtitles, captions, letters, numbers, logos or watermark anywhere. Only one Four-Ram Square Zun in any frame.
```

## S4 Review of chosen attempt

```
{"hook": 4, "visitor_view": 4, "focus": 5, "concept_fidelity": 5, "truth": 5, "counterpoint": 3, "spoken": 4, "visual_feasibility": 4, "length_fit": 5, "ending": 5}
```

Every claim is supported, the request is now within the direction-word cap, and 'bombs destroyed me' over the intact vessel at eye level is a strong, true ending. Two small fixes remain: change shot 1's reflection to 'holds a phone still' so it stops captioning line 1, and retype @Image2 so the final shot is anchored to the real zun instead of being treated as setting only.

Claim audit:
- ✅ *voice* "You photographed my rams as if untouched." — The visitor has just photographed the vessel's rams. 'As if untouched' is the narrator's wry feeling, not a historical claim. — Visitor's photo: framed corner-on with a ram head with curled horns facing the camera; the photo notes the visitor framed the ram heads head-on.
- ✅ *fact* "In nineteen thirty-eight, a Hunan hillside gave me up." — It was excavated from a hillside in Hunan in 1938. — hillside_tanheli: 'excavated in 1938 on the hillside of Zhuanerlun, Yueshanpu Village, Huangcai Town, Ningxiang County, Hunan'; unearthed_1938_ningxiang: 'unearthed in Ningxiang, Hunan, in 1938'
- ✅ *fact* "Look up. During the war, bombs destroyed me." — The vessel was destroyed by bombs during the war. No year or named war is given, and nothing is said about restoration. 'Look up' directs the visitor, who stands in front of the real object. — destroyed_bombs: 'It was destroyed by bomb attacks during the war.'

Issues:
- **polish** [segment 1 shot 1 / line 1] The reflection raising a phone acts out 'You photographed my rams', so the opening line captions its shot. This is the only thing keeping counterpoint at 3. → Change the shot 1 action to 'A visitor's faint reflection holds a phone still beside the horns.' This adds 1 word, giving 229 of 230, or 223 if the next fix is also made. The photo has already been taken, so the line now comments on a held, finished gesture instead of narrating it.
- **polish** [segment 1 request refs (@Image2, shot 3)] @Image2 contains the zun itself, but the request still labels it 'setting reference only: architecture, light and space'. Seedance may loosely redraw the vessel in the final shot, which is the one the visitor compares with the real object. → Change zun_in_place's depicts from 'environment' to an exhibit-in-place type so the compiler drops the parenthetical. The ref line should read: '@Image2 is @Image1 on its white plinth in the gallery, visitor's corner-on view.' This saves 6 direction words.

## Checks and production notes

- All hard checks pass on the chosen attempt.

Problems along the way:
- s0b: finding says 34.5, which is not in its own quote: https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html ('The vessel's body is square, with a square mouth a')
- s1#0: fact 'weight_museum' cites a source that is neither in the pack nor a verified research finding: https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html
- s1#0: fact 'weight_museum' has the number 34.5, which is in neither the pack nor the research findings
- s1#0: fact 'restoration_two_months' cites a source that is neither in the pack nor a verified research finding: https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html
- s1#0: fact 'join_casting' cites a source that is neither in the pack nor a verified research finding: https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html
- s1#0: fact 'spring_1938_hands' cites a source that is neither in the pack nor a verified research finding: https://www.chnmuseum.cn/Portals/0/web/zt/100n/guobao_content-8.html
- s3#0: segment 1 request has 305 direction words (cap 230, quoted narration not counted): references 58, shots 107, sound 77, voice 26, fixed 37; cut the largest part you control
- s3#1: segment 1 request has 232 direction words (cap 230, quoted narration not counted): references 55, shots 92, sound 31, voice 17, fixed 37; cut the largest part you control

## Narration across attempts

**#0:** You photographed my rams as if nothing had touched them. / In nineteen thirty-eight, a hillside in Hunan, China, gave me up. / Look up. During the war, bombs destroyed me.

**#1:** You photographed my rams as if untouched. / In nineteen thirty-eight, a Hunan hillside gave me up. / Look up. During the war, bombs destroyed me.

**#2:** You photographed my rams as if untouched. / In nineteen thirty-eight, a Hunan hillside gave me up. / Look up. During the war, bombs destroyed me.

