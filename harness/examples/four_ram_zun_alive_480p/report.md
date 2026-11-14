# Caught Looking

*The visitor's flash wakes the front ram, who catches them staring at his horns, flings them off in a glowing arc and catches them back into his head to show they were cast first and joined in.*

**Status: NEEDS_HUMAN** · chosen attempt #1

Run `1114-223029-photo-nopack-zun-alive` · exhibit `adhoc-four-ram-square-zun` · photo `four_ram_zun.webp` · model `claude-opus-5-5` · new spend $2.32

Prompts: keywords.md@bc94ebc2, s0_identify.md@025d7a76, s0b_research.md@63222915, s1_digest.md@7733405d, s1b_assets.md@421bb71d, s2_concept.md@2a800085, s3_script.md@eb9bbf1e, s4_review.md@6ce755ad

User input: (none)

## Attempts

| # | checks | blocking | polish | truth | min score | sum | words |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4 | 3 | 7 | 5 | 2 | 48 | 22 |
| 1 ✅ | 1 | 1 | 8 | 5 | 3 | 49 | 22 |
| 2 | 1 | 1 | 6 | 5 | 3 | 49 | 22 |

## S0 What the photo shows

- **Recognised as:** The Siyang Fangzun (Four-Ram Square Zun), a late Shang dynasty bronze ritual wine vessel with four curly-horned rams projecting from its shoulders and flaring square mouth with flanges; the label reads 四羊青铜方尊. It is held by the National Museum of China in Beijing. → `` (high)
- **Visible:** The whole vessel in a glass case on a white plinth, shot head-on at roughly eye level from close range, slightly below the rim so the flaring square mouth looms above. One ram's head with spiralling horns faces the camera directly, with two more rams projecting left and right; the scale and spiral surface patterns gleam silvery-grey under spotlights. The corner of the Chinese label is at bottom left. Reflections in the glass show other visitors, including one holding up a phone, superimposed behind the vessel, and ceiling spotlights reflect as bright dots across the dark background.
- **Visitor interest:** The head-on framing centred on the ram's face and horns suggests the visitor is curious about how the rams were sculpted into the vessel and what the intricate cast decoration means.

## Progress keywords (separate side requests)

**identify** (at 12.0s): Siyang Fangzun · Four-Ram Square Zun · late Shang dynasty · bronze · ritual wine vessel · four curly-horned rams · flaring square mouth · National Museum of China · 四羊青铜方尊
**research** (at 88.9s): Four-goat Square Zun · Late Shang (1300–1046 BC) · Ningxiang County · April 1938 · National Museum of China · 58.3cm · 34.5 kg · rams' heads with curly horns · Piece mold casting technique · Jiang Jingshu

## S0b Web research

I ran three searches and one fetch to find where the Four-Ram Square Zun was found, how it reached the National Museum of China, its date and size, how the rams were cast and what the decoration is. Further searches hit a tool limit, and I never reached the museum's own collection page.

Tool calls:
- code_execution: `{"code": "import json\nqs=[\"Four-Ram Square Zun National Museum of China\",\"四羊方尊 中国国家博物馆 高 重 出土 宁乡\",\"Siyang fangzun Ningxiang 1938 bronze casting rams\"]\nfor q in qs:\n    r=await web_search({\"query\":q})\n    for x in r[:6]:\n        print(x.get('url'),'|',x.get('title'),'|',x.get('content','')[:500].replace('\\n',' '))\n    print('---')"}`
- web_search: `{"query": "Four-Ram Square Zun National Museum of China"}`
- code_execution: `{"code": "r=await web_search({\"query\":qs[0]})\nprint(type(r), str(r)[:1500])"}`
- web_search: `{"query": "Four-Ram Square Zun National Museum of China"}`
- code_execution: `{"code": "for q in qs:\n    r=json.loads(await web_search({\"query\":q}))\n    for x in r[:6]:\n        print(x.get('url'),'|',x.get('title'),'|',x.get('content','')[:700].replace('\\n',' '))\n    print('---')"}`
- web_search: `{"query": "Four-Ram Square Zun National Museum of China"}`
- web_search: `{"query": "四羊方尊 中国国家博物馆 高 重 出土 宁乡"}`
- web_search: `{"query": "Siyang fangzun Ningxiang 1938 bronze casting rams"}`
- code_execution: `{"code": "r=json.loads(await web_search({\"query\":\"chnmuseum.cn 四羊青铜方尊\"}))\nfor x in r[:6]:\n    print(x.get('url'),'|',x.get('title'),'|',x.get('content','')[:1200].replace('\\n',' '))\nf=await web_fetch({\"url\":\"https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html\"})\nprint(json.loads(f) if isinstance(f,str) else f)"}`
- code_execution: `{"code": "f=await web_fetch({\"url\":\"http://www.china.org.cn/top10/2012-08/24/content_26326351_8.htm\"})\nprint(str(f)[:3000])"}`
- web_fetch: `{"url": "http://www.china.org.cn/top10/2012-08/24/content_26326351_8.htm"}`

