# 编剧 Agent 调试记录（整理版）

日期 2026-11-14。本文件汇总整个调试过程：做了几轮、每轮用了什么提示词和 agent、调了哪些工具、结果如何、花了多少钱。
逐条原始记录在 [CALL_LOG.md](CALL_LOG.md)；完整会话导出在 `~/Downloads/session-export-1794681033129.zip`。

---

## 0. 一页看懂

| 项目 | 数量 |
| --- | --- |
| harness 版本 | v0 → v1 → v1.1 → v1.2 → v1.3（+2 个 A/B 组）→ v1.4 |
| harness 运行次数 | 19 次（3 个测试展品：hope、sophie、sequoia） |
| harness 发给 Claude 的调用 | 169 次，其中 138 次实际调用，31 次命中缓存 |
| harness 花费（你的 API key） | **$22.59**，全部是 Claude（claude-opus-5-5），**没有调用 fal** |
| 多 agent 工作流 | 3 轮共 24 个 agent，230 次工具调用（另有 1 次启动失败，0 个 agent） |
| 提示词版本 | 25 个不同的系统提示词文本（按文件和内容哈希计） |
| 主会话（这段对话）工具调用 | 180 次（Bash 81、Write 32、任务列表/收尾 31、Edit 5、Read 5、Workflow 4、浏览器 14 等） |

工作流 agent 和主会话跑在 Claude Code 里，不走你的 API key，不计入上面的 $22.59。三轮工作流的 agent 共用了约 200 万 token。

---

## 1. 时间线

| # | 做了什么 | 调用 / agent | 花费 | 结果 |
| --- | --- | --- | --- | --- |
| 1 | 克隆仓库，装依赖（含 ffmpeg），跑测试，启动 mock 版界面，跑一部 mock 片 | 主会话 | 0 | 15 个测试通过，mock 片 57 秒 |
| 2 | 建 harness 文件夹、方法文档、v0 提示词，验证 API key | 主会话 | 约 $0.0001 | key 可用 |
| 3 | **v0** 在 Hope 上跑通（无照片） | 2 次运行，6 次实际调用 | $0.58 | 审稿通过，但人读发现编造、"通过"后不再修改等问题 |
| 4 | **第 1 轮工作流**：Seedance 调研、4 视角评审、新建 2 个测试展品 | 9 个 agent，146 次工具调用 | Claude Code | 四个评审一致指出"修改时看不到上一稿"；Seedance 价格约 $0.30/秒 |
| 5 | 用户提供实拍照片和设定图；**v1**：每个阶段都看图、新增 S1b、循环重写 | 1 次运行 | $1.38 | 审稿员发现**渲染模板 bug**（活鲸也被说成"骨架"） |
| 6 | **v1.1 / v1.2** 修模板，三个展品各跑一次 | 4 次运行 | $4.50 | 都在收敛；sequoia 误判为 30 秒 |
| 7 | **第 2 轮工作流**：4 个诊断视角、3 个盲评员比较 v0 和 v1、汇总 | 8 个 agent，71 次工具调用 | Claude Code | **盲评 v1 以 3:0 胜**；v1 的声画对位较弱；16 条改动建议 |
| 8 | **v1.3** 基线 + 2 个 A/B 组（声画对位、结尾） | 9 次运行 | $11.72 | sequoia 改为 15 秒并首次通过；Hope 变成"行程单" |
| 9 | 用户要求：**进度关键词** | 主会话 + 1 次 S0 实测 | 约 $0.03 | 关键词在第 4.9 秒弹出，阶段在第 10 秒结束 |
| 10 | **第 3 轮工作流**：每个展品 4 个版本盲排名 | 7 个 agent，13 次工具调用 | Claude Code | 平局（16/16/16/12）；"结尾"组淘汰；找到"位置词"问题 |
| 11 | **v1.4**：核心想法（X 但其实 Y），默认 15 秒 | 3 次运行 | $4.11 | Hope、Sophie 改为 15 秒，Sophie 通过；sequoia 退回 30 秒 |
| 12 | 生成对话记录和本文件 | 主会话 | 0 | |

