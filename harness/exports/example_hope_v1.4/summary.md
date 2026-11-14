# 整理版：Hope v1.4 一次运行

运行 `runs/1114-181730-hope-v1.4` · 输入：观众在 Hintze Hall 二楼拍的照片 · 完整原始记录见 [transcript.md](transcript.md)

## 一眼看懂

| 项目 | 内容 |
| --- | --- |
| Claude 调用 | **10 次**（S0、S1、S1b、S2 各 1 次，写剧本 + 审稿 3 轮 = 6 次） |
| 工具调用 | **0 次**。每次调用就是一次请求、一次结构化 JSON 回答，不调用任何工具 |
| 模型 | claude-opus-5-5，adaptive thinking，结构化输出 |
| 图片输入 | S0、S1 只看观众照片；S1b 以后每次看 4 张图：照片 + 已有的 3 张参考图（写实设定图、轻动漫设定图、生前水下复原图） |
| token | 输入约 17.5 万，输出约 3.6 万 |
| 花费 | $1.39（S0 命中缓存，没算在内） |
| 用时 | 约 6 分钟（10 次调用依次执行，合计 340 秒） |
| 结果 | 15 秒短片 "From Up There"；状态 **NEEDS_HUMAN**，交付的是第 2 稿 |

## 每一步做了什么

| # | 阶段 | 提示词 | effort | 输入 → 输出 | 关键决定 |
| --- | --- | --- | --- | --- | --- |
| 1 | S0 识别 | `s0_identify.md` | medium | 照片 + 已准备的展品清单 | 认出 Hope，置信度高；照片是从二楼拍的全景，下面的人很小 → 观众关心的是"它有多大" |
| 2 | S1 消化资料 | `s1_digest.md` | high | 照片 + 资料包 | 11 条事实；**核心想法**：观众以为"这么大的骨架一定是成年巨鲸"，其实"Hope 当时还是一头幼年雌鲸"；第二段没有新事实 → **15 秒** |
| 3 | S1b 参考图规划 | `s1b_assets.md` | medium | 照片 + 3 张已有参考图 + 素材 | 名称：the whale skeleton / the living blue whale；规划 4 张图：两张设定图的单视角侧面图（带标签的设定图本身不能送进视频）、骨架现状图、展厅原位图 |
| 4 | S2 构思 | `s2_concept.md` | high | 以上全部 | 3 个构思（反转 / 直接对观众说话 / 回到沙洲），选了 **"From where you're standing"**：从观众站的位置说起，先说长度，再揭示她还是幼年 |
| 5 | S3 第 1 稿 | `s3_script.md` | high | 以上 + 选中的构思 | 3 个镜头 + 3 句台词（见下） |
| 6 | S4 审第 1 稿 | `s4_review.md` | high | 剧本 + 资料包原文 + 渲染好的 Seedance 请求 + 照片 | 2 个 blocking（都来自代码检查）、3 条打磨意见 |
| 7 | S3 第 2 稿 | `s3_script.md` | high | 第 1 稿 + 修改意见 + 渲染请求的字数分解 | 只修了 blocking：删掉图片提示词里的"禁止文字"清单，压缩音乐描述 |
| 8 | S4 审第 2 稿 | `s4_review.md` | high | 同上 + 上一轮审稿 | blocking 全部解决；仍有 3 条打磨意见，所以再改一轮 |
| 9 | S3 第 3 稿 | `s3_script.md` | high | 第 2 稿 + 打磨意见 | 三条打磨全改了，但第一句台词被挪到了 0.3 秒 |
| 10 | S4 审第 3 稿 | `s4_review.md` | high | 同上 | 内容最好的一稿，所有分数 ≥ 4，但有 1 个计时检查不过 |

每次调用的系统提示词末尾都附加了 `prompts/_highlights.md`（关键词规则）。

## 三稿对比

| | 第 1 稿 | 第 2 稿（交付） | 第 3 稿 |
| --- | --- | --- | --- |
| 1.0 秒 | From up there, the people below look tiny next to me. | 同左 | 同左（但从 **0.3 秒**开始） |
| 第二句 | Take your time.（情绪句） | 同左 | Four point five tonnes.（事实：重量） |
| 最后一句 | Twenty-five point two metres of bone, and I was a juvenile female blue whale. | 同左 | 同左 |
| 第一个镜头 | 小小的观众从骨架下走过（和台词重复） | 同左 | 云影掠过玻璃屋顶（不再重复台词） |
| 代码检查 | 3 个问题 | 0 | 1 个（第一句开始太早） |
| blocking | 2 | 0 | 1 |
| 审稿分数（hook / 观众视角 / 焦点 / 忠于构思 / 真实 / 声画对位 / 口语 / 可渲染 / 长度 / 结尾） | 4/5/5/4/5/3/4/3/3/5 | 4/5/5/4/5/3/4/4/3/5 | 4/5/5/**5**/5/**4**/4/4/**4**/5 |

## 关键词流（观众等待时会看到的）

S0：Hope the blue whale · Hintze Hall · Diving pose from the balcony · Tiny visitors below
S1：25.2 metres · juvenile female · Wexford Harbour · 25 March 1891 · Dippy the Diplodocus · 15 seconds
后续阶段还有参考图、构思、风格、声音、核对等关键词，完整列表和回放在 `runs/1114-181730-hope-v1.4/transcript.html`，或 report.md 的 Progress feed 一节。

## 这次运行暴露的问题

1. **我写的检查有误报**：第 1 稿的两个 blocking 是假的。图片提示词写的是"No hall, cables, people, text, labels or watermarks"（禁止文字），检查却当成了"要求画面有文字"。原因是否定词的判断只认"no"后面紧跟 text 的写法。这浪费了一轮修改，还让编剧删掉了图片提示词里本该保留的"禁止文字"保护。需要修。
2. **最好的一稿没被交付**：第 3 稿内容最好，只因第一句早开始了 0.5 秒没过检查；三轮已用完，harness 按"检查问题最少"交付了第 2 稿。审稿员也说直接把这句挪到 0.8 秒放不下（会和下一句挤在一起）。可以考虑：只差计时问题时，由代码自动微调时间，或者允许多一轮只修计时的修改。
3. **"Take your time" 是凑数句**：审稿员两轮都指出了，直到打磨轮才改掉。
4. **S1 的输出里有一处乱码**：核心想法的 last_thought 写成了 "…she was only a juvenile.of course"。不影响事实，但说明结构化输出偶尔会混进杂字，检查没有覆盖这种情况。
5. **审稿员发现的画面问题**：第 2 个镜头写的是"从下方看"，和观众在二楼的视角矛盾，第 3 稿改成了"与阳台齐高"。

## 怎么核对

- 每次调用的完整提示词、输入、思考摘要、输出：[transcript.md](transcript.md)，按调用顺序排列，有目录。
- 交互版（含图片和关键词回放）：`runs/1114-181730-hope-v1.4/transcript.html`
- 运行报告（检查、审稿的逐句事实核对、Seedance 请求）：`runs/1114-181730-hope-v1.4/report.md`
- 原始文件：`runs/1114-181730-hope-v1.4/<NN_阶段>/`（request.json、output.json、thinking.md、meta.json、checks.json、feedback.md）
