# Zhipu / Z.ai GLM-4.5 → GLM-4.5-Air → GLM-4.6 家族

## 路线定位

Zhipu（海外品牌 Z.ai，源自清华唐杰组）2025 年彻底转向 **"agentic + reasoning + coding"（官方缩写 ARC）三合一 foundation model** 路线，与 DeepSeek 的"架构创新 + 极致 infra"、Qwen 的"全谱系全 size"打法明显错开 —— GLM-4.5 把**agentic capability 作为 pretrain + post-train 一等公民**而不是事后 fine-tune 出来的能力，这是和 DeepSeek-V3.1 / Kimi K2 最关键的差异化。代表作 GLM-4.5（355B-A32B）在 SWE-bench Verified / TAU-Bench / BrowseComp 系列上是 2025-Q3 唯一对标 Claude 4 Sonnet 的开源权重模型，权重 MIT 协议放出，对中国开源生态意义大约相当于 R1 之于 reasoning。([z.ai blog 2025-07-28](https://z.ai/blog/glm-4.5)、[GLM-4.5 tech report arxiv:2508.06471](https://arxiv.org/abs/2508.06471))

## 代表模型清单

| 模型 | 发布日 | 参数 / 激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| ChatGLM-6B / GLM-130B | 2022-08 / 2023-03 | dense | GLM autoregressive blank infilling 架构（已弃用） | [arxiv:2210.02414](https://arxiv.org/abs/2210.02414) |
| GLM-4 / GLM-4-9B | 2024-06 | dense 9B + 闭源大版本 | 转向 Llama-style decoder-only；9B 开源 | [github.com/THUDM/GLM-4](https://github.com/THUDM/GLM-4) |
| GLM-4-Plus | 2024-10 | 闭源 | API-only flagship，对标 GPT-4o | [z.ai blog](https://z.ai/) |
| GLM-Z1 / GLM-Z1-Rumination | 2025-04 | 32B dense | 第一代 reasoning 模型，long CoT；Rumination 加 web browsing | [github.com/THUDM/GLM-4-Z1](https://github.com/THUDM/GLM-4-Z1) |
| **GLM-4.5** | 2025-07-28 | **355B / 32B act** MoE | ARC 旗舰，hybrid thinking，agentic-first，MIT 开源 | [z.ai blog](https://z.ai/blog/glm-4.5)、[arxiv:2508.06471](https://arxiv.org/abs/2508.06471)、[HF zai-org/GLM-4.5](https://huggingface.co/zai-org/GLM-4.5) |
| **GLM-4.5-Air** | 2025-07-28 | **106B / 12B act** MoE | 同架构小版，单卡 H100/H200 可服务 | [HF zai-org/GLM-4.5-Air](https://huggingface.co/zai-org/GLM-4.5-Air) |
| GLM-4.5-X / AirX / Flash | 2025-08 | 同上 | API 上的速度档（X = 高速；Flash = 免费）；权重未单独放 | [z.ai API docs](https://docs.z.ai/) |
| GLM-4.5V | 2025-08-11 | 106B / 12B act + ViT | 在 4.5-Air 上加视觉，agentic VLM | [HF zai-org/GLM-4.5V](https://huggingface.co/zai-org/GLM-4.5V)、[arxiv:2508.06471 §6](https://arxiv.org/abs/2508.06471) |
| **GLM-4.6** | 2025-09-30 | 355B / 32B act（同 4.5 架构） | **200K context**（从 128K 扩）、coding/agent 大幅提升、token 效率 ~+15% | [z.ai blog 2025-09-30](https://z.ai/blog/glm-4.6)、[HF zai-org/GLM-4.6](https://huggingface.co/zai-org/GLM-4.6) |
| GLM-4.6-Air | 2025-11 [uncertain — 截至 2026-05 z.ai 只在 changelog 提及 "coming soon"，正式 HF release 未确认] | — | — | [z.ai changelog](https://docs.z.ai/) |
| GLM-5 / 下一代 | — | — | [unknown — 截至 2026-05 没有官方发布或可信 leak] | — |

## 架构核心（按 tech report 写的）

> 主要 source = [GLM-4.5 tech report arxiv:2508.06471](https://arxiv.org/abs/2508.06471) §3 + [github.com/zai-org/GLM-4.5](https://github.com/zai-org/GLM-4.5) 的 config.json。

### 整体形状："deep-and-thin"，刻意反 DeepSeek-V3

GLM-4.5 (355B/A32B) 和 DeepSeek-V3 (671B/A37B) 参数同量级，但形状选了相反方向：

| 维度 | GLM-4.5 | DeepSeek-V3 |
|---|---|---|
| layers | **92** | 61 |
| hidden_size | 5120 | 7168 |
| FFN intermediate (per expert) | 1536 | 2048 |
| routed experts | 160 | 256 |
| top-k routed | 8 | 8 |
| shared experts | 1 | 1 |
| attention | **GQA (96 Q-heads, 8 KV-heads)** | MLA |
| total / active | 355B / 32B | 671B / 37B |
| ctx (4.5 / 4.6) | 128K / 200K | 128K |

Tech report §3.1 明确说选 deep-and-thin 的理由是 **"reasoning capability 与 depth 的相关性高于与 width 的相关性"**，并 cite 自己在 Z1 时期的 scaling 小实验（paper Fig 2）—— 同算力同参数，layer 多 30% 在 MATH/GPQA 上稳定 +1~2 pt。这是和 Kimi K2 / DeepSeek-V3 都不同的判断，焱拳团队在 Qwen3 scaling 决策里也碰过这个 trade-off，值得对比。

### Attention：**GQA + partial RoPE + QK-Norm**，没有用 MLA

这是 GLM-4.5 和 DeepSeek 路线最大的架构差异之一。Tech report §3.1 对 MLA 的评论："we found GQA sufficient under our serving constraints, and avoids the implementation complexity of MLA's decoupled-RoPE." 关键参数：
- **96 query heads / 8 KV heads**（GQA-12），head_dim = 128
- **Partial RoPE**：只在每个 head 的前一半维度（64 维）施加 RoPE，剩下一半 no-pos —— 同 GLM-4 / ChatGLM2 时代延续下来，[uncertain — paper 给了选择，没给消融]
- **QK-Norm**：query 和 key 在 RoPE 之前各过一次 RMSNorm，稳定 long-context 训练时的 attention logits scale。这条来自 [Gemma 2 / Chameleon 系列](https://arxiv.org/abs/2405.09818)，2025 年逐渐成为标配。
- attention bias = false，head 上无 attention sink token。

KV cache 估算（128K ctx, fp16）= 92 layers × 8 KV-heads × 128 × 2 × 128K ≈ **48 GB per request**，比 DeepSeek-V3 (MLA, 128K, 同 batch) 的 ~9 GB 大 5×。这是 GLM-4.5 在长上下文 serving 上需要额外 KV 压缩 trick（FP8 KV / chunked prefill）的根本原因。GLM-4.6 把 ctx 扩到 200K，serving 上靠的是 SGLang + FP8 KV cache 而不是架构改动。([z.ai 4.6 blog](https://z.ai/blog/glm-4.6))

### MoE：fine-grained + 1 shared，aux-loss-free LB

- **160 routed experts + 1 shared，top-8 routed**。粒度比 V3（256 routed）粗一些，但 active expert 数同样 9 个（8+1）。
- Load balancing：**直接采用 DeepSeek 的 auxiliary-loss-free bias controller**（[arxiv:2408.15664](https://arxiv.org/abs/2408.15664)）。Tech report §3.2 致谢并 cite。
- 仍保留一个极小的 sequence-level aux loss 防极端，系数 1e-4 量级。
- expert 初始化用 **MoE upcycling** 的变体：先 dense pretrain 一个小模型，再 split 成 routed experts。[uncertain — paper 提到 "we explored upcycling vs from-scratch", 最终选择没给死]

### MTP（Multi-Token Prediction）

GLM-4.5 也用了 V3-style 的 1-token MTP 辅助目标 + speculative decoding head。tech report §3.3 报 MTP head 在 vLLM/SGLang 上线推理时接受率 ~75–85%（略低于 V3 的 85-90%，原因推测是 deep-and-thin 架构 main-model 已较快），TPS ~1.5–1.8×。

### Hybrid thinking 模式

和 Claude 3.7、DeepSeek-V3.1 一路：**同一份权重**用 chat template 切换 `thinking=True/False`。`<think>...</think>` 段在 thinking 模式自动产生，non-thinking 模式被 system prompt 抑制。两种模式都参与 post-train RL（关键 —— 见后），所以 GLM-4.5 的 non-thinking 也比传统 chat 模型显著强。

## 训练方法核心

### Pretrain
- **总 token 量 ~23T**（base pretrain 15T + mid-train 7T + long-context 阶段）—— [tech report §4.1](https://arxiv.org/abs/2508.06471)，数字比 V3 的 14.8T 多 ~55%。
- Tokenizer：150K BBPE，扩了中文 + 代码 + 数学符号，paper §4.2 报 zh/en token efficiency 比 GPT-4o tokenizer 高 ~15%。
- 数据 mixture：英 + 中 + code + math + **agentic trajectories**（这是和 V3/Qwen3 显著不同的地方）。tech report §4.3 称在 mid-train 阶段刻意混入合成的 tool-call / multi-turn agent trace —— 这是"agentic-first pretrain"的核心实现。具体比例未披露。
- RoPE base = 10000（partial），long-ctx 用 YaRN-style scaling 扩到 128K (GLM-4.5) / 200K (GLM-4.6)。
- Optimizer：**Muon**（[Jordan/Bernstein/Bansal 2024](https://kellerjordan.github.io/posts/muon/)，Moonshot 在 Moonlight 上验证过 frontier scale），不是 AdamW。GLM-4.5 是 DeepSeek-V3 之后**第二个公开宣称 frontier MoE 用 Muon 成功**的工作。tech report §4.4 报 Muon vs AdamW 在同 token budget 下 loss 低约 0.02 nats，且训练更稳。
- 精度：**BF16 + 部分 FP8 GEMM**（不像 V3 那样激进端到端 FP8）。
- 算力：未明确给 GPU 小时数；[unknown — paper 只说 "trained on a large H800 cluster"]。

### Mid-training / annealing
GLM-4.5 把 pretrain 分成三段：
1. **General pretrain** (15T)：标准 mixture，4K seqlen。
2. **Mid-training "capability injection"** (~7T)：上调 code、math、agentic trace 比例到 ~50%，加入合成 reasoning data（来自 GLM-Z1 generation + rejection sampling），seqlen 扩 32K。
3. **Long-context annealing**：YaRN 扩 128K，少量 token (~100B)。

这套三段式比"pretrain → cooldown"两段更接近 Llama-3.1 / Qwen2.5 的做法，paper §4.5 报 mid-train 阶段 MATH / HumanEval 涨幅 ~10 pt。

### Post-train：**Agentic RL with Slime** —— 本节重点

> Tech report §5 + [github.com/THUDM/slime](https://github.com/THUDM/slime)（Zhipu 开源的 RL 训练框架，对应 OpenRLHF / verl）。

GLM-4.5 post-train pipeline 类似 R1 多阶段，但 agentic stage 是**独立的、和 reasoning RL 并列的一阶段**，这是和 DeepSeek/Qwen 最大的不同：

1. **Cold-start SFT** (~few hundred K)：reasoning trace（从 Z1 + rejection sampling）+ agentic trajectories（合成 + 人标）+ general chat。
2. **Reasoning RL**：GRPO 变体，rule-based reward（math/code verifier，同 R1）。
3. **Agentic RL**：
   - Environment = 真实可执行 sandbox（code interpreter、web browser、tool API simulator）。
   - Reward = **task-level outcome reward**（不是 step-level PRM）：SWE-bench style 任务用 testcase 通过率；browser 任务用 final answer match；tool-use 用 trajectory 完成率。
   - 算法：GRPO + length-normalized advantage（防 long-trajectory 被惩罚）。
   - 关键 infra 挑战：每个 rollout 涉及多轮 tool call，单条轨迹可能 30K+ token，bsz × group_size × rollout_len 显存爆炸。Slime 的解法是**异步 rollout + KV cache 复用 + partial-rollout 复用**（tech report §5.3，是 paper 里最有 infra 内容的一节）。
4. **General preference RL**：写作 / 安全用 reward model，类似 RLHF。
5. **Hybrid thinking joint training**：thinking / non-thinking 两种模式**在同一 RL run 里**用不同 system prompt mask 一起训，防止 non-thinking 模式退化。

注意：**没有公开过显式的 PRM（process reward model）**。所有 reward 都是 rule / verifier 或最终 RM，这和 DeepSeek 路线一致，和 OpenAI o-series 推测的 PRM 路线相反。

### Slime 框架（值得单独看）
- [github.com/THUDM/slime](https://github.com/THUDM/slime)：Zhipu 开源的 agentic-RL 训练栈，Apache-2.0。
- 设计目标：long-horizon trajectory (tool use) 的高吞吐 RL。
- 关键特性：**rollout 和 train 解耦**（rollout 用 SGLang，train 用 Megatron），中间用环形 buffer + KV 复用。这套架构和 ByteDance verl、字节内部的 Doubao RL 栈思路接近。
- 对焱拳团队意义：如果做 Qwen agentic RL，Slime 是目前**唯一公开**且在 frontier scale 验证过 agentic-RL infra 的开源实现。

## 与 eval / benchmark 的接口

GLM-4.5 / 4.5-Air / 4.6 官方 headline（thinking 模式，[z.ai blog](https://z.ai/blog/glm-4.5) + [tech report §6](https://arxiv.org/abs/2508.06471) + [4.6 blog](https://z.ai/blog/glm-4.6)）：

| Bench | GLM-4.5-Air | GLM-4.5 | GLM-4.6 | 参考 Claude 4 Sonnet | DeepSeek-V3.1 (think) |
|---|---|---|---|---|---|
| MMLU-Pro | 81.4 | 84.6 | 87.2 | 87.3 | 84.8 |
| GPQA Diamond | 75.0 | 79.1 | 82.5 | 75.4 | 80.1 |
| AIME 2024 | 87.0 | 91.0 | 93.9 | — (no think) | 88.4 |
| MATH-500 | — | 98.2 | 98.7 | — | 97.6 |
| LiveCodeBench v6 | 63.3 | 72.9 | 82.8 | 70.5 | 74.8 |
| **SWE-bench Verified** | 57.6 | **64.2** | **68.0** | 70.4 | 66.0 |
| **TAU-Bench (avg)** | 65.5 | **70.1** | 72.4 | 70.8 | — |
| **BFCL-v3** | 76.2 | 77.8 | 79.2 | — | — |
| BrowseComp (en) | — | 26.4 | — | — | — |
| Aider-polyglot | — | — | 72.4 | 70.6 | 71.6 |

Headline message（paper 自己也强调）：**GLM-4.5 是 2025-07 开源权重里 agentic 三件套（SWE-bench / TAU-Bench / BFCL）都到 frontier 的第一个**，GLM-4.6 把 coding / agentic 进一步推到打平或略超 Claude Sonnet 4。

### 第三方独立复现 / 质疑
- **SWE-bench Verified**：[Aider leaderboard](https://aider.chat/docs/leaderboards/) 独立跑出 GLM-4.5 ≈ 60（官方 64.2），差距在 scaffold 选择上；GLM-4.6 [SWE-bench 官方 leaderboard](https://www.swebench.com/) 上 zai-org 提交在 67-68 区间，与官方吻合。
- **TAU-Bench**：[Sierra 官方 TAU-Bench leaderboard](https://github.com/sierra-research/tau-bench) 上 GLM-4.5 retail/airline 平均 ~68，比官方 70.1 略低，差距在 prompt template 上。
- **Artificial Analysis** 综合榜 2025-Q4：GLM-4.6 在"Intelligence Index"开源组排第 2（仅次于 DeepSeek-V3.2 / Kimi K2），和 Qwen3-235B-A22B-Thinking 接近。
- **agent eval contamination 风险**：GLM-4.5 在 mid-train 阶段刻意注入 agentic synthetic trace，是否包含 SWE-bench / TAU-bench 任务的近邻样本，paper 没给出 decontamination 细节，[uncertain]。这一条对焱拳团队 eval 设计是真实风险点。

## 未知与争议

- **mid-train 的 agentic synthetic data 来源**：tech report 只说"自合成 + 过滤"，具体是用哪个模型 rollout、reward 模型、过滤阈值都未披露。复现门槛极高。
- **Muon 在 355B / FP8 下的稳定性**：paper 只给 loss 曲线，未给 ablation / failure case。Moonshot 在 Moonlight tech report 给了更多 Muon 细节，建议交叉看。
- **GLM-4.6 vs 4.5 的训练增量**：z.ai blog 只说 "continual training + improved post-train"，没给增量 token 数 / 算力，[unknown]。
- **agentic RL 的 reward hacking 案例**：paper §5.4 提了一句 "we observed reward hacking when rollout length is uncapped"，没给具体例子或缓解细节，对要复现的人是 black box。
- **闭源 GLM-4.5-X / Flash 与开源版差异**：API 上的 X / Flash 是否是同权重的不同 quant / serving 配置，还是单独训练，z.ai 未明确说明。
- **GLM-4.6 对中文 agent / 工具调用的优化**：blog 提"中文 tool-use 大幅提升"，但官方没放中文 agentic bench；[unknown — 国内独立中文 agent bench 也未广泛覆盖]。

## 推荐外部材料

- [GLM-4.5 tech report (arxiv:2508.06471)](https://arxiv.org/abs/2508.06471) — 必读。架构 + Slime + agentic RL pipeline 是 2025 年继 V3 / R1 之后第二份"几乎全披露"的 frontier MoE tech report。
- [z.ai 官方 blog: GLM-4.5](https://z.ai/blog/glm-4.5) 和 [GLM-4.6](https://z.ai/blog/glm-4.6) — release notes 形式，benchmark 表最权威。
- [github.com/zai-org/GLM-4.5](https://github.com/zai-org/GLM-4.5) — 含 config.json、推理脚本、chat template；想看 hybrid thinking 怎么实现就看 template 文件。
- [github.com/THUDM/slime](https://github.com/THUDM/slime) — Zhipu 开源 agentic-RL 框架。研究 agent RL infra 必看，目前唯一在 frontier scale 验证过的开源对照物（vs verl / OpenRLHF）。
- [Nathan Lambert, "GLM-4.5 and the open agent stack" interconnects.ai 2025-08](https://www.interconnects.ai/) — Lambert 把 GLM-4.5 放在 "open agentic foundation model" 谱系里讨论，对 agentic-first 设计的判断比 z.ai 自家 blog 更冷静。[uncertain — 标题为示意，请核对具体 post]
- [Keller Jordan, "Muon: An optimizer for hidden layers in neural networks"](https://kellerjordan.github.io/posts/muon/) — Muon 原文，理解 GLM-4.5 optimizer 选择。
- [Moonshot Moonlight tech report (arxiv:2502.16982)](https://arxiv.org/abs/2502.16982) — Muon 在另一个 frontier MoE 上的独立验证，与 GLM-4.5 交叉看。
- [Sierra TAU-Bench paper (arxiv:2406.12045)](https://arxiv.org/abs/2406.12045) — 想理解 GLM-4.5 头号 agentic benchmark 怎么算分，去看 task 构造。
- [DeepSeek aux-loss-free LB (arxiv:2408.15664)](https://arxiv.org/abs/2408.15664) — GLM-4.5 直接采用，理解 MoE load balancing 必读。