---

## 2. harness 里的 agent 是怎么调用 Claude 的

- **模型**：每次调用都是 `claude-opus-5-5`，adaptive thinking（思考摘要会存下来），**结构化输出**（JSON schema 由 `schemas.py` 生成）。
- **工具**：harness 里的 agent **不调用任何工具**，每个阶段就是一次请求、一次结构化回答。看图靠把图片作为输入附上：观众照片和已有的参考图，每次最多 4 张。
- **每次运行的调用次数**：S0 识别 → S1 消化资料（检查不过最多重试 1 次）→ S1b 参考图规划 → S2 构思 → [S3 写剧本 → S4 审稿] × 最多 3 轮。所以一次运行是 6–11 次调用；没有照片时跳过 S0。
- **每个阶段的 effort**：S0 medium，S1b medium，其他 high。
- **是否通过由代码决定**：没有硬检查问题、没有 blocking、truth = 5、所有分数 ≥ 4。交付三稿里最好的一稿。
- **缓存**：按（模型、提示词全文、输入、图片哈希、schema、sample）做哈希；只改一个阶段的提示词，就只花这个阶段及之后的钱。
- **存档**：每次调用在 `runs/<run>/<NN_阶段>/` 下有 `request.json`（完整提示词和输入）、`thinking.md`、`raw.txt`、`output.json`、`meta.json`（token、费用、秒数）、`events.json`（关键词），出错时还有 `error.json`。

---

## 3. 提示词版本：每版改了什么

完整提示词原文：CALL_LOG.md 第 D 节（按内容哈希列出）和 `prompts/archive/`。

| 版本 | 改了什么 | 为什么 |
| --- | --- | --- |
| v0 | 四个阶段的初版提示词（S1–S4） | 基线 |
| v1 | 全部重写：每个阶段看图；S0 先自由识别；新增 S1b 参考图规划；S3 在上一稿上改；台词分三类（事实 / 眼前所见 / 情绪）；声画对位；口语写法；S4 先逐句核对事实；分数有锚点 | 第 1 轮四位评审的共识 + 你要求的"以看图为主" |
| v1.1–1.2 | 只改渲染模板：不同状态的参考图分开绑定；描述只写一次 | 审稿员两次指出模板 bug |
| v1.3 | 短名称绑定；只计编剧能控制的字数（上限 230）；每个镜头一句话；全片统一音乐；设定图不送进 Seedance；长度由故事主线决定 | 第 2 轮汇总的 16 条建议里采纳了 11 条 |
| v1.3 A/B | `counter`：画面和台词是两条轨，每段一个碰撞；`endings`：最后一句是想法而不是指令 | 改动风险大，先测再采纳 |
| v1.4 | S1 必须先写核心想法（观众以为 X，其实 Y，Y 必须是资料原话）；默认 15 秒；声画对位加上"画面要符合实际陈列"；位置词必须有出处；`endings` 不采纳 | 第 3 轮盲评的结论 |
| 关键词 | 每个阶段第一个字段是 2–6 个关键词，规则在 `prompts/_highlights.md` | 你的要求（进度展示） |

---

## 4. 三轮多 agent 工作流

### 第 1 轮（9 个 agent，146 次工具调用）
| agent | 任务 | 主要工具 |
| --- | --- | --- |
| research:official | 查 fal 官方文档里的 Seedance 2.0 参数、价格，以及图像模型 | WebFetch 19、WebSearch 5 |
| research:practice | 查实际使用者怎么写 Seedance 提示词 | WebSearch 13、WebFetch 15 |
| research:verify | 逐条交叉核实上面两份调研 | WebFetch 18 |
| critic × 4 | 编剧、博物馆讲解、视频生成工程、harness 工程四个视角审 v0 | Bash（读文件）、Read |
| packs:build / packs:verify | 新建 sophie、sequoia 资料包，逐条对照网页核实 | WebFetch、Bash（curl） |

