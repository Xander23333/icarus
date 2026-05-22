# Ev10 评测的 meta 问题 — contamination / Goodhart / 判官偏差 / harness 漂移

## 路线定位

前面 Ev1–Ev9 把各个能力维度的 benchmark 串了一遍。这一节回到上一层：**为什么 2024–2026 整个社区都在喊 "评测危机"**。问题不在哪个具体 benchmark 设计差，而在六个系统性病灶同时发作：(1) pretrain / RL 数据 contamination 把 held-out 变成 train set；(2) Goodhart — 一旦某个分数挂钩 OKR，刷分动作立刻覆盖被测能力本身；(3) 几乎所有有公信力的 benchmark 在 18 个月内饱和；(4) LM-as-Judge 和 LMArena 都被证明有结构性偏差；(5) 同一 benchmark 在不同 harness 下分差可达 10+ 个点；(6) 厂商 report 的 "GPT-X scored 92.3" 几乎从不写 n_samples / temperature / scaffold / 抽样策略。这一节给 Qwen eval 团队的对应防御清单。

## 1. Contamination — held-out 越来越不 held

**事实证据**：

- **SWE-Bench 污染**：Aleithan et al. 2024-10，"SWE-Bench+: Enhanced Coding Benchmark for LLMs"，[arxiv 2410.06992](https://arxiv.org/abs/2410.06992)。把 SWE-Bench Lite 重新审计，发现 (a) 32.7% 的 task patch 在 GitHub issue 描述里直接给出了 "solution leak"；(b) 31.1% 的 task 在 SOTA agent (SWE-Agent + GPT-4) 的 trace 里检测到 weak test — 模型生成的 patch 实际改的不是 bug，但弱测试通过。重新筛掉这两类后，GPT-4 + SWE-Agent 在 SWE-Bench+ 上的 resolved rate 从 33.6% → **0.55%**。
- **Test of Time** (Fatemi et al., Google, 2024-06, [arxiv 2406.09170](https://arxiv.org/abs/2406.09170))：用全合成、保证未在 web 出现过的时序推理题测主流模型，发现 GPT-4 / Claude-3 在 "看起来不难" 的 temporal reasoning 上掉到 30–50%，远低于它们在公开 ZebraLogic / FOLIO 上的分数 — 直接证据是 "公开 benchmark 高分" 至少部分来自记忆。
- **GSM1K** (Scale AI, [arxiv 2405.00332](https://arxiv.org/abs/2405.00332)，2024-05)：复制 GSM8K 出题流程造 1250 题新集，Mistral / Phi 家系列在 GSM1K 上比 GSM8K 掉 8–13 个点，而 GPT-4 / Claude / Gemini 几乎不掉，说明小模型刷分大量来自污染。
- **LiveCodeBench / Codeforces 时间切片**：LiveCodeBench (Jain et al., [arxiv 2403.07974](https://arxiv.org/abs/2403.07974)) 用 "题目发布日 > 模型 knowledge cutoff" 作为切片，反复观测到同一模型在 cutoff 后题目上的 pass@1 比 cutoff 前低 10–20 个点，Codeforces rating 评估也呈相同 pattern（OpenAI o-series tech report 自己也披露过）。
- **MATH / AIME 系列**：2024-2025 已经被反复证明 AoPS 论坛上能搜到带解的题在 pretrain 里大量存在 — 这是 AIME 2024 → AIME 2025 上几乎所有模型掉分的主要解释之一（参考 ScaleAI Humanity's Last Exam blog，2025-01）。

**防御**：

1. **时间切片** 是目前最便宜的 contamination 控制手段。任何 reasoning / coding benchmark 必须报 "cutoff 后子集" 分数。
2. **canary string + n-gram 查重** — 让数据组对自家 pretrain corpus 做 13-gram 命中率扫描（HELM / BigBench 都有现成脚本），命中率 > 1% 的 benchmark 在 official report 里降权或附 footnote。
3. **替身集 (perturbation suite)** — 用 GSM1K / MATH-Perturb / MMLU-Redux 这种 "同分布 held-out" 作 sanity check。任何 official 分数与替身集差距 > 3pp 视为污染警示。
4. **私有 holdout** — Qwen 内部已经在做，建议每次发布都附 "internal private set" 与 public set 的 delta 表格，主动 disclose。

## 2. Goodhart's Law — 一旦挂 OKR 就开始失效

经典表述："When a measure becomes a target, it ceases to be a good measure." 在 LLM 评测里至少有三类典型：

- **MMLU 刷题流水线**：2023–2024 多家把 MMLU 当 OKR，后果是 instruct/SFT 数据里大量 multiple-choice 模板。结果 MMLU 高 5 个点但 free-form QA 不变甚至变差。Anthropic 2024-05 blog "Challenges in evaluating AI systems" 里点名了这个现象。
- **HumanEval 完美主义**：HumanEval pass@1 早在 2024 中就被 frontier 模型刷到 95%+，剩下的 5% 多是题目歧义。继续优化等于在拟合标注噪声，而 SWE-Bench 这种真实任务和 HumanEval 的相关性已经很弱。
- **Chatbot Arena Elo 优化**：见 §4。
- **MATH 上的 thinking-token inflate**：reasoning RL 阶段如果 reward 直接挂 final-answer accuracy，模型很快学会 "无意义长 CoT + 偶尔猜对"，CoT faithfulness 下降但分数上升。Anthropic 2025 "Reasoning models don't always say what they think"（[anthropic.com/research/reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think)）是这类的直接证据。

**给 eval owner 的硬规则**：被列入公司 OKR 的 benchmark 必须同时列 **至少两个不相关 holdout** 作 corroboration；任何 single-number target 都默认会被 game。

## 3. Saturation — 18 个月生命周期

经验观察（按饱和年份）：

| Benchmark | 出生 | 实际饱和 | 寿命 |
|---|---|---|---|
| GLUE | 2018 | 2019 | 12mo |
| SuperGLUE | 2019 | 2020 | 14mo |
| MMLU | 2020 | 2024 (90%+) | 36mo |
| HumanEval | 2021 | 2024 (95%+) | 30mo |
| GSM8K | 2021 | 2024 (97%+) | 30mo |
| MATH | 2021 | 2025 (95%+) | 42mo |
| GPQA Diamond | 2023-11 | 2025 (85%+) | 18mo |
| AIME 2024 | 2024 | 2025 (frontier 90%+) | 12mo |
| SWE-Bench Verified | 2024-08 | 2025-Q4 (Claude 4.5 / GPT-5 75%+) | 14mo |

含义：**任何新 benchmark 出来都要预设 18 个月寿命**，eval roadmap 必须滚动维护。2025–2026 真正还没饱和的：Humanity's Last Exam ([safe.ai/hle](https://safe.ai/hle))、ARC-AGI-2、FrontierMath、NoCha、METR HCAST 长任务 (见下)、SWE-Bench Pro / Multilingual / Live。

**METR HCAST**（[metr.org/blog/2024-11-22-hcast](https://metr.org/blog/2024-11-22-hcast/)，后续 "Measuring AI ability to complete long tasks" [arxiv 2503.14499](https://arxiv.org/abs/2503.14499)）的 "task-length horizon" 框架特别值得借鉴：不是问 "分数多少"，而是问 "模型在哪个人类时长档位以上掉到 50%"。这把 saturation 从 0/1 变成持续刻度，METR 报告 2024-2025 frontier 模型 horizon 大约每 7 个月翻倍。

## 4. Judge / Arena 偏差

**LM-as-Judge** (Zheng et al., MT-Bench paper, [arxiv 2306.05685](https://arxiv.org/abs/2306.05685)) 是过去三年最被滥用的评测范式。已知偏差：

- **Position bias**：A/B 顺序换一下，胜率差 5–15pp。
- **Verbosity bias**：长答案系统性占优，即使内容更差。
- **Self-preference**：GPT-4 当 judge 偏好 GPT-4 的输出，Claude 偏好 Claude — Panickssery et al. [arxiv 2404.13076](https://arxiv.org/abs/2404.13076)。
- **Style over substance**：Markdown 排版、bullet 数量、礼貌语都能拉分。

**LMArena (Chatbot Arena)** 早期被当 "群体智慧 ground truth"，2024–2025 多篇质疑：

- "Style Outweighs Substance" (Li et al., [arxiv 2403.04132](https://arxiv.org/abs/2403.04132)) — 通过 style control 回归，发现 Arena 排名很大一部分由长度 / markdown / 表情符号解释。LMArena 团队 2024 中后期推出 "Style Control" 排行榜作为回应。
- "The Leaderboard Illusion" (Singh et al., 2024-10, [arxiv 2410.11774](https://arxiv.org/abs/2410.11774)) — 系统记录了厂商私下提交多个 variant、只公布最好那个的现象 (sampling bias)；以及 prompt 分布不均、bot vote 等问题。促使 LMArena 2025 引入 "category leaderboards" 与匿名期窗口。
- **Prompt distribution 偏向 chitchat / creative writing**，hard reasoning 占比低 — Qwen-coder / DeepSeek-Coder 类专用模型在 Arena 上被低估是结构性的。

**防御**：

1. Judge 评测必报 **position-swap 平均 + 标准差**，single-pass 一律拒收。
2. Pairwise 设置优先用 **Elo + bootstrap CI**，而不是 raw win rate。
3. 自家模型当 judge 评自家模型 = 自动作废。建议交叉 (Qwen 测 ours 用 Claude/GPT 当 judge，但要标注 judge 模型)。
4. Arena 数字可以引用，但**永远不要单挂 Arena** — 配 reasoning / coding / safety 三类硬指标。
5. **rubric-based judge** (如 Prometheus-2, FLASK) 比 free-form pairwise 偏差小，2025 后逐渐成为内部 SFT/RL preference data 的主流。

## 5. Harness 漂移 — "同一个 benchmark" 在不同代码下分差能到 10pp

最被低估的 reproducibility 杀手。已知 case：

- **MMLU**：lm-evaluation-harness、HELM、Eleuther 老版、OpenAI evals 四套实现，对 logprob normalization、prompt format、5-shot demo 选择都有差异。Llama-2-70B 在不同 harness 下 MMLU 报数从 63 到 70 都有人报过。Hugging Face Open LLM Leaderboard 2024-06 v2 改版的核心动机就是这个 ([huggingface.co/spaces/open-llm-leaderboard/blog](https://huggingface.co/spaces/open-llm-leaderboard/blog))。
- **GSM8K**：strict vs flexible answer matching、是否允许 self-consistency、CoT prompt 模板（"Let's think step by step" vs few-shot）都能让同一个模型差 5–10pp。
- **HumanEval**：temperature、n_samples、stop tokens、是否 strip markdown 都影响 pass@1；BigCode harness 与 OpenAI 原版分数差 2–4pp 是常态。
- **SWE-Bench**：官方 harness 与 SWE-Agent 内置 evaluator 早期不一致，2024 下半年才统一。

**对策**：每次官方汇报必须附：harness commit hash、prompt 模板原文、n_samples、temperature、top_p、stop、scaffold 版本、scoring 脚本。Qwen3 tech report 在这点上已经做得比 OpenAI / Anthropic 好，建议作为内部 SOP 固化。

## 6. Reporting hygiene — 一个数字背后藏的东西

Anthropic 2025 "Adding Error Bars to Evals" ([anthropic.com/research/statistical-approach-to-model-evals](https://www.anthropic.com/research/statistical-approach-to-model-evals/)) 把这件事第一次系统化。最常被偷工减料的：

- **没有 confidence interval** — 单 seed 单 run 的 70.1 vs 71.3 经常被叙述成 "+1.2pp 提升"，实际可能在 noise 内。任何 benchmark < 1000 题或 pass@k k≥1 都应该 bootstrap CI。
- **pass@1 还是 pass@k**：mathematically 不可比。frontier 模型用 maj@64 / pass@8 报，然后被对比的 baseline 是 pass@1 — 这是 2024–2025 PR 稿里最常见的暗箱。
- **avg@n 而非 best-of-n**：reasoning 评测请明确。OpenAI o1 blog 第一版用了 cons@64，社区抗议后改为同时报 pass@1。
- **inference budget**：thinking 模型在 8K / 32K / 128K thinking budget 下分数完全不同。任何 reasoning benchmark 必须报 token budget。
- **n_samples**：AIME 2024 只有 30 题，单 sample 方差极大，必须 ≥ 32 samples 再平均；很多 blog 一次 sample 直接报"满分"。
- **subset cherry-pick**：MMLU-Pro 子集、SWE-Bench Lite vs Verified vs Full 经常混报。

## 给 Qwen eval 团队的硬清单

1. **Roadmap 视角**：维护 "benchmark 生命周期表"，每季度滚动评估饱和度。对未来 6 个月会饱和的指标提前找替代。
2. **Contamination 制度**：每个 release 配 "private holdout vs public" 对照表；pretrain 数据 n-gram 扫描结果作为内部 dashboard。
3. **Single-number ban**：对外 blog 禁止 single benchmark headline (如 "MMLU 88.5")，必须 ≥ 4 类指标并列 + CI。
4. **Judge SOP**：position swap 双跑、CI、cross-family judge、style control 必报。
5. **Harness 复现包**：每次发布同时 release 内部 harness fork (commit hash + Dockerfile)，让第三方能 1-click 复跑。
6. **HCAST / horizon 范式**：把 "task length horizon" 加进 agentic eval roadmap，比单个 SWE-Bench 数字更能反映真实进步。
7. **Goodhart 检测器**：内部新增 "OKR benchmark vs non-OKR benchmark" delta 监控，单边拉开 > 5pp 自动触发 review。

## 推荐外部材料

- [SWE-Bench+ (arxiv 2410.06992)](https://arxiv.org/abs/2410.06992) — 把 SWE-Bench Lite 上 SOTA agent 的 resolved rate 打到 0.55%，是污染 + 弱测试问题最 dramatic 的实证。
- [Test of Time (arxiv 2406.09170)](https://arxiv.org/abs/2406.09170) — 全合成 benchmark 直接打脸公开 reasoning 高分。
- [GSM1K (arxiv 2405.00332)](https://arxiv.org/abs/2405.00332) — GSM8K 的"复刻版 holdout"，小模型刷分的污染证据。
- [Anthropic "Challenges in evaluating AI systems"](https://www.anthropic.com/news/evaluating-ai-systems) — 工业界第一篇系统讲评测危机的官方文章。
- [Anthropic "Adding Error Bars to Evals"](https://www.anthropic.com/research/statistical-approach-to-model-evals/) — 现在做 eval 不带 CI = 不专业。
- [MT-Bench / LLM-as-Judge (arxiv 2306.05685)](https://arxiv.org/abs/2306.05685) — judge 范式的起点，bias 讨论的源头。
- [Style Outweighs Substance (arxiv 2403.04132)](https://arxiv.org/abs/2403.04132) — Arena 的 style bias 量化。
- [Leaderboard Illusion (arxiv 2410.11774)](https://arxiv.org/abs/2410.11774) — Arena 提交策略 / sampling bias 系统分析。
- [Self-preference bias (arxiv 2404.13076)](https://arxiv.org/abs/2404.13076) — judge 偏好自家输出的直接证据。
- [METR HCAST + task horizon (arxiv 2503.14499)](https://arxiv.org/abs/2503.14499) — "task length horizon" 是 saturation 的最佳替代刻度。
- [HF Open LLM Leaderboard v2 blog](https://huggingface.co/spaces/open-llm-leaderboard/blog) — 工业界改 harness 的最佳案例研究。
- [LiveCodeBench (arxiv 2403.07974)](https://arxiv.org/abs/2403.07974) — 时间切片防污染的标杆实践。
