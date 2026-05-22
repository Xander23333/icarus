# Diffusion LLM（文本 token 上的扩散语言模型）

## 路线定位

这一节专门讲 **discrete-token diffusion language model**（LLaDA、Mercury、Gemini Diffusion 这一系），**不包括** any-to-any 多模态扩散（Transfusion / Show-o / Bagel 那一脉放在 C1）。核心赌注：把 LLM 从 left-to-right autoregressive (AR) 换成**并行 denoising / unmasking**，目标是 (a) decode 阶段 wall-clock TPS 跨数量级提升、(b) 双向 context、(c) 全局 plan / 可控编辑。竞品定位：在 **frontier 智能**上仍**落后同算力 AR 1 个身位**（这一点要老实），但 2025 H1 Inception Mercury 第一次把 diffusion text model 推到 **>1000 tok/s 商用 code 模型** + Google 在 I/O 2025 公布 **Gemini Diffusion** 把这条路线从学术拉进了 frontier lab roadmap，使它从 "SEDD/MDLM 论文趣味" 升级为正经的 architecture 候选。截至 2026-05 仍然是 **"潜力大、还没有任何一个 diffusion LM 在 GPQA/AIME/SWE-Bench 同算力下打过 AR SOTA"** 的状态。

## 代表模型清单

