# Qwen3 家族（外部视角）

> **说明**：本节读者本人就是 Qwen agentic+eval owner，内部 roadmap、数据、未发布信号不在此重复。这里只汇总**外部观察者**（HF、Raschka、Lambert、Artificial Analysis、独立复现者）公开能看到 + 公开在讨论的部分。目的是让你知道"圈外人怎么看 Qwen3"。

## 路线定位（外部口径）

外界把 Qwen3 视为 **2025 年开源权重领域三大支柱之一**（与 DeepSeek-V3/R1 系、Kimi K2 系并列），并且是其中 **family 最完整、license 最干净（Apache-2.0 为主）、size ladder 最宽（0.6B → 480B MoE → 1T 级 Qwen3-Max）** 的一家。竞争对位：开源圈对 DeepSeek、Kimi、GLM、Llama；闭源对位上 Qwen3-Max / Qwen3-VL-Plus 被 Artificial Analysis 放到与 GPT-5 / Claude 4.x / Gemini 2.5 同图比较，是首个**被 closed-frontier 榜稳定收录**的中国家族。

## 代表模型清单（仅列外部有讨论的公开 release）

| 模型 | 发布 | 参数 / 激活 | 外部关注点 | source |
|---|---|---|---|---|
| Qwen3-0.6B / 1.7B / 4B / 8B / 14B / 32B (dense) | 2025-04-29 | dense | 完整 size ladder + hybrid thinking 模式 | [qwenlm.github.io blog](https://qwenlm.github.io/blog/qwen3/) |
| Qwen3-30B-A3B (MoE) | 2025-04-29 | 30B / 3B act | 小 MoE 替代 14B dense，edge MoE 模板 | 同上 |
| **Qwen3-235B-A22B** | 2025-04-29 | 235B / 22B act | 旗舰 open MoE，对标 DeepSeek-V3 | 同上 |
| Qwen3 tech report | 2025-05 | — | 架构 + 训练配方公开 | [arxiv:2505.09388](https://arxiv.org/abs/2505.09388) |
| Qwen3-235B-A22B-Instruct-2507 / Thinking-2507 | 2025-07 | 同上 | **官方放弃 hybrid，拆成两个独立 ckpt** | [HF Qwen3-235B-A22B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507) |
| **Qwen3-Coder-480B-A35B** | 2025-07-22 | 480B / 35B act | 开源 coding/agent SOTA，256K ctx | [qwenlm blog](https://qwenlm.github.io/blog/qwen3-coder/) |
| Qwen3-Coder-30B-A3B | 2025-07 | 30B / 3B | 可本地跑的 coder 版 | HF |
| Qwen3-VL (2B/8B/32B/235B) | 2025-08 ~ 2025-10 | dense + MoE | VL 系列全面 Qwen3 化 | [qwenlm blog Qwen3-VL](https://qwenlm.github.io/blog/qwen3-vl/) |
| **Qwen3-Omni-30B-A3B** | 2025-09 | 30B / 3B | text+vision+audio+speech 统一 MoE | [qwenlm blog Qwen3-Omni](https://qwenlm.github.io/blog/qwen3-omni/) |
| **Qwen3-Next-80B-A3B** | 2025-09-12 | 80B / 3B | **hybrid linear attention + gated DeltaNet**，外部最大讨论点 | [qwenlm blog Qwen3-Next](https://qwenlm.github.io/blog/qwen3-next/) |
| Qwen3-Max (preview → GA) | 2025-09 → 2025-10 | 闭源，~1T 级 [外部估算] | API-only 旗舰，进 closed-frontier 对比 | [qwenlm blog Qwen3-Max](https://qwenlm.github.io/blog/qwen3-max/) |
| Qwen3-Max-Thinking | 2025-11 | 同 | reasoning ckpt | 同上 |
| Qwen3-VL-Plus / Max | 2026-Q1 [uncertain — 外部见到的 API 时间] | 闭源 | 进 Artificial Analysis VL 榜 | [Artificial Analysis Qwen3-VL](https://artificialanalysis.ai/) |

> 2026-05 截止：外部还没看到 Qwen4 公开标签；社区把"Qwen3-Next-架构 + Max-规模"视为下一代候选模板（[Raschka 2026-Q1 post](https://magazine.sebastianraschka.com/)）。

## 架构核心（外部能从 paper / blog / HF config 读到的）

### Dense 与 MoE 主线（Qwen3 paper）

外部看到的 Qwen3 主系列架构沿用 Llama-style 主干，叠加 Qwen2.5 已有的 GQA + RoPE + RMSNorm + SwiGLU，**没有走 MLA**（与 DeepSeek/Kimi 显著差异点之一，Raschka [LLM Architecture Comparison 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) 专门指出这一点）：

- **Attention**：GQA（不是 MLA），head 数随 size 线性放大；旗舰 235B-A22B：64 Q-head / 4 KV-head。
- **MoE**：**128 routed experts + 8 activated**（235B / 30B 都是这个 ratio）。**无 shared expert**（Raschka 在对比图里强调："Qwen3 unlike DeepSeek/Kimi drops the shared expert"），官方在 [Qwen3 paper §3](https://arxiv.org/abs/2505.09388) 解释是消融发现 share expert 收益不显著。
- **Aux-loss-free LB**：跟随 DeepSeek-V3 的 bias-controller LB 路径（paper §3.2）。
- **Norm placement**：QK-Norm（Qwen2.5 已用），加 attention/FFN pre-RMSNorm。
- **RoPE**：base 1M for long-ctx 版本，最大原生 ctx 256K（Coder/Next），通过 YaRN/Dual-Chunk attention 外推到 1M（Coder blog 自报）。
- **Tokenizer**：BBPE 151,936 vocab，沿用 Qwen2 tokenizer，未换。

### Hybrid Thinking → 拆分

外部观察到的关键演化：
1. **2025-04 首发**：模型用 `enable_thinking=True/False` 在同一个 ckpt 里切 thinking / non-thinking，社区一度把这视作 Qwen3 的标志性 feature（"first open hybrid"）。
2. **2025-07 静默回退**：官方发布 `*-Instruct-2507` 和 `*-Thinking-2507` **两个独立 ckpt**，HF 模型卡上明确写"we no longer recommend the hybrid mode"。外部读为：hybrid 配方下 reasoning 上限被压（Lambert [interconnects 2025-08](https://www.interconnects.ai/) 评论："Qwen quietly conceded what DeepSeek already showed — separate ckpts win at the top"）。
3. **影响**：之后 Qwen3-Max / VL / Coder 都按 Instruct + Thinking 双 ckpt 发布，hybrid 不再是宣传词。

### Qwen3-Next（外部讨论最多的架构创新）

[Qwen3-Next blog 2025-09-12](https://qwenlm.github.io/blog/qwen3-next/) 公开的要点：

- **Hybrid attention**：48 层中 **每 4 层只有 1 层是 full attention，其余 3 层是 Gated DeltaNet（linear attention 变体）**。这是 Qwen 第一次在 production model 里放弃全 softmax attention。
- **Ultra-sparse MoE**：80B 总参，**512 routed experts + 10 activated + 1 shared**（注意：Next 又**加回了 shared expert**，与主线 Qwen3 反向），激活率 ~2%。
- **MTP**：加了 multi-token prediction head（主线 Qwen3 没有），用于 speculative decoding 友好。
- **声称 throughput**：blog 自报 32K+ ctx 下比 Qwen3-32B dense 快 ~10×。
- 外部解读（Raschka、[Together AI 技术博客复测](https://www.together.ai/blog)、Lambert）一致：Qwen3-Next 是**继 DeepSeek MLA、Kimi MuonClip 之后，开源圈第三个有显著架构 novelty 的 production-scale release**，且是其中唯一一个押注 linear attention 的。第三方独立复现 throughput claim 尚不充分（截至 2026-05）。

### Qwen3-VL / Omni（外部能看到的接口层）

- **VL**：vision encoder 仍是 Qwen 自家 ViT 改造（M-RoPE 处理多模态位置），text backbone 直接套对应 size 的 Qwen3。外部讨论点：**Qwen3-VL-235B-A22B 是首个开源权重在 MMMU / MathVista / DocVQA 上同时进 GPT-4o / Gemini 同一档**的 VL 模型 ([HF 模型卡](https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct))。
- **Omni**：在 Qwen2.5-Omni 的"Thinker-Talker"双 backbone 基础上，把 Thinker 换为 Qwen3-30B-A3B MoE，Talker 仍是较小的 AR speech decoder（[Qwen3-Omni 技术 report arxiv:2509.17765](https://arxiv.org/abs/2509.17765)，如外部已收录）。外部把 Omni 视为"open Gemini-Live"的第一个像样替代。

## 训练方法核心（外部已知部分）

[Qwen3 tech report (arxiv:2505.09388)](https://arxiv.org/abs/2505.09388) 公开的：

- **Pretrain token**：~36T（主线），覆盖 119 语言，比 Qwen2.5 的 18T 翻倍。
- **优化器**：AdamW（**未采用 Muon**，外部明确对照点：与 Kimi 路线分叉）。
- **三阶段 pretrain**：general → reasoning-heavy → long-context（最后阶段把 ctx 拉到 32K，再用 YaRN/DCA 外推）。
- **Strong-to-weak distillation**：旗舰 235B-A22B Thinking 作为 teacher，蒸馏到 30B-A3B / 14B / 8B / 4B Thinking 系列；外部认为这是 Qwen3 小模型在 reasoning 上明显强于同 size 对手（Llama-3.1-8B、Mistral）的核心原因（Raschka 多次引用）。
- **Post-train**：四阶段（long-CoT cold-start SFT → reasoning RL → thinking-mode fusion → general RL）。RL 算法 paper 写的是 **GRPO 变体**（与 DeepSeek 同族），细节披露程度低于 K2。
- **算力**：[unknown — paper 未给 GPU-hour]；外部估算（[Lambert 2025-05](https://www.interconnects.ai/)）旗舰一次 pretrain 约 V3 同量级。

## 与 eval / benchmark 的接口（外部第三方视角）

外部独立榜单（这部分对评测 owner 是"别人怎么测你"）：

- **Artificial Analysis**：Qwen3-235B-A22B-Thinking-2507 进入 open-weights intelligence index 第一档（与 DeepSeek-R1-0528、K2-Thinking 同档），Qwen3-Max-Thinking 在 closed 榜与 GPT-5 / Claude 4.5 / Gemini 2.5 同台。([artificialanalysis.ai/models/qwen3](https://artificialanalysis.ai/))
- **LMArena**：Qwen3 系列长期占据 open 模型前列，Coder 和 VL 子榜均进 top-5。
- **LiveCodeBench / Aider polyglot / SWE-Bench Verified**：Qwen3-Coder-480B-A35B 第三方测分（Aider polyglot、SWE-Bench mini-SWE-agent harness）开源 SOTA，但绝对值仍落后 Claude Sonnet 4.5 / GPT-5（[Aider leaderboard](https://aider.chat/docs/leaderboards/)）。
- **Scale SEAL 私榜**：Qwen3-Thinking 在 hold-out 榜和公开榜一致性较好，外部未给出严重 contamination flag。
- **第三方对 Qwen3-Next 的复测**：截至 2026-05，linear attention long-ctx 质量（≥128K needle / RULER）公开复测**少**，外部主要疑问点集中在"long-ctx 性能是否如 dense 稳"。
- **Raschka 评价** ([Big LLM Architecture Comparison 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison))：把 Qwen3 dense 列为"现在还想训 dense LLM 的人最该抄的参考"，理由是 GQA / QK-Norm / RoPE base / 训练配方都成熟透明。
- **Lambert 评价**：多篇 interconnects post 把 Qwen3 family 完整度（"0.6B 到 1T、text 到 omni、base 到 thinking 到 coder"）视为"目前唯一可与 Meta+Google+OpenAI 全栈对位的中国家族"。

## 外部尚未看清的部分（外部公开承认的 unknown）

- **Qwen3-Max 真实参数与训练数据**：闭源，外部估算 ~1T 总参；官方未确认。
- **Qwen3-Next linear attention 在 reasoning RL 下的稳定性**：blog 报训练曲线，但完整 post-train 论文未出。
- **Strong-to-weak distillation 的具体配方**：paper 提到但未给关键温度 / loss mix 细节，社区复现 (e.g., [Open-R1 distill 实验](https://github.com/huggingface/open-r1)) 显示效果敏感。
- **Qwen3 系列的 agentic RL 数据 pipeline**：paper 一笔带过，外部完全无从对比 K2 / GLM 的合成 pipeline。
- **Qwen4 / 下一代时间线**：外部截至 2026-05 无可信公开信号。

## 推荐外部材料

- [Qwen3 tech report (arxiv:2505.09388)](https://arxiv.org/abs/2505.09388) — 主线架构 + 4 阶段 post-train + distillation，必读一手。
- [qwenlm.github.io/blog/qwen3/](https://qwenlm.github.io/blog/qwen3/) — 首发 blog，外界引用最多的图都在这。
- [qwenlm.github.io/blog/qwen3-next/](https://qwenlm.github.io/blog/qwen3-next/) — Gated DeltaNet + ultra-sparse MoE 的官方说明，外部讨论 Qwen3-Next 必引。
- [qwenlm.github.io/blog/qwen3-coder/](https://qwenlm.github.io/blog/qwen3-coder/) 与 [qwen3-omni](https://qwenlm.github.io/blog/qwen3-omni/) — Coder / Omni 的发布 blog。
- [Sebastian Raschka, "The Big LLM Architecture Comparison" 2025](https://magazine.sebastianraschka.com/p/the-big-llm-architecture-comparison) — 把 Qwen3 dense/MoE 与 Llama 3、DeepSeek-V3、Kimi K2、GLM、gpt-oss 同框图对比，外界视角看 Qwen3 架构定位的最佳入口。
- [Nathan Lambert, interconnects.ai Qwen3 / Qwen3-Max 多篇](https://www.interconnects.ai/) — 把 Qwen3 放进开源 vs 闭源 frontier 时序的非营销解读。
- [Artificial Analysis Qwen3 / Qwen3-Max 页](https://artificialanalysis.ai/) — 第三方综合 intelligence / speed / cost 数据，外部对 Qwen3 的"客观排名"主要看这里。
- [HF collection: Qwen/Qwen3](https://huggingface.co/collections/Qwen/qwen3) — 所有 ckpt 模型卡入口，HF 下载榜也反映外部使用量。
