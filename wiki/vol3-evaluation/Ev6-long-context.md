## Ev6 长上下文评测 — NIAH 已死，真正的 benchmark 长什么样

## 路线定位

2023 H2 起所有 frontier 模型都报 "1M / 2M / 10M context"，宣传图清一色 Greg Kamradt 的 Needle-in-a-Haystack 绿色热图。问题是：**NIAH 早在 2024 年就饱和了**——GPT-4-Turbo / Claude-3 / Gemini-1.5 全部接近 100%，而它们在真实长文档 QA、长 agent trace、长代码 repo 上的表现差异极大。这一节把 2024–2026 这两年间把"长上下文"从"会不会捞一根针"重新定义成"会不会真的用这堆 token"的几个关键 benchmark 串起来：RULER / HELMET / ∞Bench / NoCha / LongBench v2 / Fiction.LiveBench / BABILong。给 Qwen eval 团队的核心建议：**官方报告里如果还在用裸 NIAH 当长上下文证据，直接打回**。

## NIAH 的兴起与死亡

- **起源**：Greg Kamradt 2023-11 在 GitHub `gkamradt/LLMTest_NeedleInAHaystack` 提出的玩具脚本——把一句 "The best thing to do in San Francisco is eat a sandwich and sit in Dolores Park on a sunny day" 插进 Paul Graham essays，问模型 "What is the best thing to do in SF?"。绿色 = 答对，红色 = 答错。([repo](https://github.com/gkamradt/LLMTest_NeedleInAHaystack))
- 之所以爆火：Anthropic Claude 2.1 → 100K 发布时官方就用这张图自证，Google Gemini 1.5 Pro tech report 在 1M / 10M 上画了多 needle 版本，几乎所有 frontier 厂跟进。
- **2024 中起 NIAH 的几个致命缺陷被反复揭穿**：
  1. 单针 = 纯 lexical retrieval，只测 attention 能不能 hit 一个 surface token，跟 reasoning 无关。
  2. needle 与 haystack 在分布上严重不一致（PG essay 里突然出现一句 SF sandwich），模型靠 surprise 就能定位，本质是 OOD detection。
  3. multi-needle / needle-in-needle 变体仍然是 retrieval，没有跨 needle 的合成推理。
  4. 长度坐标轴的"绿色"早已饱和，无法区分 200K 的 Claude-3.5 和 1M 的 Gemini-1.5。
- 一句话总结被 RULER 论文官方化：*"passkey-style NIAH overestimates effective context length by a wide margin"*（Hsieh et al., NVIDIA, [arxiv 2404.06654](https://arxiv.org/abs/2404.06654)）。

## RULER — NIAH 的合法继承人（NVIDIA, 2024-04）

[arxiv 2404.06654](https://arxiv.org/abs/2404.06654)

- 13 个任务，4 类：**Retrieval**（multi-key / multi-value / multi-query NIAH 扩展）、**Multi-hop tracing**（variable tracking）、**Aggregation**（common / frequent words extraction）、**QA**（基于 SQuAD/HotpotQA 的长文档版本）。
- 长度从 4K 到 128K（后续社区扩到 1M），输出 "effective context length" = 模型分数仍 ≥ Llama2-7B-4K baseline 的最长长度。
- 经典发现（2024-04 版表格）：宣称支持 128K+ 的 10 个模型里，**只有 4 个 effective length 真的 ≥ 32K**（GPT-4, Command-R+, Yi-34B-200K, Mixtral-8x7B）。Gemini 1.5 Pro 在 128K RULER 上还是显著掉点（虽然单 needle 100%）。
- 2025 年起 RULER 成了"长上下文事实标准"：Llama-3.1 / Qwen-2.5 / Qwen3 / DeepSeek-V3 / Kimi-K2 / GLM-4.5 / MiniMax-M1 / Gemini-2.5 全部官方汇报 RULER@128K（部分到 1M）。
- 局限：仍以 synthetic 为主，QA 子任务对答案 surface form 敏感；不能反映 agent / coding 场景。

## HELMET — 把"长上下文"从 retrieval 解耦到能力维度（Princeton, 2024-10）

Yen, Gao, Hou et al., [arxiv 2410.02694](https://arxiv.org/abs/2410.02694), 网站 [princeton-nlp.github.io/HELMET](https://princeton-nlp.github.io/HELMET/)

- 动机：RULER 仍偏 retrieval，HELMET 强调"应用导向 + 模型可区分性 + reliable metrics"。
- 7 类任务，覆盖 8K → 128K：**RAG**（NQ/TriviaQA/HotpotQA/PopQA at length）、**Generation with citations**（ALCE）、**Re-ranking**（MS MARCO）、**Long-doc QA**（NarrativeQA / ∞Bench / QASPER）、**Summarization**（Multi-LexSum / InfBench Sum）、**In-context learning many-shot**（TREC/Banking77/NLU/CLINC）、**Synthetic recall**（RULER NIAH 子集做 sanity check）。
- 关键 finding（论文 §5）：
  - **任务之间 rank correlation 很低**——synthetic NIAH 高分不能预测 RAG/Summ；RAG 高分不能预测 ICL many-shot。也就是说"一个 long-context 分数"是伪命题。
  - **open-weight 模型在 32K 以后普遍崩塌**，即使官方 spec 写 128K（Llama-3-8B-Instruct-Gradient 1M 在 HELMET 32K RAG 已经掉到接近 0）。
  - **closed model 也分化**：GPT-4o > Claude-3.5-Sonnet > Gemini-1.5-Pro 在 cite / summ 上，但 Gemini 在纯 recall 上更稳。
- 2025 后续：HELMET 加了 v1.1（包含 multi-turn agent trace 与 code repo QA），是目前学术界引用最多的 long-context 综合 suite。

## ∞Bench / LongBench v2 — 长文档真实任务

- **∞Bench** (Zhang et al., THU, [arxiv 2402.13718](https://arxiv.org/abs/2402.13718))：第一个平均长度 > 100K 的 benchmark。12 任务覆盖英文/中文小说 QA、code debug、math computation、retrieve KV。今天主要作为 HELMET 的 long-doc QA 子集存在。
- **LongBench v2** (Bai et al., THU, 2024-12, [arxiv 2412.15204](https://arxiv.org/abs/2412.15204))：v1 (2023) 偏短且饱和，v2 重做：503 道多选题，长度 8K–2M（中位 ≈100K），人类专家答题平均 53.7%，o1-preview 57.7%。重点：
  - 全部题目 **人工撰写 + 人类专家无法靠搜索秒答**，单题需要跨段聚合 / multi-hop / long-dialogue understanding / code repo navigation。
  - 提供 w/ CoT 与 w/o CoT 两栏，**CoT 在长上下文上带来的提升远大于短上下文**（o1 类模型尤其受益）——这是后来 DeepSeek-R1 / Qwen3-Thinking 都把 long-context + thinking 一起调的实证依据。
  - 2025–2026 主要 frontier 报告（GPT-5, Claude 4.5 Sonnet, Gemini 2.5 Pro, Qwen3-Max, Kimi-K2）都报 LongBench v2，是替代 v1 的事实标准。

## NoCha — 真·长篇小说推理（UMD, 2024-06）

Karpinska et al., "One Thousand and One Pairs: A 'novel' challenge for long-context language models"，[arxiv 2406.16264](https://arxiv.org/abs/2406.16264)，leaderboard [novelchallenge.github.io](https://novelchallenge.github.io/)

- 1001 对 true/false claim，来自 67 本近期英文小说（大部分 2023 年后出版，规避 pretrain 污染）。每对一句 true / 一句 false，关于同一情节，模型要两条都答对才算分。
- 平均书长 127K tokens（最长 336K）。**关键设计**：claim 是 book-level 的（"X 角色在故事最后才意识到 Y"），不能靠局部 retrieval 解决，必须 global narrative understanding。
- 结果（2024-06 paper 原版）：
  - 人类标注员 ≈ 97%。
  - Claude-3-Opus（当时最强）55.8%；GPT-4-Turbo 33%；Gemini-1.5-Pro 48%。
  - 在 NIAH 上 100% 的模型，在 NoCha 上接近 random（50%）。
- 2025 leaderboard 更新：GPT-5 / Claude 4.5 Opus 进到 70+，Gemini 2.5 Pro 65 左右，**但仍远低于人类，且开源模型（Qwen3-235B / DeepSeek-V3.x / Llama-4-Maverick）均在 50–60 区间**。NoCha 至今仍未饱和，是 frontier 长上下文 ceiling 的最好指示器之一。

## Fiction.LiveBench — 社区驱动的 deep-comprehension 长文 benchmark

[fiction.live/stories/Fiction-liveBench](https://fiction.live/stories/Fiction-liveBench-Mar-25-2025/oQdzQvKHw8JyXbN87)

- 由互动小说平台 fiction.live 维护，每月更新。任务：把一段长故事（1K–192K token，从短到长多档）喂给模型，问关于人物关系 / 情节伏笔 / 时序的多选题。
- 与 NoCha 互补：NoCha 是 book-level true/false，Fiction.LiveBench 是 mid-length 多档 + 多选 + 月更，能看出"context length scaling curve"。
- 2025 之后被 Twitter 上 long-context 圈广为引用，因为它**第一个清楚显示 thinking 模型（o1, o3, R1, Qwen3-Thinking, Claude-thinking）在 ≥ 60K 上比 non-thinking 显著更稳**。GPT-5-thinking / Gemini-2.5-Deep-Think 在 192K 档仍能保持 60%+，而几乎所有 non-thinking 开源在 60K 后掉到 30% 以下。
- 注意：非学术 benchmark，题目 pool 不完全公开，存在 prompt leak / 选择偏差风险——做 official 汇报别拿它当主指标，但作为 sanity check 很有价值。

## BABILong — 把 bAbI 任务塞进长 haystack（AIRI, 2024-06）

Kuratov et al., [arxiv 2406.10149](https://arxiv.org/abs/2406.10149)

- 思路：经典 bAbI 20 个 reasoning 任务（chain of facts, counting, induction, deduction…），把相关 facts 散布到 PG-19 长文本里，长度档从 1K 到 10M token。
- 卖点：**唯一一个测到 10M context 的公开 benchmark**，Gemini-1.5 / Magic-Dev / RecurrentGemma / Mamba 系都拿它当 marketing。
- 实际结果：所有模型在 ≥ 1M 长度上的多 fact 推理任务接近 random；即使在 128K，多数模型也只在 single-fact retrieval 上保留 NIAH 级别表现。BABILong 已经成为"长度宣传水分检测器"。

## 给 Qwen eval 团队的可执行建议

1. **裸 NIAH 仍可保留作 sanity check，但不能作为 long-context 主要证据。** 任何官方表 / blog 必须配 RULER@当前 max length + HELMET 至少 RAG/Summ/Cite 三类 + LongBench v2 + NoCha。
2. **报告 "effective context length" 而不是 spec length。** 用 RULER 的 baseline 阈值法或 HELMET 的 task-by-task 衰减曲线。Qwen3 系列从 Qwen3-Coder 开始已经这么做了，继续坚持。
3. **Thinking 与 non-thinking 分开报。** Fiction.LiveBench + LongBench v2 都证明 thinking 在长上下文上是结构性增益，混在一起会高估 base model。
4. **NoCha 必报。** 这是目前最难被 contamination 的长上下文 benchmark，对开源模型与 frontier 闭源的 gap 最敏感。
5. **小心 10M / ∞ context 的 marketing 图。** BABILong / RULER 在 1M+ 上的真实数字应该和 spec 长度并列展示，否则就是误导。

## 推荐外部材料

- [RULER paper (arxiv 2404.06654)](https://arxiv.org/abs/2404.06654) — NVIDIA，目前最广泛使用的长上下文标准；"effective context length" 概念的来源。
- [HELMET paper + site](https://princeton-nlp.github.io/HELMET/) — Princeton，task-decoupled 设计，长上下文综合 suite 首选。
- [NoCha leaderboard](https://novelchallenge.github.io/) — 至今未饱和，frontier ceiling 指示器。
- [LongBench v2 (arxiv 2412.15204)](https://arxiv.org/abs/2412.15204) — 真实长文档多选，人类专家也只有 53.7%。
- [Greg Kamradt NIAH repo](https://github.com/gkamradt/LLMTest_NeedleInAHaystack) — 历史源头，今天主要价值是"反面教材 + sanity check"。
- [BABILong (arxiv 2406.10149)](https://arxiv.org/abs/2406.10149) — 10M context 唯一公开 benchmark，揭穿长度营销。
- [Fiction.LiveBench](https://fiction.live/stories/Fiction-liveBench-Mar-25-2025/oQdzQvKHw8JyXbN87) — 月更，最早把 thinking × long-context 的 gap 量化出来的社区 benchmark。
- [∞Bench (arxiv 2402.13718)](https://arxiv.org/abs/2402.13718) — 第一个 100K+ 平均长度 suite，今天主要作为 HELMET 子集存在。
