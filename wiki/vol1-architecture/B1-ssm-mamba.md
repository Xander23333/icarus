# SSM / Mamba / Hybrid 家族

## 路线定位

State Space Model (SSM) 这条线的核心赌注是 **把 attention 的 $O(N^2)$ 换成 $O(N)$ 的 recurrent / convolutional 计算**，同时保留长序列建模能力。2023-2024 这条路线被 Mamba 一作 Albert Gu / Tri Dao 带到高点，2024 下半年起**纯 SSM 在 frontier capability 上明显落后于 transformer**（in-context retrieval、MMLU-level 知识检索吃亏），战线于是收缩到两个方向：(1) **hybrid**——SSM 层和少量 attention 层交错，代表 Jamba（AI21）、Zamba2（Zyphra）、Nemotron-H（NVIDIA）、Samba（Microsoft）、Granite 4.0（IBM）；(2) **纯 SSM 但走特定 niche**——Falcon-Mamba（TII，证明 7B 纯 Mamba 能 match Llama-3 8B）。竞争对手不是同家族而是**长上下文 transformer + 各种 sparse attention**（DeepSeek DSA、NSA、MoBA）。截至 2026-05，hybrid 在 production 已被多家上线（Jamba 1.5、Granite 4.0），**纯 SSM 在 frontier 上没有 winner**。Sasha Rush 2024-09 talk [\"Is Attention All You Need?\"](https://www.youtube.com/watch?v=dKJEpOtVgXc) 的结论一句话：\"the answer is yes-ish, but the hybrid is winning\"。

## 代表模型清单

| 模型 | 发布日 | 参数 / 架构 | 关键变化 | 一手 source |
|---|---|---|---|---|
| S4 | 2021-10 | — | HiPPO 初始化 + diagonal+lowrank SSM，长序列 benchmark (LRA) 横扫 | [arxiv:2111.00396](https://arxiv.org/abs/2111.00396) |
| H3 | 2022-12 | — | SSM + 简单 gating，第一次接近 transformer LM 困惑度 | [arxiv:2212.14052](https://arxiv.org/abs/2212.14052) |
| **Mamba (S6)** | 2023-12 | 130M – 2.8B dense | **selective SSM**：A、B、C 变成输入依赖；parallel scan kernel | [arxiv:2312.00752](https://arxiv.org/abs/2312.00752) |
| Jamba v0.1 | 2024-03 | 52B / 12B act, MoE | **第一个 production hybrid**：1:7 attn:mamba ratio + MoE | [arxiv:2403.19887](https://arxiv.org/abs/2403.19887) |
| **Mamba-2** | 2024-05 | 130M – 2.7B dense | **SSD (State Space Duality)**：SSM 等价于结构化 mask attention，吃满 matmul 硬件 | [arxiv:2405.21060](https://arxiv.org/abs/2405.21060) |
| Zamba 7B | 2024-05 | 7B hybrid | shared attention block（参数复用），1 attn / 多 mamba | [arxiv:2405.16712](https://arxiv.org/abs/2405.16712) |
| Samba 3.8B | 2024-06 | 3.8B hybrid | Mamba + SWA (sliding-window attn) 交错，Phi-3 数据 | [arxiv:2406.07522](https://arxiv.org/abs/2406.07522) |
| Falcon-Mamba 7B | 2024-08 | 7B pure Mamba-1 | **纯 SSM 7B 第一次 match Llama-3 8B**（avg HF leaderboard） | [TII blog](https://huggingface.co/blog/falconmamba), [tech report](https://arxiv.org/abs/2410.05355) |
| Codestral Mamba 7B | 2024-07 | 7B pure Mamba | Mistral 出的 code 专用 Mamba，256K ctx | [Mistral blog](https://mistral.ai/news/codestral-mamba/) |
| **Jamba 1.5 Mini/Large** | 2024-08 | 52B/12B, 398B/94B MoE hybrid | **256K context，production**；ExpertsInt8 量化 | [arxiv:2408.12570](https://arxiv.org/abs/2408.12570) |
| Zamba2 1.2B/2.7B/7B | 2024-10 ~ 2024-12 | dense hybrid | Mamba-2 + 2 个 shared attention block（交替插入），LoRA on shared block | [Zyphra blog](https://www.zyphra.com/post/zamba2-7b), [arxiv:2411.15242](https://arxiv.org/abs/2411.15242) |
| Hymba 1.5B | 2024-11 | hybrid | NVIDIA：**parallel** attn+SSM head（同一层并行），meta-token | [arxiv:2411.13676](https://arxiv.org/abs/2411.13676) |
| Bamba 9B | 2024-12 | hybrid | IBM/Princeton/CMU 联合开源，复刻 Nemotron-H 思路 | [github IBM/bamba](https://github.com/foundation-model-stack/bamba), [arxiv:2502.13923](https://arxiv.org/abs/2502.13923) |
| **Nemotron-H 8B/47B/56B** | 2025-04 | dense hybrid | NVIDIA：92% Mamba-2 + 8% attn 层，**对标 Llama-3.1 70B**；FP8 训练 | [arxiv:2504.03624](https://arxiv.org/abs/2504.03624) |
| Falcon-H1 (0.5B–34B) | 2025-05 | hybrid family | TII 转 hybrid（放弃 pure Mamba 路线），parallel attn+SSM | [arxiv:2507.22448](https://arxiv.org/abs/2507.22448) |
| **IBM Granite 4.0** | 2025-10 | 3B/7B/32B-A9B hybrid | **第一个全 hybrid 的企业 LLM 家族**，9:1 Mamba-2:attn，MoE 版 32B | [IBM blog](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models), [tech report PDF](https://github.com/ibm-granite/granite-4.0-language-models) |
| Qwen3-Next 80B-A3B | 2025-09 | hybrid MoE | Qwen 团队：**Gated DeltaNet + Gated Attention** 交错（不是 Mamba 但同家族 linear attention）；3:1 比例 | [Qwen blog](https://qwen.ai/blog?id=qwen3_next), [HF model](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct) |
| MiniMax-01 | 2025-01 | 456B MoE | **lightning attention (linear)** + 1:7 softmax，4M ctx | [arxiv:2501.08313](https://arxiv.org/abs/2501.08313) |
| RWKV-7 \"Goose\" | 2025-03 | 0.1B–2.9B | RWKV 系（不严格是 SSM，但同 linear-recurrent 家族）generalized delta rule | [arxiv:2503.14456](https://arxiv.org/abs/2503.14456) |
| 后续 Mamba-3 / SSD-2 | — | — | [unknown — 截至 2026-05 Albert Gu / Tri Dao 未发布 Mamba-3。Tri Dao 重心已转向 FlashAttention-3 + Together AI inference stack；Gu 在 CMU 继续做 SSM 理论但无 frontier 规模新 release] | — |

## 架构核心

### S4 → Mamba(S6)：从 LTI 到 selective

> Mamba paper [arxiv:2312.00752](https://arxiv.org/abs/2312.00752) §3；Sasha Rush 注释版 [The Annotated S4](https://srush.github.io/annotated-s4/) / [The Annotated Mamba](https://srush.github.io/annotated-mamba/) 是最好的入门。

SSM 的连续形式：$h'(t) = A h(t) + B x(t)$, $y(t) = C h(t)$。离散化后递推 $h_t = \bar A h_{t-1} + \bar B x_t$，输出 $y_t = C h_t$。

- **S4 (2021)**：$A, B, C$ **time-invariant**（LTI），所以整条序列可以展开成一个 $\bar K = (C\bar B, C\bar A \bar B, \dots)$ 的卷积核，FFT 训练 $O(N\log N)$。问题：LTI 模型**没有 content-based selection**，无法在长序列里有选择地记/忘特定 token——in-context retrieval 任务（如 induction head、selective copy）做不了。
- **Mamba / S6**：让 $B_t, C_t, \Delta_t$ **都成为输入 $x_t$ 的函数**（A 仍是结构化对角）。这样模型可以"看到 $x_t$ 后决定要不要更新 state"。代价：失去 LTI ⇒ 不能再用 FFT 卷积训练。
- **Selective Scan kernel**：Tri Dao 写了一个**硬件感知的 parallel scan**（associative scan in shared memory，类似 Blelloch scan，但避免把 hidden state 写回 HBM）。这是 Mamba 能真上的关键工程。对比 attention：训练时 attn 是 $O(N^2)$ compute / $O(N)$ memory IO（FlashAttention），Mamba scan 是 $O(N)$ compute / $O(N)$ memory IO，**长序列下 Mamba 训练吞吐能高 3-5×**。
- **Mamba block**：input → 两路分支（一路 Conv1d + SiLU + SSM，一路 SiLU gate）→ 相乘 → out proj。结构类似 GLU + SSM，没有 attention 也没有 MLP，单层就既算 mixing 又算 nonlinearity。

### Mamba-2 与 SSD (State Space Duality)

> Mamba-2 paper [arxiv:2405.21060](https://arxiv.org/abs/2405.21060) §3-§5；Tri Dao [Mamba-2 blog 系列](https://tridao.me/blog/2024/mamba2-part1-model/) 4 篇是 paper 的更易读版。

核心发现：**selective SSM 在 $A$ 退化为标量 × 单位阵（"scalar-identity" SSM）时，等价于一种 1-semiseparable mask attention**。即：
$$
y_t = \sum_{s \le t} \left( \prod_{r=s+1}^{t} a_r \right) (C_t^\top B_s) x_s
$$
正好是 $Q K^\top \odot M$ 的形式，$M$ 是一个 cumulative-product 下三角 mask。

实际收益：
- **可以用 matmul-heavy 算法训练 SSM**（"SSD algorithm"，把序列切 chunk，块内用 matmul，块间用 scan 传 state），把 selective-scan 的 elementwise bottleneck 干掉，**训练快 2-8×**。
- **Head 维度可以做大**（Mamba-1 head dim 通常 16-64，Mamba-2 可以到 128-256），更贴近 attention 的实现习惯。
- 提供了 SSM ↔ attention 的**形式化桥梁**，hybrid 设计有了语言。

但 **SSD 是有损的**：要求 $A$ 是 scalar × I，没有 Mamba-1 那么 expressive。Mamba-2 paper 报告在小规模 LM perplexity 上和 Mamba-1 打平甚至略优，但具体任务有 trade-off。

### 为什么纯 Mamba 在 frontier 输了：retrieval gap

> [Jamba paper §6](https://arxiv.org/abs/2403.19887)；[Waleffe et al. "An Empirical Study of Mamba-based LMs" NVIDIA 2024-06, arxiv:2406.07887](https://arxiv.org/abs/2406.07887)；[RULER](https://arxiv.org/abs/2404.06654) / [Phonebook 任务](https://arxiv.org/abs/2402.18510)。

NVIDIA 2024-06 那篇是关键的 negative result：**控制变量（同 8B、同 1.1T token）下，pure Mamba-2 在 MMLU、GSM8K 上和 transformer 相当或略输；但在 needle-in-haystack、phonebook、5-shot retrieval-heavy 任务上 gap 巨大**（>20pt）。
- 直觉解释：SSM 的 state 是**固定大小**的 compressed memory（典型 $d_{state}=128$），无论 context 多长都是这个 size。需要精确召回某个 token id 的任务，固定 state 容量是硬瓶颈。
- Attention 的 KV cache 是**无损**的 per-token memory，这就是为什么 hybrid 里**少量 attention 层就足够补上这块**——NVIDIA 论文报告**8% 的 attention 层就够**，再多边际收益消失。

Tri Dao 在多个 talk 里直接承认这点（[Stanford MLSys talk 2024](https://www.youtube.com/watch?v=8Js0hN7iAdo)）：\"For pure recall tasks, you need attention. Hybrid is just better.\"

### Hybrid 设计空间

主要分三种 layout：

1. **Sequential interleaving**（主流）：层与层交替。Jamba 1:7（每 8 层里 1 层 attn），Nemotron-H ~1:12，Granite 4.0 1:9，Zamba2 用 2 个 shared attention block 周期性插入。
2. **Parallel within layer**：同一层里 attn head 和 SSM head 并行算，concat 输出。Hymba（NVIDIA）、Falcon-H1。优势：每层都有两种 mixing；劣势：实现复杂，调度难。
3. **Cross-layer parameter sharing**：Zamba/Zamba2 把 attention block 在多层间**共享权重**，省参数。Zamba2-7B 报告这样能省 ~10% 参数同时 perplexity 不掉。

Granite 4.0 tech report 的 ablation 给出现在的"默认配方"：**Mamba-2 backbone + 每 9-10 层插一层 GQA + 不用 positional encoding（NoPE，SSM 自带位置感知）**，这套被 IBM、NVIDIA、Zyphra 三家独立收敛。

### Qwen3-Next 与 Gated DeltaNet：linear attention 的回归

Qwen 团队 2025-09 的 Qwen3-Next 80B-A3B [严格说不是 Mamba 家族，是 linear attention 家族](https://qwen.ai/blog?id=qwen3_next)，但属于同一战线（subquadratic recurrent）：
- 用 **Gated DeltaNet**（[arxiv:2412.06464](https://arxiv.org/abs/2412.06464)）替换 SSM，delta rule + gating，理论上比 Mamba-2 在 state 利用率更高。
- 3 layer gated DeltaNet : 1 layer gated full attention 比例。
- MoE：80B 总参 / 3B 激活，**激活率 ~3.7%**，极致 sparse。
- 收益：训练成本仅为 Qwen3-32B-dense 的 ~10%，long-context (256K) 推理吞吐 10×+。

这条线说明：**hybrid 思路已经从 Mamba 泛化到所有 linear-recurrent 家族**（Mamba-2 / GLA / RWKV-7 / DeltaNet / Lightning Attention），具体算子可替换，架构 pattern 稳定。

## 训练方法核心

### Pretrain 规模与数据
- **Mamba 原论文**：最大 2.8B，300B token，The Pile + SlimPajama。属于学术规模。
- **Falcon-Mamba 7B**：5.5T token + 长 ctx 阶段，TII 在 [tech report arxiv:2410.05355](https://arxiv.org/abs/2410.05355) 里详细比对了和 Falcon-3 transformer 同数据的差距，结论是 dense pretrain perplexity 持平。
- **Jamba 1.5 Large 398B/94B**：训练数据未披露具体规模，AI21 只说 \"multi-trillion tokens\"。
- **Nemotron-H 56B**：**20T token**，FP8 训练全程，NVIDIA 自家 Megatron-LM 跑。Paper §4 详细给了 hybrid 模型的 FP8 训练 stability 注意事项——SSM 的 state 累积容易在 fp8 下数值爆掉，要给 SSM 层单独保留 bf16。
- **Granite 4.0 32B-A9B**：22T token (multi-stage)，**核心 selling point 是 enterprise 长上下文推理成本**（128K ctx 内存占用约为同尺寸 dense transformer 的 1/5）。

### 长 context 训练
- SSM/Mamba 一个常被宣传的优势是\"训短测长可外推\"。**实测严重打折扣**——Mamba 论文里能外推到训练长度的 ~2-4×，再长就崩。Jamba 1.5 256K 是**显式训练过的**，不是外推。
- Hybrid 的 attention 层仍然吃 RoPE / NoPE / ALiBi 的设计选择。Granite 4.0 用 **NoPE on attention layers**（SSM 层提供位置信号），简化了长 ctx scaling。

### Post-train
- **Jamba 1.5 Large** 做了 SFT + DPO，AI21 没披露具体配方。
- **Granite 4.0** 走完整 instruct/RLHF 流程，IBM 重点是企业 tool-use / RAG 调优。
- **R1-style RLVR on hybrid**：截至 2026-05 没有看到 hybrid 模型公开的 GRPO/RLVR 训练报告。Zamba2-Instruct、Jamba Reasoning 等都还是传统 SFT+DPO 路线。**这是一个明显的空白**——理论上 hybrid 不影响 RL 训练，但目前所有 RLVR 成功案例都是 dense/MoE transformer。读者团队如果要做 SSM agentic RL，先要解决 inference 框架（vLLM、SGLang 对 Mamba 支持是 2025-Q2 才进，对 hybrid 仍不完整）。

## 与 eval / benchmark 的接口

代表性官方报数：

| 模型 | MMLU | GSM8K | HumanEval | RULER 128K | 备注 |
|---|---|---|---|---|---|
| Mamba 2.8B | 33.3 (5-shot) | — | — | — | 同 Pythia-2.8B 量级 |
| Falcon-Mamba 7B | 65.0 | 52.5 | 29.9 | — | 接近 Llama-3 8B (66.6 MMLU) |
| Jamba 1.5 Large | 81.2 | 87.0 | — | **96.7** | RULER 显著超 Llama-3.1 405B (90.3) |
| Nemotron-H 56B | 77.0 | 93.7 | — | — | hybrid 对标 Llama-3.1 70B (79.3 MMLU) |
| Zamba2-7B | 64.7 | 65.9 | — | — | 同尺寸 dense Llama-3 8B 略优 |
| Granite 4.0 32B-A9B | 75.6 | 88.9 | 84.1 | 高 | IBM 报 enterprise task 持平 Llama-3.1-70B-instruct |
| Qwen3-Next 80B-A3B | 80.6 | 92.5 (math) | — | 高 | 长 ctx 吞吐 10× Qwen3-32B |

第三方：
- [Open LLM Leaderboard 2 (2024)](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) Falcon-Mamba 7B 排在同尺寸 dense 第一梯队，复现了 TII claim。
- **RULER**（NVIDIA）和 **LongBench v2** 是 hybrid 模型最爱用的 benchmark，原因是这两个 benchmark 既考 retrieval 又考 reasoning，hybrid 优势能体现；纯 needle-in-haystack 任务 hybrid 也 OK，但纯 Mamba 仍然差。
- [Together AI 2024-07 benchmark](https://www.together.ai/blog/inference-engine) 测 Mamba 7B 推理吞吐在 batch=1 long-context 比 Llama-3 8B 快 3-5×，confirm 了主要 selling point。

Contamination / overfit 信号：
- SSM/hybrid 模型整体 release 量小，contamination 研究少。Granite 4.0 IBM 自己做了 contamination check（公开 dataset 比对），其它家普遍没说。
- **Jamba 1.5 Large 的 RULER 96.7 数字** 被几个第三方质疑（[LMSYS forum thread 2024-09](https://discord.com/invite/lmsys)，[uncertain]），主要因为 AI21 没公开 RULER 评测的具体 needle 配置。

## 未知与争议

- **Mamba-3 / SSD-2 是否会出**：Albert Gu 2025-Q1 在 [CMU talk](https://www.youtube.com/results?search_query=albert+gu+mamba+2025) 里暗示在做 \"continuous-time SSM with better state utilization\"，但没 paper。Tri Dao 公开重心已转 FlashAttention-3 / Together inference。[unknown]
- **Hybrid 的最佳 attn:ssm 比例**：Jamba 1:7，Nemotron-H 1:12，Granite 1:9，差异大。Nemotron-H paper §6 的 ablation 显示从 1:7 到 1:24 perplexity 变化在 ±0.1 之内，但下游 retrieval 性能在 attn 比例 < 5% 后明显掉。**没有一个公认 sweet spot**。
- **SSM 在 RL post-train 下表现**：理论无问题，但 inference 框架支持差导致工程难。截至 2026-05 没有 R1-class hybrid reasoning model。[unknown — 没找到一手 source 报告 hybrid 在 GRPO 下的 reward curve]
- **是否 SSM 对 multimodal 友好**：[Cobra (arxiv:2403.14520)](https://arxiv.org/abs/2403.14520)、VL-Mamba 等小项目存在，但 frontier VLM 全是 transformer-based。SSM 在 vision token 序列上的优势没有被验证（vision token 通常 < 4K，attention 没什么压力）。
- **MiniMax-01 的 lightning attention 严格说算 SSM 吗**：[争议]，MiniMax 自家分类是 \"linear attention\"，但其形式（输入依赖的 gating + recurrent state）和 Mamba-2 SSD 同构。本章把它和 Qwen3-Next 一起归在 \"广义 linear-recurrent\"。

## 推荐外部材料

- [Mamba paper (arxiv:2312.00752)](https://arxiv.org/abs/2312.00752) — 必读。§3 selective mechanism + §3.3 hardware-aware scan 是全部 idea。
- [Mamba-2 paper (arxiv:2405.21060)](https://arxiv.org/abs/2405.21060) — SSD 等价性，配合 Tri Dao 4 篇 [blog](https://tridao.me/blog/2024/mamba2-part1-model/) 读，paper 太长 blog 更易懂。
- [Sasha Rush, The Annotated S4 / The Annotated Mamba](https://srush.github.io/annotated-mamba/) — 代码级讲解，跑通一遍 SSM 数学全清楚。
- [Sasha Rush, "Is Attention All You Need?" Simons Institute talk 2024-09](https://www.youtube.com/watch?v=dKJEpOtVgXc) — 一小时把 SSM/Mamba/hybrid 历史和当下定位讲清楚，最佳 overview。
- [Jamba 1.5 paper (arxiv:2408.12570)](https://arxiv.org/abs/2408.12570) — 第一个 production hybrid 的完整 recipe，§3 architecture 决策表格直接抄就能复现。
- [NVIDIA, "An Empirical Study of Mamba-based LMs" (arxiv:2406.07887)](https://arxiv.org/abs/2406.07887) — 关键 negative result：纯 Mamba 在 retrieval 上输，hybrid 8% attn 补齐。决定了之后所有人转 hybrid。
- [Nemotron-H tech report (arxiv:2504.03624)](https://arxiv.org/abs/2504.03624) — 当前最完整的 hybrid frontier-scale 训练实录，含 FP8 在 hybrid 上的踩坑。
- [Albert Gu, "On the Tradeoffs of SSMs and Transformers" blog 2024-05](https://goombalab.github.io/blog/2024/mamba2-part1-model/) — 一作自己写的 SSM vs attention 取舍，比 paper 直白。
- [Tri Dao, FlashAttention → Mamba → FlashAttention-3 演讲合集](https://tridao.me/) — 想理解 SSM 工程化为什么难必看，硬件 IO 视角。
- [Qwen3-Next blog (Qwen team)](https://qwen.ai/blog?id=qwen3_next) — Gated DeltaNet + hybrid 在 MoE frontier 上的最新实践，2026 hybrid 战线代表。
- [Granite 4.0 launch + tech report (IBM)](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models) — enterprise 视角的 hybrid，含完整 serving cost 对比，2025-10 最重磅 hybrid release。
