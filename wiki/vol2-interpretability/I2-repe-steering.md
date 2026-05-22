# I2 — Representation Engineering & Activation Steering（截至 2026-05）

## 路线定位

如果说 **mech-interp**（circuit / SAE）是「拆开模型看零件」，那么 **representation engineering (RepE) + activation steering** 这条线是「不拆，直接在 residual stream 上加一个向量」。哲学上更接近 controllability 工程：先用一对 contrastive prompt 抽出「这个概念在哪个方向」，然后推理时把这个方向加进去（或减出去），观察行为变化。

它对 Qwen eval team 的现实价值有两点：(1) **probe-as-eval** ——比纯 behavioral eval 更早发现 deception / sycophancy / refusal 偏移，因为不依赖模型「愿意承认」；(2) **干预 baseline** ——评一个 safety post-train 是否真改了内部表征，对照 steering vector 是最便宜的 sanity check。和 SAE 的关系：steering vector ≈ 「监督版的 1-d feature」，SAE feature ≈ 「无监督版的 steering direction」，两条路 2024-2026 在快速融合。

---

## 核心方法谱系

### RepE（Hendrycks / Andy Zou et al., 2023-10）

- 论文：[arxiv 2310.01405](https://arxiv.org/abs/2310.01405)，站点 [representation-engineering.org](https://www.representation-engineering.org/)。Andy Zou + Dan Hendrycks（CAIS）+ CMU 一伙人。
- 方法核心：**Linear Artificial Tomography (LAT)** ——给一对 contrastive stimulus（如 "honest" vs "lying"），从 residual stream 抓 activation，做 PCA，第一主成分就是「这个概念方向」。然后：
  - **Reading**：投影到这个方向 → 得到 honest-ness scalar，可用作 probe / lie detector。
  - **Control**：把方向加回 residual stream（每层加一份，强度 α），可强制 / 抑制行为。
- 实验覆盖：honesty, power-seeking, morality, emotion, memorization、bias。Llama-2 上 honesty steering 把 TruthfulQA 提升十几个点。
- 与 ITI 的区别：RepE 是 **whole-stack framework**（reading + control + 自动评测），ITI 是 RepE 出现前一个月的一个具体技术；2024-2026 文献里 "RepE" 常被泛指整条 contrastive-direction 路线。

### ITI — Inference-Time Intervention（Li et al., 2023-06）

- 论文：[arxiv 2306.03341](https://arxiv.org/abs/2306.03341)，Kenneth Li 等，NeurIPS 2023。
- 方法：在 **每个 attention head 的输出空间** 单独训一个 linear probe 区分 truthful/untruthful，挑 top-K probe accuracy 最高的 head，推理时把这些 head 的输出沿「truthful 方向」平移 α 个 std。
- 关键发现：(1) truthfulness 信息 **稀疏在少数 head**（Llama-7B 上 ~48 个 head 里 top-48 已经够）；(2) 提升 TruthfulQA MC1 ~10 个点，对 MMLU 几乎零 tax。
- 局限：head-level，需要标注数据训 probe；后续 CAA / RepE 走 residual stream 更通用。

### Activation Steering / Activation Addition（Turner et al., 2023-08）

- 论文：[arxiv 2308.10248](https://arxiv.org/abs/2308.10248)，Alex Turner + team shard，最早叫 ActAdd。
- 方法朴素到一句话：拿一对 prompt（如 "Love" vs "Hate"），forward 各跑一遍，在某层把两份 activation 相减得到 "steering vector"，推理时把这个向量直接加到对应层 residual stream。
- 历史意义：**没有训练、没有 probe**，一对 prompt + 一次 forward 就能改风格。证明 LLM residual stream 的线性可加性比想象中强。
- 和 RepE 关系：ActAdd 是 RepE 的 N=1 极端情况；RepE 的 PCA over many pairs 更稳健。

### CAA — Contrastive Activation Addition（Rimsky et al., 2023-12）

- 论文：[arxiv 2312.06681](https://arxiv.org/abs/2312.06681)，Nina Rimsky（Anthropic alignment team intern 时期工作）。
- 改进点：用 **多对** contrastive prompt（如 Anthropic 的 `sycophancy-eval` 风格 A/B 选择题，正确 vs sycophantic 两个 answer letter），在 answer token 位置抓 activation，**平均差** 当 steering vector。比 ActAdd 鲁棒，比 RepE 简单。
- 实验：Llama-2-7B/13B-Chat 上 steer 7 种行为（sycophancy, corrigibility, hallucination, refusal, survival-instinct, power-seeking, myopia），单一向量平移可以双向（+α 强化、-α 抑制）显著改变 multiple-choice 行为。
- 工程价值：CAA 是 2024-2026 **最常被复用的 baseline**，因为代码就 200 行，数据格式 = A/B 选择题，社区已经在 Mistral / Qwen / Gemma 上有各种复现。Rimsky 的实现：[nrimsky/CAA](https://github.com/nrimsky/CAA)。

### Anthropic Persona Vectors（2025）

- Blog / paper：Anthropic 2025 年放的 [Persona Vectors: Monitoring and Controlling Character Traits in Language Models](https://www.anthropic.com/research/persona-vectors)（arxiv [2507.21509](https://arxiv.org/abs/2507.21509)，2025-07）。
- 是 CAA 思路的 **production-grade 扩展**：自动化 pipeline——给定一个 trait 描述（"sycophancy", "evil", "hallucination"），LLM 自动生成 contrastive prompt 对，抽 persona vector，然后用于：
  1. **监测**：finetune 数据 / RLHF 过程中投影看 persona 是否漂移（Anthropic 公开案例：Claude 3.5 → 3.7 训练中检测到一段 sycophancy 上升，回滚）。
  2. **缓解**：训练时减去 persona vector，比纯数据过滤更精准。
  3. **inference-time control**：和 CAA 一样。
- 给 Qwen eval 团队的复刻 take：自动 persona vector 生成 pipeline 本身值得抄——data 侧只需要 trait description，不需要人工标 A/B 题，可以挂到任意 model snapshot 上做 trait drift dashboard。

### Goodfire Ember（产品化路线）

- 见 I4 章节详述。Goodfire 走的是 **SAE feature 当 steering 维度**（无监督，feature 数量 ~10⁵-10⁶ 量级），和 CAA/RepE 的「监督单向量」路线互补：
  - SAE feature：覆盖广、可搜索（"找跟 deception 相关的 feature"），但每个 feature 单独效应弱、有 feature splitting 问题。
  - CAA / persona vector：单向量效应强、概念明确，但你必须先知道要 steer 什么。
- 2025 起 Goodfire 也加了 "**conditional steering**" / 多 feature 组合 API，本质是把 RepE 的 supervised direction 和 SAE 的 unsupervised feature 拼成一个 control plane。

---

## 评测视角：怎么用这些工具评 Qwen-class 模型

1. **作为 probe（无干预）**：CAA 抽出来的方向投影回 hidden state，得 per-token 标量 → 当 deception / sycophancy 监测器。比 LM-as-judge 便宜两个数量级，且不依赖被测模型自陈。Apollo Research 2024 [Scheming reasoning evals](https://www.apolloresearch.ai/research/scheming-reasoning-evaluations) 用类似手段做 frontier model in-context scheming 检测。
2. **作为 ablation**：post-train 一个新版本，看 steering vector 的 **效应大小** 是否变了——如果旧版 sycophancy vector α=2 能强烈引起拍马屁，新版 α=2 几乎无效，说明 finetune 真的把这个方向「压扁」了（≠ 仅仅是输出层覆盖）。
3. **作为 jailbreak / red-team**：refusal 方向已经被反复证明是 Llama / Qwen / Mistral 上的 **单一方向** ——Arditi et al. 2024 [Refusal in LLMs is mediated by a single direction](https://arxiv.org/abs/2406.11717) 显示在 refusal direction 上做 weight-orthogonalization 可以无损去掉 safety RLHF。eval 团队应当把「refusal direction ablation 后的 ASR」列为标配 robustness 指标。
4. **capability tax 评测**：所有 steering 论文都会报「steered model 在 MMLU/HellaSwag 上掉几个点」，但是 long-context / multi-turn agentic 上的 tax 系统报告极少 [unknown — 截至 2026-05 没看到 systematic study on agentic tax of steering]，这是 Qwen agentic eval 团队可以补的空白。

---

## 与 mech-interp 的边界

| 维度 | RepE / steering | Mech-interp (circuit + SAE) |
|---|---|---|
| 单位 | 一个 direction（监督） | 一个 circuit / 一个 feature（无监督） |
| 数据需求 | contrastive prompt 对（10²-10³） | 大量 activation（10⁸+ token）训 SAE |
| 解释力 | "这个方向控制 X 行为" | "这个 feature 在 X 时激活，参与 Y → Z 计算" |
| 干预便利 | 加一个向量，O(d) | 关 / 钳一个 feature，O(d·n_features) |
| 失败模式 | 找错方向 / 单向量过载多概念 | feature splitting / dead feature / polysemantic 残留 |
| 工业落地 | Anthropic persona vectors, Goodfire conditional | Goodfire feature search, Anthropic Claude internal SAE |

实务上两条路在 2025-2026 已经互相吸收：persona vector 训练时会和 SAE feature 对齐（验证「这个方向落在哪些 feature 上」），SAE feature dashboard 上也会标「这个 feature 对应 CAA 的哪个 trait direction」。

---

## 未知与争议

- **线性表征假设的边界**：RepE / CAA 都默认 trait 是 **线性方向**。Park et al. 2024 [The Linear Representation Hypothesis](https://arxiv.org/abs/2311.03658) 给了理论支持，但 2025 起 Anthropic / DeepMind 都报过 **非线性 trait**（如 multi-step reasoning quality）找不到稳定单向量 [uncertain — 具体 paper id 待补]。Qwen 这种强推理模型，naive CAA 可能在「reasoning style」类 trait 上失效。
- **steering 的 OOD 崩盘**：steering vector 在 in-distribution prompt 上漂亮，agentic 长 trajectory 上经常突然产生 incoherent 输出（model "意识到" residual stream 被改了）。Anthropic persona vectors paper 里用 "training-time" 而非 "inference-time" 应用，部分原因就是规避这问题。
- **是否可被对抗规避**：如果一个 deceptive model 知道自己被 probe，它能否学会让 deception 不落在标准 direction 上？2025 有几篇 prelim 工作显示 **adversarial training against the probe** 可以让 probe accuracy 降到 chance [uncertain — Apollo / Redwood 有讨论]，这对把 RepE probe 当 safety guarantee 是直接 challenge。
- **跨模型可迁移性**：refusal direction 在同家族不同 size 上几乎可迁移，跨家族（Llama ↔ Qwen ↔ Mistral）不行。这意味着 Qwen 要自己维护一套 trait vector 库，不能直接抄 Anthropic 的。

---

## 推荐外部材料

- [representation-engineering.org](https://www.representation-engineering.org/) — RepE 官方站，有 LAT 代码 + honesty/morality demo notebook，入门最快。
- [Nina Rimsky — CAA repo & blog posts](https://github.com/nrimsky/CAA) — CAA 实现 + 一系列 LW 帖子，把 contrastive steering 讲得最清楚。
- [Anthropic — Persona Vectors (2025-07)](https://www.anthropic.com/research/persona-vectors) — 工业化 CAA 的范本，含 training-time 减去 persona 的 recipe。
- [Arditi et al. — Refusal is mediated by a single direction (2024)](https://arxiv.org/abs/2406.11717) — 看 refusal 方向并做 jailbreak / robustness eval 的必读。
- [Apollo Research — Scheming evaluations](https://www.apolloresearch.ai/research/scheming-reasoning-evaluations) — probe-as-eval 的代表性外部 case。
- [Neel Nanda — Steering vectors are a weak form of activation patching](https://www.alignmentforum.org/posts/) [uncertain url, search title] — 把 steering 和 mech-interp 联系起来的概念帖。
- [Goodfire research blog](https://goodfire.ai/research) — SAE-feature steering 在 prod 的工程坑。
