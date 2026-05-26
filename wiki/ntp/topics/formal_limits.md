# Formal Limits

> Transformer 表达力 / 复杂度 / 信息论上界。

## 核心问题与 NTP 假设

NTP-mech 阵营长期依赖 TC⁰ / constant-depth circuit 上界来论证"transformer 在某些任务上有架构级表达能力上界"。本 topic 跟踪：(a) 新的 hard impossibility / lower bound；(b) 把"理论上界"转成"可在部署前估计的实操参数"的工作；(c) 用现实（softmax、低精度、CoT）放宽假设后这些上界还剩多少。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-21 | Lost in Tokenization (Graph Trade-offs) | 不同 tokenization (spectral/RW/adjacency) 对同一图函数诱导多项式级 depth gap；表达力 = (architecture, tokenization) 联合属性 | mech (extends C1) | [2605.22471](../papers/paper_notes/2026-05-27-2605.22471-graph-tokenization-tradeoffs.md) |
| 2026-05-18 | MHA as NW Ensemble | MHA = H 个 NW kernel 估计器的结构化 ensemble；variance reduction 由 head decorrelation (principal angles) 主导 | mech (soft, framework) | [2605.20271](../papers/paper_notes/2026-05-27-2605.20271-mha-as-nw-ensemble.md) |
| 2026-05-08 | Fresh-Symbol Classification (Logistic Theory) | 在 kernel logistic regime 下把 transformer 学到的 template 分类器分解为 ideal classifier + 词汇 overlap 扰动；NTP readout 强制 token-name 依赖使该分解失效 | mech (boundary clarification) | [2605.07120](../papers/paper_notes/2026-05-27-2605.07120-fresh-symbol-classification.md) |
| 2026-05-21 | Deterministic Horizon (Guo) | 由层数与嵌入宽度决定的推理深度上界 H* ∈ [19,31]，超出后训练无法恢复 | mech | [2605.23024](../papers/paper_notes/2026-05-26-2605.23024-deterministic-horizon.md) |
| 2026-05-19 | Measure-Theoretic Reasoning (Zhang et al.) | OT/Wasserstein 框架下，RoPE 保 shift invariance；Dyck-k → TC⁰ depth lower bound | mech | [2605.19944](../papers/paper_notes/2026-05-26-2605.19944-measure-theoretic-reasoning.md) |
| 2026-05-18 | Low-Prec Softmax + (Summarized) CoT (Brösamle & Eckstein) | softmax + 低精度 + log-grow depth 仍 Turing-complete；summarized CoT 把 size 从 log-time 降到 log-space | counter-evidence | [2605.18079](../papers/paper_notes/2026-05-26-2605.18079-lowprec-softmax-cot.md) |

## 当前共识 / 争议

- **共识**：在 no-CoT、固定生成长度下，TC⁰ 类 depth 下界仍是公认的硬限制；2026-05 两篇新工作把它从"渐近"做到"可测量"。
- **争议**：一旦允许 CoT（即使是 summarized / latent CoT），上界基本被打开到 Turing-complete 级；这意味着"NTP-mech 推理深度上界"这一表述必须**强行区分 no-CoT vs CoT-augmented 两个 setting**，否则容易陷入伪命题。
- 仍未澄清：Deterministic Horizon 的 H* 是否在加 CoT 之后退化为"每条 CoT step 一个 horizon 周期"的复合上界。
- **新增 (2026-05-27)**：tokenization 选择本身是 depth 决定因素（Lost in Tokenization）——这意味着 NTP-mech 候选 C1 的参数集应从 (L, d) 扩为 (L, d, tokenization)；BPE 之于 LLM 可能就是某些"机制级失败"的真因，而非模型本身。同时 (Fresh-Symbol Classification) 指出 **NTP 的 readout 强制 token-name 依赖** 是 fixed-label 实验与 NTP 之间的本质 gap。