结论：Seedance 用 `reference-to-video`，单次最长 15 秒，最多 9 张参考图，自带声音，2.0 没有 seed，720p 约 $0.30/秒。四位评审一致：修改时看不到上一稿；"通过"后不再修改；缺声画对位。

### 第 2 轮（8 个 agent，71 次工具调用）
- 4 个诊断视角（修改循环、时长判断、编剧手艺、可渲染性），读全部 v1.2 运行记录。
- 3 个盲评员（导演 / 普通观众 / 讲解专家）比较 v0 和 v1 的 Hope 剧本，标签隐藏，顺序打乱，只看文本、不开文件。
- 1 个汇总 agent 给出 16 条按优先级排序的改动。
- 结果：**v1 以 3:0 胜**，但三位都认为 v1 的声画对位不如 v0。

### 第 3 轮（7 个 agent，13 次工具调用；之前 1 次启动因参数错误失败，0 个 agent）
- 每个展品 2 位评委（导演 / 讲解专家），各自读一个匿名文件，给 4 个版本排名；字母和版本的对应只在脚本里，评委看不到。
- Borda 积分：v1.2 16、v1.3 16、counter 16、endings 12。
- 导演偏好"一个想法加一个转折"，讲解专家偏好有出处、覆盖面广；"结尾"组淘汰；6 个胜出剧本里有 5 个滥用位置词。

---

## 5. 所有运行

| 运行 | 新调用 | 花费 | 状态 | 片名 |
| --- | --- | --- | --- | --- |
| 1114-170208-hope-v0 | 2 | $0.11 | 中途报错（schema 转换 bug，已修） | — |
| 1114-170409-hope-v0 | 4 | $0.47 | 模型自评通过 | Not Even Grown |
| 1114-172400-hope-v1 | 10 | $1.38 | NEEDS_HUMAN | Just a Young One |
| 1114-173051-hope-v1.1 | 6 | $1.09 | NEEDS_HUMAN | Young Giant |
| 1114-173547-hope-v1.2 | 5 | $0.90 | NEEDS_HUMAN | Young Giant |
| 1114-173549-sophie-v1.2 | 9 | $1.34 | NEEDS_HUMAN | Almost Whole |
| 1114-173551-sequoia-v1.2 | 9 | $1.17 | NEEDS_HUMAN | Under the Dust |
| 1114-175519-hope-v1.3 | 9 | $1.96 | NEEDS_HUMAN | All of Me in One Frame |
| 1114-175520-sophie-v1.3 | 9 | $1.69 | NEEDS_HUMAN | The Hilltop |
| 1114-175523-sequoia-v1.3 | 9 | $1.13 | PASS_WITH_OPEN_POLISH | Only a Slice |
| 1114-180509-hope-v1.3-counter | 6 | $1.52 | NEEDS_HUMAN | All of Me in One Frame |
| 1114-180511-hope-v1.3-endings | 7 | $1.56 | NEEDS_HUMAN | From Wexford Sand to This Hall |
| 1114-180513-sophie-v1.3-counter | 6 | $1.28 | NEEDS_HUMAN | The hilltop |
| 1114-180515-sophie-v1.3-endings | 7 | $1.24 | NEEDS_HUMAN | One Hilltop, Then Here |
| 1114-180517-sequoia-v1.3-counter | 6 | $0.89 | PASS_WITH_OPEN_POLISH | Only a Slice |
| 1114-180519-sequoia-v1.3-endings | 7 | $0.75 | PASS_WITH_OPEN_POLISH | Read Me Like a Clock |
| 1114-181730-hope-v1.4 | 9 | $1.39 | NEEDS_HUMAN | From Up There |
| 1114-181731-sophie-v1.4 | 9 | $1.31 | PASS_WITH_OPEN_POLISH | Found Whole |
| 1114-181734-sequoia-v1.4 | 9 | $1.41 | NEEDS_HUMAN · REGRESSION_FAIL | From the Eaves to the Forest |

