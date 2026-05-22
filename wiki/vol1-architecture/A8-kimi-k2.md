# Kimi K1.5 → K2 → K2-Instruct / K2-Thinking 家族

## 路线定位

Moonshot AI（月之暗面）2024 年靠 Kimi Chat 长上下文做 to-C 起家，但真正在 frontier 拿到话语权是 **2025-01 K1.5（首个对标 o1 的中文多模态 reasoning 模型，与 R1 同周发布）** 和 **2025-07 K2（开源 1T-param MoE，MuonClip 把 Muon 推到 trillion 尺度第一次成功）**。竞品定位：open-weight 圈对标 DeepSeek-V3.1/V3.2、Qwen3-MoE、GLM-4.5；闭源圈以 agentic + tool-use 能力（K2-Thinking）正面挑 Claude Sonnet/Opus 4.x 和 GPT-5。Moonshot 与 DeepSeek 最大的方法论差异：**优化器层面押注 Muon 系**，而非 DeepSeek 走的 AdamW + 架构/系统优化路线 —— K2 是这个赌注的第一个 frontier-scale 公开验证。

## 代表模型清单

| 模型 | 发布日 | 参数 / 激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| Moonshot v1 (Kimi Chat) | 2023-10 | 闭源 dense | 200K → 2M ctx 的 to-C chatbot | [moonshot.cn blog](https://www.moonshot.cn/) |
| **Kimi K1.5** | 2025-01-22 | 闭源（API），尺寸未披露 | **多模态 long-CoT RL**，long2short、partial rollouts | [arxiv:2501.12599](https://arxiv.org/abs/2501.12599), [github.com/MoonshotAI/Kimi-k1.5](https://github.com/MoonshotAI/Kimi-k1.5) |
| **Kimi K2-Base** | 2025-07-11 | **1.04T total / 32B act**, MoE 384+1 | **MuonClip** 优化器，15.5T pretrain token，agentic-oriented data | [arxiv:2507.20534 K2 tech report](https://arxiv.org/abs/2507.20534), [github.com/MoonshotAI/Kimi-K2](https://github.com/MoonshotAI/Kimi-K2) |
| **Kimi K2-Instruct** | 2025-07-11 | 同 K2-Base | non-thinking chat/agent 模型，开源 weights (Modified MIT) | [HF moonshotai/Kimi-K2-Instruct](https://huggingface.co/moonshotai/Kimi-K2-Instruct) |
| Kimi K2-Instruct-0905 | 2025-09-05 | 同 K2 | post-train refresh，agentic + coding 提升，ctx 128K → 256K | [HF Kimi-K2-Instruct-0905](https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905) |
| **Kimi K2-Thinking** | 2025-11-06 | 同 K2 base | **reasoning + interleaved tool calls**，**INT4 native QAT**，长 horizon agentic (≥200 tool calls) | [moonshot blog Kimi-K2-Thinking](https://moonshotai.github.io/Kimi-K2/thinking.html), [HF Kimi-K2-Thinking](https://huggingface.co/moonshotai/Kimi-K2-Thinking) |
| Kimi K2-Thinking-Turbo | 2026-02 [uncertain 具体日期] | 同 K2 | latency-optimized 版本，speculative decoding + indexer 优化 | [moonshot platform release notes](https://platform.moonshot.cn/) |
| K3 | — | — | [unknown — 截至 2026-05 没有官方 K3 发布] | — |

## 架构核心

K2 的 backbone 在结构上**和 DeepSeek-V3 高度同源**（MLA + DeepSeekMoE 的 fine-grained + shared expert + aux-loss-free LB），差异是 **expert 数更多、attention head 更少**，以及优化器换成 MuonClip。

### Backbone 数字（看 [K2 tech report §2](https://arxiv.org/abs/2507.20534)）

| 项 | K2 | DeepSeek-V3 对照 |
|---|---|---|
| 总参数 | 1.04T | 671B |
| 激活参数 / token | 32B | 37B |
| 层数 | 61 | 61 |
| Attention | **MLA**, 64 head | MLA, 128 head |
| $d_{model}$ | 7168 | 7168 |
| MLA $d_c$ / $d_h^R$ | 512 / 64 | 512 / 64 |
| Routed experts | **384** | 256 |
| Shared experts | 1 | 1 |
| top-k routed | 8 | 8 |
| expert FFN dim | 2048 | 2048 |
| Vocab (BBPE) | 160K | 128K |
| Pretrain ctx | 4K → 32K → 128K | 4K → 32K → 128K |

要点：
- **Attention head 砍半到 64**（DeepSeek-V3 是 128）：作者在 §2.1 解释这是为了控 attention 计算量，因为 K2 的 token-to-param ratio（15.5T / 32B 激活 ≈ 480）已经很挤，attention FLOPs 在 long-ctx 阶段比 MoE FFN 更紧；64 head 把每 token attention cost 降一半，同时观察到 64 vs 128 head 在 loss 上几乎无差。
- **Expert 数 256 → 384**：fine-grained 程度进一步加深，top-8/384 = 稀疏度 2.08%（V3 是 3.13%）。直觉是"更多 specialist 池子 + 更少同时激活"。
- **Shared expert 仍是 1**，沿用 DeepSeekMoE 范式。
- **Aux-loss-free LB（带 bias controller）** 直接抄 DeepSeek-V3（[arxiv:2408.15664](https://arxiv.org/abs/2408.15664)），加一个极小 sequence-level aux。K2 paper §2.3 确认这一点。
- **没用 MTP**：K2-Base 不带 multi-token prediction head（与 V3 不同的少数选择之一）。理由 paper 未细说，[推测] 是 MuonClip + MTP 联合调参成本太高，团队先稳住主目标。

### MuonClip —— 这一节是 K2 的真正卖点

> 看 K2 tech report §3 + Moonshot 之前的 [Muon-MoE-Scaling Law (arxiv:2502.16982)](https://arxiv.org/abs/2502.16982) + 原始 Muon: [Jordan et al. 2024-10](https://kellerjordan.github.io/posts/muon/)。Lambert 在 [interconnects.ai \"Kimi K2 and the new frontier of open models\" (2025-07)](https://www.interconnects.ai/p/kimi-k2-and-when-deepseek-came-from) 给了非数学角度的总结。Sasha Rush 在 X / [his blog](https://srush.github.io/) 多次评论 MuonClip 是\"AdamW 替代者第一个真上 frontier\"。

**背景**：Muon 是 Keller Jordan 2024 提出的 hidden-layer 优化器，核心是把每个 weight matrix 的梯度做 **Newton-Schulz 5 步迭代近似的正交化** $G \to \text{NS}(G)$，再做更新。在 NanoGPT speedrun 上把 wall-clock 砍到 AdamW 的 ~60%。但社区一直怀疑它在 (a) 大 batch、(b) trillion-param、(c) MoE routing 不稳的情况下是否 hold。

**Moonshot 之前的工作 (Muon-MoE-Scaling Law, 2025-02)** 用 MoE 9B/16B 验证 Muon 在 sample efficiency 上**对 AdamW 有 ~2× 的优势**，但当时报告了一个**致命问题：max attention logit 会随训练发散**（$\max |QK^T / \sqrt{d}|$ 涨到几千），最终撞 softmax overflow / 训练崩。

**MuonClip 的设计**（K2 paper §3.2）：
1. **Muon 主干**保留：hidden-layer 2D weight 用 NS-正交化更新；embedding / LM head / 1D param (bias、LN gain) 仍用 AdamW。
2. **Per-head QK-clip**：每 step 之后，监控每个 attention head 的 max logit $S_h^{\max} = \max_{i,j} q_i^{(h)} \cdot k_j^{(h)} / \sqrt{d_h}$。若超过阈值 $\tau$（K2 用 $\tau = 100$），就把这个 head 的 $W_Q^{(h)}$ 和 $W_K^{(h)}$ 同时乘以 $\sqrt{\tau / S_h^{\max}}$（开根号是为了对称，logit 是 Q·K 的双线性）。
3. **关键点**：clip 是 **post-hoc rescale 权重本身**，不是改 grad 或 loss。等价于事后把 attention 拉回安全区，下一步 Muon 继续正常跑。仅对**触发的 head** 生效（K2 训练全程平均不到 5% head 在任意步触发，触发率随训练前期高、后期归零）。
4. **效果**：K2 在 15.5T token 训练全程 max logit 稳在 100 附近，**zero loss spike**。Paper §3.2 Fig 2 是关键图。AdamW baseline 在 9B scale 已经能稳，但 sample efficiency 输；纯 Muon 在 1T scale 发散；MuonClip 是唯一在 1T × 15.5T 稳的组合。
5. **实现细节**：
   - NS 迭代用 5 步、float32 累加。
   - 学习率：hidden Muon 用 $\eta = 0.02 \cdot (1/\sqrt{\max(d_{in}, d_{out})})$ 这种 dim-aware scaling（这是 Muon 标准做法，类似 muP 但靠 NS 而非 init 决定 scale invariance）。
   - MoE expert 的 FFN weight 也用 Muon（每个 expert 独立 NS）。这部分通信代价 K2 paper §6 提到用了 **block-diagonal NS + 分布式 reduce-scatter** 的实现。
   - Memory：Muon 只存一阶 momentum（不需要 v），optimizer state 比 AdamW 省 ~33%。

**对焱拳的意义**：如果 Qwen 想换优化器，MuonClip 是目前唯一在 frontier MoE 上 end-to-end 跑通的样本；Moonshot 把训练代码开源在 [github.com/MoonshotAI/Moonlight](https://github.com/MoonshotAI/Moonlight)（含 MuonClip 实现）。需要注意 NS 迭代对 grad scale 极敏感，bf16 grad + fp32 NS 是 Moonshot 实测最稳组合。

### INT4 native QAT（K2-Thinking 起）

K2-Thinking 是**第一个 frontier-scale 用 INT4 weight 原生发布**的开源模型：
- **W4A16 + QAT**：weight 4-bit (group-128, asymmetric)、activation bf16，post-train 阶段 RL 是**在 INT4 forward 下做的**（QAT，非 post-training quantization）。
- 收益：单 H100 8-GPU 节点能装下 1T 模型 (1T × 0.5 byte ≈ 500GB → 加 MLA cache 和 expert offload 后实测 ~620GB)，TPS 比 fp8 ×1.8-2×。
- 公开报告（[Kimi-K2-Thinking blog 2025-11](https://moonshotai.github.io/Kimi-K2/thinking.html)）声称 INT4 vs bf16 reasoning benchmark 下降 < 0.5 pt。
- 这个动作把 K2-Thinking 从"开源但你跑不起"变成"中等机房能本地跑 frontier reasoning + agent"，是 2025-Q4 开源圈最关键的可用性事件之一。

## 训练方法核心

### Pretrain (K2-Base)

- **Token 量 15.5T**，BBPE 160K tokenizer。([K2 tech report §4.1](https://arxiv.org/abs/2507.20534))
- **数据 mixture**：web + code + math + 中文 + 多语，**重度合成 agentic data**（tool-use traces、code-execution traces，paper §4.1.3）。Moonshot 强调 K2-Base 在 pretrain 阶段就 expose 到 tool-call schema 和 multi-turn agent rollouts —— 这是它和 V3-Base 的主要数据差异。
- **Token-efficiency-driven data engineering**：paper §4.1 提出 \"rephrase + verify\" 的数据 augmentation（用一个中等模型把 web 内容多次改写并 cross-check），声称在固定算力下相比直接 epoch 重训涨点更多。具体合成比例没全披露。
- **RoPE base** = 50000（比 V3 的 10000 大），长上下文阶段直接到 128K，没用 YaRN。
- **算力**：[unknown — K2 tech report 提到 \"trained on a large GPU cluster\" 但没公开 GPU-hour 数字]。社区估算（Lambert 引用）1T × 15.5T ≈ V3 算力的 2-3 倍。Moonshot 用的是 H800 (NVIDIA 中国特供)，[据 36kr 报道](https://www.36kr.com/) 数千卡级别。

### Post-train: K1.5 RL recipe（先理解这个，K2 是它的放大版）

> [K1.5 tech report arxiv:2501.12599](https://arxiv.org/abs/2501.12599) —— 与 R1 同周发布、但配方完全不同，值得对照读。Lambert [\"Kimi k1.5 vs DeepSeek R1\" interconnects 2025-01](https://www.interconnects.ai/p/why-reasoning-models-will-generalize)。

K1.5 的 RL 设计是 **policy gradient + length penalty + partial rollouts + long2short**，关键点：

1. **算法不是 GRPO，也不是 PPO**：K1.5 用一个简化的 **online policy mirror descent** 变体，objective $\mathcal{L} = -\mathbb{E}[(r - \bar r) \log \pi_\theta(y|x)] + \tau \cdot \text{KL}(\pi_\theta \| \pi_{\text{ref}})$，**没有 value model，也没有 PPO clipping**。Reward baseline $\bar r$ 是 group mean（这一点和 GRPO 类似）。
2. **Reward = rule-based + RM 混合**：math/code 用 verifier；非可验证任务用 model judge。
3. **Length penalty**：直接在 reward 里减 $\alpha \cdot \text{len}(y)$，避免 R1-Zero 那种 response 无限膨胀。
4. **Partial rollouts**（K1.5 paper §3.3.1，**这是 K1.5 最有工程价值的 trick**）：long-CoT RL 的痛点是 rollout tail 长（一些 trace 30K+ token），同 batch 短的等长的浪费 GPU。K1.5 把没跑完的 trace **存到 replay buffer**，下一个 iteration 接着跑，inference engine 从 cache 恢复。**等价于把 RL 的 wall-clock 从 \"被 99th percentile 拖死\" 变成 \"按 mean 跑\"**。Paper 报告 throughput 提升 ~1.5×。
5. **Long2Short**：先训一个 long-CoT 模型当 teacher，再训一个 short-CoT student（用 model merging、shortest-rejection-sampling、DPO 三种方法），让 student 在更短 token 预算下逼近 teacher。这是工业部署关键 —— 长 CoT 太贵。
6. **多模态原生**：vision encoder 联合训练，K1.5 在 MathVista、MMMU 上当时领先所有开源 reasoning 模型。

### Post-train: K2-Instruct（non-thinking）

- **SFT**：大规模 instruction + tool-use SFT。paper §5.1 强调 **agentic SFT 数据是合成生成的**，pipeline 是\"工具集随机化 → LLM 编场景 → LLM 扮 user/assistant 多轮交互 → rule + judge 过滤\"，类似 [Toolformer / Gorilla] 思路放大版。
- **Agentic RL**（§5.2，**这是 K2 的第二个卖点**）：在一个**可验证 task 池**（code、math、browser tasks、SWE-bench-like、tool API tasks）上跑 RL，reward 是 verifier （code pass、unit test、答案匹配、最终 state 检查）。算法仍是 K1.5 的 policy gradient + length penalty 变体。
- **General RLHF**：常规 preference RM + RL，覆盖写作、安全、对话。
- 结果：K2-Instruct 是 non-thinking 模式，**不输出 `<think>` block**，直接给答 + 在需要时 inline tool call。SWE-Bench Verified 65.8%、Tau-Bench retail 70.6%（paper §6），open-weight 非 reasoning 模型里 SOTA。

### Post-train: K2-Thinking（2025-11）

- 加 **reasoning RL**：在 K2-Instruct-0905 基础上做 long-CoT RL，配方延续 K1.5（partial rollouts 仍在用），reward 池扩到 ~50 类 verifiable task。
- **Interleaved thinking + tool use**：和 o3 / Claude Sonnet 4.5 的 thinking-with-tools 一致，模型可以在 `<think>` 内调用工具、看结果、继续 think。Moonshot blog 给的极限示例：**单 task 200+ tool calls**，Humanity's Last Exam (HLE) with tools 44.9%（开源 SOTA，超越 GPT-5 thinking 41.7%, [moonshot blog](https://moonshotai.github.io/Kimi-K2/thinking.html) 自报）。
- **INT4 QAT** 见上面架构节。
- **Test-Time Scaling**：blog 强调 K2-Thinking 支持显式的 \"thinking budget\" 控制（max think tokens + max tool calls），用户可在 reasoning 深度 / latency / cost 之间权衡。

## 与 eval / benchmark 的接口

K2 官方报的关键 headline（[K2 tech report §6](https://arxiv.org/abs/2507.20534) + [Thinking blog](https://moonshotai.github.io/Kimi-K2/thinking.html)）：

| Bench | K1.5 | K2-Instruct (07-11) | K2-Instruct-0905 | K2-Thinking |
|---|---|---|---|---|
| MMLU-Pro | 77.5 | 81.1 | 82.1 | 84.6 |
| GPQA Diamond | — | 75.1 | 76.0 | **84.5** |
| AIME 2024 | 77.5 | 69.6 | — | **94.5** |
| AIME 2025 (no tools) | — | — | — | 92.4 |
| HLE (no tools) | — | — | — | 23.9 |
| **HLE (with tools)** | — | — | — | **44.9** |
| MATH-500 | 96.2 | 97.4 | — | 97.8 |
| LiveCodeBench v6 | — | 53.7 | 60.0 | 71.3 |
| SWE-Bench Verified | — | 65.8 | 69.2 | 71.3 |
| Tau-Bench retail | — | 70.6 | 72.8 | 84.0 |
| BrowseComp | — | — | — | **60.2** (vs GPT-5 54.9 自报) |

第三方观察：
- **Artificial Analysis** ([artificialanalysis.ai/models/kimi-k2](https://artificialanalysis.ai/)) K2-Thinking 综合 intelligence index 接近 GPT-5 / Claude Opus 4.5，**开源第一**。
- **LiveCodeBench / Aider polyglot** 第三方测分与官方接近，无明显虚报。
- **SWE-Bench Verified** Moonshot 用的 scaffold 是自家 agent，**和 Anthropic / OpenAI 不同 scaffold**，绝对值不严格可比 —— Lambert 多次强调 SWE-Bench 数字必须看 scaffold。
- **Tau-Bench** 数字争议较小，因为环境 + harness 标准化。
- **Contamination 信号**：[Scale SEAL leaderboard](https://scale.com/leaderboard) K2-Instruct 在 hold-out 私榜上排名与公开榜大致一致 (±2 pt)，相对干净。Math/code 高分类似 R1，难独立判 contamination。
- **MuonClip 复现**：截至 2026-05，**没有第三方独立在 100B+ 上复现 MuonClip 的稳定性**。社区在 1B-10B（[nanotron Muon impl](https://github.com/huggingface/nanotron/pull/249)、[Essential AI Muon scaling](https://github.com/EssentialAI/muon-scaling)）确认 sample-efficiency claim，但 trillion-scale 仍只有 Moonshot 一家数据点。
- **Lambert 评价**（[interconnects 2025-11](https://www.interconnects.ai/p/kimi-k2-thinking)）：K2-Thinking 是\"DeepSeek R1 时刻之后开源世界第二次显著拉近与 closed lab 差距\"，特别是 agentic + reasoning 联合能力。

## 未知与争议

- **MuonClip 通用性**：Moonshot 之外没有公司公开宣布在 trillion-scale 上用 Muon 系。Anthropic / OpenAI / DeepSeek 是否在内部试过、放弃 / 采纳，[unknown]。Qwen3-MoE 据知用 AdamW（[Qwen3 tech report](https://arxiv.org/abs/2505.09388)），未提 Muon。
- **K2 的实际算力 / 成本**：tech report 没给 GPU-hour 数字。社区估算 $20-30M 量级，无官方确认。
- **Agentic SFT 数据的合成 pipeline 细节**：tool 集、判 model、过滤阈值 paper 写得很泛。这是 K2 agentic 能力的真正护城河，Moonshot 没开源数据。
- **K1.5 的多模态 encoder 架构** paper 几乎没写（只说\"jointly trained vision encoder\"），尺寸 / 训练数据 / 是否冻结 [unknown]。
- **INT4 QAT 在 RL 阶段的稳定性**：blog 一句带过，没给消融。RL forward 是 INT4、backward 怎么处理（直通估计？）technical 细节未公开。
- **K2-Thinking BrowseComp 60.2%** 这个数字与 OpenAI 自报 GPT-5 的 54.9% 不严格可比（不同 browser harness、不同时间快照），需要 Vector Institute / Artificial Analysis 这类第三方在同 harness 复测后才有定论。
- **K3 / K2.5**：截至 2026-05 无官方信号。

## 推荐外部材料

- [Kimi K2 tech report (arxiv:2507.20534)](https://arxiv.org/abs/2507.20534) — 必读。架构 §2、MuonClip §3、data §4、post-train §5、eval §6 五部分齐全，比 V3 paper 在 post-train / agent 部分写得更细。
- [Kimi K1.5 tech report (arxiv:2501.12599)](https://arxiv.org/abs/2501.12599) — partial rollouts、long2short、多模态 RL 配方的原文，与 R1 paper 配对读最有信息量。
- [Moonshot Muon-MoE Scaling Law (arxiv:2502.16982)](https://arxiv.org/abs/2502.16982) — 理解 MuonClip 为什么必要的前传：纯 Muon 在 MoE 上 attention logit 发散问题第一次被记录。
- [Keller Jordan, \"Muon: An optimizer for hidden layers\" (2024-10)](https://kellerjordan.github.io/posts/muon/) — Muon 原始 blog，NS 迭代和正交化梯度的直觉讲解。
- [github.com/MoonshotAI/Moonlight](https://github.com/MoonshotAI/Moonlight) — MuonClip 的官方实现（PyTorch），含分布式 NS 和 QK-clip 代码，要复现这是第一站。
- [github.com/MoonshotAI/Kimi-K2](https://github.com/MoonshotAI/Kimi-K2) — 主 repo，含 inference code、模型卡、agentic demo。
- [Nathan Lambert, \"Kimi K2 and when DeepSeek came from\" interconnects.ai 2025-07](https://www.interconnects.ai/p/kimi-k2-and-when-deepseek-came-from) — K2 发布当周的最佳综述，把 K2 放在开源 frontier 时序里。
- [Nathan Lambert, \"Kimi K2 Thinking\" interconnects 2025-11](https://www.interconnects.ai/p/kimi-k2-thinking) — K2-Thinking 评测 + agentic 能力的非营销解读。
- [Sasha Rush 关于 Muon / K2 的 X 串](https://x.com/srush_nlp) — 学术视角对 MuonClip 是否真的是 \"AdamW 替代\" 的怀疑与肯定混合，值得追踪。
- [Kimi-K2-Thinking 发布 blog](https://moonshotai.github.io/Kimi-K2/thinking.html) — INT4 QAT、interleaved tool-use、HLE 44.9% 的一手 source。
- [Artificial Analysis K2 / K2-Thinking 页](https://artificialanalysis.ai/models/kimi-k2-thinking) — 第三方综合排名 + latency / cost 数据，做 eval 对比时直接引用。