## 关键证据线 (chronological, 长程视角)

把本 topic 的源头拉回到 circuit complexity 而不是 LLM 时代，可以看清"TC⁰ 上界"不是 2020 后的新发现，而是 1984 年就已存在的硬数学事实被重新挂到 transformer 上。

- **1984，Furst–Saxe–Sipser**："Parity, Circuits, and the Polynomial-Time Hierarchy"（FOCS 1981 / MST 1984）证明 PARITY ∉ AC⁰。这是一切现代 "transformer 不能数奇偶" 论证的远端祖先；TC⁰ 比 AC⁰ 多了 threshold 门，但 PARITY ∈ TC⁰ 也只是 *uniformly* 在 depth O(1) 可解，常数本身相当大。
- **2019-06，Hahn**："Theoretical Limitations of Self-Attention in Neural Sequence Models" [arxiv:1906.06755](https://arxiv.org/abs/1906.06755)。第一篇把 hard-attention / soft-attention 的形式上界直接挂到 PARITY 和 Dyck-2 上的工作。Hahn 的关键 trick 是用 Lipschitz / influence bound 论证 fixed-depth transformer 无法解决任意长度的 PARITY——这一论证在 2026 仍是 mech 阵营 citing 最高频的"原始引用"。
- **2021-06，Merrill–Sabharwal–Smith**："Saturated Transformers are Constant-Depth Threshold Circuits" [arxiv:2106.16213](https://arxiv.org/abs/2106.16213)。把 saturated attention 正式塞进 TC⁰。该论文是"TC⁰ wall"这个比喻被锁死的关键节点。
- **2022-02，Chiang–Cholak**："Overcoming a Theoretical Limitation of Self-Attention" [arxiv:2202.12172](https://arxiv.org/abs/2202.12172)。第一份正面 counter-evidence：通过 layer-norm + position-aware attention，PARITY 在某种 setting 下可以被学到——但需要任务相关的 positional bias，不是 free lunch。
- **2022-07，Merrill–Sabharwal**："The Parallelism Tradeoff: Limitations of Log-Precision Transformers" [arxiv:2207.00729](https://arxiv.org/abs/2207.00729)。把"log precision + 固定 depth"作为现实假设，证明这样的 transformer 仍落在 TC⁰ 内。这是把渐近上界往"现实可部署模型"上贴的第一步。
- **2022-10，Liu et al.**："Transformers Learn Shortcuts to Automata" [arxiv:2210.10749](https://arxiv.org/abs/2210.10749)。揭示了一种 mech 阵营常忽视的现象：transformer 不学正确的 automaton，而学一个 shortcut——这个 shortcut 在 train distribution 内贴近真值、在 long-horizon 上系统性失败。这是后来"length generalization"研究线的起点之一。
- **2023-05，Feng et al.**："Towards Revealing the Mystery behind Chain of Thought" [arxiv:2305.15408](https://arxiv.org/abs/2305.15408)。给出"CoT 把 transformer 的表达力扩张到 P/poly 一类"的形式构造；与 Merrill–Sabharwal 的 CoT-as-Turing-tape 论证 (2310.07923) 互为镜像。
- **2023-06，Sanford–Hsu–Telgarsky**："Representational Strengths and Limitations of Transformers" [arxiv:2306.02896](https://arxiv.org/abs/2306.02896)。引入 *q-sparse averaging* 任务，证明 transformer 有它做不到的 strict separation——这是少数把 lower bound 给到 *task family* 而非 single problem 的工作。
- **2023-10，Merrill–Sabharwal**："The Expressive Power of Transformers with Chain of Thought" [arxiv:2310.07923](https://arxiv.org/abs/2310.07923)。正式版："log CoT steps ⇒ L (log-space)，poly CoT ⇒ P"。这一对 bound 让此后所有 "no-CoT vs CoT" 的形式讨论都必须显式标注 CoT 长度。

判断：从 1984 到 2023 这条线最值得记住的不是"transformer 弱"，而是 **它的表达力等级强依赖 (precision, attention saturation, CoT length, positional encoding) 这四个旋钮**。任何不指明四旋钮就谈 "TC⁰ 上界" 的论断都是 under-specified——这也是 2024 之后这一支文献被批评 *cherry-picking assumptions* 的根本原因。

## 当前最强的 mech 候选

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-1 | no-CoT depth wall | fixed-depth, log-precision transformer 在 input length n 上的可解任务严格 ⊂ uniform TC⁰ | 找到一个 n-scaled task，fixed-depth log-precision transformer 在 generalization gap → 0 意义下 solve 它 |
| C-FORM-2 | CoT-length 等级 | 给定 CoT 长度 k(n)，可解问题类 = TIME[k(n) · poly] ∩ NTP-realizable | k(n)=O(log n) 时若能解出 NP-complete 实例 family，则证伪 |
| C-FORM-3 | tokenization-as-depth | 同一函数族在不同 tokenization 下的最小 depth 差为多项式级，故 depth 上界必须写成 (L, d, tokenization) 三元组 | 找到 tokenization 不变的 depth lower bound family（Lost in Tokenization 2605.22471 反方向） |

C-FORM-1 与 C-FORM-2 是当前文献的最大公约数；C-FORM-3 是 2026-05 之后才被 take seriously 的，仍处于"形式上自洽但实测证据少"的状态。

## 反例与上界突破

- **Chiang–Cholak 2022** (上引)：PARITY 在合适 positional bias 下可学，说明 Hahn 2019 的 lower bound 是 *architecture+input-encoding* 联合的，而非纯 architecture 的。
- **Brösamle–Eckstein 2026-05** (本页表中 2605.18079)：低精度 softmax + log-grow depth 仍 Turing-complete；summarized CoT 把空间从 log-time 进一步压到 log-space。这一结果直接 weaken 了 Merrill–Sabharwal 2207.00729 的 "log precision = TC⁰" 推论的实际杀伤力——只要允许 depth 随 n 缓慢增长，TC⁰ wall 就不再是 wall。
- **Liu et al. 2022 shortcuts**：反方向 counter-evidence——即使理论上某任务在 transformer 表达力内，训练得到的解也可能是 *shortcut* 而非 correct mechanism；这意味着"理论可表达"与"NTP 训练能学到"之间存在第二道 gap，不能用 expressivity 论证替代 learnability 论证。

## 与其它 topic 的接口

- → [reasoning](reasoning.md)：C-FORM-2 是 reasoning 页 C-REAS-1（CoT-as-scratchpad）的形式底座；二者证伪条件互为充分必要。
- → [scaling_limits](scaling_limits.md)：C-FORM-1 是 scaling 页 C-SCALE-1（架构级 compute ceiling）的 *上界* 来源；scaling 法则只能在 C-FORM-1 之内运作。
- → [world_model](world_model.md)：C-FORM-3 的 tokenization 旋钮直接影响 world_model 页 C-WM-1（closed-world bottleneck）的有效 horizon。
- → 样章 [N2-the-tc0-wall](../samples/N2-the-tc0-wall.md)：本 topic 的 chronology §1984→2023 即 N2 §1-§2 的素材底；N2 负责把它叙事化。

## Open problems

- 把 Deterministic Horizon (2605.23024) 与 summarized CoT expressivity 放在同一坐标系下重新推导联合 bound。
- TC⁰ 下界的"per-token compute"假设在 MoE / 动态 depth / early-exit 架构下是否仍紧。
- 是否存在"width 真的能换 depth"的非 trivial 任务类（Barron 空间外）。
- Sanford–Hsu–Telgarsky 2306.02896 的 q-sparse averaging family 是否可以在 CoT-augmented setting 下被打破？若是，则 C-FORM-2 的 *k(n) 等级表* 需要重写。