另有一次只跑 S0 的关键词实测（`runs/_smoke_s0`，约 $0.03），以及 v1.4 第一次误用旧文件启动、被我中止的三次运行（只跑了前几个阶段，结果已作为缓存被复用）。

---

## 6. 关键结论（附证据位置）

1. **盲评比审稿员自评可靠**：自评分数常常聚在 4 分；盲评能区分好坏（`research/round2/`、`research/round3/`）。
2. **同一个阻断问题改几稿都不消失，先查模板或 harness**：v1 和 v1.1 的阻断问题都出在 `seedance.py`（CHANGELOG v1 一节）。
3. **两种"好"需要同时满足**：导演要一个想法加一个转折，讲解专家要有出处。v1.4 的"观众以为 X，其实 Y，Y 必须是资料原话"就是为了兼顾两者（`research/round3/round3_raw.json` 的 decision）。
4. **按故事主线定长度会变成行程单**：时间线总能再加一站（第 3 轮的回归分析）。
5. **打磨轮可能把剧本改坏**：Sophie v1.4 第 2 稿比第 1 稿差，靠"交付最好的一稿"兜底。

---

## 7. 我犯的错（都已处理）

- 写 v1 提示词时覆盖了 v0 提示词。后来从运行记录里恢复到 `prompts/archive/v0/`；S0 的 v0 从没跑过，所以无法恢复。
- 渲染模板 bug 两次，都由审稿员发现，已修。
- 第 3 轮第一次启动传错了参数：立即失败，0 个 agent，没花钱。
- v1.4 第一次启动用错了提示词文件（旧的 counter 版），发现后中止重跑。
- `run.py` 有一处缩进错误，提交前已改正。
- **API key 出现在了会话里**：你把它贴在消息里，我在创建 `.env` 时也把它写进了一条命令。所以 `~/Downloads` 里的会话导出 zip **包含这个 key**，不要分享这个 zip。CALL_LOG.md 和本文件已经把 key 打码。建议黑客松结束后换一个新 key。

---

## 8. 还没解决、没验证的

- sequoia 的长度规则：v1.4 又选了 30 秒。"第二段带来新事实"太容易满足。
- Hope v1.4 的声画对位和长度匹配只有 3 分，状态 NEEDS_HUMAN。
- 打磨轮的副作用：考虑涉及计时和字数的打磨意见不要再改。
- **没有渲染过任何视频**：Seedance 能否听懂这种写法、两段之间声音能否一致、参考图会不会导致画面里出现两个主体，都没验证。
- 每个测试展品只抽样一次：比较结论的置信度只有"中等"。

---

## 9. 怎么核对

| 想看什么 | 去哪里 |
| --- | --- |
| 某次运行完整对话（提示词、图片、思考、回答、关键词回放） | `runs/<run>/transcript.html`（`uv run python view.py <run>` 生成） |
| 某次运行的结果和检查 | `runs/<run>/report.md` |
| 某个阶段实际发出的请求 | `runs/<run>/<NN_阶段>/request.json` |
| 每次调用的 token 和费用 | CALL_LOG.md 第 A 节 |
| 每个工作流 agent 的任务提示词和工具调用 | CALL_LOG.md 第 B 节；agent 完整对话在会话导出 zip 里 |
| 提示词全文（每个版本） | CALL_LOG.md 第 D 节，`prompts/`，`prompts/archive/` |
| 方法和标准 | METHOD.md |
| 每版改了什么、依据是什么 | CHANGELOG.md |
| 调研和盲评原始结果 | `research/round1_raw.json`，`research/round2/`，`research/round3/` |
