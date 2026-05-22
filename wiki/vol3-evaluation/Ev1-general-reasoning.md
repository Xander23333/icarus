# Ev1 — 通用知识与推理评测（截至 2026-05）

## 路线定位

读者天天对着 SWE-Bench / Terminal-Bench 调 scaffold，回头被产品/媒体问 "你们模型 MMLU 多少"、"GPQA 过 90 没"、"HLE 是不是要饱和了" — 这一节就是这些问题的弹药库。**2024-2026 的两年里，"通用 reasoning" 板块经历了三次集体搬家**：MMLU → MMLU-Pro / MMLU-Redux（修噪声、抗 saturation）；MATH / GSM8K → GPQA Diamond + AIME + HLE（人类专家级 / 长尾）；single-shot reasoning → ARC-AGI-2 + MuSR（abstraction + 多跳叙事）。SimpleQA 单独占一格 — 它是目前唯一被 frontier 公认 "幻觉率 = 1 − accuracy" 的干净 closed-book QA。本节覆盖 9 个 benchmark，每个写：测什么、当前天花板、谁先打穿、contamination/gotcha。

## benchmark 清单

| 名称 | 测什么 | 规模 | 当前 SOTA（2026-05）| 一手 source |
|---|---|---|---|---|
| MMLU-Pro | 57 学科 → 重写到 14 类，10 选项，强 reasoning | 12,032 | GPT-5 / Claude 4.5 / Gemini 3 在 ~88-91%，已接近 ceiling | [arxiv 2406.01574](https://arxiv.org/abs/2406.01574) |
| MMLU-Redux | 30 子集人工重标，去 MMLU 噪声 | 5,700 | frontier ~93-95%（与原 MMLU 同模型差 3-6 点） | [arxiv 2406.04127](https://arxiv.org/abs/2406.04127) |
| GPQA Diamond | PhD 级 bio/chem/phys，"Google-proof" | 198 | GPT-5 ~88%、Claude Opus 4.5 ~87%、Gemini 3 Pro ~89%；专家人类 ~81% | [arxiv 2311.12022](https://arxiv.org/abs/2311.12022) |
| BBH | BIG-Bench Hard 23 任务子集 | 6,511 | 已饱和（frontier >95%），逐渐退出主榜 | [arxiv 2210.09261](https://arxiv.org/abs/2210.09261) |
| HLE (Humanity's Last Exam) | 跨学科专家众包封闭题，含 multimodal | 2,500（最终版） | GPT-5 Pro ~31-32%、Gemini 3 Deep Think ~37-38%、Grok 4 Heavy ~44%（自报）；纯 text 比 multimodal 高 ~5 点 | [arxiv 2501.14249](https://arxiv.org/abs/2501.14249), [scale.com/leaderboard/humanitys_last_exam](https://scale.com/leaderboard/humanitys_last_exam) |
| ARC-AGI-1 | 视觉 grid，少样本 abstraction | 400 public + 400 semi-private + 100 private | o3-preview (high) 2024-12 报 87.5%（私集），但 cost ~$3,400/题；2025 后 frontier 在低算力档稳定 50-75% | [arcprize.org/leaderboard](https://arcprize.org/leaderboard) |
| ARC-AGI-2 | v1 加难版，专门抗 brute-force search | 1,000+ | 2026-05 公共榜首 ~20-25%，private 更低；人类 ~60% | [arcprize.org/arc-agi-2](https://arcprize.org/arc-agi-2) |
| MuSR | 多跳叙事推理（murder mystery / object placements / team allocation） | 756 | frontier ~85-90% 但 inter-task variance 大；murder mystery 仍 <80% | [arxiv 2310.16049](https://arxiv.org/abs/2310.16049) |
| SimpleQA | 短答 factoid，人类标注难度 | 4,326 | GPT-5 ~54%、Claude 4.5 ~50%、Gemini 3 ~56%；这就是 1 − hallucination rate | [openai.com/index/introducing-simpleqa](https://openai.com/index/introducing-simpleqa/) |

> 分数以官方 leaderboard / paper / system card 截至 2026-05 公开数为准。多家自报数差异以 ±2 点为常见噪声，本节不再每条标 [uncertain]，但凡是没有第三方复现的口径都按"厂商自报"读。

---

## MMLU-Pro

### 它要修什么

原 MMLU 三大问题：(1) 4 选项 → random baseline 25%，区分度低；(2) 大量"查得到"的事实题，奖励 memorization；(3) 标注噪声 ~6% [^redux]。MMLU-Pro 的回应是：扩到 **10 选项**、重写到偏 reasoning、去掉 14 个最噪学科（合并到 14 类）[^mmlupro]。同模型从 MMLU 到 MMLU-Pro 平均掉 16-33 点（paper Figure 2），区分度回来了。

### 当前状态

frontier 已贴近天花板。GPT-5 / Claude Opus 4.5 / Gemini 3 Pro 在 88-91% 区间，且第二/第三梯队（Qwen3-235B-A22B-Thinking、DeepSeek-V3.2、GLM-4.6-thinking）也都 >83%。**继续作为 leaderboard 头条的边际意义在下降** — 但作为 mid-train 监控信号仍然非常 robust：分数掉了基本能定位到 data mix 或 RL 阶段的 regression。

### gotchas

- **CoT vs no-CoT 必须分开报**。Paper 自己给了两栏，社区跑分常只挑高的那栏。读 system card 时如果只看一个数字 → 默认是 CoT。
- **contamination**：MMLU-Pro 一半题来自 STEM-themed 公开题源（TheoremQA、SciBench 等），2024 后期数据混合里大概率已被见过。可信 delta 是 "MMLU-Pro − MMLU-Pro-NoOptions"（去掉选项让模型自由作答）— Anthropic 在 Claude 4 system card 用过此 ablation [^claude45]。
- **prompt sensitivity**：paper 自己说 prompt 24 种变体 std ~2 点；社区报分常无 prompt 声明。

---

## MMLU-Redux

UIUC + CMU 2024-06 的工作，挑了 MMLU 30 个最噪子集（5,700 题）人工重标，发现 6.49% 的题有"错误答案/题面歧义/没有正确选项"问题 [^redux]。**意义不在跑分本身，而在告诉你 MMLU 高分上有 6 个点是噪声地板。** 实际 reading：

- 同模型 MMLU vs MMLU-Redux 差值 ~3-6 点，且差值随模型变强而变大（强模型更能"被噪声坑"，因为它本可全对）。
- **virology** / **professional_law** / **college_chemistry** 三个子集是噪声重灾区。如果你看到某模型这几科特别低，先怀疑标注而不是能力。
- Redux 没出 v2，2025 起 frontier 看的是 MMLU-Pro + GPQA + HLE 组合，Redux 主要作为"MMLU 数字打多少折"的参考表。

---

## GPQA Diamond

### 设计

448 题总集，**Diamond = 198 题专家间一致 + 非专家加 Google 30min 仍做错** 的子集 [^gpqa]。学科分布 bio/chem/phys，PhD-in-field 人类 ~81%、PhD-out-of-field + Google ~34%。这是目前 frontier 最常被 quote 的"专家级"分数。

### 当前状态

2025-Q4 起 frontier 集体过 85%：

- GPT-5 / GPT-5 Pro 在 87-89%（reasoning_effort=high）。OpenAI 2025-08 system card [^gpt5card]。
- Claude Opus 4.5 ~87%（extended thinking 开）。Anthropic 2025-11 model card。
- Gemini 3 Pro / Deep Think ~89-92%（DeepMind 2025-11 报）。
- Grok 4 Heavy 自报 ~87-88%（xAI 2025）。

**已经压住 expert ceiling**。继续刷主要是 thinking budget 和 majority vote 在做功。Epoch AI 的 "GPQA Diamond expert+" 复评（2025-09）建议把 expert baseline 修正到 ~85%（原 81% 偏低），那么 "frontier 超人" 这条叙事其实是 2025 中开始的，不是 2024。

### gotchas

- **样本量小（198）**：±1 点 ≈ 2 题。**单次跑 1 个 seed 没意义**，要 best-of-k / mean-of-k 报。HAL 主张报 95% CI；当前主流是 32 次 majority vote。
- **chemistry 子集 contamination 信号**：题源涉及 ACS exam pool，部分题在 RedPajama / DCLM crawl 里能 substring-match 到。Sakana AI / Epoch 都做过 audit。可比较 chem vs phys 分差，frontier 若 chem >> phys 警惕。
- **"Google-proof" 是 2023 年定的**：2026 年 Google 自己已经能解部分题（Gemini 在 search 模式下），意味着 retrieval-augmented baseline 不再是 ~34%；纯 closed-book 才是公平比较。

---

## BBH

历史地位题。BIG-Bench Hard 是 2022 Suzgun et al. 从 BIG-Bench 200+ 任务里挑出 23 个"few-shot CoT 当时不能解"的任务，6,511 题 [^bbh]。**2024 末已经事实饱和**：frontier 在多数子任务 >95%，剩余难度集中在 `dyck_languages`、`tracking_shuffled_objects_seven`、`word_sorting` 这种 syntactic / 长 sequence 的 corner。

写给 reader：BBH 现在的用法是 mid-train ablation 的 "免费稳定信号" — 跑得便宜，对 reasoning regression 敏感，但不要再放主榜。已经被 BBEH（BIG-Bench Extra Hard，Google 2025-02，[arxiv 2502.19187](https://arxiv.org/abs/2502.19187)）正式替代，BBEH 在 frontier 上仍 <50%。

---

## HLE (Humanity's Last Exam)

### 设计

Center for AI Safety + Scale AI 2025-01 [^hle]，目标是造一个 "frontier 不能解、专家能解、不能 Google" 的封闭题集。流程：全球公开征题（1,000+ 学者投稿）、双盲审、剔除任何 frontier 模型 ≥50% 命中的题。最终 2,500 题（text + 部分 multimodal），覆盖 100+ 学科，含正式数学证明、graduate physics、古典语言学、医学诊断等长尾。

### 当前状态

leaderboard 在 [scale.com/leaderboard/humanitys_last_exam](https://scale.com/leaderboard/humanitys_last_exam)。截至 2026-05：

- text-only：Gemini 3 Deep Think ~37-38%、GPT-5 Pro ~31-32%、Grok 4 Heavy 自报 ~44%（有 verification 争议）、Claude Opus 4.5 ~25-28%。
- multimodal 子集（约 10% 题量）所有模型比 text 低 5-10 点。
- 一年内从 Jan 2025 的 ~3-4%（o1/Claude 3.5）爬到 30%+。**饱和速度比作者预期快 ~3x** — HLE v2 在路上（CAIS 2026-Q2 announce）。

### contamination & gotchas

- **题面不公开 hold-out**：约 20% 题作为 private set，只有 Scale 内部跑分。读 paper / leaderboard 时注意分公开 / 私有。
- **xAI Grok 4 Heavy 44% 的争议**：第三方（如 ARC Prize team、Epoch AI）独立复现拿到的数字偏低 5-8 点；xAI 用了 8x parallel + 自一致投票 + 私有 verifier，定义"分数"的方式与 OpenAI/Anthropic 不一致。读 leaderboard 看 "single-run" 列。
- **题目偏 STEM-heavy**：humanities / law 子集小，"覆盖人类知识"是营销话术，实际 60%+ 题是 STEM-grad 难题。
- **正确答案 grading**：multi-choice 部分硬 grading；short-answer 用 LM-judge（GPT-4o + 规则），LM-judge agreement rate ~93%，剩 7% 是公开的 known noise。

---

## ARC-AGI-1 / ARC-AGI-2

### ARC-AGI-1 简述

Chollet 2019 提出的 abstraction & reasoning corpus，30x30 grid → grid，每题 2-5 个 demo。公开 400 + 半私有 400 + 私有 100。**2024-12 o3-preview 在 ARC Prize 公开比赛拿到 87.5%（high-compute）/ 75.7%（low-compute）**，对应 "private eval" 集，cost 分别 ~$3,400 / ~$20 每题 [^arcprize]。这是 LLM 路线在 ARC 上的第一次 "人类级"。但 ARC Prize 团队明说：这是 **brute-force test-time search + LLM 当 program proposer** 的胜利，不是 "scale 解决"。

ARC-AGI-1 当前状态（2026-05）：在中算力档（<$10/题）frontier 稳定 50-75%。o3-mini / Claude Opus 4.5 thinking / Gemini 3 Deep Think 都在这区间。**ARC-AGI-1 在低算力下没饱和**，但作为 "frontier 全力开火能赢" 的 benchmark 已经 retired，主榜转 v2。

### ARC-AGI-2

2025-03 release [^arc2]，1000+ 题，专门针对 v1 上能 brute-force 的解法做了对抗设计：(1) 增加每题需要的"概念组合数"；(2) 引入更多 symmetry/反例陷阱；(3) 加入需要 multi-step 抽象的题。结果：**v1 上 87.5% 的 o3 在 v2 上首发 ~4%**，frontier 集体回到地板。

2026-05 状态：

- public leaderboard 顶部 ~20-25%（包括 ARC Prize 2025 winning solutions，多数是 program-synthesis + LLM hybrid）。
- pure LLM zero-scaffold ~5-10%。
- 人类 baseline ~60%。
- ARC Prize 2026 在跑，500k 奖金留给首个 >85% 且 cost <$0.42/题的方案。

### gotchas

- **不要把 v1 的 87.5% 当 frontier capability 数字写在 PPT 里** — cost 量级是普通 inference 的 1000x，且 ARC Prize 后来公开 o3 用的 program search 占算力 90%+。"模型本身"贡献多少未拆解。
- **public 与 private 分数差异**：v1 上 public eval 比 private 简单 ~10 点，v2 上差距更大；社区跑分常只报 public。
- **ARC 与 reasoning 主流的关系**：很多 frontier lab 不再把 ARC 列为主榜（OpenAI/Anthropic/Google system card 不报 v2），原因公开理由是"测的不是 LM 想测的能力"，实际原因更像"现在打不动"。读者作为 eval lead 决定要不要纳入需要 weigh：ARC 的信号纯净度高（zero contamination 风险），但和下游 agentic 性能 correlation 弱。

---

## MuSR

UT Austin 2023-10 [^musr]。三类 narrative reasoning 任务：**murder mystery**（who/where/why）、**object placement**（基于 ToM 的物体定位）、**team allocation**（约束满足）。每题 ~1000 token 叙事 + multi-choice 答案。设计目标：测多跳推理 + 常识 + ToM 的组合，且故事**程序化生成**避免 contamination。

当前状态：

- frontier 平均 85-90%，但 **murder mystery 子集仍 <80%**（要求侦探式 elimination）。
- object placement 在 Claude Opus 4.5 / GPT-5 上接近饱和（>92%）。
- team allocation 与 SAT-solver-style 强相关，frontier RLVR 之后明显改善。

gotchas：

- **程序生成 ≠ 无 contamination**：生成模板和姓名池在 paper 公开，2024 后训练数据可能复现这些模板分布。Salesforce / Anthropic 内部 ablation 显示 frontier 在 MuSR 上 prompt 模板敏感（变 prompt 掉 5+ 点）。
- **chain-of-thought 强依赖**：no-CoT 分数比 CoT 低 15-25 点。报分必须声明。
- **MuSR 不是 ToM benchmark 主选**。如果 reader 要测 ToM，看 ToMi / BigToM / FANToM（[arxiv 2310.15421](https://arxiv.org/abs/2310.15421)）更合适。

---

## SimpleQA

OpenAI 2024-10 [^simpleqa]，4,326 short-answer factoid，人类双标 + 长尾难度。**关键属性：题的答案是单一短串（人名、年份、地名），grading 不靠 LM-judge，幻觉 = 答错且自报 confidence 高**。

当前状态：

- GPT-5 ~54%（无 browsing） / ~87%（有 browsing）。 
- Claude Opus 4.5 ~50%。
- Gemini 3 Pro ~56%。
- 加 retrieval 后 frontier 普遍 80-90%，**这条 benchmark 主要用来测 "纯参数化知识 + 抗幻觉校准"**。

为什么 reader 该关心：SimpleQA 是目前唯一被 OpenAI/Anthropic/Google 都报 "**1 − accuracy = hallucination rate**" 的 benchmark，可以横向比厂商的 honest-calibration 训练效果。Anthropic 2025 在 Claude 4 上加的 "I don't know" RLHF 信号在 SimpleQA 上把 "**hallucinate rate**" 从 ~55% 降到 ~40%（accuracy 不变，refusal 上升）— 这是 calibration 真正 work 的 case study [^claude45]。

gotchas：

- **答案有时效性**："现任 X 是谁" 类题，2024 收题 → 2026 跑分会因事实变化扣分。OpenAI 标了 ~5% 题有此问题，已剔除大多但不全。
- **browsing 模式下 grading 仍硬匹配**：模型答案与 gold 字符串需 substring match 或经轻规则归一化，对名字拼写敏感。读 leaderboard 时区分 "raw match" 与 "normalized"。
- **不要拿 SimpleQA 替代 TruthfulQA 或 HaluEval**：测的是 factoid recall，不是 misconception 抗性或 generation-level 幻觉。

---

## 横向：当下 (2026-05) reasoning leaderboard 该怎么读

给读者的实操建议（写给自己 Qwen 评测 owner 视角）：

1. **head benchmark 组合**：MMLU-Pro + GPQA Diamond + HLE + ARC-AGI-2 + SimpleQA 五件套足够覆盖 "知识广度 / 专家深度 / frontier 长尾 / abstraction / 幻觉"。MMLU/MMLU-Redux 留给 mid-train 监控，BBH 留给 quick-sanity，MuSR 当 narrative 专项。
2. **必须报 cost/compute**：HAL 已经把这条卷起来。GPQA "best-of-32" 和 "single-run" 是两个 benchmark。
3. **contamination check 三招**：(1) GPQA chem vs phys diff；(2) MMLU-Pro vs MMLU-Pro-NoOptions；(3) SimpleQA temporal cohort split。这三招社区 reproducible，可写进 eval pipeline。
4. **frontier 厂商口径差异**：xAI Grok 报分历史偏高、第三方复现普遍 -5 到 -10 点（HLE、ARC、GPQA 都有此模式）；OpenAI/Anthropic/Google 的 system card 数字一般可复现到 ±2 点；中国家（DeepSeek/Qwen/Kimi/GLM）的 GPQA/HLE 自报基本对得上，但 SimpleQA 有 4-6 点的 gap（推测与 retrieval/post-train 差异有关，[uncertain]）。

---

## 未知与争议

- **HLE 的"专家可解"假设**：作者声称专家平均能解 ~75%，但只在小样本（每题 1 个专家）上验证过；frontier 30%+ 是不是已经超 broad expert ceiling 仍未结论 [uncertain]。
- **ARC-AGI 的预测力**：ARC 分数与 downstream agentic / coding 性能 correlation 弱（多数 lab 内部 study 显示 r<0.3）。"ARC = AGI 进度" 的命题在学界仍争论中。
- **MMLU-Pro 的 long-tail option contamination**：10 个选项里的 distractor 是 GPT-4 生成的，部分 distractor 自身可能在训练集中出现 — Tianle Cai 2024-12 raise 过此问题，尚无系统 audit [uncertain]。
- **SimpleQA 的代表性**：4326 题对厂商内部 "知识图谱" 的覆盖采样偏向英文 + 西方文化。Qwen / DeepSeek 在 SimpleQA-zh（社区版）上分布完全不同。

---

## 推荐外部材料

- [arxiv 2406.01574 — MMLU-Pro 原 paper](https://arxiv.org/abs/2406.01574) — TIGER-Lab，必读，方法节有所有 10-option 重写规则。
- [arxiv 2406.04127 — MMLU-Redux](https://arxiv.org/abs/2406.04127) — 把 MMLU 噪声地板钉死的工作。
- [arxiv 2311.12022 — GPQA](https://arxiv.org/abs/2311.12022) — 必读，标注流程值得 eval team 学。
- [arxiv 2501.14249 — HLE](https://arxiv.org/abs/2501.14249) + [scale.com leaderboard](https://scale.com/leaderboard/humanitys_last_exam) — 一手 paper + 活榜单。
- [arcprize.org/leaderboard](https://arcprize.org/leaderboard) + [arxiv 2412.04604 — o3 on ARC 分析](https://arxiv.org/abs/2412.04604)（如适用） — ARC Prize team blog 的 retrospective 比 paper 更直白。
- [arxiv 2310.16049 — MuSR](https://arxiv.org/abs/2310.16049) — narrative reasoning + ToM 视角。
- [openai.com/index/introducing-simpleqa](https://openai.com/index/introducing-simpleqa/) — 短而清楚，附数据集发布。
- [Princeton HAL leaderboard](https://hal.cs.princeton.edu/) — cost-normalized 视角，必须订阅。
- [Epoch AI benchmarking dashboard](https://epoch.ai/benchmarks) — 跨 benchmark 第三方独立复现，frontier 跑分的 sanity check 来源。

---

[^mmlupro]: Wang et al., "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark", [arxiv 2406.01574](https://arxiv.org/abs/2406.01574).
[^redux]: Gema et al., "Are We Done with MMLU?", [arxiv 2406.04127](https://arxiv.org/abs/2406.04127).
[^gpqa]: Rein et al., "GPQA: A Graduate-Level Google-Proof Q&A Benchmark", [arxiv 2311.12022](https://arxiv.org/abs/2311.12022).
[^bbh]: Suzgun et al., "Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them", [arxiv 2210.09261](https://arxiv.org/abs/2210.09261).
[^hle]: Phan et al., "Humanity's Last Exam", [arxiv 2501.14249](https://arxiv.org/abs/2501.14249).
[^arcprize]: ARC Prize 2024 Results, [arcprize.org/2024-results](https://arcprize.org/2024-results).
[^arc2]: ARC-AGI-2 announcement, [arcprize.org/arc-agi-2](https://arcprize.org/arc-agi-2).
[^musr]: Sprague et al., "MuSR: Testing the Limits of Chain-of-thought with Multistep Soft Reasoning", [arxiv 2310.16049](https://arxiv.org/abs/2310.16049).
[^simpleqa]: Wei et al., "Measuring short-form factuality in large language models", [openai.com/index/introducing-simpleqa](https://openai.com/index/introducing-simpleqa/).
[^gpt5card]: OpenAI, "GPT-5 System Card", 2025-08.
[^claude45]: Anthropic, "Claude 4 / 4.5 model card", 2025.
