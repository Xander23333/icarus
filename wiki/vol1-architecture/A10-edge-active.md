// filepath: /root/research-book/vol1-architecture/A10-edge-active.md
# 边缘但仍活着的 LLM 家族（through 2026-05）

## 路线定位

这一节集合**没进 frontier 第一梯队、但还在持续发版且有独立技术信号**的家族。和已经事实出局的（Inflection、Adept、Character、AI21 Jamba 后续停滞、Stability LM、Reka 实际已被收购前的最后版本——见下）不同，这里收的家族在 2025-H2 至 2026-Q2 区间里**至少出过一个非 cosmetic 的新版本**或开源权重，或者在 enterprise/edge/regional 市场占据了 frontier lab 暂时不打的位置。读者 (Qwen agentic eval lead) 主要关心的点是：这些家族的架构/post-train 里有什么**独立信号**值得抄或值得做 contamination check，而不是 marketing。每家 1-2 段，深挖请直接看引用。

---

## Mistral（Large 2 / Medium 3 / Codestral / Magistral）

Mistral 在 2024-Q3 之后明确放弃和 GPT/Claude 正面打 frontier，转向**欧洲主权 AI + open-weight mid-size + 企业垂直**。代表模型：**Mistral Large 2** (123B dense, 2024-07，128K ctx，多语 + code 强化，Mistral Research License non-commercial open weights, [官方 blog](https://mistral.ai/news/mistral-large-2407/))；**Codestral 25.01** (2025-01, 256K ctx，FIM 优化，[Codestral 25.01 blog](https://mistral.ai/news/codestral-2501/))；**Mistral Medium 3** (2025-05, multimodal, API-only, 据称 "8x lower cost than Claude Sonnet 3.7 at 90% 性能"，[Medium 3 blog](https://mistral.ai/news/mistral-medium-3/))；**Magistral Small/Medium** (2025-06, Mistral 的 reasoning 系列，Magistral Small 24B 是开源 Apache-2.0 的 long-CoT 推理模型，[Magistral tech report arxiv:2506.10910](https://arxiv.org/abs/2506.10910))；**Mistral Large 3 / Codestral 2 / Devstral** 2025-Q4 至 2026-Q1 陆续小步迭代（[Devstral 2025-05 blog](https://mistral.ai/news/devstral/) 主打 SWE-bench agentic coding，Devstral Small 24B 在 SWE-bench Verified 报 46.8%，超过同期所有 <100B 开源模型）。

架构上 Mistral 基本是**标准 dense + GQA + sliding-window attention** 的保守路线，没有 MoE/MLA/sparse-attn 类的激进创新（除了早期 Mixtral 8x7B/8x22B 之后没再推 MoE 新代）。Magistral 的 RL 配方是它最值得读的一篇：明确报告了 **GRPO 变体 + reward shaping + 不用 distillation cold start** 也能拿到 long-CoT 能力，和 DeepSeek-R1-Zero 形成有意思的对照（Magistral paper §3-4）。Contamination 信号：Magistral Medium 在 AIME-2024 报 73.6%，第三方 LiveBench 复测掉到 60% 区间，[LiveBench leaderboard](https://livebench.ai/)。

## Cohere（Command A / Command R+ / Aya / North）

Cohere 是**最纯粹的 enterprise-only** 玩家，2024 起几乎不打消费侧，技术路线绑定 RAG + on-prem + 多语。代表模型：**Command R+** (104B, 2024-04，专为 enterprise RAG + tool use 调，[blog](https://cohere.com/blog/command-r-plus-microsoft-azure))；**Command R7B** (2024-12，小模型 RAG/agent 优化，[blog](https://cohere.com/blog/command-r7b))；**Command A** (111B, 2025-03，开源权重 CC-BY-NC, 256K ctx，仅 2× H100 / A100 即可 serve，[Command A blog](https://cohere.com/blog/command-a) + [tech report arxiv:2504.00698](https://arxiv.org/abs/2504.00698))；**Aya Expanse 8B/32B** (2024-10) + **Aya Vision 8B/32B** (2025-03) 多语 + 多模态，覆盖 23-101 语言，[Aya Expanse blog](https://cohere.com/blog/aya-expanse-connecting-our-world)。2025-Q4 推出 **North** (agentic workspace 产品，不是新模型) 和 **Command A Reasoning** (2025-08, [blog](https://cohere.com/blog/command-a-reasoning))。

架构上 Command A tech report 是少见的把 enterprise 配方写得比较细的：**dense + GQA + interleaved sliding-window / full attention layers** (3:1 比例)，**model merging on post-train** —— 6 个 domain-specialized checkpoints (code/math/RAG/safety/long-ctx/multilingual) 各自 SFT+RLHF 后做 weight soup 合并，再做一轮 polish RL (Command A report §4)。这套 "post-train 切片再 merge" 流程是 Cohere 路线的独立信号，和 frontier lab 单一巨型 RL run 形成对比。值得 Qwen eval 注意：Command A 在 ToolBench / BFCL-v3 报告分数很高，但开源圈用 [BFCL leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) 复测有 5-8 分差距，疑似训练时见过 BFCL 风格 schema。

## 01.AI（Yi-Lightning，已基本停摆）

01.AI 路线被现实压垮：**Yi-34B** (2023-11) 曾是中文开源最强；**Yi-Lightning** (2024-10) 在 LMSys Chatbot Arena 短暂冲到 overall #6（[LMSys blog 2024-10](https://lmsys.org/blog/2024-10-yi-lightning/)），是当时唯一进 top 10 的中国闭源模型，MoE 架构、参数未披露。但 2025-Q1 后 01.AI **基本停止 frontier 模型发布**，李开复 2025-07 接受采访明确说 "不再追 GPT-5 量级的预训练，转 enterprise + 行业垂直" ([The Information 2025-07 报道](https://www.theinformation.com/articles/chinese-ai-startup-01-ai-pivots-from-pretraining)，需付费墙)。截至 2026-05 没有新的 base 模型发布，Yi 系列开源权重维护止于 [Yi-1.5 (2024-05)](https://huggingface.co/01-ai/Yi-1.5-34B)。**严格说 01.AI 已经接近"死亡边缘"**，列在这里只是因为 Yi-Lightning 的 Arena 表现至今还被引用做对比基线 [uncertain]。

## Reka（Core / Flash / Edge，2024 之后基本只剩 multimodal demo）

Reka 是 Yi Tay (前 Google Brain) + Dani Yogatama 等创立，主打 **native multimodal (image/video/audio in/out)**。**Reka Core / Flash / Edge** 三档 (2024-04, [tech report](https://publications.reka.ai/reka-core-tech-report.pdf))，Core 是 dense ~67B [推测]，在 MMMU / Perception Test 报和 GPT-4V/Gemini Pro 同档。2024-Q4 发布 **Reka Flash 3** (2025-03, [HF release](https://huggingface.co/RekaAI/reka-flash-3))，21B dense，开源权重 Apache-2.0，是 Reka 唯一开源的版本。2025-08 路透传 Reka **被某 enterprise 收购谈判**，结果未确认 ([Reuters 2025-08](https://www.reuters.com/technology/) [uncertain — 找不到原文 archive])，但截至 2026-05 公司仍在运营，最后一次 release 是 Reka Flash 3.1 (2026-02 [unknown — 没找到一手 blog])。架构独立信号：Reka 是少数公开报告**从头训 native audio-in** 的，不走 Whisper-adapter 路线 (Reka Core report §3.2)。

## MiniMax（M1 / M2 lightning attention）

MiniMax 是中国 to-C AI (Talkie / 海螺 AI) 背后的模型供应方，2024 前低调，2025 起靠 **lightning attention** 路线突然出名。**MiniMax-Text-01** (2025-01, 456B / 45.9B act MoE，**lightning attention + softmax 混合**，1M ctx，[arxiv:2501.08313](https://arxiv.org/abs/2501.08313))，是第一个公开权重的 hybrid linear-attention 大模型。**MiniMax-M1** (2025-06, [arxiv:2506.13585](https://arxiv.org/abs/2506.13585)) 在 M0 base 上做 long-CoT RL，1M ctx，推理时 FLOPs 比 DeepSeek-R1 低 25% on 100K-token generation (M1 paper §5)。**MiniMax-M2** (2025-10, [HF release](https://huggingface.co/MiniMaxAI/MiniMax-M2)) 230B / 10B act，**回到全 softmax attention**，官方解释是 lightning attention 在 agentic / tool-use 任务上召回不稳 ([M2 blog 2025-10](https://www.minimax.io/news/minimax-m2))。这个**从 hybrid linear 退回 softmax** 的决策对 Qwen 团队判断 linear attention 路线值不值得跟非常关键。

架构核心：lightning attention = Linear Attention 的 IO-aware 实现 (类似 FlashAttention 之于 softmax)，[原 paper arxiv:2405.17381](https://arxiv.org/abs/2405.17381)。M1 的 hybrid layout 是 **7 lightning : 1 softmax** 交替，softmax 层带 RoPE 保证位置敏感性。M2 撤回这套，含蓄说明 agentic 长 trajectory 里 linear attention 的"压缩状态"会丢关键 tool-call 上下文 [推测，M2 blog 没明说]。

## Tencent Hunyuan（混元 Large / TurboS / T1）

Tencent 路线是**大公司自用 + 开源刷存在感**，技术上比较保守但稳定出活。**Hunyuan-Large** (2024-11, **389B / 52B act MoE**, 256K ctx, 开源权重，[arxiv:2411.02265](https://arxiv.org/abs/2411.02265))，是当时开源 MoE 里参数最大的之一，架构是 GQA + 标准 MoE (top-2 routing) + KV cache 压缩 (cross-layer attention)。**Hunyuan-TurboS** (2025-03, [blog](https://llm.hunyuan.tencent.com/)) 闭源 API，号称 hybrid Transformer-Mamba，参数未披露。**Hunyuan-T1** (2025-03, reasoning 模型，[blog](https://tencent.github.io/llm.hunyuan.T1/))，[uncertain — tech report 没公开]。**Hunyuan-A13B** (2025-06, 80B/13B act，开源，[HF release](https://huggingface.co/tencent/Hunyuan-A13B-Instruct)) 是面向部署的小 MoE。2025-Q4 至 2026-Q1 又陆续开源了 **Hunyuan-7B/4B/1.8B/0.5B** dense 系列 ([HF org page](https://huggingface.co/tencent))，明显在补齐 edge 模型矩阵。独立信号有限，主要价值是开源权重许可比 Qwen 更宽松 (允许商用，月活 <1 亿，[Hunyuan License](https://github.com/Tencent/Tencent-Hunyuan-Large/blob/main/LICENSE.txt))。

## Baichuan（百川）

Baichuan 走的是**医疗垂直 + 中文 base**。**Baichuan2-7B/13B** (2023-09) 开源后基本不再更新开源版。**Baichuan3** (2024-01, 闭源, [blog](https://www.baichuan-ai.com/home))，中文 benchmark 强但英文弱。**Baichuan4-Turbo / Baichuan-M1** (2025-01, 医疗专用，[arxiv:2501.15368](https://arxiv.org/abs/2501.15368))，M1 paper 是这家最值得读的：报告了**医疗领域 SFT + RLHF + 医学知识图谱注入**的完整 pipeline，在 USMLE / MedQA 上超过同期 GPT-4o。2025-Q3 起 Baichuan 基本退出通用模型市场，[36kr 2025-09 报道](https://36kr.com/p/3023456789) 称王小川公开承认 "不再追通用 frontier，只做医疗" [uncertain — 链接占位，需核实]。

## 阶跃星辰 Step（Step-1 / Step-2 / Step-3）

阶跃是**中国少数公开报告万亿参数训练**的公司。**Step-1V** (2024-03, multimodal, 闭源)；**Step-2** (2024-07, **万亿参数 MoE, MoE 激活未披露**, [blog](https://www.stepfun.com/))；**Step-3** (2025-07, [tech report](https://stepfun.ai/research/en/step3))，多模态 reasoning，宣称 "training cost 1/10 of GPT-4 同等性能"，参数未披露。架构独立信号：Step-3 tech report §4 报告了一种叫 **"Multi-Matrix Factorization Attention" (MFA)** 的 attention 变体，号称 KV cache 比 MLA 小一半且性能不掉。这一点对 Qwen 团队评估 attention 创新值得专门看。第三方复现 [unknown — 没找到独立实现]。Step 系列基本只通过自家 API 和 to-B 渠道，没开源权重，可见度低于实际技术含量。

## ByteDance Doubao / Seed 系列

字节是**所有玩家里 to-C 用户量最大但模型对外可见度最低**的家族。**Doubao** (豆包) 是产品名，背后模型是 **Seed 系列**。代表：**Doubao-pro / Doubao-1.5-pro** (2024-12 / 2025-01, [Seed blog](https://team.doubao.com/))，宣称在多项中文 benchmark 超 GPT-4o，闭源 API-only。**Seed-Thinking-v1.5** (2025-04, [arxiv:2504.13914](https://arxiv.org/abs/2504.13914)) — 字节第一次公开 reasoning model tech report，**200B / 20B act MoE**，long-CoT RL，AIME 2024 86.7，和 o3-mini 同档。**Seed1.5-VL** (2025-05, [arxiv:2505.07062](https://arxiv.org/abs/2505.07062)) 多模态版。**Seed-OSS-36B** (2025-08, [HF release](https://huggingface.co/ByteDance-Seed/Seed-OSS-36B-Base)) 是字节**第一次开源权重**，dense 36B，512K ctx，Apache-2.0。**Doubao-1.5-thinking-pro** (2025-04) 和 **Doubao-1.6** (2025-Q3, [unknown — 没找到具体 blog]) 持续迭代。2026-Q1 传 **Seed-2.0** 在训 [uncertain]。

架构独立信号：Seed-Thinking-v1.5 paper §3 报告了一套 **"value-policy hybrid RL"**，policy 用 GRPO，但同时训一个 value head 做 advantage estimation，号称比 pure GRPO 在长 trajectory 上方差更低。这是除 DeepSeek/Kimi 之外比较少见的把 RL 配方写细的中文 lab。字节最大问题是**几乎所有报告都没参数披露 + 没开源（Seed-OSS 是例外）**，独立复现极少。

---

## 横向对比（一图流）

| 家族 | 最新版本 (2026-05 时点) | 开源? | 独立技术信号 | 主要竞争位 |
|---|---|---|---|---|
| Mistral | Devstral 2 / Magistral Medium | 部分 (Apache-2.0 small / MRL large) | 保守 dense + 欧洲主权 | 欧洲 enterprise + open-weight 中端 |
| Cohere | Command A Reasoning | 权重 CC-BY-NC | post-train model merging | 北美 enterprise RAG |
| 01.AI | Yi-Lightning (2024-10, 后无新版) | Yi-1.5 开源 | 已基本停 frontier | 行业垂直 |
| Reka | Flash 3.1 [uncertain] | Flash 3 Apache-2.0 | native multimodal (audio-in 从头训) | multimodal niche |
| MiniMax | M2 | 开源权重 | 试过 lightning attn 又退回 softmax | to-C 中文 + agentic |
| Tencent Hunyuan | A13B / 小尺寸 dense 矩阵 | 商用许可宽松 | cross-layer attention KV 压缩 | 中文开源 + 腾讯生态 |
| Baichuan | M1 (医疗) | 早期版本开源 | 医疗垂直 RLHF + 知识图谱 | 医疗 |
| Step | Step-3 | 闭源 | MFA attention (KV 比 MLA 更小) | 中国万亿参数赛道 |
| ByteDance Seed | Seed-OSS-36B / Seed-Thinking-v1.5 | 仅 Seed-OSS 开源 | value-policy hybrid RL | 字节 to-C 量级最大 |

## 未知与争议

- **MiniMax 为何 M2 退回 softmax**：blog 含糊，没有 ablation。这是 linear/hybrid attention 路线的一个负面信号点，但没有详细数据。
- **Step "MFA"**：tech report 描述简短，无开源实现，无第三方复现。可能是 MLA 的另一种 reparameterization，可能是真新东西，[uncertain]。
- **Doubao 真实参数**：所有传言都是非官方，字节从未在任何 paper 里写 Doubao-pro 的参数数。Seed-Thinking-v1.5 的 200B/20B 是 paper 里唯一公开的具体数字。
- **01.AI / Baichuan 是否还会回到 frontier**：从 2025 全年没有大模型发布看，概率低，但都还在融资续命，不能完全 mark dead。

## 推荐外部材料

- [Artificial Analysis model leaderboard](https://artificialanalysis.ai/models) — 这些 edge 玩家的 API 价格 / 延迟 / 质量三轴对比，比 LMSys Arena 更接近 enterprise 选型视角。
- [Magistral tech report](https://arxiv.org/abs/2506.10910) — Mistral 的 RL pipeline 写得比 DeepSeek-R1 paper 更工程化，适合直接抄 reward design。
- [Command A tech report arxiv:2504.00698](https://arxiv.org/abs/2504.00698) — 唯一一篇把 enterprise post-train（domain checkpoints + model soup）写细的报告。
- [Seed-Thinking-v1.5 paper](https://arxiv.org/abs/2504.13914) — 字节第一次公开 reasoning 配方，value-policy hybrid RL 值得对比 GRPO / DAPO。
- [MiniMax-01 paper arxiv:2501.08313](https://arxiv.org/abs/2501.08313) + [M1 paper arxiv:2506.13585](https://arxiv.org/abs/2506.13585) — 跟踪 lightning attention 路线的兴衰，配合 M2 撤回的 blog 一起读。
- [Hunyuan-Large paper arxiv:2411.02265](https://arxiv.org/abs/2411.02265) — 大 MoE + cross-layer KV 压缩的工程实现细节。
- [Reka Core tech report](https://publications.reka.ai/reka-core-tech-report.pdf) — native multimodal 训练（含 audio）少见的公开描述。
