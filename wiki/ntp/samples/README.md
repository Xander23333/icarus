# NTP 候选样章 — 总览

> 本目录用 Thesis 候选样章 (`wiki/samples/`) 的同款风格写 NTP 系列长文。每篇 4000–5000 字，Harari 式叙事 + 真实人物 + 密集 arxiv 引用 + 诚实判断 + 反例意识。

样章是为了**让读者一篇就能进入 NTP 的世界**，而不是逐条读 paper note。它们与 `survey/`（严肃综述）和 `daily_reports/`（增量日报）互补。

## 写作约束

- 每篇 **3500–5500 字**正文，标题对话化、结构 4–6 大节 + 尾声
- 引用方式：[arxiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)，不确定的标 `[uncertain]` / `[unknown]`
- 真实人物出场（用真名），避免 \"研究者们\" 这种泛指
- 每篇结尾给一段诚实的反例 / 元评论，不藏立场
- 不写营销语言，不用 \"令人激动 / 革命性 / 突破性\"

## 已有篇目

| 编号 | 标题 | 状态 |
|---|---|---|
| N1 | [这个问题为什么突然变重要了](N1-the-ntp-question.md) | ✅ 首篇 (Xander 亲写) |
| N2 | [Transformer 的形式表达力——TC⁰ 之墙到底有多硬](N2-the-tc0-wall.md) | 🔨 推进中（§1–§4 / 估计 4500字） |
| N3 | [Reversal Curse / 不忠实 CoT / Faith-and-Fate——三块拼图](N3-three-puzzle-pieces.md) | 🔨 推进中（§1–§3 / 估计 4500字） |
| N4 | [Pearl 的因果阶梯与 LLM 的天花板](N4-pearl-ladder-and-llm-ceiling.md) | 🔨 推进中（§1–§2 / 估计 4500字） |
| N5 | Embodiment 真的不可 tokenize 吗——VLA 路线的隐含赌注 | 📝 待写 |
| N6 | World model = 视频生成？三个团队的三种答案 | 📝 待写 |
| N7 | Continual learning：为什么 LLM 不会持续学习 | 📝 待写 |
| N8 | Sutton 又赢一次？回顾被打脸的"机制墙" | 📝 待写 |

后续篇目由 **半小时 cron** (`ntp-deepen-30min`) 自动续写——每次只挑一篇 stub 推进 ≤800 字，或扩写 topic 页面。每日 07:00 daily cron 会在日报里 roll-up 过去 24h 的扩写记录。

## 与其他子目录的关系

- `samples/`（本目录）：长篇可读样章
- `survey/`：严肃综述、timeline、taxonomy（紧凑、可引用）
- `topics/`：8 大 topic 持续累积证据
- `papers/paper_notes/`：单篇精读笔记，每日新增
- `daily_reports/`：每日 arxiv 扫描 + 综合解读