Sources:
- [Top 10 masterpieces inside the National Museum of China - China.org.cn](http://www.china.org.cn/top10/2012-08/24/content_26326351_8.htm) — China.org.cn
- [Bronze vessel with ram-head sculptures: masterpiece from the Shang Dynasty](https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html) — China Daily
- [四羊方尊 - 维基百科](https://zh.wikipedia.org/zh-hans/%E5%9B%9B%E7%BE%8A%E6%96%B9%E5%B0%8A) — Wikipedia (Chinese)
- [Four-goat Square Zun](https://en.wikipedia.org/wiki/Four-goat_Square_Zun) — Wikipedia
- [Shang Siyang Bronze Square Zun](https://baike.baidu.com/en/item/Shang%20Siyang%20Bronze%20Square%20Zun/941638) — Baidu Baike
- [The Four-Ram Square Zun (商四羊方尊)](https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369) — Springer, Contextual Dictionary of Chinese Cultural Knowledge
- [中国国家博物馆镇馆之宝——四羊方尊](http://wenwuchina.com/a/203/201295.html) — 中国文物网
- [四羊方尊 宁乡出土毋庸置疑](https://wap.ningxiangnews.cn/content/2012/09/04/5674647.html) — 宁乡新闻网 (Red Net)
- [学者称四羊方尊原出土于河北 后被带入宁乡埋藏](https://www.chinanews.com.cn/cul/2012/09-03/4153515.shtml) — 中新网 (China News Service)
- [National Treasure – Bronze Zun with Four Rams (Shang Dynasty)](https://live2makan.com/2025/06/11/treasures-bronze-zun-with-four-rams-shang-dynasty/) — live2makan (blog)
- [A Technical Study of the Double-ram Zun Ancient Chinese Bronze Vessel in the British Museum](https://www.researchgate.net/publication/287968320_A_Technical_Study_of_the_Double-ram_Zun_Ancient_Chinese_Bronze_Vessel_in_the_British_Museum) — ResearchGate

Findings (verified URLs only):
- (exhibit) The vessel was excavated in spring 1938 from Ningxiang County in Hunan Province. It is named after the rams' heads with curly horns on the shoulders of its four corners. — <http://www.china.org.cn/top10/2012-08/24/content_26326351_8.htm>
- (exhibit) China.org.cn lists the height as 58.3 cm, the mouth as 52.4 cm and the weight as 34.5 kg, and dates it to the Late Shang (1300–1046 BC). — <http://www.china.org.cn/top10/2012-08/24/content_26326351_8.htm>
- (exhibit) The zun with four ram-head sculptures was unearthed in Ningxiang, Hunan province, in 1938. It is now in the permanent collection of the National Museum of China. — <https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html>
- (exhibit) China Daily calls the zun a wine vessel and dates it to the Shang Dynasty (c.16th century–11th century BC). — <https://govt.chinadaily.com.cn/s/202206/06/WS629d9cd4498e6a12c122e1df/bronze-vessel-with-ram-head-sculptures-masterpiece-from-the-shang-dynasty.html>
- (exhibit) Chinese Wikipedia gives a height of 58.3 cm and a weight of about 34.5 kg. Each of the four shoulder corners has a ram's head with curled horns. — <https://zh.wikipedia.org/zh-hans/%E5%9B%9B%E7%BE%8A%E6%96%B9%E5%B0%8A>
- (exhibit) Chinese Wikipedia says the ram horns were cast first and then joined in when the moulds were assembled and poured. The skill was so high that the joins are hard to see and the piece looks like one whole. — <https://zh.wikipedia.org/zh-hans/%E5%9B%9B%E7%BE%8A%E6%96%B9%E5%B0%8A>
- (exhibit) The whole vessel is covered in elaborate decoration: phoenix-bird patterns, beast-face patterns, banana-leaf patterns and cloud-and-thunder patterns. — <https://zh.wikipedia.org/zh-hans/%E5%9B%9B%E7%BE%8A%E6%96%B9%E5%B0%8A>
- (exhibit) Baidu Baike says the ram horns and dragon heads were cast separately first. They were then placed in the outer mould before the whole vessel was cast. — <https://baike.baidu.com/en/item/Shang%20Siyang%20Bronze%20Square%20Zun/941638>
- (exhibit) Baidu Baike says the whole vessel was cast in a single pour using the piece-mould technique. — <https://baike.baidu.com/en/item/Shang%20Siyang%20Bronze%20Square%20Zun/941638>
- (exhibit) English Wikipedia says four entwining dragons in high relief sit on the zun's shoulders. — <https://en.wikipedia.org/wiki/Four-goat_Square_Zun>
- (exhibit) A Springer reference dictionary calls it the largest bronze fang zun (square wine vessel) of the Shang Dynasty. It says the zun was excavated in 1938 on the hillside of Zhuanerlun, Yueshanpu Village, Huangcai Town, Ningxiang County, Hunan Province. — <https://link.springer.com/rwe/10.1007/978-981-99-5009-6_10369>
- (exhibit) One morning in April 1938, the brothers Jiang Jingshu, Jiang Jingqiao and Jiang Xiqiao were clearing land halfway up Zhuanerlun hill in Huangcai Town, Ningxiang, to plant sweet potatoes. — <http://wenwuchina.com/a/203/201295.html>
- (exhibit) While examining the find, the brothers accidentally knocked a palm-sized fragment off the vessel's rim. — <http://wenwuchina.com/a/203/201295.html>
- (exhibit) In May 1938, the Huangcai antique dealer Zhang Wanli bought the zun for 400 silver dollars. — <https://wap.ningxiangnews.cn/content/2012/09/04/5674647.html>
- (exhibit) Zhang Wanli passed the zun on to Changsha. The government soon confiscated it and gave it to the Hunan Provincial Bank of the time for safekeeping. — <https://wap.ningxiangnews.cn/content/2012/09/04/5674647.html>
- (exhibit) Jiang Jingshu later handed the fragment to the Hunan Provincial Museum, which still holds it. — <https://wap.ningxiangnews.cn/content/2012/09/04/5674647.html>
- (exhibit) A blog says the zun was transferred to the National Museum of China in 1959 and remains there today. — <https://live2makan.com/2025/06/11/treasures-bronze-zun-with-four-rams-shang-dynasty/>
- (context) People from Guangzong (in Hebei) believe the zun was dug up in Guangzong in 1933 and later moved to Hunan. — <https://www.chinanews.com.cn/cul/2012/09-03/4153515.shtml>
- (context) A technical study of the British Museum's Double-ram Zun notes a four-ram zun found at Ningxiang in 1938, now in the National Museum of China. It says that zun may have been studied, but no detailed information was available. — <https://www.researchgate.net/publication/287968320_A_Technical_Study_of_the_Double-ram_Zun_Ancient_Chinese_Bronze_Vessel_in_the_British_Museum>

Conflicts:
- Date: China Daily says Shang Dynasty, c.16th–11th century BC. China.org.cn says Late Shang (1300–1046 BC), and a blog quoting a label says c. 14th–11th century BC. The narrower 'late Shang' date is safer, and it matches the vessel's own label.
- Weight: China.org.cn gives exactly 34.5 kg, while Chinese Wikipedia says about (约) 34.5 kg and wenwuchina says nearly (近) 34.5 kg. Keep 'about 34.5 kg'.
- Find-spot: Hebei scholars, reported by China News Service in 2012, claim it was first dug up in Guangzong, Hebei, in 1933 and later taken to Ningxiang. Ningxiang's cultural relics bureau rejects this. The Ningxiang 1938 find-spot is the mainstream account and the safer one; the Guangzong claim should be presented only as a minority view.
- Shoulder decoration: English Wikipedia describes four dragons in high relief, and Baidu says the dragon heads were cast separately. Chinese Wikipedia mentions only the ram heads on the shoulders. These can be combined only cautiously, because none of these sources is the museum's own page.
- Holding museum: I never reached the National Museum of China's own collection page. Every fact here comes from secondary sources.

Not found:
- The National Museum of China's own collection record for the zun, including its official date, dimensions and inventory number
- What the ram motif and the patterns (beast-face, phoenix, cloud-and-thunder) meant to the Shang, according to an authoritative source
- Who made it, where it was cast, and exactly what ceremony it was used in
- Details of any wartime damage and restoration, and of the 1959 transfer, from an official source
- Whether it is on the list of cultural relics banned from leaving China for exhibition; I saw this only as a heading on Chinese Wikipedia

## Final package (final.json)

- Image jobs (visitor photo + prompt): 3 (~$0.45): zun_now, hall_inplace, ram_awake
- Existing images used: none
- Missing images: none
- Video requests: 1 (~$2.1), image_urls: <job:zun_now>, <job:hall_inplace>, <job:ram_awake>

## S1 Material

**Emotional core:** The curling horns that look carved out of the body were in fact cast first and joined into the vessel so skilfully that the joins are hard to see. This suggests the visitor is looking at a single moment of pouring that has held separate parts together for three thousand years of being read as one.

**Length:** 15s — The film rests on one turn: the seamless horns were cast first and joined in during the pour, which the spine tells in under thirty words. No further exhibit fact advances that turn, so a second segment would only add an unrelated chronology.

Facts:
- `excavated_spring_1938` (exhibit) The vessel was excavated in spring 1938 from Ningxiang County in Hunan Province.
- `named_for_rams` (exhibit) It is named after the rams' heads with curly horns on the shoulders of its four corners.
- `height` (exhibit) Its height is 58.3 cm.
- `mouth` (exhibit) Its mouth is 52.4 cm.
- `weight` (exhibit) It weighs about 34.5 kg.
- `date_late_shang` (exhibit) It dates to the Late Shang (1300–1046 BC).
- `wine_vessel` (exhibit) The zun is a wine vessel.
- `nmc_permanent` (exhibit) It is now in the permanent collection of the National Museum of China.
- `horns_cast_first` (exhibit) The ram horns were cast first and then joined in when the moulds were assembled and poured.
- `joins_hard_to_see` (exhibit) The skill was so high that the joins are hard to see and the piece looks like one whole.
- `decoration` (exhibit) The whole vessel is covered in elaborate decoration: phoenix-bird patterns, beast-face patterns, banana-leaf patterns and cloud-and-thunder patterns.
- `parts_in_outer_mould` (exhibit) The ram horns and dragon heads were cast separately first, then placed in the outer mould before the whole vessel was cast.
- `single_pour` (exhibit) The whole vessel was cast in a single pour using the piece-mould technique.
- `dragons_relief` (exhibit) Four entwining dragons in high relief sit on the zun's shoulders.
- `largest_fang_zun` (exhibit) It is called the largest bronze fang zun (square wine vessel) of the Shang Dynasty.
- `zhuanerlun_hillside` (exhibit) It was excavated in 1938 on the hillside of Zhuanerlun, Yueshanpu Village, Huangcai Town, Ningxiang County, Hunan Province.
- `brothers_sweet_potatoes` (exhibit) One morning in April 1938, the brothers Jiang Jingshu, Jiang Jingqiao and Jiang Xiqiao were clearing land halfway up Zhuanerlun hill in Huangcai Town, Ningxiang, to plant sweet potatoes.
- `rim_fragment_knocked` (exhibit) While examining the find, the brothers accidentally knocked a palm-sized fragment off the vessel's rim.
- `sold_400_silver` (exhibit) In May 1938, the Huangcai antique dealer Zhang Wanli bought the zun for 400 silver dollars.
- `confiscated_bank` (exhibit) Zhang Wanli passed the zun on to Changsha; the government soon confiscated it and gave it to the Hunan Provincial Bank of the time for safekeeping.
- `fragment_in_hunan_museum` (exhibit) Jiang Jingshu later handed the fragment to the Hunan Provincial Museum, which still holds it.
- `transfer_1959` (exhibit) A blog says the zun was transferred to the National Museum of China in 1959 and remains there today.
- `guangzong_claim` (context) People from Guangzong (in Hebei) believe the zun was dug up in Guangzong in 1933 and later moved to Hunan.
- `no_detailed_study` (context) A technical study of the British Museum's Double-ram Zun says the four-ram zun found at Ningxiang in 1938 may have been studied, but no detailed information was available.

Visitor questions:
- How were these rams and their curling horns made as part of the vessel? → horns_cast_first, parts_in_outer_mould, single_pour, joins_hard_to_see
- What do the patterns all over it mean? → decoration
- What was it used for? → wine_vessel
- How old and how big is it? → date_late_shang, height, mouth, weight, largest_fang_zun
- Where was it found and how did it get to this museum? → brothers_sweet_potatoes, zhuanerlun_hillside, rim_fragment_knocked, sold_400_silver, confiscated_bank, transfer_1959, nmc_permanent

Conflicts:
- Date: China Daily says Shang Dynasty, c.16th–11th century BC; China.org.cn says Late Shang (1300–1046 BC). Safe wording: 'Late Shang'.
- Weight: China.org.cn gives 34.5 kg exactly; Chinese Wikipedia says about 34.5 kg. Safe wording: 'about 34.5 kg'.
- Find-spot: Guangzong (Hebei) people claim it was dug up there in 1933 and later moved to Hunan; Ningxiang's cultural relics bureau rejects this. Safe wording: excavated at Ningxiang in 1938; the Guangzong claim is only a minority view and should not be narrated as fact.
- Shoulder dragons: only English Wikipedia (dragons in high relief) and Baidu (dragon heads cast separately) mention dragons; Chinese Wikipedia mentions only the rams. Safe to speak only of the ram horns being cast first.
- Casting sources differ in detail: Chinese Wikipedia says horns were cast first and joined in when moulds were assembled; Baidu says horns and dragon heads were placed in the outer mould and the whole cast in a single pour. Safe wording: 'the horns were cast first, then joined in when the vessel was cast'.
- No source is the National Museum of China's own page; all facts are secondary. 'Largest bronze fang zun of the Shang' rests on one Springer dictionary entry only.
- Easily confused dates: April 1938 is when the brothers were clearing land on the hill; May 1938 is when the dealer bought it for 400 silver dollars; 1959 is the transfer to the National Museum of China (blog source only). Do not attach the 400 silver dollars to the find, or 1959 to the excavation.
- The rim fragment is held by the Hunan Provincial Museum, not the National Museum of China; no source says whether the rim on display was restored.

**Controlling idea:** the visitor thinks *The rams and their curling horns were sculpted out of one solid piece of bronze.*, but actually *The ram horns were cast first and then joined in when the moulds were assembled and poured; the joins are hard to see and the piece looks like one whole.* [horns_cast_first, joins_hard_to_see, parts_in_outer_mould] · second half: [none] · last thought: "Those horns were cast first, then joined in."

Through-lines:
- **Horns that were cast before the vessel** ✅ lead (15s): Four rams with curling horns seem to grow seamlessly out of the bronze. → *The horns were cast first, on their own, then set into the mould before the whole vessel was cast.* → The joins are so hard to see that the piece looks like one whole.
  > spine (30 words): These curling horns were cast first. Then they went into the mould, and the whole vessel was cast. The joins are so hard to see it looks like one whole.
- **From a sweet-potato hillside to the national collection** (30s): In April nineteen thirty-eight three brothers were clearing a Ningxiang hillside to plant sweet potatoes. → *The vessel became a thing sold, confiscated and kept by a bank, and then a national treasure in Beijing.* → It is now in the permanent collection of the National Museum of China.
  > spine (52 words): In April nineteen thirty-eight, three brothers were clearing a hillside in Ningxiang to plant sweet potatoes. In May, a dealer bought the zun for four hundred silver dollars. The government soon confiscated it and gave it to a bank for safekeeping. In nineteen fifty-nine it came to the National Museum of China.
- **A piece of the rim in another museum** (15s): Examining the find, the brothers accidentally knocked a palm-sized fragment off its rim. → *The fragment went one way, to the Hunan Provincial Museum; the vessel went another, to Beijing.* → The Hunan Provincial Museum still holds the fragment, while the vessel is in the National Museum of China.
  > spine (31 words): Examining it, the brothers knocked a palm-sized piece off its rim. That piece is still held by the Hunan Provincial Museum. The vessel is here, in the National Museum of China.

## S1b Reference-image plan

**Names:** the Four-Ram Square Zun / the bronze ram

**Subject lock:** A dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned.

**Living form lock:** A stylized cartoon bronze ram, dark grey-black bronze with silvery-grey patina, thick spiralling ridged horns, scale-patterned chest, cloud-and-thunder spirals on flanks, large expressive dark eyes.

- **zun_now** (subject_view) — Identity anchor for the exhibit's exact shape, colours and markings in every shot.
  > From this photo, show the Four-Ram Square Zun alone at the same slightly-low three-quarter angle, the front ram head facing the viewer, on a plain seamless light grey background in even, soft, neutral studio light with all glare and reflections removed. A dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned. The tall flaring neck carries long banana-leaf blade panels edged by notched ridged flanges; the bulging shoulder holds four ram heads projecting from the corners, each with thick spiralling ridged horns curling forward around the ears, long snouts, and chests covered in overlapping scale pattern; the belly panels are filled with fine cloud-and-thunder spirals and beast-face patterns in silvery-grey relief on near-black ground; the square foot below has notched flanges, ram hooves in relief and banana-leaf panels. The whole vessel is fully visible, centred, sharp, with a soft contact shadow only.
  > avoid: text, labels, captions, watermarks, people, reflections of visitors or phones, glass case, glass reflections, spotlights, plinth, museum label card, second copies of the vessel, colour shifts to gold or green
- **hall_inplace** (in_place) — Reference for the exhibit in its hall and for the final return shot.
  > From this photo, keep the same angle and framing: the Four-Ram Square Zun standing on its white plinth in the dim National Museum gallery, a dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned. Clean the image: remove every visitor and every reflection of people and phones, remove all glare and spotlight reflections on the glass so no glass is visible, remove the label card and any readable text. The background is an empty, softly lit warm-beige gallery wall and dark ceiling with a few distant display cases, no one present. The vessel keeps exactly its shape, its silvery-grey relief patterns and the front ram head facing the viewer, lit by a gentle top spotlight.
  > avoid: people, faces, figures, reflections of people or phones, glass reflections, glare, label card, signs, readable text, watermarks, second copies of the vessel
- **ram_awake** (living_form) — Character reference for the front ram that comes alive, keeping the exhibit's bronze identity.
  > From this photo, design the front ram of the vessel as a stylized animated character: a stylized cartoon bronze ram, dark grey-black bronze with silvery-grey patina, thick spiralling ridged horns, scale-patterned chest, cloud-and-thunder spirals on flanks, large expressive dark eyes. A full-bodied, sturdy little ram standing on four hooves in three-quarter view, head slightly raised with a curious, proud, friendly expression and a soft closed smile; its horns curl forward around the ears exactly like the vessel's ram heads, with the same ridged spiral; its long snout, chest of overlapping scale pattern and flank panels of fine cloud-and-thunder spirals and banana-leaf motifs are rendered in silvery-grey relief on near-black bronze, matching the vessel's surface, now flexible like a living animal. Plain light grey background, even soft light, the ram alone, fully visible and centred.
  > avoid: text, labels, captions, watermarks, people, the vessel, other rams, glass case, multiple poses, expression grids, extra horns, gold or green colouring, fluffy wool

## S2 Concepts

### 0. Caught Looking ✅ chosen — character / (C) IT NOTICES YOU, with one beat of (D) MATERIAL MAGIC; lines ordered as reveal
- **Logline:** The visitor's flash wakes the front ram, who catches them staring at his horns, flings them off in a glowing arc and catches them back into his head to show they were cast first and joined in.
- **Hero:** the front ram wants Show off his horns · first sign: Flash pops and the front ram's eye blinks, then his ear flicks, by 2 s. · big move: The ram whips his head hard and both horns fly off in a fast, glowing arc, spinning above him; he snaps his head up and they slam back onto his skull with a ringing bronze clang, a ripple of molten light sealing the base and setting dark.
- **Spectacle shot:** Two glowing bronze spiral horns spinning in the air above a bare-headed bronze ram, a beat before they crash back onto his head.  · return trace: A faint silvery glint runs once around the base of each horn on the still vessel and fades into the patina, leaving no visible seam.
- **Hook:** The vessel in its dim case at the visitor's own low angle, front ram facing the lens; a camera flash pops white across the bronze, and the ram's bronze eye blinks once. — "Flash? You're staring at my horns, aren't you."
- **Arc:** Startle and amusement (the bronze is awake and has noticed me) to surprise (the horns were a separate piece) to playful challenge (now I want to look for the join myself).
- **Ending:** The real Four-Ram Square Zun, still and whole, at the visitor's slightly low head-on angle, front ram facing the camera with both horns in their spiral, spotlights glinting on the scale pattern. — "Find the join. Hard, isn't it?"
- **Answers:** How were these rams and their curling horns made as part of the vessel?

### 1. Horns Go First — character / (B) ESCAPE AND RETURN; lines ordered as decisive moment
- **Logline:** The front ram bolts out of the vessel and gallops the empty gallery, then races home where his horns lock into place first and the rest of him slams in after, ending the exhibit whole.
- **Hero:** the front ram wants Get back in time · first sign: The front ram's horns twitch and rotate a little on their own at 2 s. · big move: The ram sprints back across the dark gallery at full gallop, hooves clanging, leaps, and his horns shoot ahead and lock into the shoulder with a hard metallic clack before his body thuds in behind them, shaking the vessel on its plinth.
- **Spectacle shot:** A bronze ram mid-leap toward the vessel, his spiral horns flying a beat ahead of him into the empty shoulder.  · return trace: The vessel gives one last tiny settle on the plinth; a thin line of light around the horn bases dims to nothing.
- **Hook:** Close on the front ram's head on the vessel; its spiral horns twitch and turn by themselves before the face moves. — "Watch the horns. They always go first."
- **Arc:** Curiosity to thrill of the chase to satisfying click of everything locking back, then quiet admiration of the seamless result.
- **Ending:** The real vessel whole on its white plinth at the visitor's head-on angle, front ram facing the lens, horns curling forward. — "Looks like one piece. It isn't."
- **Answers:** How were these rams and their curling horns made as part of the vessel?

### 2. Liquid Horns — awaken / (D) MATERIAL MAGIC; lines ordered as reveal
- **Logline:** The front ram's horns wake in place, melt into glowing ribbons of bronze, uncoil, then recoil and set into their spiral so seamlessly the visitor can't find where they meet.
- **Hero:** the front ram's horns wants Prove they're separate · first sign: The horn tip glows orange and a drop of light runs along its ridges by 2 s. · big move: The glowing horns uncoil fast into two liquid-bronze ribbons that whip outward, then snap back into a tight spiral and set with a hiss of steam, the glow draining into the body.
- **Spectacle shot:** Two ribbons of molten bronze whipping out from a ram's head and coiling back into perfect spirals.  · return trace: A wisp of steam curls off the horn and vanishes; the horn is dark and seamless.
- **Hook:** Macro on one curling horn of the front ram; the ridged bronze begins to glow orange from the tip inward. — "These horns weren't carved out of me."
- **Arc:** Wonder at the impossible glow to understanding (separate piece, joined in casting) to a hushed sense of skill.
- **Ending:** The real vessel at the visitor's angle, the front ram's horns dark and still in their spiral under the spotlights. — "Those horns were cast first, then joined in."
- **Answers:** How were these rams and their curling horns made as part of the vessel?

**Why this one:** Caught Looking makes the ram a real character who reacts to the visitor's own flash, so the film feels like a reply to their photo, and its spectacle beat, horns flying off and clanging back on, acts out the hidden fact that the horns were a separate piece joined in. The lines answer the top question in a few short breaths using only the casting facts. It renders as one character, one transformation per shot and a single camera move each time. When the visitor looks up, they will search the base of the real horns for a seam, find none, and see that ram as both a joke they shared and a feat of casting.

## S3 Script (chosen attempt)

```
{
  "duration_s": 15,
  "mode": "character",
  "hero_mover": "the front ram",
  "act_shots": [
    "1.3"
  ],
  "force_words": 7,
  "style": "stylized",
  "narrator": "voiceover",
  "segments": 1,
  "shots": 4,
  "spoken_words": 22,
  "words_per_second": 1.47,
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

- **Mode / hero:** character / the front ram (wants Show off his horns); still: the other three rams and the rest of the vessel
- **Look:** stylized 3D animated feature, soft rim light, gallery at night · style stylized · narrator voiceover
- **Voice:** A spry middle-aged male voice, warm deep bronze-toned baritone with a dry teasing edge, neutral English accent, quick playful pace.
- **Attitude:** Amused and flattered to be caught being stared at; teases the visitor like a show-off who knows his best trick.
- **Music:** no music
- **Subject lock:** A dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned.

### Segment 1 (15.0s · The empty gallery after hours, the zun on its white plinth under one top spotlight · refs: zun_now, hall_inplace, ram_awake)

| t | refs | framing / camera | action | visual |
| --- | --- | --- | --- | --- |
| 0.0–3.0 **still** | zun_now, hall_inplace | cut → medium, slightly low head-on, front ram centred / slow push-in, ending at chest height | A white flash pops across the bronze; at two seconds the front ram's eye blinks once, then one ear flicks sharply. |  |
| 3.0–7.0 **stir** | zun_now, ram_awake | cut → close-up on the front ram at the vessel corner / slow push-in | He strains forward hard and locks his eyes on camera. ⟶ rigid ram head -> softens and flows outward over four seconds, neck and forelegs pulling free -> front half leans out of the corner |  |
| 7.0–11.0 **act** | ram_awake, hall_inplace | cut → low wide across the plinth top / locked off | The ram leaps down heavily onto the plinth, whips his head hard; both horns fly off glowing and spin overhead; he snaps his head up and they slam back on, sparks skittering across the plinth. |  |
| 11.0–15.0 **return** | hall_inplace, zun_now | match cut on the horn spiral → medium, the visitor's slightly low head-on angle / locked off | The vessel stands whole and still; a faint silvery glint runs once around each horn base and fades. |  |

Narration:
- `1.0s` *voice* "You're staring at my horns, aren't you?" 
- `3.9s` *fact* "My horns were cast first, then joined in." [horns_cast_first]
- `11.3s` *fact* "Find the join; it's hard to see." [joins_hard_to_see]

Audio: gallery hum; sfx: shutter click, bronze grinding, hooves thud, ringing clang, molten hiss; music: No music.
End frame: The still Four-Ram Square Zun at the visitor's slightly low head-on angle, front ram facing the camera, horns in their spiral, the glint faded.

### Assets

- **zun_now** (generate, the zun, exact shape and decoration) — Identity anchor for the exhibit's exact shape, colours and markings in every shot.
  > From this photo, show the Four-Ram Square Zun alone at the same slightly-low three-quarter angle, the front ram head facing the viewer, on a plain seamless light grey background in even, soft, neutral studio light with all glare and reflections removed. A dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned. The tall flaring neck carries long banana-leaf blade panels edged by notched ridged flanges; the bulging shoulder holds four ram heads projecting from the corners, each with thick spiralling ridged horns curling forward around the ears, long snouts, and chests covered in overlapping scale pattern; the belly panels are filled with fine cloud-and-thunder spirals and beast-face patterns in silvery-grey relief on near-black ground; the square foot below has notched flanges, ram hooves in relief and banana-leaf panels. The whole vessel is fully visible, centred, sharp, with a soft contact shadow only. No text, labels, watermarks, people, glass case, reflections, spotlights, plinth or label card; no gold or green colour shift.
- **hall_inplace** (generate, setting and final angle) — Reference for the exhibit in its hall and for the final return shot.
  > From this photo, keep the same angle and framing: the Four-Ram Square Zun standing on its white plinth in the dim gallery, a dark grey-black Shang bronze square wine vessel with silvery-grey patina, flaring square mouth with hooked ridged flanges, four curly-horned ram heads at shoulder corners, densely patterned. Remove every visitor and every reflection of people and phones, remove all glare and spotlight reflections so no glass is visible, remove the label card and any readable text. The background is an empty, softly lit warm-beige gallery wall and dark ceiling with a few distant display cases, no one present. The vessel keeps exactly its shape, its silvery-grey relief patterns and the front ram head facing the viewer, lit by a gentle top spotlight. No people, faces, signs, text or watermarks.
- **ram_awake** (generate, the front ram character) — Character reference for the front ram that comes alive, keeping the exhibit's bronze identity.
  > From this photo, design the front ram of the vessel as a stylized animated character: a stylized cartoon bronze ram, dark grey-black bronze with silvery-grey patina, thick spiralling ridged horns, scale-patterned chest, cloud-and-thunder spirals on flanks, large expressive dark eyes. A full-bodied, sturdy little ram standing on four hooves in three-quarter view, head slightly raised with a curious, proud, friendly expression and a soft closed smile; its horns curl forward around the ears exactly like the vessel's ram heads, with the same ridged spiral; its long snout, chest of overlapping scale pattern and flank panels of fine cloud-and-thunder spirals and banana-leaf motifs in silvery-grey relief on near-black bronze, now flexible like a living animal. Plain light grey background, even soft light, the ram alone, fully visible and centred. No text, labels, watermarks, people, vessel, other rams, glass, multiple poses, extra horns, gold or green colouring, or fluffy wool.

## Seedance requests

Segment 1: `bytedance/seedance-2.0/reference-to-video` · duration 15 · 480p 16:9 · refs ['<zun_now>', '<hall_inplace>', '<ram_awake>'] · 353 direction words {'refs': 45, 'lock': 26, 'style': 10, 'shots': 207, 'voice': 21, 'sound': 15, 'constraint': 29} · 375 total · ~$2.1

```
References: @Image1 = the Four-Ram Square Zun, identity anchor: shape, decoration and colours exactly as shown; ignore its background; @Image2 = setting and final angle (setting only); @Image3 = the front ram, the character: same design, colours and markings in every shot; ignore its background.
Only the front ram comes alive. the other three rams and the rest of the vessel stay still. The Four-Ram Square Zun ends whole and unchanged.
Stylized 3D animated feature, soft rim light, gallery at night.
Shot 1 (0-3s) [the Four-Ram Square Zun from @Image1, the setting from @Image2]: medium, slightly low head-on, front ram centred, slow push-in, ending at chest height. A white flash pops across the bronze; at two seconds the front ram's eye blinks once, then one ear flicks sharply. Shot 2 (3-7s) [the Four-Ram Square Zun from @Image1, the front ram from @Image3]: close-up on the front ram at the vessel corner, slow push-in. He strains forward hard and locks his eyes on camera; rigid ram head -> softens and flows outward over four seconds, neck and forelegs pulling free -> front half leans out of the corner. Shot 3 (7-11s) [the front ram from @Image3, the setting from @Image2]: low wide across the plinth top, locked off. The ram leaps down heavily onto the plinth, whips his head hard; both horns fly off glowing and spin overhead; he snaps his head up and they slam back on, sparks skittering across the plinth. Shot 4 (11-15s) [the setting from @Image2, the Four-Ram Square Zun from @Image1]: Match cut on the horn spiral: medium, the visitor's slightly low head-on angle, locked off. The vessel stands whole and still; a faint silvery glint runs once around each horn base and fades.
Voiceover, a spry middle-aged male voice, warm deep bronze-toned baritone with a dry teasing edge, neutral English accent, quick playful pace: "You're staring at my horns, aren't you?" "My horns were cast first, then joined in." "Find the join; it's hard to see."
Sound: gallery hum; shutter click; bronze grinding; hooves thud; ringing clang, molten hiss. No music.
Clean picture: no subtitles, captions, lettering, logos or watermark. No people in frame. Never two copies of the Four-Ram Square Zun or of the front ram in one frame.
```

## S4 Review of chosen attempt

Fantasy legibility: **pass**

```
{"hook": 4, "visitor_view": 5, "aliveness": 4, "spectacle": 4, "escalation": 4, "physicality": 4, "character": 4, "return_shot": 4, "renderability": 3, "truth": 5, "sound": 4, "voice_fit": 4}
```

Truth stays clean, and the orbit and the overloaded transformation are fixed. The spectacle shot (two glowing spiral horns spinning above a bare-headed bronze ram on the plinth before they slam back on) now sits in a renderable locked-off frame. It still cannot ship: the request is 353 direction words against the cap. The earlier timing, duplicate-ram, match-cut and flash notes were all left untouched, and applying them would make this close to final.

Claim audit:
- ✅ *voice* "You're staring at my horns, aren't you?" — none; the ram teases the visitor for looking at his horns — none
- ✅ *fact* "My horns were cast first, then joined in." — The ram horns were cast before the vessel and joined into it during casting — horns_cast_first: 'The ram horns were cast first and then joined in when the moulds were assembled and poured.'
- ✅ *fact* "Find the join; it's hard to see." — The horns meet the vessel at a join, and that join is hard to see — joins_hard_to_see: 'the joins are hard to see and the piece looks like one whole' (the join itself comes from horns_cast_first: 'then joined in')

Issues:
- **blocking** [segment 1 request (whole prompt)] The automatic check fails: 353 direction words against a cap of 300. The reference preamble (45 words) and the bracketed per-shot reference labels (about 40 words across the four shots) are the main bloat. The constraint block (29 words) also repeats the lock. → References: '@Image1 = the zun: exact shape, decoration, colours; @Image2 = setting and final angle; @Image3 = the front ram character, same in every shot; ignore backgrounds.' Replace each shot's bracket with ids only, e.g. 'Shot 3 (7-11s) [@Image3, @Image2]'. Lock: 'Only the front ram comes alive; everything else stays still. The zun ends whole.' Constraint: 'No text, no people, never two front rams in one frame.' Trim the voice description, in both the script voice field and the request, to 'warm deep male baritone, dry teasing edge, neutral English accent, quick pace'. Keep every speed, force and consequence word in shots 2 and 3. Target about 230.
- **polish** [segment 1 lines 1–2 (t 1.0, t 3.9)] Line 1 ends about 3.8, only 0.1 s before line 2 starts. Line 2 (8 words) ends about 7.1, which spills into the act beat that should play without speech. The subtitle ending at 6.3 is wrong. → Line 1: 'Staring at my horns, aren't you?' (6 words) at t 0.6, ending about 3.0; subtitle 0.6–3.0. Line 2: 'Cast first, my horns, then joined in.' (7 words; horns_cast_first: 'cast first and then joined in') at t 4.0, ending about 6.8; subtitle 4.0–6.8.
- **polish** [segment 1 line 3 (t 11.35)] The line ends about 14.15, under one second before the segment ends, so lip-sync may clip. → Keep 'Find the join; it's hard to see.' and start it at t 11.1 so it ends about 13.9. Subtitle 11.1–13.9.
- **polish** [segment 1 shot 3] @Image2 shows the vessel with its front ram intact while the freed ram stands on the plinth. That invites a duplicate front ram, the exact failure the closing constraint is trying to forbid. → Append to shot 3: 'the vessel behind cropped out above frame, only its foot visible, soft-focused.' This keeps the full amplitude of the leap, whip, spinning horns, slam and sparks.
- **polish** [segment 1 shot 4 transition] 'Match cut on the horn spiral' needs shot 3 to end on a horn close-up. Shot 3 ends wide on the plinth, so the match will not read and Seedance may invent a bridging move. → Change it to 'Hard cut on the clang', with the clang's ring sustained under the locked-off return.
- **polish** [segment 1 shot 1 action] The trigger is still a camera flash. That models flash photography in a gallery, and the visitor's photo shows no flash. → 'A phone shutter clicks; at 1.5 s the front ram's bronze eye blinks once, then one ear flicks sharply.' The sfx already reads 'shutter click', so the sound needs no change.
- **polish** [segment 1 shot 2 request order] In the request, 'He strains forward hard and locks his eyes on camera' comes before the transformation. The ram may act before he has pulled free. → Reorder: 'Over four seconds the rigid ram head softens and flows outward, neck and forelegs pulling free, until his front half strains hard out of the corner, eyes locking on camera.'
- **polish** [segment 1 request order] The no-people and no-duplicate constraints still sit after the sound list, where they carry the least weight. → Move the shortened constraint line directly after the lock line, before the style line.
- **polish** [asset hall_inplace / shot 4] The vessel is displayed in a glass case, but the reference strips all glass. The return shot is therefore not quite the visitor's view. → Add to the hall_inplace prompt: 'keep the clean edge of the glass case faintly visible, no reflections of people or phones.'

## Checks and production notes

- ❌ segment 1 request has 353 direction words (cap 300, quoted narration not counted): references 45, shots 207, sound 15, voice 21, fixed 65; cut sound and light words first, never speed, force or consequence words
- 📝 segment 1 request has 353 direction words (soft limit 260)
- 📝 segment 1 request is 375 words including narration

Problems along the way:
- s1#0: controlling idea's last thought is longer than ten words
- s3#0: segment 1 shot 2 is 69 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#0: segment 1 shot 3 camera stacks moves ('fast low tracking arc of sixty degrees around the plinth, then hold'); cut, or write timed beats
- s3#0: segment 1 shot 3 is 59 words; keep each shot to about 40 (one tight sentence, verbs first)
- s3#0: segment 1 request has 450 direction words (cap 300, quoted narration not counted): references 55, shots 266, sound 43, voice 21, fixed 65; cut sound and light words first, never speed, force or consequence words
- s3#1: segment 1 request has 353 direction words (cap 300, quoted narration not counted): references 45, shots 207, sound 15, voice 21, fixed 65; cut sound and light words first, never speed, force or consequence words
- s3#2: segment 1 request has 336 direction words (cap 300, quoted narration not counted): references 45, shots 200, sound 13, voice 13, fixed 65; cut sound and light words first, never speed, force or consequence words

## Narration across attempts

**#0:** You're staring at my horns, aren't you? / My horns were cast first, then joined in. / Find the join; it's hard to see.

**#1:** You're staring at my horns, aren't you? / My horns were cast first, then joined in. / Find the join; it's hard to see.

**#2:** You're staring at my horns, aren't you? / My horns were cast first, then joined in. / Find the join; it's hard to see.

