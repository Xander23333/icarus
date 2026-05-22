# Ev2 — Math reasoning 评测（截至 2026-05）

## 路线定位

数学 benchmark 是 2024–2026 reasoning model 时代被刷得最猛、也最先暴露 contamination / prompt-format / sampling 三大坑的赛道。读者是 Qwen 自家 eval owner，对 AIME、MATH-500、HMMT 这套早就熟，本节只挑会直接影响你给 Qwen-Math / Qwen3-Thinking 报数的几个问题做硬讨论：(1) **AIME / HMMT 这种「年度 30 题」的统计不确定性远大于报出的 0.x 个点差异**；(2) **MATH-500 是 OpenAI PRM 工作的 hold-out subset，不是 MATH 全集**，跨论文同名不同物；(3) **FrontierMath 经历 OpenAI funding 披露争议后，"private hold-out" 不再 = "unseen by lab"**；(4) **Putnam-AXIOM 通过变量扰动证明 contamination 真存在**；(5) **prompt format + sampling 协议（cons@k / maj@k / pass@k）几乎决定 ±10 点的报数空间**。本节按 benchmark 走，最后给一份给 Qwen owner 的报数 checklist。

## benchmark 清单

| 名称 | 题目数 | 来源 / 年份 | 当前 frontier（2026-05）| 一手 source |
|---|---|---|---|---|
| AIME 2024 | 30（I+II 各 15） | MAA, 2024-02 | top reasoning model maj@64 ≈ 90–95% | [matharena.ai](https://matharena.ai/), [MAA](https://maa.org/maa-invitational-competitions) |
| AIME 2025 | 30 | MAA, 2025-02 | GPT-5 / Gemini 3 / Claude 4.5 Opus maj@64 ≈ 90%+；Qwen3-Thinking 也 >85% | [matharena.ai/competitions/aime-2025](https://matharena.ai/) |
| HMMT 2024 / 2025 Feb | 30 | Harvard-MIT Math Tournament | frontier ≈ 70–85%，比 AIME 难一档 | [hmmt.org](https://www.hmmt.org/), matharena |
| MATH-500 | 500 | Lightman et al. (OpenAI PRM 论文), hold-out subset of Hendrycks MATH | frontier ≈ 97–99%，已饱和 | [arxiv 2305.20050](https://arxiv.org/abs/2305.20050) |
| OlympiadBench | 8,476（含图） | Tsinghua, 2024 | text-only 子集 frontier ≈ 60–70%；含图子集更低 | [arxiv 2402.14008](https://arxiv.org/abs/2402.14008) |
| FrontierMath | ~300（tiered，部分公开） | Epoch AI, 2024-11 | frontier reasoning model T1–T3 ≈ 25–50%；T4 仍 <10% | [arxiv 2411.04872](https://arxiv.org/abs/2411.04872), [epoch.ai/frontiermath](https://epoch.ai/frontiermath) |
| Putnam-AXIOM | 236 original + 52 variations | Stanford, 2025-02 | frontier on original ≈ 40–55%；variation drop 10–30 点 | [arxiv 2502.05195](https://arxiv.org/abs/2502.05195) |
| HARP | 4,780 | Princeton, 2024-12 | 分难度档；最难档 frontier <40% | [arxiv 2412.08819](https://arxiv.org/abs/2412.08819) |

> 数字以 matharena.ai + 各官方 leaderboard 截至 2026-05 为准。reasoning era 后，几乎所有报数都是 maj@k / cons@k，pass@1 已不是主指标 — 这本身是报数变化的核心。

---

## AIME 2024 / 2025（+ HMMT）

### 为什么这一组 benchmark 在 reasoning era 仍然是主战场

整型答案（0–999），grading 完全机器可验证，题目每年新出，contamination 在赛后 2–3 周内是干净的 — 这三点让 AIME / HMMT 在 o1 之后成了 reasoning model 的标准 demo。matharena.ai（ETH + 个人项目）维护跨家、统一 sampling 的复现榜，是目前最不被 marketing 污染的 source [^matharena]。

### 30 题的统计噪声

这是读者最容易踩的坑。AIME 一届 30 题，pass@1 = 80% 意味着对了 24 题、错 6 题。Wilson 95% CI 大致 ±13 点。换言之 **AIME 上 83% vs 87% 几乎不显著**，但 paper / blog 经常拿这种差作为新模型的卖点。matharena 自己在 FAQ 里明说要看 maj@k 的 CI [^matharena_faq]。

实际操作上，标准协议演化成：
- **采 k=32 或 64 次，每次独立 sample，T=0.6–1.0**（具体 T 因家而异，OpenAI o1 系列 T≈1.0、Anthropic 系常 T=0.7）；
- **maj@k**（多数投票最终答案）或 **cons@k**（consensus，要求 k 次中 ≥ 某阈值同意）作为主分；
- pass@1 用 k 次 sample 的均值估计，附 std；
- pass@k 偶尔报 — 但 AIME 上 pass@64 几乎都 >95%，已无区分度。

frontier 报 "AIME 2024 = 94.0%" 一般是 **maj@64 over k=64 samples**，部分家会再外加一层 verifier。读者比 Qwen3 数字时务必核 k 与 aggregation — 不同协议差 5–10 点常态。

### 2025 后的 contamination 信号

AIME 2024 在 2024-02 出题，到 2024-08 已被多个开源 SFT 数据集吃进去。Qwen2.5-Math / DeepSeek-Math-V2 训练数据里 AIME-style 题大量出现。**AIME 2025 在 2025-02 一发布，matharena 在 48h 内挂出所有 frontier 跑分**，这一窗口的数字最干净；2025-08 之后再报 AIME 2025 已经不可信。HMMT 同理。

### 报数 checklist（AIME 一组）

| 字段 | 必填 |
|---|---|
| 年份与赛轮（I / II 还是合并）| 是 |
| sample 数 k | 是 |
| temperature / top-p | 是 |
| aggregation（pass@1 mean / maj@k / cons@k）| 是 |
| 是否带 verifier / reranker | 是 |
| prompt 模版（CoT prefix? few-shot? 系统提示？）| 是 |
| 切题时间（在 vs 后竞赛日）| 强烈建议 |

---

## MATH-500

### 这个数据集到底是什么

读者应该熟，但学界经常混淆 — **MATH-500 不是 Hendrycks et al. (2021) 的 MATH 全集**。它是 Lightman, Cobbe et al. 2023 *Let's Verify Step by Step*（OpenAI PRM 论文）的 **hold-out 500 题 subset**，从 MATH 测试集里取出来用于评估 PRM 训练效果 [^lightman]。论文表 1 即报 MATH-500 baseline。后来这个 500 题 split 因为「OpenAI 用过、规模小、可快速对照」流行起来，但严格来说它是 **OpenAI 选的子集**，不是 community-neutral split。

### 为什么 frontier ≈ 99% 不再是有意义信号

MATH-500 在 2024 末已经被 GPT-4 / Claude 3.5 Sonnet / Qwen2-Math-72B 等多家干到 95%+。reasoning model 上来后基本 98–99%。**剩下的 1–2% 多数是 grading 噪声**：答案等价但表达不同（√2/2 vs 1/√2、分数 vs 小数、LaTeX 形式差异）导致 string match 失败。MATH 原始 grader（Hendrycks 的脚本）+ Minerva 风格 sympy normalize 都解不掉全部 corner case。

实操含义：**Qwen 不应把 MATH-500 列为重点指标**，它现在只该当 sanity check / regression test 用，且要看具体哪几题错 — 经常是 grader 问题。社区在 2025 后向 MATH-Hard / MATH-Lvl5 only 迁移。

### contamination 状态

MATH 训练集和测试集都在 GitHub 公开 5 年，几乎所有 pretrain corpus 都吃过。这是 reasoning model 上分主因之一 — **MATH-500 高分不蕴含 generalization**。Putnam-AXIOM 那篇用变量扰动定量了这条。

---

## OlympiadBench

Tsinghua 2024 [arxiv 2402.14008](https://arxiv.org/abs/2402.14008)。8,476 题，覆盖 math + physics，部分含图，中英双语。读者关心的几点：

- **难度档**：题源是中国 / 国际奥赛 + 模拟题，平均难于 AIME，难度变异大；text-only 数学子集是社区最常报的 split。
- **multimodal split** 是 2024 少数提供数学几何图的 benchmark 之一，但 grader 仍按答案 string 比，因此 vision model 只在「认对图 → 算对」这条链上拿分。
- **contamination**：题目大量来自公开题库，开源 math SFT data 几乎全包含。2024-2025 报的高分需当心 — 若你的模型在 NuminaMath、OpenMathInstruct-2 等数据上做过 SFT，OlympiadBench 数字会显著虚高。

---

## FrontierMath

Epoch AI 2024-11 [arxiv 2411.04872](https://arxiv.org/abs/2411.04872) + [epoch.ai/frontiermath](https://epoch.ai/frontiermath)。研究级数学题，按 Tier 1–4 分难度，T4 是「fields medalist 也需思考几小时」级。**初版 frontier ≈ 2%**（GPT-4o, Claude 3.5 Sonnet 同水准），是 reasoning era 之前最难刷的数学 benchmark。

### 现状（2026-05）

- o3 / GPT-5 / Gemini 3 Pro Thinking / Claude 4.5 Opus 在 T1–T3 上做到 25–50%（具体数字按家因协议不同浮动）；
- **T4 仍 <10%**，是当下数学 benchmark 真正未饱和的部分；
- Epoch 持续加新题、轮换 hold-out。

### OpenAI funding 披露争议（读者要知道）

2024-12 媒体 + 社区披露：**OpenAI 对 FrontierMath 提供资金支持，且对部分题目有访问权**，这在原 paper / Epoch 早期宣传里未明示 [^frontiermath_disclosure]。Epoch 事后致歉并更新披露 + 引入 "holdout set" 概念 — 把一部分题目对所有 lab（含 OpenAI）保密，这部分用作 OpenAI 之外的独立信号。

对读者的实操意义：
1. **"private benchmark" ≠ "unseen by all labs"**。FrontierMath 这个标杆事件让整个圈子重新审视 private hold-out 的可信度结构 — 谁出钱、谁拿到题、谁审计。
2. 比较 OpenAI 与其他家在 FrontierMath 上分时，要区分是否在 holdout set 上报。Epoch 之后的报告会标注这一点。
3. 对 Qwen 报 FrontierMath 数字时，建议显式声明"使用 Epoch 2025-XX 版 public split"或"holdout set"，并附 Epoch 当期 changelog 链接。

### sampling 协议

FrontierMath 鼓励 best-of-N + verifier。Epoch 官方报告里 GPT-5 等 frontier 数字多为 pass@1 over k samples（具体 k 按时点变化）。**注意 cons@k 在 FrontierMath 上意义弱**——题目答案空间大、collision 罕见，maj@k 经常 = pass@1。

---

## Putnam-AXIOM

Stanford 2025-02 [arxiv 2502.05195](https://arxiv.org/abs/2502.05195)。读者必看的论文，它给出了 reasoning era 数学 benchmark 上 **contamination 真实存在的硬证据**。

### 设计

- **236 道 Putnam 原题**（1985–2023）+ **52 道 variation**：每道 variation 通过改变量名、常数、问题表述生成 — 数学结构不变、答案变。
- 报分协议：boxed-answer extraction + sympy equivalence。

### 关键发现

- frontier model 在 **original Putnam 题** 上能拿到 40–55%；
- 在结构等价的 **variation** 上同模型常常掉 10–30 个点，差异统计显著；
- 差异越大 = 模型越「认题」而非「会做」。论文 figure 3 / 4 给出每家模型的 drop 幅度。

读者实操：**任何在 Qwen-Math 上的新 RL trick，都应该在 Putnam-AXIOM original vs variation 上跑一对，看 drop 是缩还是张。** drop 缩 = 真泛化；drop 不变 = 大概率是 reward-shaping 把已知题刷得更熟。Putnam-AXIOM 是目前最便宜可信的"contamination probe"。

### 局限

- 变量扰动不一定保持难度等价（有时变易、有时变难）；
- 52 个 variation 仍是小样本，CI 宽；
- 只覆盖 Putnam 风格 — 不能推到所有 math。

---

## HARP

Princeton 2024-12 [arxiv 2412.08819](https://arxiv.org/abs/2412.08819)。4,780 题，分 6 个难度等级，覆盖代数 / 数论 / 几何 / 组合 / 微积分。设计目标是 **填 MATH 和 Olympiad/Putnam 之间的难度梯度**，每档样本够大 → CI 比 AIME 窄。

读者用 HARP 主要两个场景：
1. **细粒度难度分析**：Qwen3-Thinking 在 lvl3 vs lvl5 上的 gap 比单一 benchmark 的总分更能定位模型短板（reasoning depth vs 题型熟悉度）。
2. **statistical reliability**：每档 500+ 题，0.5–1 个点的差异已经显著 — 比 AIME 强。

contamination：来源含公开题库与人工创作混合，论文有 contamination 检测段落但承认无法完全清。

---

## human baseline 可比性

这是读者写 paper / 给老板汇报时最容易踩的坑。常见错误声称："模型在 AIME 上超过人类"。实际情况：

- **AIME** 满分 15（每题 1 分，共 15 题 × 2 = 30）。AIME 是 AMC10/12 后的筛选赛，**参赛者本身已是 top ~5%**。AIME 平均分约 5–6 / 15（≈ 33–40%）。"超过人类平均" 没意义 — 该比的是 AIME 高分段，通常 top 50 cutoff 在 10–11 / 15（≈ 70%）。**目前 frontier 在 AIME 上的水平接近 USAMO qualifier**，但还不是 IMO 金牌选手 — IMO 金牌选手的相应难度是 USAMO / IMO 题，AIME 对他们是 warm-up。
- **HMMT** 同理，参赛者是 self-selected 强者，绝对分不直接和 random human 比。
- **MATH** 原 paper 报 "Berkeley undergrad ~40%, PhD ~75%"，但样本极小且时间不限 — 频繁被误引为"模型已超博士"。
- **FrontierMath** Epoch 报 "expert mathematician 几小时一题"——是设计目标，不是被严格测过的 human baseline。
- **Putnam** 中位数 0/120（是的，零）— 因为题太难、大量选手交白卷。**Putnam top 500 cutoff 通常 < 30/120**。模型在 Putnam-AXIOM 上 50% 已经远超 median 人类参赛者，但这没有数学上的意义 — Putnam 的难度分布是长尾。

实操：写报告时**不要写"超过人类"**，写"在 X benchmark 上达到 Y% maj@k，相应人类参赛者的 top-N% cutoff 约 Z%"。

---

## 跨 benchmark 横切观察

1. **prompt format 是隐藏自由度**。同一道 AIME 题，"Please reason step by step and put final answer in \boxed{}" vs "Answer with a single integer 0–999" vs few-shot CoT prompt — frontier reasoning model 的差异常在 3–8 点。matharena 用统一 prompt 跑就是为修这条。
2. **sampling 协议决定 ±10 点**。pass@1 vs maj@64 vs cons@64+verifier 在同模型上经常差 8–15 点。**报数必须显式声明 k、T、aggregation**。
3. **answer extraction 是 silent killer**。\boxed{} 之外的格式、LaTeX 变体、分数 vs 小数都能让 5–10% 题被 grader 误判。这是 MATH-500 卡在 99% 不进的主因，也是 AIME 上 frontier 之间 "1 点差异" 多半是 grader 噪声而非能力差异的原因。
4. **contamination 在数学上比 code 更严重**。题量小、答案 distinct、网络转发率高。Putnam-AXIOM 的 variation 方法是当下最干净的 probe。
5. **饱和顺序**：MATH-500 (2024) → AIME 2024 (2025 中) → AIME 2025 / HMMT (2026)；FrontierMath T4 + Putnam-AXIOM variation 是当下仍未饱和、且 contamination 抵抗较强的两块。
6. **reasoning trace 长度膨胀**。frontier 在 AIME 上一题平均生成 5–20k token thinking。报 cost / latency 时必须把 thinking token 算入 — 跟 SWE / agent eval 报 cost 同源问题。

## 给 Qwen eval owner 的报数模板

任何 math benchmark 报数行至少包含：

```
{benchmark} {版本/年份}: {分数} ({aggregation}@{k}, T={t}, prompt={prompt_id}, grader={grader_id}, thinking_token_budget={B})
```

例：
```
AIME 2025: 89.6 (maj@64, T=0.7, prompt=matharena-v2, grader=sympy+manual, budget=32k)
```

这把 prompt-format、sampling、grader 三大变量都钉死，是当前 frontier lab 自报数据里仍普遍缺失但最该补的字段。

## 未知与争议

- **FrontierMath holdout set 是否真的对所有 lab 都不可见**：Epoch 的内部 access 协议没完整公开 [unknown]。
- **AIME 2025 之后的 contamination 窗口具体多长**：matharena 没给定量数据 [uncertain]。
- **MATH-500 之外的"MATH community-neutral hold-out"**：至今没有被广泛接受的替代 split。Lightman 的 500 题选择标准 paper 里只说"random"，未公开 seed [uncertain]。
- **Putnam-AXIOM variation 的难度等价性**：作者声明 invariant，但社区有讨论某些 variation 实际更易 [uncertain]。
- **Qwen3-Thinking 等开源 reasoning model 在 FrontierMath 上的 holdout set 数字**：Epoch 2026 reports 是否有覆盖 [unknown — 待核 Epoch 最新季报]。

## 推荐外部材料

- [matharena.ai](https://matharena.ai/) — 跨家、统一 prompt + sampling 的 reasoning model 数学复现榜，目前最不被 marketing 污染的 source。
- [Let's Verify Step by Step, arxiv 2305.20050](https://arxiv.org/abs/2305.20050) — MATH-500 出处 + PRM 训练标准 paper，理解 reasoning model verifier 路线必读。
- [FrontierMath paper, arxiv 2411.04872](https://arxiv.org/abs/2411.04872) + [Epoch 2024-12 disclosure update](https://epoch.ai/blog/openai-and-frontiermath) — 一手 source + funding 争议复盘，是理解 "private benchmark 可信结构" 的标杆案例。
- [Putnam-AXIOM paper, arxiv 2502.05195](https://arxiv.org/abs/2502.05195) — variation probe 是当下检测 math contamination 最便宜的方法，照搬到自家 eval 性价比极高。
- [OlympiadBench paper, arxiv 2402.14008](https://arxiv.org/abs/2402.14008) — multimodal math 设计参考。
- [HARP paper, arxiv 2412.08819](https://arxiv.org/abs/2412.08819) — 难度分档 + CI 友好，做细粒度 ablation 用。
- [Hendrycks MATH original, arxiv 2103.03874](https://arxiv.org/abs/2103.03874) — 区分 MATH 全集 vs MATH-500 的根基。
- [Sasha Rush — On evaluating reasoning models](https://twitter.com/srush_nlp)（不定期 thread）— 关于 sampling / aggregation / grader 噪声的 thread，工程视角最贴近 eval owner 日常。

[^matharena]: matharena.ai 由 ETH Zurich 学生维护，2025 起被 Anthropic / OpenAI 在 system card 中引用作为第三方对照。
[^matharena_faq]: matharena FAQ 关于 30 题统计噪声段。
[^lightman]: Lightman et al., *Let's Verify Step by Step*, OpenAI, 2023. MATH-500 split 在论文 Section 3 / Appendix。
[^frontiermath_disclosure]: Epoch AI 2024-12 公开声明，承认 OpenAI 资助 + 部分 access；后续引入 holdout set 机制。报道：LessWrong / TechCrunch 2024-12。
