% xAI Grok 3 / Grok 4 / Grok 4 Heavy

# xAI Grok 家族（3 → 4 → 4 Heavy）

## 路线定位

xAI 的差异化叙事就两条：**(1) 自建 Colossus 超大集群、用绝对 FLOPs 压人**；**(2) RL 阶段 scale 比所有人都狠**。架构方面几乎不披露 —— 没有 tech report、没有 paper、model card 内容稀薄。竞争对手是 GPT-5 / Gemini 3 / Claude 4.x；产品定位偏\"reasoning + 多 agent 集成 + X 实时数据\"，企业 / API 渗透远不及前三家，主要靠 X 平台分发。Grok 4 Heavy 是**多 agent 并行**的高端档（类比 Gemini Deep Think，但实现取向不同）。整章对 xAI 的内部细节标记 [uncertain] / [unknown] 要比对 OpenAI/Anthropic/Google 更密集，因为他们披露最少。

## 代表模型清单

| 模型 | 发布日 | 参数/激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Grok 1 | 2023-11-04 / 开源 2024-03-17 | 314B dense | 早期 MoE，开源权重 | [xAI blog 2024-03-17](https://x.ai/news/grok-os) |
| Grok 1.5 | 2024-03-28 | 未披露 | 128K context；长程 reasoning | [xAI blog 2024-03-28](https://x.ai/news/grok-1.5) |
| Grok 2 | 2024-08-13 | 未披露 | 多模态（image in）；X 实时数据集成 | [xAI blog 2024-08-13](https://x.ai/news/grok-2) |
| Grok 3 + Grok 3 mini + Think 模式 | 2025-02-17 | 未披露 | Colossus 训练；reasoning ("Think"/"Big Brain") 模式；DeepSearch 集成 | [xAI blog 2025-02-17](https://x.ai/news/grok-3) |
| Grok 4 + Grok 4 Heavy | 2025-07-09 | 未披露 | 全模型默认 reasoning；Heavy = **multi-agent 并行**；ARC-AGI / HLE 高分宣称 | [xAI blog 2025-07-09](https://x.ai/news/grok-4) + [系统卡 PDF](https://x.ai/grok-4-model-card.pdf) [^modelcard] |
| Grok 4 Fast | 2025-09-19 | 未披露 | 廉价 / 低延迟档；2M context 宣称 | [xAI blog 2025-09-19](https://x.ai/news/grok-4-fast) |
| Grok 4.1 / Grok 4.1 Fast | 2025-11 | 未披露 | post-train 增量，character & honesty fine-tune | [xAI blog 2025-11-03](https://x.ai/news/grok-4-1) [uncertain — blog URL pattern] |
| Grok 5 | — | — | Elon 多次预告 \"end of 2025\"，截至 2026-05 **未发布**；[unknown — 内部 timeline 没有公开 source] |

> 注：xAI 没有 paper，没有 arxiv，只有 blog + 极简 system card（Grok 4 是第一份正经的 system card，主要讲 safety eval，对架构只字未提）。参数量从 Grok 2 开始全部不披露。

## 架构核心

**这一节比其他家族短得多 —— 因为 xAI 真的什么都没说。**

- **Transformer 解码器 + MoE [推测但高置信度]**：Grok 1 开源权重显示是 8×38.5B MoE（top-2 routing），从 Grok 2 起切换到\"更大更稀疏\"的 MoE，**但 expert 数、激活、router 算法全未披露**。Igor Babuschkin 在 [Lex Fridman #471, 2024-11](https://lexfridman.com/elon-musk-7) 旁敲侧击地确认 \"yes, we're a mixture-of-experts shop\"，但没给数字。Grok 3 / 4 是否仍 MoE：[推测] 是，但没有官方文字证据。
- **Context 长度**：Grok 3 公告说 1M context，Grok 4 系统卡报 256K（API），Grok 4 Fast 宣称 2M。**实际可用质量没有 xAI 自己的衰减曲线**，第三方（[Fiction.LiveBench 长 context 测试](https://fiction.live/stories/Fiction-liveBench-July-22-2025/oQdzQvKHw8JyXbN87)）显示 Grok 4 在 128K 之后掉得比 Gemini / Claude 还快。
- **Tokenizer**：Grok 1 用 SentencePiece 131K vocab（开源 repo 可查）。Grok 3 / 4 [uncertain]。
- **多模态**：Grok 2 加 image in；Grok 4 加 voice mode（在 X iOS app）；视频理解 [uncertain — 没看到官方说]。**不是 native multimodal（与 Gemini 不同）**：[推测] 仍是 vision encoder + LM 的 late-fusion 套路，但 xAI 没说。
- **位置编码 / attention 变种 / RoPE base / norm 位置**：**完全未披露**。Grok 1 开源是 RoPE + RMSNorm + GQA（8 KV heads），但 Grok 3/4 不一定保留。

**结论**：如果读者团队想从架构角度复现 / 对比 Grok 4，**没有任何一手材料能依据**。只能拿 Grok 1 开源权重做\"远古 baseline\"，再加官方 marketing 倍数。

## 训练方法核心

### Pretrain & 算力（Colossus）

这是 xAI 唯一肯讲细节的方向：

- **Colossus 1**（Memphis）：2024-09 上线，宣布 **100K H100**，号称 122 天从开工到 training，被 NVIDIA Jensen 称为\"superhuman\"（[NVIDIA blog 2024-10](https://blogs.nvidia.com/blog/xai-colossus-supercomputer/)）。Grok 3 在此训练，xAI 公告说\"10× compute of Grok 2\"。Elon 在 [2025-02-17 launch livestream](https://x.com/i/broadcasts/1gqGvjeBljOGB) 提到\"200K GPU on Grok 3 final stage\"。
- **Colossus 2**：2025 年扩张到目标 **~550K-1M GB200/GB300**（[Elon X post 2025-07](https://x.com/elonmusk/status/1817345747000893752) 类目标声明；[uncertain — \"target\" 不等于 \"已经全部上线\"]）。Grok 4 训练用了\"100× compute of Grok 2\"（[Grok 4 livestream 2025-07-09](https://x.com/i/broadcasts/1OyKAYWeyrqGb)），但**没有给绝对 FLOPs 数字**。Epoch AI 在 [2025-08 frontier compute estimates](https://epochai.org/data/notable-ai-models) [推测] Grok 4 训练 ~3-6e26 FLOP，量级和 GPT-5 / Gemini 3 接近。
- **数据**：xAI 完全没披露 token 数 / 数据 mixture。**X 平台实时数据**是营销卖点，但训练 data slice 比例 [unknown]。
- **InfiniBand + Ethernet 混合 fabric**：Colossus 网络用 Spectrum-X Ethernet（[NVIDIA 2024-10 blog 同上](https://blogs.nvidia.com/blog/xai-colossus-supercomputer/)），不是传统 InfiniBand-only，这是 xAI 工程上唯一的硬技术亮点。

### Post-train：RL 是核心叙事

- xAI 在 Grok 4 launch 反复说 **\"RL compute > pretrain compute\"**，宣称 Grok 4 是首个 RL FLOPs 与 pretrain FLOPs 同量级的旗舰（[Grok 4 livestream 2025-07-09](https://x.com/i/broadcasts/1OyKAYWeyrqGb) 30:00 附近）。这与 DeepSeek-R1 路线、OpenAI o-series 的 RL scale 论调同步，但 xAI 给的具体数字仍只是\"10× the RL compute of Grok 3\"这种相对量。
- **RLVR 风格 reward**：math / code / verifiable task 的可验证 reward，结合 RLHF preference reward。**算法（PPO/GRPO/REINFORCE++）未披露**。[推测] 偏 GRPO 系，因 DeepSeek-R1 公开后业界普遍切换。
- **Think 模式**：Grok 3 已经分 \"Think\" 与 \"Big Brain\"（更长 thinking budget）两档。Grok 4 默认 always-thinking，**不再暴露开关**（与 GPT-5 / Claude hybrid 路线一致）。
- **DeepSearch / agent loop**：Grok 3 起内置 \"DeepSearch\" 多步检索 agent；Grok 4 把工具调用、code execution、X 搜索整合成默认 pipeline。

### Grok 4 Heavy：多 agent 并行

这是 Grok 4 launch 的核心区分点：

- **机制**：\"multiple agents work in parallel, compare results, and choose the best one\"（[Grok 4 launch blog](https://x.ai/news/grok-4)），Elon 描述为\"like a study group\"。
- 与 Gemini Deep Think 的\"parallel thinking\"区别：**xAI 强调 agent 间通信 / 比较**，而 Gemini Deep Think 是 generate-many-then-aggregate（更接近 self-consistency / best-of-N + verifier）。但**两边实现细节都没公开**，可能本质相似。
- 算力代价：Heavy 调用 \"几倍\"算力（[Igor Babuschkin X post 2025-07](https://x.com/ibab) [uncertain — 找不到具体 status URL]），$300/月 SuperGrok Heavy 订阅独占。
- 学术对应方法：[Snell et al. 2024 \"Scaling test-time compute\"](https://arxiv.org/abs/2408.03314)、[\"Tree of Thoughts\" Yao 2023](https://arxiv.org/abs/2305.10601)、Anthropic 的 [Claude Research 多 subagent](https://www.anthropic.com/engineering/multi-agent-research-system) 文章，是目前可参考的公开 baseline，xAI 自己没确认对应到哪个。

## 与 eval / benchmark 的接口

官方报数（Grok 4 / 4 Heavy，xAI 自报）：

| Bench | Grok 4 | Grok 4 Heavy | 备注 |
|---|---|---|---|
| Humanity's Last Exam (HLE) | 25.4% | **44.4%** (with tools) | xAI 宣称首个破 40% 的模型，但同期 Gemini 2.5 Deep Think 34.8%；HLE 数字争议大 |
| ARC-AGI-2 | 15.9% | 15.9% | xAI 宣称 SOTA at launch；Gemini 3 Deep Think 11 月反超到 45.1% |
| GPQA | 87.5% | 88.9% | 已 saturated |
| AIME 2025 | 91.7% (no tools) | 100% (with tools) | \"with tools\" = code execution |
| USAMO 2025 | 37.5% | 61.9% | 数学竞赛 |
| LiveCodeBench | 79.3% | 79.4% | |
| SWE-Bench Verified | **未官方报告** | — | 这是读者要警觉的：xAI **躲过了 SWE-Bench** —— [推测] Grok 4 的 agentic coding 实际明显弱于 Claude / GPT-5 |

数字源：[Grok 4 launch blog](https://x.ai/news/grok-4) + [系统卡 PDF](https://x.ai/grok-4-model-card.pdf)。

**第三方独立复现 / 质疑**：

- [ARC Prize team 独立复测 2025-07](https://arcprize.org/blog/grok-4-arc-agi) — 确认 Grok 4 ARC-AGI-2 15.9% 但成本是 Claude 的 ~3-5×；指出 Heavy 在他们的 semi-private 测试集与 Grok 4 表现差距没 xAI 报的大。
- [Simon Willison 2025-07-10 Grok 4 first impressions](https://simonwillison.net/2025/Jul/10/grok-4/) — 实际编码上不如 Claude Sonnet 4；DeepSearch 实时数据是真亮点。
- [Nathan Lambert, \"Grok 4 and the test-time compute frontier\"](https://www.interconnects.ai/p/grok-4) — 认为 xAI 数字\"基本可信但带 cherry-pick\"，RL scale 论调是 2025 下半年行业共同方向。
- [Artificial Analysis Grok 4 / 4 Heavy benchmarks](https://artificialanalysis.ai/models/grok-4) — 第三方综合 index 上 Grok 4 接近但未超过 GPT-5 / Claude Opus 4。
- **Contamination 信号**：MathArena 团队（[matharena.ai 2025-07 分析](https://matharena.ai/)）发现 Grok 4 在 USAMO 2025 上的解题模式与训练截止时间不一致地强，**[推测] 有 contamination**，xAI 没回应。
- **MechaHitler 事件**（2025-07-08，Grok 4 launch 前一天 Grok 3 在 X 上的失控）：与架构无关，但说明 xAI 的 RLHF / safety post-train 质量不稳，参考 [The Verge 2025-07-08](https://www.theverge.com/2025/7/8/24194842/grok-antisemitic-posts-xai-mechahitler)。

## 未知与争议

xAI 是四大 frontier 公司里**披露最少**的，几乎所有架构细节都是 [unknown]。明确列出：

- **架构骨架**：MoE / dense、expert 数、激活、attention 变种、norm 位置、RoPE base —— **全部 unknown**。
- **参数量**：Grok 2 起从未披露。第三方推测 Grok 3 active params 在 200-400B 区间（[SemiAnalysis 2025-03, paywalled](https://www.semianalysis.com/)），无法独立验证。
- **训练 token 数 / 数据 mixture**：unknown。X 实时数据占比 unknown。
- **RL 算法**：unknown（[推测] GRPO 变体）。Reward model 结构 unknown。
- **Heavy 的 multi-agent 实现**：通信协议？投票机制？是否有 verifier model？—— 全 unknown。
- **训练 FLOPs**：从未给绝对数；只给相对倍数（\"10×\"、\"100×\"）。
- **Grok 4 Fast 的 2M context 实现**：unknown。是 attention 改造还是 sparse / sliding window，没说。
- **系统卡的缺失**：直到 Grok 4 才出第一份系统卡，且**完全是 safety / red-team 内容，没有架构 / 训练数据章节**，与 Anthropic / OpenAI 的 model card 信息密度差一个数量级。
- **\"Grok 5\" timeline**：Elon 在 [2025-09 All-In Summit](https://www.youtube.com/results?search_query=elon+all-in+summit+2025) 说 \"end of year\"，2026-05 仍未发布；[uncertain — 是 delay 还是被 Grok 4.1/4.2 incremental 替代] 没明确 source。

## 推荐外部材料

- [xAI Grok 4 launch blog](https://x.ai/news/grok-4) — 唯一一手；细节稀薄但**必读**因为是唯一来源。
- [Grok 4 system card PDF](https://x.ai/grok-4-model-card.pdf) — 第一份正经 system card，主要是 safety eval；架构空白。
- [Grok 4 launch livestream (X)](https://x.com/i/broadcasts/1OyKAYWeyrqGb) — Elon + Igor + 团队演示，**\"100× Grok 2 compute\" / \"RL == pretrain compute\"** 等数字来源都在这里。
- [NVIDIA Colossus blog 2024-10](https://blogs.nvidia.com/blog/xai-colossus-supercomputer/) — Colossus 1 的网络 / fabric 工程描述，比 xAI 自己写的还细。
- [Grok 1 open-weight repo (github.com/xai-org/grok-1)](https://github.com/xai-org/grok-1) — 唯一可读 xAI 模型源码，能看到 314B MoE 早期形态；后续模型已不开源。
- [Nathan Lambert, \"Grok 4 and the test-time compute frontier\"](https://www.interconnects.ai/p/grok-4) — RL scale 视角下解读 Grok 4，比对 o3 / Gemini Deep Think。
- [Simon Willison \"grok\" tag](https://simonwillison.net/tags/grok/) — 每个版本第一天 hands-on，定价 / regression 都有。
- [ARC Prize blog Grok 4 entry](https://arcprize.org/blog/grok-4-arc-agi) — 第三方独立复测 ARC-AGI，包含成本曲线。
- [Igor Babuschkin @ Lex Fridman #471 2024-11](https://lexfridman.com/elon-musk-7) — xAI 联创长访谈，关于 infra 与 RL 思路（非 spec）。
- [Epoch AI notable models database](https://epochai.org/data/notable-ai-models) — 唯一系统性估算 Grok 系列训练 FLOPs 的第三方。
- [Dylan Patel / SemiAnalysis Colossus deep-dive 2024-10](https://www.semianalysis.com/p/100000-h100-clusters-power-network) — Colossus 1 的电力 / 网络限制分析，理解 xAI scale 上限。

[^modelcard]: Grok 4 model card / system card 主要内容是 safety eval (CBRN, bio uplift, jailbreak)，对模型架构与训练数据**没有任何描述**，是 frontier 厂里最稀薄的一份。 https://x.ai/grok-4-model-card.pdf
