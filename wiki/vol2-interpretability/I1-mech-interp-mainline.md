# I1 — Mechanistic interpretability 主线（截至 2026-05）

## 路线定位

mech interp 的"主线"指 **Anthropic + 跟随者** 推的这一条：把 LLM 的中间激活通过 sparse dictionary learning 拆成「feature」，再把 feature 之间的因果连接图建出来，最后想读这张图来回答「模型为什么这么答」。2022 *Toy Models of Superposition* 是理论起点，2023 *Towards Monosemanticity* 证明 small transformer 可行，2024 *Scaling Monosemanticity* 推到 Claude 3 Sonnet，2024 末 transcoders + sparse crosscoders 修补 SAE 的几个缺陷，2025-03 *Circuit Tracing / On the Biology of a LLM* 把这些零件拼成 **attribution graph** 工作流，是这一条线 2025-2026 的当前 state-of-the-art。读者关心评测，对这条线最该理解的是：**它的产出是\"对单个 prompt 的局部解释\"，不是\"模型完整规格\"，且在 frontier scale 上目前只有 Anthropic 自己跑得动**。

## 主线时间轴

| 时间 | 工作 | 核心贡献 | 一手 source |
|---|---|---|---|
| 2022-09 | Toy Models of Superposition (Elhage et al., Anthropic) | superposition 的玩具模型证明，feature 比维度多时 ReLU 网络会叠加 | [transformer-circuits.pub/2022/toy_model](https://transformer-circuits.pub/2022/toy_model/index.html) |
| 2023-09 | Sparse Autoencoders Find Highly Interpretable Features (Cunningham, Ewart, Riggs, Huben, Sharkey) | 独立组用 SAE 在 Pythia 上拿到可解释 feature，比 Anthropic 早小半步公开 | [arxiv 2309.08600](https://arxiv.org/abs/2309.08600) |
| 2023-10 | Towards Monosemanticity (Bricken et al., Anthropic) | 1L transformer + SAE，系统化了 dictionary learning 范式 | [transformer-circuits.pub/2023/monosemantic-features](https://transformer-circuits.pub/2023/monosemantic-features/) |
| 2024-05 | Scaling Monosemanticity (Templeton et al., Anthropic) | Claude 3 Sonnet 上 34M feature SAE，"Golden Gate Bridge" feature 演示 | [transformer-circuits.pub/2024/scaling-monosemanticity](https://transformer-circuits.pub/2024/scaling-monosemanticity/) |
| 2024-06 | OpenAI — Scaling and Evaluating Sparse Autoencoders (Gao, Goh, Sutskever et al.) | TopK SAE，GPT-4 上训 16M feature，提出 downstream-loss 评估 | [arxiv 2406.04093](https://arxiv.org/abs/2406.04093) |
| 2024-08 | Gemma Scope (DeepMind) | Gemma-2-2B/9B 全层 JumpReLU SAE 开源，事实 community baseline | [arxiv 2408.05147](https://arxiv.org/abs/2408.05147) |
| 2024-10 | Sparse Crosscoders (Lindsey et al., Anthropic) | 跨层 / 跨模型共享字典，解决 SAE 的 layer-by-layer 冗余 | [transformer-circuits.pub/2024/crosscoders](https://transformer-circuits.pub/2024/crosscoders/index.html) |
| 2024-末 | Transcoders（Dunefsky, Chlenski, Nanda） | 用 SAE 替换 MLP 输出而非 residual，得到可读的 input→output 映射，circuit-friendly | [arxiv 2406.11944](https://arxiv.org/abs/2406.11944) |
| 2025-03 | Circuit Tracing + On the Biology of a LLM (Anthropic) | 用 cross-layer transcoders 自动构造 attribution graph；Haiku 3.5 上做了 ~12 个 case study | [transformer-circuits.pub/2025/attribution-graphs/methods](https://transformer-circuits.pub/2025/attribution-graphs/methods.html), [biology](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) |
| 2025-2026 | Goodfire Ember (Llama 3 70B/405B + Llama 4)、Neuronpedia 上 attribution graph 公共 demo | 工业化、托管化，但仍限于 open-weights | [goodfire.ai/research](https://goodfire.ai/research)、[neuronpedia.org/graph](https://www.neuronpedia.org/graph) |

## 从 SAE 到 transcoder 到 attribution graph：演进的为什么

### 1. SAE：把 superposition 拆开

- **问题**：transformer 一个 residual stream 维度（比如 4096 维）里塞了远多于 4096 个"概念"（Toy Models 的核心论点 [^toy]）。直接看 neuron 是 polysemantic 的。
- **方法**：训一个 over-complete sparse autoencoder $h \approx \text{ReLU}(W_{\text{enc}} x + b)$，要求 $h$ 稀疏（L1 / TopK / JumpReLU），$W_{\text{dec}} h$ 重建 $x$。期望每个 dim of $h$ 对应一个 monosemantic feature。
- **2023→2024 配方迭代**：
  - L1 SAE（Towards Monosemanticity）→ **shrinkage** 偏差。
  - **Gated SAE**（DeepMind 2024-04，[arxiv 2404.16014](https://arxiv.org/abs/2404.16014)）：分离 "是否激活" 和 "激活多少" 两个分支。
  - **TopK SAE**（OpenAI 2024-06 [^openai_sae]）：直接强制每 token 只有 k 个 feature 非零，超参少、dead feature 少。
  - **JumpReLU**（Gemma Scope [^gemma_scope]）：保留连续激活但有 hard 阈值，重建/稀疏 Pareto 当前最好之一。
  - **BatchTopK / Matryoshka**（2024-末-2025）：跨 batch 的 top-k 让单 token 自由度更大；Matryoshka 让一个 SAE 同时有多 dictionary size，避免 feature splitting。
- **scale 上限**：Anthropic 2024-05 在 Claude 3 Sonnet 上训了 1M / 4M / 34M feature 三套，发现 feature 数目越大解释越细但出现 **feature splitting**（"科学" 被切成 "物理学/生物学/..."）和 **feature absorption**（细 feature 吸收掉父 feature 的激活），下游分析不能简单选一个 size [^scaling_mono]。OpenAI GPT-4 上的 16M TopK SAE 报告了类似现象 [^openai_sae]。

### 2. Transcoders：让 circuit 能读出来

- **问题**：SAE 装在 residual stream 上，告诉你"这一层这里有 feature X 亮"，但 **feature 之间的连接** 还要通过原始 MLP/attention 反推，反推涉及非线性，attribution 不闭合。
- **Transcoder** [^transcoder]：把 MLP 子层近似成 `SAE_in → sparse hidden → SAE_out`，**直接替换 MLP 计算图**。Circuit 边变成 "feature_i (layer L) → feature_j (layer L+1)" 的线性可解析连接（attention path 仍是线性的）。
- **Cross-layer transcoder**（Anthropic 2025-03 attribution graphs paper [^circuit_tracing]）：进一步让 transcoder 的 hidden 写到后续 **所有** 层而不仅下一层，等价于一个跨层稀疏字典，attribution graph 边数大幅减少。这是 *Biology of a LLM* 的基础设施。

### 3. Attribution graph：本卷其他章节会用到的"产物"

- 给一个 prompt（如"Dallas → Texas → Austin" 类比），方法：
  1. 把模型替换成 transcoder 近似版本。
  2. 在 prompt 上 forward，记录所有活跃 feature。
  3. 用线性 attribution（含 stop-gradient on attention pattern 这一类 frozen choice）算每个 feature 对最终 logit / 上游 feature 的贡献，剪枝得到一张 DAG。
  4. 人工给每个 feature 起名（Top activating examples + logit lens + auto-interp）。
- *Biology of a LLM* 用这套做了 12 个 case study [^biology]：multi-step reasoning（Texas 例子）、planning in poems、加减法 lookup-table-like 电路、refusal / jailbreak 的 feature 路径、链式推理中 *hidden goals* 的中间表示等。每个 case 都给了一张人能读的 graph + 干预实验验证（ablate / patch 某 feature 后输出按预期变）。
- **重要 caveat**（Anthropic 自己写在 methods 里）：transcoder 近似有 ~5-15% loss recovery gap；attribution graph 是对"近似模型"的解释，不是对真模型的；frozen attention 让某些注意力机制（induction head 等）不在 graph 里显式出现。

## 关键 honest section：scale ceiling 和复现

- **Frontier 模型上只有 Anthropic 自己跑过完整 pipeline**。Scaling Monosemanticity 是 Claude 3 Sonnet（中尺寸 dense？参数未披露 [unknown]），Biology of a LLM 用的是 Haiku 3.5。Claude 3.5/4/4.5 Opus、GPT-5、Gemini-2.5 级别的 attribution graph 公开渠道都没见过 [unknown — 没找到 2026-05 前的 release]。
- **开源能复现到哪**：Gemma-2-9B（Gemma Scope SAE） + Goodfire 的 Llama-3-70B/405B SAE + Llama 4 Scout 是当前能拿到 feature-level 接口的最大开源模型。Llama-4 Maverick / DeepSeek-V3 / Qwen3-235B 这种 MoE 级别 [uncertain — 截至 2026-05 没看到 publish 的官方 SAE/transcoder release，社区零散尝试存在但质量参差]。
- **MoE 是单独的难点**：expert routing 让每 token 走不同子网，SAE 训练数据分布严重 imbalance，crosscoders / per-expert SAE 都是 active research，没共识 baseline。Anthropic 的 paper 主线模型都是 dense，回避了这个问题。
- **算力**：Scaling Monosemanticity 一节 SAE 训练消耗"和小一档预训练相当" [^scaling_mono]；attribution graph 推理时构造一张图秒级到分钟级，但 transcoder 训练是离线大投入。给评测团队估算：要在自家 70B 模型上跑一遍 pipeline，**约等于多花 5-15% 预训练算力 + 一个 3-5 人的 interp team 半年**。

## 与评测的接口（给 Qwen 团队的建议）

- **可立刻拿来用**：
  - benchmark 失败样本上跑 Neuronpedia 的 graph demo（限 Gemma / Llama），看是否复现已知 failure mode。
  - 在 Qwen3-8B/32B（dense 部分）上自己训 SAE（SAELens / EleutherAI sparsify），针对 reward hacking 或 hallucination 样本做 feature attribution，能做 internal red-team 工具。
- **暂时做不到 / 别承诺**：
  - 给 Qwen3-235B-MoE 出 attribution graph：基础设施都不成熟。
  - 用 mech interp 做 capability eval：目前所有 attribution 都是 *post-hoc 局部解释*，不能反过来证明模型"会 / 不会"某 capability，那是 behavioral eval（vol3）的职责。
- **真正值得跟踪的 2026 信号**：
  - Anthropic 是否把 attribution graph 用到 Claude 4.5/5 系列的 model card / system card（**alignment audit** 这条线，见 I8）。
  - 是否出现 **MoE-friendly** 的 transcoder 变体（看 Anthropic / DeepMind / Goodfire 哪家先发）。
  - 是否有人在 reasoning model（o-series / R1 类）的 CoT 阶段做 attribution graph，回答 CoT faithfulness 问题（见 I7）。

## 未知与争议

- **SAE feature 是不是"真实存在"**：feature splitting / absorption 让"unit of interpretation"不稳定。Anthropic 2024-10 update [transformer-circuits.pub/2024/october-update](https://transformer-circuits.pub/2024/october-update/index.html) [uncertain url — 以站点目录为准] 公开讨论过这个怀疑，社区里 Lee Sharkey、Joseph Bloom 等也有详细 critique post（LessWrong / AlignmentForum）。
- **attribution ≠ causation**：Anthropic 在 methods paper 里小心区分了 attribution edge 和真实 causal effect；下游引用者经常忽略这一点，把 graph 当因果图卖。
- **是否 scalable 到 frontier**：乐观派（Anthropic interp team）认为线性 transcoder 范式可推到 Opus 级，悲观派认为 reasoning model 的多步 thinking trace + tool use 会让单 prompt graph 爆炸，需要新抽象 [推测]。
- **第三方 reverse-engineer 的检验**：Biology of a LLM 的 12 个 case study 是 Anthropic 自己挑+自己解释的，外部独立复现（即使限于 Haiku 同档开源模型）截至 2026-05 还没看到系统化的工作 [uncertain]，这是 review 这条 line 的最大 unknown。

## 推荐外部材料

- [Anthropic Transformer Circuits Thread (主页)](https://transformer-circuits.pub/) — 这条 line 的官方流水账，按时间倒序读最新 5-6 篇就够 onboarding。
- [Neel Nanda — A Comprehensive Mechanistic Interpretability Explainer](https://www.neelnanda.io/mechanistic-interpretability/glossary) — 词典级背景，特别适合给评测同事统一术语。
- [Anthropic — On the Biology of a Large Language Model (2025-03)](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) — 12 个 case study，是本节的"看图说话"对照物。
- [Lee Sharkey — Sparse autoencoders: A literature review](https://www.alignmentforum.org/posts/...sparse-autoencoders) [uncertain exact URL — 搜 \"Sharkey SAE literature review\"] — 站在外部视角批判性总结 SAE 路线。
- [Goodfire — Llama 3 SAE blog](https://goodfire.ai/blog) — 看工业界把 SAE 当 product 卖时遇到的 ablation / steering 实际坑。
- [arxiv 2406.04093 — OpenAI Scaling and Evaluating SAEs](https://arxiv.org/abs/2406.04093) — TopK SAE 的 reference，附 downstream-loss 评估指标值得借鉴到 eval 流程。

[^toy]: [Toy Models of Superposition, Elhage et al. 2022](https://transformer-circuits.pub/2022/toy_model/index.html)
[^scaling_mono]: [Scaling Monosemanticity, Templeton et al. 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity/)
[^openai_sae]: [Scaling and Evaluating Sparse Autoencoders, Gao et al. 2024](https://arxiv.org/abs/2406.04093)
[^gemma_scope]: [Gemma Scope, Lieberum et al. 2024](https://arxiv.org/abs/2408.05147)
[^transcoder]: [Transcoders Find Interpretable LLM Feature Circuits, Dunefsky et al. 2024](https://arxiv.org/abs/2406.11944)
[^circuit_tracing]: [Circuit Tracing: Revealing Computational Graphs in Language Models, Anthropic 2025-03](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)
[^biology]: [On the Biology of a Large Language Model, Anthropic 2025-03](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
