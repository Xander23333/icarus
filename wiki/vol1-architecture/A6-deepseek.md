# DeepSeek V2 → V3 → R1 → V3.1/V3.2 家族

## 路线定位

DeepSeek (幻方旗下) 走的是**"open-weight + 架构创新 + 极致 infra 效率"** 路线，是 2024-2025 唯一在 frontier capability 上能逼近 closed lab 的中国开源团队。技术差异化集中在四件事：**MLA**（KV cache 压到 GQA 的 ~1/4）、**aux-loss-free MoE load balancing**、**MTP (Multi-Token Prediction) 训练目标**、以及 **R1-Zero 证明纯 RL（无 SFT cold start）可以涌现 long CoT**。竞品在 open 圈是 Qwen、Llama 4、Kimi K2；在 closed 圈是 GPT-4o/o-series 和 Claude。商业模式上靠极低 API 价格 + Liang 在采访中明确说"AGI research first, revenue 不是目标"（[暗涌 36kr 2024-07](https://www.36kr.com/p/2898488061386881)、[Liang 2024-11 访谈](https://www.chinatalk.media/p/deepseek-ceo-interview-with-chinas)）。

## 代表模型清单

| 模型 | 发布日 | 参数 / 激活 | 关键变化 | 一手 source |
|---|---|---|---|---|
| DeepSeek LLM 7B/67B | 2024-01 | dense | 第一代 base，Llama-arch dense | [arxiv:2401.02954](https://arxiv.org/abs/2401.02954) |
| DeepSeekMoE 16B | 2024-01 | 16B / 2.8B act | **fine-grained expert + shared expert** 提出 | [arxiv:2401.06066](https://arxiv.org/abs/2401.06066) |
| DeepSeek-V2 | 2024-05 | 236B / 21B act | **MLA** + DeepSeekMoE 合体，128K ctx | [arxiv:2405.04434](https://arxiv.org/abs/2405.04434) |
| DeepSeek-V2.5 / V2-Coder | 2024-09 / 2024-06 | 236B / 21B | chat + code 合并版 | [github.com/deepseek-ai/DeepSeek-V2](https://github.com/deepseek-ai/DeepSeek-V2) |
| DeepSeek-V3 | 2024-12-26 | **671B / 37B act** | aux-loss-free LB + MTP + FP8 训练，14.8T token，**$5.576M** H800 报价 | [arxiv:2412.19437](https://arxiv.org/abs/2412.19437) |
| DeepSeek-R1-Zero / R1 | 2025-01-20 | 同 V3 base | **纯 RL 涌现 reasoning**；R1 = 加 cold-start SFT + multi-stage RL | [arxiv:2501.12948](https://arxiv.org/abs/2501.12948) |
| R1-Distill (Qwen/Llama 1.5B-70B) | 2025-01-20 | dense | 用 R1 输出 SFT 蒸馏 | 同上 |
| DeepSeek-Prover-V2 | 2025-04-30 | 671B | Lean4 formal math，Whole-proof RL | [arxiv:2504.21801](https://arxiv.org/abs/2504.21801) |
| DeepSeek-V3-0324 | 2025-03-24 | 同 V3 | minor refresh，post-train tuning | [HF release](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324) |
| DeepSeek-R1-0528 | 2025-05-28 | 同 R1 | RL 继续扩，AIME 79.8→87.5；幻觉降 45-50% | [HF model card](https://huggingface.co/deepseek-ai/DeepSeek-R1-0528) |
| **DeepSeek-V3.1** | 2025-08-21 | 671B / 37B | **hybrid thinking + non-thinking 单模型**（一套权重两个模式），128K ctx 默认 | [api-docs.deepseek.com V3.1](https://api-docs.deepseek.com/news/news250821) |
| DeepSeek-V3.1-Terminus | 2025-09-22 | 同 V3.1 | 修 V3.1 的语言混杂、tool-use bug | [HF DeepSeek-V3.1-Terminus](https://huggingface.co/deepseek-ai/DeepSeek-V3.1-Terminus) |
| **DeepSeek-V3.2-Exp** | 2025-09-29 | 671B / 37B | **DeepSeek Sparse Attention (DSA)**：lightning indexer + top-k token selection，长 ctx 推理成本骤降，API 价 -50% | [arxiv:2509.xxxxx / tech report PDF](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp), [api-docs V3.2](https://api-docs.deepseek.com/news/news250929) |
| DeepSeek-V4 / R2 | 2026 上半年? | — | [unknown — 截至 2026-05 没找到 V4 或 R2 的官方发布。2025-Q4 多次外媒/X 传 R2 跳票（[Reuters 2025-08](https://www.reuters.com/technology/artificial-intelligence/deepseeks-r2-launch-delayed-by-huawei-chip-issues-ft-reports-2025-08-14/) 关于 Huawei 910C 训练失败传言），但 DeepSeek 官方未确认。不强行编造] | — |

## 架构核心

### MLA (Multi-head Latent Attention) —— V2 起的核心

> 看 V2 paper §2.1 + 苏剑林 [缓存与效果的极限拉扯](https://kexue.fm/archives/10091) / [MLA 续集](https://kexue.fm/archives/10592)。

动机：**KV cache 是 long-context inference 的硬瓶颈**。GQA / MQA 是把多个 head 共享同一份 KV 来压缩；MLA 走另一条路 —— 把 KV 投影到一个低维 latent $c_t^{KV} \in \mathbb{R}^{d_c}$，inference 只 cache $c_t^{KV}$，每次 attention 时再 up-project 回各 head 的 K、V。

关键技术点：
- **低秩压缩**：$c_t^{KV} = W^{DKV} h_t$，$d_c = 4d_h$（V2 里 $d_c=512$，原始 $d_{model}=5120$，64 head × $d_h=128$）。KV cache 每 token 只存 $d_c + d_h^R$ ≈ 576 维 fp16 = 1.15KB，对比 GQA-8 的 ~2.3KB、MHA 的 ~16KB。([V2 paper Table 1](https://arxiv.org/abs/2405.04434))
- **Decoupled RoPE**：MLA 麻烦在 RoPE 不能直接作用在 latent 上（位置编码和 latent 不交换）。解法 = 把 K 拆成两路：一路从 latent 上投影 (no-RoPE)，另一路 **额外** 维护一个小 head $k_t^R \in \mathbb{R}^{d_h^R}$（$d_h^R=64$）专门带 RoPE，然后拼接。Query 同理拆 $q^C$ + $q^R$。这是 MLA paper 最容易踩坑的实现细节，苏剑林 [这篇](https://kexue.fm/archives/10592) 讲得最细。
- **吸收技巧 (inference)**：$W^{UK}$ 和 $W^Q$ 可以提前合并成单个矩阵，attention 计算时不需要真的把 K 解压出来，等价于直接在 latent 空间做 attention。这是 MLA 比朴素 LoRA-KV 快的关键。
- **效果**：V2 paper Table 1 报，MLA 比 MHA KV cache 小 93.3%，同时 MMLU/BBH 等略**优于** MHA 同算力 baseline（因为 latent bottleneck 类似一种 regularization）。这一点和直觉相反，但多个第三方（Together AI、SGLang impl 团队）独立确认 MLA 在 perplexity 上不输 GQA。

V3 / V3.1 / V3.2 都继承 MLA 不变，参数同 V2（$d_c=512, d_h^R=64$，head 数 128）。

### DeepSeekMoE：fine-grained + shared expert

> 看 DeepSeekMoE paper [arxiv:2401.06066](https://arxiv.org/abs/2401.06066)，V3 paper §2.2。

- **Fine-grained**：把每个 expert 切小（FFN intermediate 维度小一半甚至四分之一），同时把激活 expert 数加多。V3 = 256 routed experts + 1 shared，每 token top-8 routed + 1 shared，激活 37B。对比 Mixtral 8×7B（8 expert top-2）粒度细 ~30×。理论动机：finer-grained 让 expert 更容易 specialize，避免"每个 expert 学得很杂"。
- **Shared expert**：固定 1 个 expert 所有 token 都过，承担 common knowledge，让 routed expert 专心学 specialty。

### MoE Load Balancing：**Auxiliary-Loss-Free**（V3 起）

> V3 paper §2.1.2 + [arxiv:2408.15664 "Auxiliary-Loss-Free LB Strategy"](https://arxiv.org/abs/2408.15664)（DeepSeek 提前发的小 paper）。

历史问题：Switch / GShard 用 auxiliary load-balancing loss（鼓励 expert 用量均匀）会**牺牲主任务 loss**，因为它强行把 token 推到不该去的 expert。

DeepSeek 方案：**给每个 expert 一个 bias $b_i$**，routing score $s_{i,t} = \sigma(\text{gate}) + b_i$ 用于 top-k 选择，但 **weight 计算不带 $b_i$**。训练中按 expert 实时负载调整 $b_i$：过载就 $b_i \mathrel{-}= \gamma$，欠载就 $b_i \mathrel{+}= \gamma$。**没有梯度，纯 controller**。

- 好处：主 loss 不受污染。V3 paper Table 4 报 aux-loss-free 比 aux-loss baseline 在 14 个 bench 几乎全胜，最大 +1.5 pt MMLU。
- 仍保留一个**极小**的 sequence-level aux loss（防止单个序列内极端不均衡），系数 0.0001 量级。
- 实现要点：bias 更新是 per-step 的，$\gamma$ 是超参（V3 用 0.001）。

这个 trick 现在已经被 Qwen3-MoE、Kimi K2 等多家跟进，成为 2025 MoE 训练事实标准。

### MTP (Multi-Token Prediction)

> V3 paper §2.2.2；动机来自 Meta [Better & Faster LLMs via MTP, arxiv:2404.19737](https://arxiv.org/abs/2404.19737)，但 DeepSeek 改了实现。

- 在主模型最后一层之上再接 $D$ 个**串行**（sequential，而非 Meta 的并行 head）的轻量 transformer block，每个预测 $t+2, t+3, \dots$。V3 用 $D=1$（只多预测 1 个未来 token）。
- 第 $k$ 个 MTP module 输入 = 主模型 hidden + 前一个 module 的 hidden + 真实 token embedding，过一个 transformer block + shared head/embedding。
- Loss = 主 NTP loss + $\lambda \sum_k L_k^{MTP}$，$\lambda=0.3$（前 10T token），0.1（剩余）。
- 训练完后 **MTP module 可以扔掉**（V3 上线推理只用主模型），但也可以**保留做 speculative decoding**：第 2 个 token 直接由 MTP module 草拟，主模型验证。V3 paper §5.4.3 报 MTP module 接受率 85-90%，TPS ~1.8×。
- 收益：V3 paper §4.5.1 ablation 说 MTP 让 MMLU +0.5 / HumanEval +2.4，**作为辅助目标本身就涨点**，不光是推理加速。

### FP8 mixed-precision 训练（V3 paper §3）

V3 是**第一个公开 fine-grained FP8 训练成功**的 frontier-scale MoE。要点：
- **Tile-wise / block-wise scaling**：activation 用 1×128 tile，weight 用 128×128 block，各自一个 fp32 scale。避免单一 tensor scale 在 outlier 下崩。
- 关键 GEMM 在 FP8，accumulation 提到 fp32（H800 tensor core 内部 fp32 累加精度不够，DeepSeek 改成定期把部分 partial sum 提升到 CUDA core fp32 累加）。
- master weight / optimizer state 仍 fp32 / bf16。Embedding、output head、attention softmax、MoE gate 全保留高精度。
- 整体训练 loss 与 bf16 baseline 偏差 <0.25%。

整套实现是 V3 能在 **2048×H800 上 2 个月** 训完 14.8T token 的最大单一原因。Liang 在 2024-12 接受 [36kr 暗涌](https://www.36kr.com/p/2898488061386881) 采访说"我们不是在追求便宜，是在追求 efficient frontier"，FP8 + DualPipe + 自研 all-to-all kernel 是这句话的实质。

### DeepSeek Sparse Attention (V3.2-Exp)

> [DeepSeek-V3.2-Exp tech report (github)](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp)，2025-09-29。

V3.2 把 MLA 之上再套了一层 **token-level sparse attention**：
- **Lightning Indexer**：极轻量（少量 head，fp8）的 scoring net，给每个 query 算它对所有过往 token 的相关度。
- **Top-k selection**：每个 query 只对 top-2048 token 做 full MLA attention（其他丢掉）。
- 训练分两阶段：先 dense warmup 让 indexer 学 alignment，再 sparse fine-tune。
- 收益：128K context decoding 成本约 **下降 50%**，benchmark 与 V3.1-Terminus 几乎打平（MMLU-Pro 持平、AIME 略涨）。API 价直接砍半（input cache-miss $0.28 → $0.14 / Mtok）。
- 这是 2025 公开 sparse attention 方案里**第一个在 frontier 体量上真上线**的，预计被广泛跟进。

### Hybrid Thinking (V3.1 起)

V3.1 把"chat" 和 "reasoning" 合到**同一权重**，由 prompt template 切换（`<think>` 是否启用）。这和 Claude 3.7 hybrid reasoning 思路一致，与 R1 时期"V3 base + R1 reasoning model 分离"的旧设计告别。V3.1-Terminus 修复了 V3.1 初版的中英文混杂和 tool-call 偶发故障。

## 训练方法核心

### Pretrain
- V3：**14.8T token**，document packing，FIM (Fill-in-Middle) 比例 0.1。Tokenizer 是 BBPE 128K。([V3 §3.4](https://arxiv.org/abs/2412.19437))
- 数据 mixture：英文 + 中文 + 代码 + math 比例未细披露，但 V3 paper 提到比 V2 显著增加 math + code 占比。
- RoPE base：V3 = 10000，long-context 阶段 YaRN 扩 4K→32K→128K，scaling factor 40。
- 算力：**2.788M H800 GPU-hours total**（含 pretrain + ctx-ext + post-train），按 $2/h 折合 **$5.576M**。这个数字只是 GPU 租用电费等价物，不含研发/失败/数据/工资 —— 很多媒体误读为"总训练成本"。Liang 在采访中也强调"这不是 frontier 模型的真实门槛"。

### Post-train: R1-Zero —— **本节重点**

> [arxiv:2501.12948](https://arxiv.org/abs/2501.12948)。配合 Sebastian Raschka [Understanding Reasoning LLMs](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms)、Nathan Lambert [interconnects.ai R1 解析](https://www.interconnects.ai/p/deepseek-r1-recipe-for-o1) 一起看。

**核心 claim**：**直接对 V3-Base 做 RL，不做任何 SFT cold start，long CoT 行为会自然涌现**，包括 self-verification、reflection、"aha moment"（paper Table 3 给了著名的"Wait, let me rethink"例子）。

具体配方：
- **算法 = GRPO (Group Relative Policy Optimization)**，[arxiv:2402.03300 DeepSeekMath](https://arxiv.org/abs/2402.03300) 提出。和 PPO 的区别：
  - 不训 value model，advantage 用 **同 prompt 多 sample 的 reward 的 z-score**：$A_i = (r_i - \text{mean}(r)) / \text{std}(r)$。
  - Loss = clipped ratio × A + β·KL(πθ || π_ref)，KL 直接对 token-level policy 做。
  - 省一个 critic 模型的显存 → 同算力可以 sample 更多 group（V3 paper 报 group size = 16~64）。
- **Reward = rule-based**（**关键，无 reward model**）：
  1. **Accuracy reward**：math 题对答案数值判等；code 题跑 testcase 看 pass。**完全 verifiable，没有 PRM/ORM。**
  2. **Format reward**：要求 `<think>...</think><answer>...</answer>` 结构，违反给 0。
- **训练曲线**（paper Fig 2/3）：
  - AIME 2024 pass@1 从 V3-Base 的 15.6% **平滑爬到 71.0%**（majority@16 86.7%），数千 step 之内。
  - 平均 response length 从 ~1K token 自发涨到 ~10K token，**长度不是被 reward 显式鼓励的**，而是模型发现"想得长 → 答对率高 → reward 高"。
  - Paper §2.2.4 "Aha Moment" 章节展示 mid-training 模型突然出现 "Wait, wait. Wait. That's an aha moment I can flag here." 的自我反思，作者明确说这是涌现的、不在数据里的。
- **R1-Zero 的问题**：可读性差，中英文混杂，有时跳过 reasoning 直接给答。所以**R1（非 Zero）= 多阶段管道**：
  1. **Cold-start SFT**：用 R1-Zero 生成的高质量 trace + 人工 refine 的 few-thousand 长 CoT 样本 SFT。
  2. **Reasoning RL**（同 R1-Zero 配方，加 language consistency reward）。
  3. **Rejection sampling + SFT**：用上一步模型 sample 大量 reasoning trace，rule-based 过滤，混入 general-domain SFT (writing/QA 等) 600K + 200K。
  4. **第二轮 RL**：reasoning task 仍用 rule reward；general/safety task 用 preference reward model。
- **R1-Distill**：用上面 800K SFT 数据直接 SFT Qwen2.5-1.5/7/14/32B 和 Llama-3.x-8/70B。**不做 RL** 就能在 AIME 上把 Qwen2.5-32B 从 17% 拉到 72%。这一发现的实践含义：**对小模型，蒸馏 reasoning trace 比自己跑 RL cost-effective 得多**——读者团队做 Qwen agentic distill 时这条路径直接被验证过。
- Paper §3.2 同时报告一个**失败实验**：直接对 Qwen-32B-Base 跑 R1-Zero 配方 RL，效果远不如 distill。Authors 推测小 base 缺少 reasoning 的"基础能力存量"，RL 无法从零激发。这一点和 [Yixin Liu/Tsinghua "RL doesn't add new capability" 系列](https://arxiv.org/abs/2504.13837) 形成有趣对照。

### Post-train: R1-0528
2025-05 更新。RL 继续扩 token budget（traces 平均长度从 R1 的 ~12K 涨到 ~23K），AIME 2024 79.8% → **87.5%**。幻觉率官方报告下降 45-50%。重要 release notes：[github.com/deepseek-ai/DeepSeek-R1 README](https://github.com/deepseek-ai/DeepSeek-R1)。

### Post-train: V3.1+ 的 agentic + tool RL
V3.1 引入 tool use / agent 模式，post-train 加入 tool-use trajectory RL（细节未在 paper 公开，只在 API release notes 提及）。具体 reward shaping / verifier 设计 [unknown]。

## 与 eval / benchmark 的接口

V3 / R1 / R1-0528 / V3.2 官方 headline：

| Bench | V3 | R1 | R1-0528 | V3.1 (think) | V3.2-Exp |
|---|---|---|---|---|---|
| MMLU-Redux (EM) | 89.1 | 92.9 | — | 91.8 | 93.1 |
| GPQA Diamond | 59.1 | 71.5 | 81.0 | 80.1 | 79.9 |
| AIME 2024 pass@1 | 39.2 | 79.8 | **87.5** | 88.4 | 89.3 |
| MATH-500 | 90.2 | 97.3 | — | 97.6 | — |
| HumanEval-Mul | 82.6 | — | — | 83 | — |
| LiveCodeBench | 40.5 | 65.9 | 73.3 | 74.8 | 75.4 |
| SWE-Bench Verified | 42.0 (V3) | 49.2 (R1) | — | 66.0 (V3.1 think) | 67.8 |
| Aider-polyglot | — | 53.3 | — | 71.6 | — |

第三方复现 / 质疑：
- R1 的 AIME 数字 [LiveCodeBench/AIME 复现 Hugging Face Open-R1 项目](https://github.com/huggingface/open-r1) 大致复现到 ±2 pt。
- LiveBench / SimpleBench 等独立榜 R1 排在 o1 之下、Sonnet 之上，与 paper claim 一致。
- **Contamination 信号**：[Scale AI 2024-12 study](https://scale.com/research/mmlu-redux) 测 V3 在 MMLU-Pro 上的"自家测的版本"与第三方 hold-out 差距 < 1 pt，相对干净。但 R1 在 MATH-500 接近饱和（97.3），细颗粒的 contamination 检查难做。
- **GRPO 复现**：开源 verl / OpenRLHF / TRL 都已实现 GRPO，Open-R1、SimpleRL-Zoo、TinyZero 等项目在小模型 (Qwen 1.5B-7B) 上**部分复现**了"长度自发增长 + aha moment"，但 [Sea AI lab 2025-02 "There may not be Aha Moment"](https://oatllm.notion.site/oat-zero) 论证"aha"字符串其实在 base 模型 generation 里已有，RL 只是放大频率，质疑涌现叙事。这点读者团队如果做 RL ablation 值得重点关注。

## 未知与争议

- **训练数据细节**：14.8T 的语种 / domain 比例 / 是否含 OpenAI 输出（蒸馏指控）—— DeepSeek 否认蒸馏 OpenAI，但 [Bloomberg 2025-01 报道](https://www.bloomberg.com/news/articles/2025-01-29/microsoft-probing-if-deepseek-linked-group-improperly-obtained-openai-data) 微软在调查。无定论。
- **R2 / V4 发布时间**：传闻多次，官方一直没确认。截至 2026-05 没有可信一手 source。
- **Huawei 910C 训练失败传言**：[FT 2025-08](https://www.ft.com/content/) 报 R2 试图用 Ascend 训练遇挫，DeepSeek 未回应。
- **GRPO 是否真的优于 PPO**：DeepSeekMath paper 给了 ablation，但 [TRL/Hugging Face 团队 2025-Q1 系列 blog](https://huggingface.co/blog/grpo) 在小模型上发现 PPO + 简化 reward 可以追平 GRPO。在 frontier 上谁更好仍开放。
- **R1-Zero 的"涌现"性质**：见上面 Sea AI lab 质疑。"是否真的从 Base 涌现" 取决于 base 模型预训练里 reasoning trace 的密度，V3-Base 用了多少 reasoning-flavor 数据未披露。
- **Aux-loss-free LB 的稳定性**：少数复现报告（Skywork-MoE 团队）反映 bias controller 在某些数据 schedule 下震荡；DeepSeek 自己未发声。

## 推荐外部材料

- [DeepSeek-V3 technical report (arxiv:2412.19437)](https://arxiv.org/abs/2412.19437) — 必读。MLA / aux-loss-free / MTP / FP8 / DualPipe 五件套全在一篇里。
- [DeepSeek-R1 paper (arxiv:2501.12948)](https://arxiv.org/abs/2501.12948) — R1-Zero 配方原文，第 2 节就是全部 RL pipeline，比想象的短。
- [苏剑林 "缓存与效果的极限拉扯" + MLA 续集](https://kexue.fm/archives/10091) — MLA 推导与 RoPE 解耦最清楚的中文讲解，比 paper 自己写得好。
- [张俊林《关于 DeepSeek 的几点思考》知乎 2025-02](https://zhuanlan.zhihu.com/p/19994464327) — V3/R1 全景，配合"长 CoT 为什么 work"的解释，国内最系统的一篇。
- [Sebastian Raschka, Understanding Reasoning LLMs 2025-02](https://magazine.sebastianraschka.com/p/understanding-reasoning-llms) — 把 R1 / R1-Zero / Distill 三条线和 o1 / Sky-T1 等并排比较，图很清楚。
- [Nathan Lambert, "DeepSeek R1's recipe" interconnects.ai 2025-01](https://www.interconnects.ai/p/deepseek-r1-recipe-for-o1) — RL/post-train 视角，把 R1 放在 RLVR 历史脉络里。
- [Hugging Face Open-R1 项目](https://github.com/huggingface/open-r1) — 开源复现，含完整 GRPO 训练代码和数据 pipeline，要自己跑 R1-style RL 第一站。
- [DeepSeek-V3.2-Exp tech report (github)](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp) — Sparse attention 实现细节 + lightning indexer 训练 trick。
- [Liang Wenfeng 暗涌专访 (36kr)](https://www.36kr.com/p/2898488061386881) + [ChinaTalk 英译版](https://www.chinatalk.media/p/deepseek-ceo-interview-with-chinas) — 想理解为什么 DeepSeek 把架构创新放在 capability 之前，唯一一手 source。
- [Sea AI Lab "There may not be Aha Moment"](https://oatllm.notion.site/oat-zero) — 对 R1-Zero 涌现叙事的最严肃质疑，做 RL ablation 的人必读。