| 模型 | 发布日 | 参数 / 类型 | 关键变化 | 一手 source |
|---|---|---|---|---|
| **D3PM** (Austin et al, Google) | 2021-07 | 理论框架 | discrete-state diffusion 的奠基，定义 absorbing / uniform transition kernel | [arxiv:2107.03006](https://arxiv.org/abs/2107.03006) |
| Diffusion-LM (Li/Hashimoto, Stanford) | 2022-05 | 80M continuous-embedding | 在词向量空间做 Gaussian diffusion，可控生成 demo | [arxiv:2205.14217](https://arxiv.org/abs/2205.14217) |
| **SEDD** (Lou, Meng, **Ermon**) | 2023-10 | 170M-1.3B | **score entropy** 目标，第一次让 discrete diffusion 在 LM perplexity 上接近同尺寸 GPT-2 | [arxiv:2310.16834](https://arxiv.org/abs/2310.16834) |
| **MDLM** (Sahoo et al, Cornell/NYU) | 2024-06 | 110M-340M | **masked diffusion** 的简化 ELBO，证明等价于 weighted cross-entropy on masked tokens，让训练像 BERT 一样简单 | [arxiv:2406.07524](https://arxiv.org/abs/2406.07524) |
| RADD (Ou et al) | 2024-06 | — | reparam absorbing diffusion，进一步简化采样 | [arxiv:2406.03736](https://arxiv.org/abs/2406.03736) |
| **LLaDA 8B** (RUC / Ant Group) | 2025-02-14 | 8B dense | **第一个 instruction-tuned 8B masked-diffusion LM**，号称 in-context learning 与 LLaMA3-8B 同档 | [arxiv:2502.09992](https://arxiv.org/abs/2502.09992), [ml-gsai.github.io/LLaDA-demo](https://ml-gsai.github.io/LLaDA-demo/) |
| **Mercury Coder** (Inception Labs, **Ermon** co-founder) | 2025-02-26 | 闭源，估算 ~7B 级 | **首个商用 diffusion code LM**，H100 上 **1109 tok/s**（自报），Copilot Arena top-2 速度 | [inceptionlabs.ai blog](https://www.inceptionlabs.ai/news/announcing-mercury), [Mercury tech report arxiv:2506.17298](https://arxiv.org/abs/2506.17298) |
| LLaDA-V (多模态) | 2025-05 | 8B + ViT | LLaDA + vision adapter，验证 diffusion LM 可走 VLM 路径 | [arxiv:2505.16933](https://arxiv.org/abs/2505.16933) |
| **Gemini Diffusion** (Google DeepMind) | 2025-05-20 (Google I/O) | 闭源、尺寸未披露 | **第一次 frontier lab 公开 diffusion text model**，experimental demo, 自报 **1479 tok/s** | [deepmind.google/models/gemini-diffusion](https://deepmind.google/models/gemini-diffusion/), [Google I/O 2025 keynote](https://blog.google/technology/google-deepmind/gemini-diffusion/) |
| Mercury Coder Small / Mini | 2025-Q3 | 闭源 | API 商用化，加 fill-in-middle、IDE plugin | [platform.inceptionlabs.ai](https://platform.inceptionlabs.ai/) |
| **LLaDA 1.5 / LLaDA-MoE** | 2025-09 / 2025-11 [uncertain 具体日] | 8B → MoE | RUC 团队后续，加 RL post-train + MoE，benchmark 仍落后同尺寸 Qwen2.5 | [github.com/ML-GSAI/LLaDA](https://github.com/ML-GSAI/LLaDA) |
| Block Diffusion (BD3-LM, Arriola et al, Cornell) | 2025-03 | 350M-1.3B | **block-autoregressive diffusion** 混合范式，AR 在 block 间、diffusion 在 block 内，KV-cache 可用 | [arxiv:2503.09573](https://arxiv.org/abs/2503.09573) |
| **Mercury v2 / Mercury Reasoning** | 2026-Q1 [uncertain] | 闭源 | Inception 路线图，加 reasoning trace。**截至 2026-05 是否已发布 [unknown — 没找到一手 source 确认]** | — |
| Gemini Diffusion GA | — | — | [unknown — 截至 2026-05 仍是 experimental waitlist，未进 Gemini 主线 API] | — |

## 架构核心

### 1. Masked diffusion 的基本数学（绝大多数 2024+ 工作的 backbone）

> 推荐先读 Sasha Rush 的 [Diffusion Models for Discrete Data 讲义](https://srush.github.io/annotated-mamba/) 系列里的 discrete diffusion 章，和 [Aaron Lou 的 SEDD 博客版讲解](https://aaronlou.com/blog/2024/discrete-diffusion/)。

记 vocab $V$，加一个特殊 `[MASK]` token。前向过程 $q(x_t | x_0)$ 是**每个位置独立、以概率 $\alpha_t$ 保留原 token、以 $1-\alpha_t$ 替换成 [MASK]**（"absorbing kernel"，D3PM 的特例）。$\alpha_0 = 1$，$\alpha_1 = 0$（全 mask）。

**反向 / 训练目标**（MDLM 的简化形式）：
$$\mathcal{L} = \mathbb{E}_{t, x_0, x_t} \left[ \frac{-\alpha'_t}{1-\alpha_t} \sum_{i: x_t^{(i)} = \text{MASK}} \log p_\theta(x_0^{(i)} \mid x_t) \right]$$

要点：
- **就是带权 BERT-MLM 训练**。所以训练 infra 几乎不用改：取一个 batch，按 $t \sim U[0,1]$ 采样 mask ratio，mask 掉相应比例 token，预测原 token，按 $1/(1-\alpha_t)$ 重加权 loss。
- transformer backbone 用 **bidirectional attention**（**没有 causal mask**）—— 这是和 AR LM 最大的实现差异之一。
- **没有 KV-cache**（每步 denoise 都要 full forward），这是后面性能讨论的关键约束。

LLaDA 8B 直接用上式（[LLaDA paper §3.1](https://arxiv.org/abs/2502.09992)），SEDD/score-entropy 是另一条等价路线（Lou 等证明 score-entropy 与 MDLM ELBO 在 absorbing 设定下等价，参见 [MDLM §4](https://arxiv.org/abs/2406.07524) + [Shi et al 2024 \"Simplified and Generalized Masked Diffusion\"](https://arxiv.org/abs/2406.04329)）。

### 2. 采样（这是 diffusion LM 真正与 AR 分道扬镳的地方）

LLaDA / Mercury 通用 sampler（[LLaDA paper §3.2](https://arxiv.org/abs/2502.09992) + [Mercury tech report §3](https://arxiv.org/abs/2506.17298)）：
1. 初始化：prompt 之后 N 个位置全 `[MASK]`（N = 用户指定的生成长度，**这是相比 AR 的一个 UX 退步：要预先定长**，LLaDA 用 semi-autoregressive block 部分缓解）。
2. 选定步数 $T$（典型 $T=64$ 或 $T=128$；远小于 N）。
3. 每步：full bidirectional forward → 得到所有 masked 位置的 logits → 按某个 **remasking strategy** 选一批位置 commit、剩下重新 mask。
4. 常用 remasking：**low-confidence remasking**（保留 top-k confidence，其他重 mask）或 **random remasking**。LLaDA 用 low-confidence；Mercury 没完全公开但 [推测] 类似。
5. 直到全部 unmask 或步数耗尽。

**关键性质**：
- **步数 $T$ 可调**：少步速度快、质量差；多步反过来。这是 diffusion LM 的核心 trade-off 旋钮，类似 image diffusion 的 NFE。
- **每步 FLOPs = 一次 full forward over N tokens**，所以 wall-clock 成本 ≈ $T \cdot N \cdot$ (per-token FLOPs)。AR 是 $N \cdot$ (per-token FLOPs，带 KV-cache)。**diffusion 只在 $T \ll N$ 且不需要 KV-cache memory 优势时才赢**。
- **Mercury 1109 tok/s 的真实来源**：(a) 并行 commit 多 token，(b) batch 内多个 sequence 并行（throughput 而非 single-stream latency），(c) [推测] 模型本身比同档 AR 小 + INT8/FP8 + 高度 fuse 的 H100 kernel。Inception 没公布 model size，没法做 FLOPs-matched 对比。

### 3. Semi-autoregressive / block 模式

纯 diffusion 的痛点：**长度必须预定**、**长文档质量崩**。两个工程妥协：

- **LLaDA 的 semi-AR**（[paper §3.2.2](https://arxiv.org/abs/2502.09992)）：把生成长度切成 length-$L$ block，**block 之间 AR**（左到右一块一块出），**block 内部 diffusion**（一块内并行 unmask）。effectively 把"预定长度"问题缩到 block 级。
- **Block Diffusion / BD3-LM**（[arxiv:2503.09573](https://arxiv.org/abs/2503.09573)）：同样思想但更系统化，关键发现是 **block 间 AR 让 KV-cache 重新可用**（缓存已 commit 的 block），跨 block 推理省一大笔。Cornell 团队（包含 MDLM 作者 Sahoo, Kuleshov）。这是目前学术上最 promising 的 hybrid 路线。
- Gemini Diffusion 是否用了 block 模式 [unknown — Google 没披露任何架构细节，只放了 demo 视频和 throughput 数字]。

### 4. Mercury 的工程实现 [大半推测]

Inception Labs 没开源、tech report 也很简短（[arxiv:2506.17298](https://arxiv.org/abs/2506.17298) 主要是 benchmark + product positioning，不讲架构）。能确认的：
- backbone 是 transformer，**bidirectional attention**。
- 训练目标是 masked diffusion 系（Ermon 的工作脉络）。
- 推理端有专门 kernel，强调 H100 throughput。
- code-specific：FIM、code-context 优化。

不能确认的：模型尺寸、训练 token 量、tokenizer、是否 semi-AR、采样步数。

## 训练方法核心

### Pretrain

- **LLaDA 8B**：2.3T token，从头训（不是从 LLaMA 蒸馏）。Tokenizer 是自家 BBPE。Bidirectional transformer，~LLaMA3-8B 同尺寸。算力 ~0.13M H800-hours（[paper §4](https://arxiv.org/abs/2502.09992)）。**关键 finding**：在 fixed compute 下，diffusion 训练的 scaling law 斜率与 AR 相近，但**绝对 loss 高约 0.2 nats**，对应 downstream benchmark 落后 5-10 pt。这是目前 diffusion LM 最诚实的代价。
- **Mercury**：[unknown — Inception 没披露训练数据 / 算力 / tokenizer]。
- **Gemini Diffusion**：完全 [unknown]。

### Post-train

- **LLaDA SFT**：直接在 masked diffusion 目标上做 instruction tuning（mask response 部分，prompt 不 mask），数据 ~4.5M 样本（[paper §4.2](https://arxiv.org/abs/2502.09992)）。
- **LLaDA RL**：1.5 版本加了 preference learning，但**还没有公开的、严肃的 RLVR on diffusion LM** 工作 —— GRPO 类算法默认假设 AR token-level log-prob，在 diffusion 上 reward 怎么 attribute 到 denoising step 是开放问题。RUC 后续在 [arxiv:2509.xxxxx LLaDA-RL uncertain] 提了一个 step-wise reward 设计，但效果未达到 Qwen2.5-RL 同档。
- **Mercury RLHF**：[unknown — 仅 product blog 说 "instruction-tuned and aligned"]。

### 训练稳定性

- masked diffusion 训练**比 AR 稳**（本质上是 BERT-style MLM，社区做了 5 年），LLaDA paper 报告无 loss spike。
- bidirectional attention 的注意点：**没有 causal mask 意味着 train-test 模式一致**（不像 AR 有 teacher-forcing → free-run gap），但也意味着 **flash-attention causal 优化路径用不上**，需要走 full attention kernel。

## 与 eval / benchmark 的接口

诚实地说 —— 这是 diffusion LM 现在最薄弱的一环。

| Bench | LLaDA 8B Instruct | LLaMA3-8B Instruct | Qwen2.5-7B Instruct | Mercury Coder Small (自报) |
|---|---|---|---|---|
| MMLU | 65.9 | 68.4 | 74.2 | — |
| GSM8K | 70.7 | 79.6 | 85.4 | — |
| HumanEval | 33.5 | 59.8 | 84.8 | **88.0** [自报] |
| MBPP | 38.2 | 57.6 | 79.2 | **77.1** [自报] |
| BBH | 49.8 | 61.1 | 70.4 | — |

来源：[LLaDA paper §5](https://arxiv.org/abs/2502.09992), [Mercury tech report Table 1](https://arxiv.org/abs/2506.17298)。

要点（**给评测 owner 看的话**）：
- **LLaDA 8B 在所有通用 bench 上输给同尺寸 LLaMA3-8B 5-15 pt，输给 Qwen2.5-7B 更多**。Paper 自己承认"在 reasoning / math 上仍有 gap"。
- **Mercury 的 HumanEval/MBPP 数字看起来漂亮，但 (a) 模型尺寸不披露，没法 FLOPs-match，(b) Copilot Arena 速度第二、质量未进前列，(c) HumanEval 早被认为过度优化、看 LiveCodeBench / SWE-Bench 更稳**。Inception 在 tech report 给了 LiveCodeBench / EvalPlus，分数中等。
- **Gemini Diffusion** 只有 demo，没有公开 benchmark。Google I/O 演示主要是 throughput 和"实时 typing"视觉效果。
- **没有任何 diffusion LM 公开过 AIME / GPQA / SWE-Bench Verified 的有竞争力数字**（截至 2026-05）。这是判断这条路线是否真的能挑战 AR 的下一个里程碑。

第三方信号：
- **Artificial Analysis** 把 Mercury Coder 列在 speed leaderboard 而非 intelligence leaderboard，分类很说明问题。
- **Copilot Arena**（[copilot-arena.github.io](https://copilot-arena.github.io/)）Mercury 排在 latency Pareto 前沿，但 quality 维度落后 Claude / GPT-4 系。
- **Sasha Rush, Yoav Goldberg, 张俊林** 在 X 上对 Gemini Diffusion 的共识：**impressive engineering demo, 但还不能下结论说这是 AR 的替代品**，等 Google 出第一个 frontier 级 benchmark 数字再说。

## 未知与争议

- **同 FLOPs 下 diffusion LM 是否能追上 AR**：现有证据（LLaDA scaling、SEDD scaling）显示**还落后 0.1-0.3 nats 的 loss**。这个 gap 是不是可被新目标 / 新采样关上，是 2026-2027 决定这条路线生死的核心实证问题。
- **Diffusion LM + RL**：reward attribution、advantage estimation 没有 settled algorithm。Ermon 组、CMU、Cornell 几条线在做，但还没有 "GRPO-for-diffusion" 的标准答案。
- **长上下文**：LLaDA 训练 ctx 4K，最长测过 8K。**diffusion LM 在 100K+ ctx 是否 work [unknown]** —— bidirectional full attention 在长 ctx 下 FLOPs 比 AR 翻倍以上，工程上很难。
- **Test-time scaling**：diffusion 的"步数 $T$"是天然的 compute knob，是否能像 o1 的 thinking-token 那样换来 monotonic 智能提升？早期实验（LLaDA paper Fig 5）显示 $T$ 增加只在低 $T$ 时有用，high-$T$ 区段 plateau —— 远不如 AR thinking 的 scaling 好。
- **Gemini Diffusion** 是 production roadmap 还是科研 demo 实在难说。Google 至今没把它放进 Gemini 2.5 / 3 主线产品。[推测] DeepMind 内部把它当作 long-term bet 而非短期产品。
- **Mercury 真实模型尺寸 / 训练成本**：Inception 完全 black box。社区估算 7-13B AR-equivalent，无确认。
- **Any-to-any diffusion（Transfusion / Bagel / Show-o）** 与本节文本 diffusion **是不同的赌注** —— 那些模型 backbone 仍是 AR transformer，只在图像 token 上用 diffusion head。属于 C 部分，不要混。
- **Mercury v2 / Mercury Reasoning** [uncertain]：Inception 在 2025 末预告过 reasoning 版本，截至 2026-05 是否 GA [unknown — 没找到一手 source]。

## 推荐外部材料

- [LLaDA paper (arxiv:2502.09992)](https://arxiv.org/abs/2502.09992) — 必读。8B masked diffusion LM 的第一篇 frontier-attempt，附完整 scaling、SFT、benchmark；§3 是 masked diffusion 数学最 readable 的入门。
- [Mercury tech report (arxiv:2506.17298)](https://arxiv.org/abs/2506.17298) — 短，但是 Inception 唯一的一手技术 source；要看 Mercury 怎么 position 自己，看这个。
- [SEDD (arxiv:2310.16834)](https://arxiv.org/abs/2310.16834) — Ermon 组开启这一波 discrete diffusion 复兴的核心论文，score entropy 目标的原文。
- [MDLM (arxiv:2406.07524)](https://arxiv.org/abs/2406.07524) — 把 masked diffusion 目标简化为加权 BERT loss，**之后所有 masked-diffusion LM (含 LLaDA) 训练 infra 的事实标准**。
- [Block Diffusion / BD3-LM (arxiv:2503.09573)](https://arxiv.org/abs/2503.09573) — block-AR + 内 diffusion 的 hybrid，目前学术上最 promising 的"工程妥协"路线，关键是恢复 KV-cache。
- [Aaron Lou, "What is Discrete Diffusion?" blog (2024)](https://aaronlou.com/blog/2024/discrete-diffusion/) — SEDD 一作的非论文解释，直觉远好于直接读 paper。
- [Sasha Rush 的 discrete-diffusion 讲义 + nanoGPT-style minimal impl](https://github.com/srush/MiniDiffuse) — 想自己跑一个最小 masked-diffusion LM，从这里开始。
- [Gemini Diffusion 官方页](https://deepmind.google/models/gemini-diffusion/) — Google 唯一公开材料，看 demo 视频感受 "千 tok/s typing" 的 UX。
- [Inception Labs blog](https://www.inceptionlabs.ai/news/announcing-mercury) — Mercury 发布稿，含 Ermon / Stefano 团队背景，理解为什么 Mercury 是 SEDD 路线的商业化延伸。
- [Lilian Weng, "Diffusion Models" (2021, 持续更新)](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/) — 不是专门讲文本 diffusion，但 forward/reverse process / ELBO 推导是所有 diffusion 的共同基础。
- [张俊林 知乎 "扩散语言模型：从 SEDD 到 LLaDA"](https://zhuanlan.zhihu.com/) [uncertain 具体链接 — 张俊林 2025 H1 多次写过 diffusion LM 综述，搜关键词可找] — 中文视角综述。
