# B3 · B4 — Linear-attention 家族 与 Hybrid (Attention + SSM/Linear) 家族

> 范围：截至 2026-05 公开可见的工作。两节合并因为这两条线在 2025-2026 已经合流：纯 linear-attn 路线整体**停滞**（B3），活下来的玩法是 hybrid（B4），而 hybrid 中真正进 production-scale 的代表案例之一是 Qwen3-Next，已在 A7 详写，这里只做对比定位。

---

# B3 — 纯 linear / RNN-style 路线：RWKV、RetNet、Mamba 系、其它 linear-attn 变体

## 路线定位（外部口径）

这条线 2023-2024 的核心 thesis 是 "干掉 softmax attention 的 O(N²)，用 recurrence/linear-kernel 拿 O(N) 训练 + O(1) 推理 state"。到 2026-05，**纯 linear/RNN 路线在 frontier intelligence 榜上没有一个 ckpt 站住**：要么被 hybrid 收编（Jamba/Zamba/Samba/Qwen3-Next 路线，进 B4），要么在 7-14B 段做小生态（RWKV-7、Mamba-2 finetune 社区），要么转去做 edge / on-device / 长序列 niche（state-space 在 audio、DNA、video token 上仍活）。Sasha Rush 在 [2025 ICML "State Space Models in 2025" talk](https://www.youtube.com/results?search_query=sasha+rush+state+space+2025) 的总结基本是开源社区共识：**"pure SSMs lost the frontier race; the interesting question is now what hybrid ratio wins"**。

## 代表模型清单（外部能看到的公开 release）

| 模型 | 发布 | 参数 | 类型 | 一手 source |
|---|---|---|---|---|
| RWKV-6 "Finch" | 2024-04 | 1.6B / 3B / 7B / 14B | 纯 RNN-style linear attn (token-shift + data-dependent decay) | [arxiv:2404.05892](https://arxiv.org/abs/2404.05892) |
| RetNet | 2023-07 | up to 6.7B paper-scale | retention = exponential-decay linear attn，三种 forward (parallel/recurrent/chunkwise) | [arxiv:2307.08621](https://arxiv.org/abs/2307.08621) |
| Mamba | 2023-12 | up to 2.8B | selective SSM，input-dependent A,B,C | [arxiv:2312.00752](https://arxiv.org/abs/2312.00752) |
| Mamba-2 | 2024-05 | up to 2.7B | SSD：把 SSM 写成 structured matrix，对硬件友好 + 与 linear attn 形式统一 | [arxiv:2405.21060](https://arxiv.org/abs/2405.21060) |
| Gated Linear Attention (GLA) | 2023-12 → 2024 | research-scale | data-dependent gate，启发后续 DeltaNet / Gated DeltaNet | [arxiv:2312.06635](https://arxiv.org/abs/2312.06635) |
| DeltaNet / Gated DeltaNet | 2024 → 2025 | research → 进 Qwen3-Next | Delta rule (在线最小二乘) + gate，state 容量比 GLA 大 | [Yang et al. arxiv:2406.06484](https://arxiv.org/abs/2406.06484), [Gated DeltaNet arxiv:2412.06464](https://arxiv.org/abs/2412.06464) |
| **RWKV-7 "Goose"** | 2024-12 preview → 2025 paper | 0.1B – 2.9B 主线 ckpt | "expressive dynamic state evolution"，作者主张超过 attention 的表达上限 (TC⁰ 之外) | [arxiv:2503.14456](https://arxiv.org/abs/2503.14456) |
| RWKV-7-World 系列 | 2025-Q1 → Q3 | up to ~14B 社区训练 | multilingual base | [HF BlinkDL/rwkv-7-world](https://huggingface.co/BlinkDL) |
| Falcon-Mamba-7B | 2024-08 | 7B 纯 Mamba | TII 出的 first "production" pure-SSM 7B | [arxiv:2410.05355](https://arxiv.org/abs/2410.05355) |
| Codestral-Mamba-7B | 2024-07 | 7B Mamba code 模型 | Mistral 出的唯一 Mamba 主线 | [Mistral blog 2024-07](https://mistral.ai/news/codestral-mamba/) |
| Hawk / Griffin (DeepMind) | 2024-02 | up to 14B | RG-LRU + local attn 的纯 RNN / hybrid 对照实验 | [arxiv:2402.19427](https://arxiv.org/abs/2402.19427) |
| RetNet 后续 | — | — | **作者团队 2024 起转向 YOCO / DIFF Transformer 等其它方向**，RetNet 主线无后续大 ckpt | — |
| TTT (Test-Time Training layers) | 2024-07 | research | 把 state 设成可训 model，每 token 做一步 grad | [arxiv:2407.04620](https://arxiv.org/abs/2407.04620) |
| xLSTM | 2024-05 | 1.4B → 7B | sLSTM + mLSTM | [arxiv:2405.04517](https://arxiv.org/abs/2405.04517), [xLSTM 7B 2025-03 arxiv:2503.13427](https://arxiv.org/abs/2503.13427) |

截至 2026-05，**纯 linear/RNN 家族里没有一个 ckpt 进入 Artificial Analysis open-weights intelligence index 前 15**（参见 [artificialanalysis.ai/models](https://artificialanalysis.ai/models)）。

## 架构核心（按 paper 写的）

### 共同骨架
所有这条线的 layer 都能写成同一个 abstract recurrence：`S_t = f(S_{t-1}, k_t, v_t)`，`o_t = g(S_t, q_t)`。差异只在 **state 形状**、**update rule**、**gate**。Sasha Rush 的 "Linear Attention is All You Need (Sometimes)" 系列把这个统一视角讲得最清楚 ([blog series 2024](https://srush.github.io/))。

### RWKV-6 → RWKV-7（[paper arxiv:2503.14456](https://arxiv.org/abs/2503.14456)）
- **RWKV-6 Finch**：data-dependent time-mix + channel-mix，decay 与 token 相关。
- **RWKV-7 Goose**：把 state update 改成更一般的 "vector-valued state, matrix-valued transition"，paper §3 用 TC⁰ 表达力论证可以**严格超过 standard softmax-attention transformer**在某些 state-tracking 任务上的上限（引用 Merrill & Sabharwal 的 TC⁰ 结果）。
- 训练规模：作者发布 0.1B / 0.4B / 1.5B / 2.9B 主线，社区有 7B/14B World 续训。
- 外部独立评测：[HF Open LLM v2](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) 上 RWKV-7-2.9B 与同 size dense transformer 互有胜负；**没有一份公开复测显示 RWKV-7 在 7B+ size 上 reasoning / code 能追平 Qwen3-7B / Llama-3.1-8B**（这是 community 的明牌弱点）。

### RetNet（[arxiv:2307.08621](https://arxiv.org/abs/2307.08621)）
- retention = `Q (K ⊙ decay-mask)^T V`，固定 per-head decay。
- 三种 forward：parallel（训练）、recurrent（生成）、chunkwise（长 ctx）。
- 现状：原班 (MSR/Tsinghua) 后续转 YOCO ([arxiv:2405.05254](https://arxiv.org/abs/2405.05254))、DIFF Transformer ([arxiv:2410.05258](https://arxiv.org/abs/2410.05258))，**RetNet 没有出 30B+ 主线 ckpt**。外界把 RetNet 视为 "把 linear attn 这条路 push 到了 paper 工程极致，但没能突破 quality ceiling" 的典型 case。

### Mamba / Mamba-2 / Falcon-Mamba
- Mamba：selective SSM，A,B,C 与输入相关，HiPPO 初始化。
- Mamba-2 的 SSD（[arxiv:2405.21060](https://arxiv.org/abs/2405.21060) §3）证明 selective SSM 与 linear attention "structured masked" 形式数学等价，这是 2024 年最关键的统一性结果，之后 hybrid 路线都建在这上面。
- Falcon-Mamba-7B：**唯一一个进 HF Open LLM leaderboard top-50 的纯 SSM 7B**（[TII blog 2024-08](https://huggingface.co/blog/falconmamba)），但发布后 12 个月内没有 follow-up。
- 已知失败模式（多个第三方独立复现，e.g., [Waleffe et al. 2024 "Empirical Study of Mamba" arxiv:2406.07887](https://arxiv.org/abs/2406.07887)）：**copy / multi-query associative recall / long-context retrieval 上明显弱于同 size attention**。这是 hybrid 路线诞生的直接驱动。

### Gated DeltaNet（进 production 的 linear-attn 变体）
- [Gated DeltaNet arxiv:2412.06464](https://arxiv.org/abs/2412.06464)：在 DeltaNet 的 "delta rule" 在线学习 state 上面加一个 forget gate，paper 在 1.3B/3B 上证明 recall 任务超过 Mamba2 / GLA。
- **这是唯一一个被 frontier-scale production model 选用的 linear-attn 变体**（Qwen3-Next 的 linear 层），详见 B4 / A7。

### xLSTM（[arxiv:2405.04517](https://arxiv.org/abs/2405.04517) + [xLSTM 7B arxiv:2503.13427](https://arxiv.org/abs/2503.13427)）
- 把 LSTM 的 scalar gate 改成 exponential gate (sLSTM) + matrix memory (mLSTM)。
- 7B 报告在 dense baseline 上有一定效率优势，**reasoning / code 仍落后同 size transformer**，社区接受度低。

## 训练方法核心

这块比 transformer 主线还要 sparse。绝大多数纯 linear 路线发布的就是 base ckpt + 简单 SFT；**完整 RLVR / agentic RL pipeline 几乎没有一家在 linear-only 架构上跑通并公开**：

- RWKV-7：社区有 DPO finetune，无公开 large-scale RLVR ([uncertain — 2026-05 前没见到一手 report])。
- Mamba 系：[Zephyr-Mamba 等社区 SFT](https://huggingface.co/) 存在，无 production RL。
- 这是评测视角下的关键事实：**当你在评一个 reasoning / agent 榜上看不到 pure-SSM/RNN 模型时，往往不是架构问题，而是它们根本没经过同等强度的 post-train**。架构能力与 post-train 投入两个变量在公开数据里是 confounded 的。

## 与 eval / benchmark 的接口

- **HF Open LLM Leaderboard v2**：RWKV-7 / Mamba-2 / xLSTM 在小 size (≤3B) 段与 dense baseline 互有胜负，到 7B+ 全面落后。
- **RULER / HELMET long-ctx**：纯 SSM 在 needle-in-haystack ≥32K 上明显掉点，是 hybrid 化的最强经验证据 (Waleffe et al. 2024; [HELMET arxiv:2410.02694](https://arxiv.org/abs/2410.02694))。
- **MMLU-Pro / GPQA / LiveCodeBench**：纯 linear 家族没有 ckpt 在第三方榜上进过 top tier。
- **没有已知 contamination 争议** — 因为没人测它们。

## 未知与争议

- RWKV-7 关于"超过 attention 表达力"的论证是 **worst-case TC⁰ 区分**，外界（Merrill 等）普遍认为这与 practical capability ranking 关系弱。
- 纯 SSM 在 long-context retrieval 上的弱点是 **架构 hard limit 还是 training recipe 问题**，社区有分歧；[Ben Athiwaratkun et al. 2024](https://arxiv.org/abs/2402.18668) 倾向前者，部分 hybrid 工作 (Samba) 倾向后者。
- **2026-05 时点的客观事实**：没有一家 frontier lab 在 pure linear / pure SSM 上 bet 旗舰，全部押宝在 hybrid。

## 推荐外部材料

- [Sasha Rush, "State Space Models in 2025" ICML talk + slides](https://srush.github.io/) — 这条线发生了什么、为什么收敛到 hybrid 的最权威 1 小时总结。
- [Mamba-2 paper arxiv:2405.21060](https://arxiv.org/abs/2405.21060) — SSD 把 SSM 与 linear attn 统一，是理解后续所有 hybrid 工作的前置。
- [Waleffe et al., "An Empirical Study of Mamba-based LMs" arxiv:2406.07887](https://arxiv.org/abs/2406.07887) — NVIDIA 团队用同 budget 横向 train Mamba / Mamba-Hybrid / Transformer，得出"hybrid 8% layers attention 就够"的关键结论。
- [RWKV-7 paper arxiv:2503.14456](https://arxiv.org/abs/2503.14456) — 纯 RNN 路线最新一次正面论证。
- [Gated DeltaNet arxiv:2412.06464](https://arxiv.org/abs/2412.06464) — 唯一进 production-scale (Qwen3-Next) 的 linear-attn 变体，理解 B4 必读。
- [Sebastian Raschka, "Understanding State Space Models" 2024](https://magazine.sebastianraschka.com/) — 评测侧最易读的 SSM 入门。

---

# B4 — Hybrid 家族：Attention + (SSM | Linear Attention)

## 路线定位（外部口径）

Hybrid 是 2024-2026 这条线**实际跑赢**的结果。共识 recipe：**留一小部分 full softmax attention 层（5-25%）做 in-context retrieval / induction-head 类工作，剩下大多数层换成 Mamba / Mamba-2 / Gated DeltaNet / sliding-window attention 之类 O(N) 单元拿吞吐**。代表玩家：AI21 (Jamba)、Zyphra (Zamba)、Microsoft (Samba)、Nvidia (Hymba / Nemotron-H)、Mistral (Codestral 后续未公开)、Alibaba (Qwen3-Next，已在 A7 详写)、IBM (Bamba)、TII (Falcon-H1)。

## 代表模型清单

| 模型 | 发布 | 参数 / 激活 | hybrid 配方 | 一手 source |
|---|---|---|---|---|
| **Jamba v0.1** | 2024-03 | 52B / 12B act (MoE) | Transformer + Mamba + MoE，每 8 层 1 层 attention | [arxiv:2403.19887](https://arxiv.org/abs/2403.19887) |
| Jamba-1.5 Mini / Large | 2024-08 | 52B / 398B (94B act) | 同结构 scaled up，256K ctx | [arxiv:2408.12570](https://arxiv.org/abs/2408.12570) |
| **Zamba-7B** | 2024-05 | 7B | Mamba blocks + **shared global attention**（参数共享给所有 attention "slot"） | [arxiv:2405.16712](https://arxiv.org/abs/2405.16712) |
| Zamba2-7B / 2.7B / 1.2B | 2024-10 → 2025-Q1 | 1.2B – 7B | Mamba2 + shared attention，open-weights efficiency 标杆 | [Zyphra blog](https://www.zyphra.com/post/zamba2-7b), [arxiv:2411.15242](https://arxiv.org/abs/2411.15242) |
| **Samba** | 2024-06 | up to 3.8B paper-scale | Mamba + Sliding Window Attention 交替，每层都 hybrid | [arxiv:2406.07522](https://arxiv.org/abs/2406.07522) |
| Phi-4-Mini-Flash | 2025 | — | Samba 风格被 MS 后续 Phi 小模型采用 [uncertain — 公开 config 部分确认] | [Phi-4 tech report](https://arxiv.org/abs/2412.08905) |
| **Hymba** (Nvidia) | 2024-11 | 1.5B | 每层 *并行* attention + Mamba head 拼接（不是层级交替） | [arxiv:2411.13676](https://arxiv.org/abs/2411.13676) |
| **Nemotron-H** (Nvidia) | 2025-04 | 8B / 47B / 56B | 大 size hybrid base，公开 weight | [arxiv:2504.03624](https://arxiv.org/abs/2504.03624), [Nvidia blog](https://research.nvidia.com/) |
| **Falcon-H1** (TII) | 2025-Q2 | 0.5B / 1.5B / 3B / 7B / 34B | Mamba2 + attention 并行 hybrid，full size ladder | [Falcon-H1 tech report arxiv:2507.22448](https://arxiv.org/abs/2507.22448) |
| **Bamba** (IBM + Princeton + CMU) | 2024-12 → 2025 | 9B | open-data hybrid，全套训练数据公开 | [IBM blog](https://research.ibm.com/blog/bamba-ssm-transformer-model), [arxiv:2502.13145](https://arxiv.org/abs/2502.13145) |
| **Qwen3-Next-80B-A3B** | 2025-09 | 80B / 3B act | 48 层中每 4 层 1 层 full attention，其余 3 层 Gated DeltaNet；MoE 512/10+1 | [qwenlm blog](https://qwenlm.github.io/blog/qwen3-next/) — 详写在 A7 |
| MiniMax-01 / MiniMax-Text-01 | 2025-01 | 456B / 45.9B act | **Lightning Attention (linear) + softmax** 每 7:1 比例，原生 1M ctx | [arxiv:2501.08313](https://arxiv.org/abs/2501.08313) |
| Granite 4.0 (IBM) | 2025-10 | 3B / 7B / 32B | Mamba2 + attention hybrid，IBM 主线 | [IBM Granite 4.0 release](https://www.ibm.com/granite) |

> 2026-05 时点判断：hybrid **已经成为开源中小 size (1B–10B) base 的事实主流之一**（与 dense GQA 并列），在 frontier MoE 段唯一进过 top-tier 讨论的是 Qwen3-Next 与 MiniMax-01。

## 架构核心

### Jamba 系（[arxiv:2403.19887](https://arxiv.org/abs/2403.19887) + [1.5 paper](https://arxiv.org/abs/2408.12570)）
- block 设计：Mamba layers + 每 8 层穿插 1 层 Transformer attention，MoE 在部分 layers。
- 论证：少量 attention 层修复 SSM 在 in-context recall (induction head) 上的能力 ceiling。
- 1.5 Large 256K ctx，Jamba 是**第一个公开声明 production scale (>50B) hybrid 的家族**。

### Zamba 系（[Zamba 2024](https://arxiv.org/abs/2405.16712), [Zamba2 2024](https://arxiv.org/abs/2411.15242)）
- 关键创新：**shared attention block**——所有需要 attention 的位置都路由到同一份 attention 参数（参数复用降本），是和 Jamba 最大的区别。
- Zamba2-7B 在同等训练 token 下打平 Llama-3-8B 是社区引用最多的 efficiency 结果（Zyphra blog 自报，[Artificial Analysis](https://artificialanalysis.ai/) 第三方测速验证 throughput 优势）。

### Samba（[arxiv:2406.07522](https://arxiv.org/abs/2406.07522)）
- 配方：每一层都是 Mamba + Sliding Window Attention 交替的小模块，不是 Jamba 那种"绝大多数层纯 SSM + 偶尔一层 attention"。
- paper claim 在 4K 训长度下外推到 256K perplexity 稳定，是 hybrid + 短训长外推方向的代表。

### Hymba / Nemotron-H（Nvidia 两路 bet）
- **Hymba**：layer 内**并行** attention head 与 Mamba head 拼接，不是层级交替。1.5B size 上声称同 budget 超过同 size Llama / Mamba。
- **Nemotron-H** ([arxiv:2504.03624](https://arxiv.org/abs/2504.03624))：把 hybrid 推到 56B 公开权重，attention 层比例约 8%（与 Waleffe 2024 推荐一致），是 hybrid 在 ≥50B size 上的关键公开数据点。Nvidia 自报与同算力 Llama-3.1 dense 持平且推理快 ~3×。

### Falcon-H1（[arxiv:2507.22448](https://arxiv.org/abs/2507.22448)）
- TII 在 Falcon-Mamba 教训后转 hybrid，**0.5B–34B 完整 size ladder**，每 size 都有 hybrid + 同 size pure-transformer 对照。这是目前公开材料里 hybrid vs transformer 头对头 ablation 最完整的一家。

### MiniMax-01（[arxiv:2501.08313](https://arxiv.org/abs/2501.08313)）
- 456B / 45.9B act MoE，Lightning Attention (linear softmax-free 变体) : softmax = 7:1 层比，原生 1M ctx。
- 是 **2025-01 时点最大的 hybrid open-weights MoE**，但后续 MiniMax 没有发布 follow-up hybrid 旗舰（社区视为"做了一发就静默"）。

### Qwen3-Next（详细见 A7）
- 此处只列对位：在 hybrid family 中 Qwen3-Next 是**第一个把 hybrid 与 ultra-sparse MoE (~2% 激活率) 同时 push 到 production-scale**的，linear 层用的是 Gated DeltaNet 而非 Mamba2，是 B3 工作 → B4 production 的最直接证据链。

### Granite 4.0 / Bamba (IBM 路线)
- IBM 押 hybrid 做 enterprise base：Bamba 是开源完整数据 + 配方版本，Granite 4.0 是产品版。规模上不与 frontier 直接竞争。

## 训练方法核心

公开材料里 hybrid 的训练配方比纯 SSM 详细一些，关键点：
- **数据**：与同 size dense 主流配方基本一致，没有 hybrid 专属数据 trick。
- **优化器**：清一色 AdamW；Muon 暂无 hybrid 大模公开报告 [uncertain]。
- **Long-ctx 训练**：hybrid 在长 ctx 续训阶段普遍比 dense 便宜，是核心卖点之一（Jamba 1.5 Large 256K，MiniMax-01 1M，都受益于此）。
- **Post-train (RLVR / agentic)**：到 2026-05 公开 RLVR 配方跑通的 hybrid 旗舰本质只有 Qwen3-Next 一家（且 RL 细节也未完整披露，见 A7）。Jamba / Zamba / Nemotron-H 都是 base + instruct SFT 为主。这是 hybrid 路线 "intelligence 上限是否被验证"的最大未知。

## 与 eval / benchmark 的接口

- **Artificial Analysis intelligence index**：Qwen3-Next-80B-A3B-Thinking 是 hybrid 路线**唯一进 open-weights 第一档**的 ckpt（2025-Q4 上榜）。Jamba 1.5 Large、Nemotron-H 56B 在中段。
- **RULER / HELMET long-ctx**：hybrid 比 pure-SSM 在 ≥64K needle 上明显回血，但比 full-attention + good rope 仍然有 gap；这是评测 owner 看 hybrid 时最该关注的轴。[RULER](https://github.com/NVIDIA/RULER) 第三方测分 Jamba-1.5 Large 64K 段稳定，128K 段掉点比 dense Qwen3 显著。
- **LiveCodeBench / SWE-Bench Verified**：除 Qwen3-Next 外，hybrid 家族没有 ckpt 进入第一档。
- **吞吐 / 长 ctx 推理成本**：Zamba2-7B、Nemotron-H、Qwen3-Next 都被 Artificial Analysis speed 榜验证比 same-size dense 快 1.5–10× (随 ctx 长度 scale)。这是 hybrid 当前**最硬的卖点**。

## 未知与争议

- **Hybrid 的 reasoning RL 上限**：截至 2026-05，除 Qwen3-Next 外没有公开 large-scale RLVR 跑通的 hybrid 旗舰，"intelligence ceiling 是否真的与 dense 相当"是开放问题。
- **最优 attention 比例**：Waleffe 2024 / Nemotron-H 取 ~8%，Qwen3-Next 取 25%，Samba 取 50%，Jamba 取 ~12.5%。没有外部共识公式，每家靠 ablation。
- **长 ctx 真实质量**：hybrid 的 long-ctx perplexity 漂亮但**下游 task** (RULER / LongBench-v2) 仍有 gap，社区分歧大。
- **Mamba2 vs Gated DeltaNet vs Lightning Attention 谁是 winner**：Qwen3-Next 选 Gated DeltaNet 是个明牌信号（Alibaba 内部 ablation 公开版本未发），但样本 = 1。
- **没有任何一家 frontier 闭源 lab (OpenAI / Anthropic / Google / xAI) 公开承认在主线产品使用 hybrid**。Gemini 系曾在 paper 提过 SSM 实验，没有产品对应物。

## 推荐外部材料

- [Waleffe et al., "An Empirical Study of Mamba-based LMs" arxiv:2406.07887](https://arxiv.org/abs/2406.07887) — Nvidia 在 8B size 上系统对比 Mamba / Hybrid / Transformer，得出 "hybrid 5-10% attention 最优" 的关键经验结论，hybrid 路线的奠基性实证。
- [Jamba 1.5 paper arxiv:2408.12570](https://arxiv.org/abs/2408.12570) — production-scale hybrid 最完整的第一份 tech report。
- [Falcon-H1 tech report arxiv:2507.22448](https://arxiv.org/abs/2507.22448) — 同一家在多 size 下完整对照 hybrid / transformer，复现 friendly。
- [Nemotron-H tech report arxiv:2504.03624](https://arxiv.org/abs/2504.03624) — Nvidia 56B hybrid 公开权重的训练细节，吞吐数据一手。
- [Qwen3-Next blog](https://qwenlm.github.io/blog/qwen3-next/) + 本书 A7 — 当前 hybrid + ultra-sparse MoE 最强产品例。
- [MiniMax-01 paper arxiv:2501.08313](https://arxiv.org/abs/2501.08313) — Lightning Attention 7:1 hybrid + 1M ctx，是 hybrid 路线 long-ctx 极端 push 的代表。
- [Sasha Rush, "Linear Attention is All You Need (Sometimes)" 博客系列](https://srush.github.io/) — 统一 linear attention / SSM / hybrid 的最佳教学材料。
- [Sebastian Raschka, "The Big LLM Architecture Comparison" 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) — 把 Qwen3-Next、Jamba、Mamba 与 dense 主流同框对比，外部视角最权威的 cross-family 图。
