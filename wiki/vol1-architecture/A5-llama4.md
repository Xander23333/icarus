# Llama 4 家族（Scout / Maverick / Behemoth）+ 4.5/5 传闻

## 路线定位

Llama 4 是 Meta **第一代原生 MoE + 原生多模态（early-fusion）+ 超长 ctx (iRoPE)** 的开源（open-weights，license 受限）家族，2025-04-05 与 LlamaCon 同日抢发。技术上想一次性追平三件事：DeepSeek-V3 的 MoE 效率、Gemini 的 1-10M 长 ctx、GPT-4o 的原生多模态。结果是**架构野心很大、训练执行翻车**——Behemoth 直到 2026-05 仍未发布且被多家媒体报道 [事实上搁置](https://www.theinformation.com/articles/meta-delays-flagship-ai-model-amid-disappointing-performance)，Maverick 的 LMArena 提交事件让 Meta 在 open 社区信誉受损。竞品上：open 圈对位 DeepSeek-V3 / Qwen3-235B-A22B / Kimi K2，closed 圈对位 GPT-4o / Gemini 2.5 Flash。对焱拳团队的可比性：Llama 4 MoE 与 Qwen3-MoE 是**同时期最直接的两条 MoE 路线**，差异点（active 大小、shared expert、interleave dense/MoE、no-aux-loss vs aux-loss）下面会逐条对照。

## 代表模型清单

| 模型 | 发布日 | 参数 / 激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Llama 4 Scout | 2025-04-05 | 109B / **17B act**，16 routed experts + 1 shared | 单 H100 (Int4) 可跑，**10M ctx** (iRoPE)，early-fusion vision | [ai.meta.com blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/), [HF model card](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct) |
| Llama 4 Maverick | 2025-04-05 | **400B / 17B act**，128 routed + 1 shared，**dense/MoE 交替** | 1M ctx，多模态对位 GPT-4o | [ai.meta.com blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/), [HF Maverick card](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct) |
| Llama-4-Maverick-03-26-Experimental | 2025-03-26 (仅 LMArena) | 同上权重 + 实验性 chat post-train | **LMArena 提交事件主角**，与公开权重不同 | [LMArena 声明 2025-04-08](https://blog.lmarena.ai/blog/2025/maverick-tracker/) |
| Llama 4 Behemoth (preview) | preview only | **~2T / 288B act**，16 experts | 内部 teacher，蒸馏 Scout/Maverick 用 | [ai.meta.com blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) |
| Llama 4 Reasoning | 预告 LlamaCon 2025 | 未发布 | Zuckerberg LlamaCon keynote 提及，2025-06 后无下文 | [LlamaCon 2025 keynote (YouTube)](https://www.youtube.com/watch?v=FZ-RZ0dKO8o) |
| Llama 4.5 / Llama 5 | — | — | [unknown — 截至 2026-05 没有官方 4.5 或 5 release。2025-06 Meta 成立 \"Superintelligence Labs\"（[Bloomberg 2025-06-30](https://www.bloomberg.com/news/articles/2025-06-30/meta-creates-new-superintelligence-ai-group-led-by-scale-s-wang)），Alexandr Wang 主导，传 Llama 5 推倒重来；Behemoth 被多次报\"无限期搁置\"（[The Information 2025-05](https://www.theinformation.com/articles/meta-delays-flagship-ai-model-amid-disappointing-performance)、[WSJ 2025-08](https://www.wsj.com/tech/ai/meta-ai-llama-behemoth-delay)）。不强行编造日期] | — |

## 架构核心

### MoE 结构：interleaved dense / MoE + shared expert

> [Llama 4 blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)、[HF Maverick model card](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct) 的 config.json。

- **Maverick**：transformer block **dense ↔ MoE 交替**（odd 层 dense FFN，even 层 MoE，或反之，blog 没明说顺序；从 HF config `interleave_moe_layer_step=1` 推断是 1:1 交替）。128 routed experts + 1 shared，**top-1 routing**（不是 DeepSeek 的 top-8）。这导致虽然 expert 多但 selection 粒度极粗。
- **Scout**：**每层都是 MoE**（`interleave_moe_layer_step=1` 但配 16 experts），16 routed + 1 shared，top-1。
- **Shared expert**：和 DeepSeekMoE 同思路，每 token 必过 1 个 shared FFN 承担 common knowledge。
- **激活规模 17B 是刻意选的**：对位 Llama 3.3-70B 的 70B dense，宣称 inference cost 远低于 70B dense 同时 quality 持平/更好。Scout int4 可单卡 H100 部署是 marketing 主打。
- **vs Qwen3-MoE / DeepSeek-V3 对比**（焱拳关心的点）：

| | DeepSeek-V3 | Qwen3-235B-A22B | Llama 4 Maverick | Llama 4 Scout |
|---|---|---|---|---|
| 总参/激活 | 671B / 37B | 235B / 22B | 400B / 17B | 109B / 17B |
| Routed experts | 256 | 128 | 128 | 16 |
| Top-k | 8 | 8 | **1** | **1** |
| Shared expert | 1 | 0（Qwen3 取消了 V2 的 shared）| 1 | 1 |
| Dense/MoE 交替 | 全 MoE（前 3 层 dense） | 全 MoE | **1:1 交替** | 全 MoE |
| LB 策略 | aux-loss-free (bias controller) | aux-loss-free + 微小 z-loss | [unknown — blog 未披露，HF code 里看不到 bias controller] | 同 |
| Granularity | fine-grained | fine-grained | **coarse**（top-1 + 大 expert） | coarse |

  **Llama 4 在 MoE 设计上选了和 DeepSeek/Qwen3 相反的方向**：少 expert、大 expert、top-1。理论上 top-1 会让训练 LB 更难（gradient signal 稀疏），Llama 4 怎么稳住的 blog 没说。这也是 Scout 上长 ctx 评估翻车（见下文）的可能根因之一 [推测]。

### iRoPE（interleaved RoPE / NoPE）—— 长 ctx 的关键技巧

> blog 只用 \"interleaved attention layers without positional embeddings\" 一句话带过；细节靠 [HF transformers 实现](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama4/modeling_llama4.py) 和 Sebastian Raschka [The Big LLM Architecture Comparison 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) 反推。

- **大部分层用 RoPE**，**每隔若干层有一层完全不加位置编码（NoPE）**。NoPE 思路来自 [Kazemnejad et al. 2023 \"Impact of Positional Encoding on Length Generalization\" (arxiv:2305.19466)](https://arxiv.org/abs/2305.19466)：causal attention 本身就有隐式位置信息，去掉显式 PE 反而长度外推更好。
- Scout 的 ratio 是 **每 4 层一层 NoPE**（HF code `no_rope_layers` 索引），即 3 RoPE + 1 NoPE 循环。
- **训练时只在 256K 上训**，靠 NoPE 层的长度外推宣称跑到 **10M ctx**（Scout）/ 1M（Maverick）。
- 推理时 RoPE 层用了 **inference-time temperature scaling on attention logits**（blog 提了一句 \"scaling of attention at inference time\"），细节未公开。
- **争议**：10M ctx 是结构上能 forward pass，但**实际 retrieval 质量极差**。[Fiction.LiveBench 长 ctx 测](https://fiction.live/stories/Fiction-liveBench-Mar-25-2025/oQdzQvKHw8JyXbN87) 报 Scout 在 60K 以上就显著退化，128K 时 needle-in-haystack 之外的多跳召回接近随机。这点 r/LocalLLaMA 多个帖子（[\"Llama 4 Scout 10M context is a lie\"](https://www.reddit.com/r/LocalLLaMA/comments/1jt7hlc/) 等）独立确认。换句话说：**10M 是\"训练支持的 max ctx 配置\"，不是\"有用的 ctx\"**。

### Early-fusion 多模态

> blog \"Early fusion enables joint pre-training with text and vision tokens\" 段；架构图见 [ai.meta.com blog 图 2](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)。

- **Early-fusion** = vision token 和 text token 在**主 transformer backbone 第 0 层之前就拼到同一序列**里，共用所有 attention/FFN。和 Llama 3.2 Vision、IDEFICS 那种 \"frozen vision encoder + cross-attention adapter\" 的 late-fusion 形成对比，和 Gemini / Chameleon 同路。
- Vision encoder 基于改进的 **MetaCLIP**，blog 称重训过、token 化策略改了（具体 patch size / token count 没披露）。
- Pretrain 阶段就喂 **混合 text + image + video token**（30T+ multi-modal token，是 Llama 3 的 2 倍），不再走\"先文本再 vision adapter 接\"的两段式。
- 实际效果：MMMU、ChartQA 等视觉 bench 上 Maverick 接近 GPT-4o，但**没有原生输出图像/音频**（仅 input 多模态，output 仍是 text）。对比 GPT-4o 的 \"true any-to-any\" 还差一截。

### 其他

- Tokenizer：仍是 BBPE，词表扩到 **202K**（Llama 3 是 128K），加了更多多语言 + 代码 token。
- Attention head 数 / dim：Maverick `num_attention_heads=128, num_kv_heads=8`，GQA 16:1；Scout 类似。MLA 没采用（Meta 在 Llama 3 时期就坚持 GQA，4 代未变）。
- Norm：RMSNorm；activation：SwiGLU。和 Llama 3 一致。
- **没有 MTP**，**没有 FP8 训练公开披露**（blog 提 \"FP8 precision\" 一次，没 V3 那样的 fine-grained scaling 细节）。

## 训练方法核心

### Pretrain

- **>30T token** 混合 text + image + video（Scout 40T，Maverick 22T，blog 报）。Llama 3 是 15T。语言覆盖扩到 200+，但 Meta 自己说**精细 fine-tune 覆盖 12 种**。
- 训练硬件：**32K H100** 集群规模（[Meta blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)），FP8 precision（细节未披露）。
- **MetaP**：blog 提到一个新技巧叫 MetaP，\"reliably set critical model hyper-parameters such as per-layer learning rates and initialization scales\"。看描述像 μP / MuP 的变体（hyperparameter transfer across scale），但没 paper，**实现细节未知**。
- RoPE base / NoPE 层比例 / long-ctx training schedule：blog 没给数字，HF config 里 `rope_theta=500000`（同 Llama 3.1）。

### Mid-train / Annealing

- blog 提到一个 \"mid-training\" 阶段专门做 **long-context 扩展 + 关键能力补强**。具体 token 数 / schedule 未披露。Scout 10M 的能力据称是这里训出来的。

### Post-train

新 pipeline，三步（[blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) §Post-training）：
1. **Lightweight SFT**（仅占老 pipeline 数据量的一小部分，因为 Meta 发现\"过度 SFT 限制 RL 探索\"——这一论断与 DeepSeek-R1-Zero 的发现一致）。
2. **Online RL**（continuous RL，没说是不是 GRPO；prompt 难度 adaptive 筛选）。
3. **Lightweight DPO** 收尾。

无具体 reward model 细节，无 RLVR claim（不像 R1 那样 verifiable reward）。这套 \"少 SFT、多 RL、DPO 兜底\" 的配方思路是合理的，但实际产出（特别是 reasoning 能力）远低于同期 DeepSeek-R1 和 Qwen3-Thinking。

### Behemoth 蒸馏

Scout/Maverick 都是从 Behemoth **codistilled**（blog 用词）。具体蒸馏 loss / 是 logit 蒸馏还是数据蒸馏未披露。Behemoth 本身从未公开发布。

## 与 eval / benchmark 的接口

官方 headline（[blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) 表格）：

| Bench | Scout | Maverick | Behemoth (preview) |
|---|---|---|---|
| MMLU-Pro | 74.3 | 80.5 | 82.2 |
| GPQA Diamond | 57.2 | 69.8 | 73.7 |
| MATH-500 | — | — | 95.0 |
| LiveCodeBench | 32.8 | 43.4 | 49.4 |
| MMMU | 69.4 | 73.4 | 76.1 |
| ChartQA | 88.8 | 90.0 | — |
| DocVQA | 94.4 | 94.4 | — |

第三方 / 复现：
- **Aider polyglot**：Maverick 16%（[aider.chat leaderboard](https://aider.chat/docs/leaderboards/)），远低于 DeepSeek-V3 的 48% 和 Sonnet 3.7 的 65%。Coding 实战与 headline 差距大。
- **LiveBench**：Scout/Maverick 综合排在 DeepSeek-V3 之下、Qwen2.5-72B-Instruct 之上，并未达到 \"GPT-4o 级别\" 的宣传。
- **Fiction.LiveBench long-ctx**：Scout 在 60K+ 显著退化，10M 实际不可用（见 iRoPE 节）。
- **SimpleBench / EQ-Bench / MMLU-Redux**：均报告 Llama 4 比 Llama 3.3-70B Instruct **不一定更强**，多个 dimension 退步。

### 🚨 LMArena 提交事件（2025-04 最大争议）

时间线：
- 2025-04-05 Meta 发布 Llama 4，宣传 \"Maverick 在 LMArena 排名第 2，仅次于 Gemini 2.5 Pro\"，ELO 1417。
- 网友很快发现 LMArena 上跑的是名为 **\"Llama-4-Maverick-03-26-Experimental\"** 的版本，**与 HuggingFace 上的开源权重不是同一个**。
- 2025-04-08 [LMArena 官方声明](https://blog.lmarena.ai/blog/2025/maverick-tracker/)：Meta 提交的是\"专为 conversational chat 优化的实验版本\"，违反了 \"submit the same model you release\" 的隐性约定；LMArena 把开源权重重新跑了一遍，ELO 掉到 **~1271**（第 32 名档），与公开权重的实际 chat 能力一致。
- LMArena 同时公开了两版 sample output 对比：experimental 版极度 emoji 化 + 谄媚化（典型 chatbot arena hack）。
- Meta 回应（[VP Ahmad Al-Dahle on X 2025-04-07](https://x.com/Ahmad_Al_Dahle/status/1909302532306092253)）：承认 03-26 版是 \"experimental chat version\"，否认 \"在测试集上训练\"，但没解释为什么宣发用了那个版本的分数。
- 行业影响：**这是 2025 年公共信誉损害最严重的开源 release 事件**。直接导致 LMArena 后续更新 submission policy 要求版本一致性；也让\"LMArena ELO 作为唯一指标\"的合法性受到广泛质疑（Lambert、Hardmaru、karpathy 都发声）。

### 已知 contamination / overfit 信号

- Behemoth preview 分数（特别是 MATH-500 95.0）社区无法独立验证（模型从未发布）。
- Maverick 在 MMLU-Pro 80.5 与第三方独立复现（74-76 区间）有 4-5pt 落差，但 contamination 的直接证据没有，目前定性为 \"宣发选用了最有利评测配置\"。

## 未知与争议

- **Behemoth 是否会发布**：截至 2026-05 仍 preview-only。[The Information 2025-05](https://www.theinformation.com/articles/meta-delays-flagship-ai-model-amid-disappointing-performance) 和 [Reuters 2025-08](https://www.reuters.com/technology/) 报道 Meta 内部对 Behemoth 性能不满，发布无限期搁置。Zuckerberg 在 Q2 2025 财报会上回避了具体时间表（[Meta Q2 2025 earnings call transcript](https://www.fool.com/earnings/call-transcripts/2025/07/30/meta-platforms-meta-q2-2025-earnings-call-transcr/)）。
- **Llama 4 Reasoning model**：LlamaCon 2025-04 keynote 预告了一个 reasoning 专用模型，至今未发。
- **Llama 4.5 / 5**：2025-06 Meta 成立 Superintelligence Labs，Alexandr Wang 任 Chief AI Officer，[Bloomberg 报道](https://www.bloomberg.com/news/articles/2025-06-30/meta-creates-new-superintelligence-ai-group-led-by-scale-s-wang)称新团队\"重新评估\"了 Llama 路线图，旧 GenAI org 与新 lab 并行。多家媒体（[The Information 2025-09](https://www.theinformation.com/articles/) 等）传 \"Llama 5 推倒重来\"，但具体架构方向、是否仍走 MoE、是否走 hybrid reasoning 均**无一手 source**。截至 2026-05 没有任何官方 Llama 4.5 / 5 release 或 paper。
- **MetaP 细节**：blog 提了名字，没 paper，社区只能猜测是 μP-like hyperparameter transfer。
- **Aux-loss-free LB 是否采用**：HF code 里看不到 bias controller，疑似 Meta 仍在用 aux loss。未确认。
- **License 限制**：>700M MAU 公司不能用，欧盟用户在多模态模型上受限——这让 Llama 4 在严格意义上 **不是 OSI 定义的 open source**，社区一直有意见。

## 推荐外部材料

- [Meta Llama 4 官方 blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) — 一手 source，架构 + 训练 + 安全四个 section，注意宣传腔，对 \"10M ctx\"、\"LMArena 第二\" 这类 claim 要交叉验证。
- [Sebastian Raschka, \"The Big LLM Architecture Comparison\" 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) — 把 Llama 4、Qwen3、DeepSeek-V3、Kimi K2、GPT-OSS 并排画架构图，**iRoPE / interleaved MoE 这两节是目前最清楚的二手讲解**。
- [LMArena Maverick tracker 声明](https://blog.lmarena.ai/blog/2025/maverick-tracker/) — LMArena 事件官方说明 + ELO 对比数据，做评测的人必读。
- [r/LocalLLaMA \"Llama 4 Scout 10M context is a lie\" 帖](https://www.reddit.com/r/LocalLLaMA/comments/1jt7hlc/) — 社区对长 ctx 实际表现的最早系统质疑，含多个 needle-in-haystack 复现。
- [Fiction.LiveBench 长 ctx 排行](https://fiction.live/stories/Fiction-liveBench-Mar-25-2025/oQdzQvKHw8JyXbN87) — Scout/Maverick 长 ctx 实测掉分曲线，可直接拿来回击\"10M 宣发\"。
- [Nathan Lambert, \"Llama 4: post-truth model release\" interconnects.ai 2025-04](https://www.interconnects.ai/p/llama-4) — RL/post-train 视角分析 Meta 翻车原因，把 Llama 4 放在\"frontier open-weight 节奏\"里看，行业 narrative 最有信息量的一篇。
- [Kazemnejad et al. \"Impact of Positional Encoding on Length Generalization\" arxiv:2305.19466](https://arxiv.org/abs/2305.19466) — NoPE 原始论文，理解 iRoPE 为什么\"敢去掉 PE\"的理论基础。
- [HuggingFace Llama 4 modeling code](https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama4/modeling_llama4.py) — `no_rope_layers`、`interleave_moe_layer_step` 这些 config 字段是反推 iRoPE / MoE interleave 实现的唯一可靠途径，blog 不写代码写。
- [The Information \"Meta delays flagship AI model\" 2025-05](https://www.theinformation.com/articles/meta-delays-flagship-ai-model-amid-disappointing-performance) — Behemoth 搁置的最早可信报道，要订阅，但行业内基本以这篇为准。
