# Formal Limits

> Transformer 表达力 / 复杂度 / 信息论上界。

## 核心问题与 NTP 假设

NTP-mech 阵营长期依赖 TC⁰ / constant-depth circuit 上界来论证"transformer 在某些任务上有架构级表达能力上界"。本 topic 跟踪：(a) 新的 hard impossibility / lower bound；(b) 把"理论上界"转成"可在部署前估计的实操参数"的工作；(c) 用现实（softmax、低精度、CoT）放宽假设后这些上界还剩多少。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-26 | NITP: Next Implicit Token Prediction | 在 NTP 之上叠加用浅层激活作下一 token 的稠密 self-supervised target；9B MoE MMLU-Pro +5.7%；论证 NTP one-hot 留下的 hidden-state 自由度可被 auxiliary 对潜空间的几何约束修掉，几何欠约束属 objective-engineering 层 | counter-evidence (削弱"NTP 表征几何不可救"mech 论调) | [2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md) |
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

## 经验验证线 — TC⁰ 之墙的实测史 (chronological)

上一节是 1984–2023 的**理论**血脉；本节追的是另一条更短但更脏的线：在真实 transformer / 真实数据集上**到底有没有看到那堵墙**。这条线的特点是几乎每一篇都既被 mech 派引用、又被 cap 派引用——因为同一组数字在两种 framing 下读出来意思完全相反。

- **2020-09 — Bhattamishra–Ahuja–Goyal**，*On the Ability and Limitations of Transformers to Recognize Formal Languages* ([arxiv:2009.11264](https://arxiv.org/abs/2009.11264))。这是第一篇系统在 PARITY / Dyck-1 / Dyck-2 / Shuffle-Dyck 上 train + test 小 transformer 的工作。结论很硬：固定深度的 vanilla transformer 在 PARITY 上**根本学不会**（test accuracy 在长度外推时直接掉到 chance），Dyck-1 可以但 Dyck-2 边界处崩。Hahn 2019 的形式论断第一次在实验上拿到匹配信号。
- **2022-07 — Delétang et al. (DeepMind)**，*Neural Networks and the Chomsky Hierarchy* ([arxiv:2207.02098](https://arxiv.org/abs/2207.02098))。把 Transformer / LSTM / Stack-RNN / Tape-RNN 同台跑 Chomsky 阶梯任务。结果：Transformer 在 *regular* (PARITY) 与 *context-free* (Dyck) 上长度外推都不行，而带显式 stack/tape 的 RNN 可以。这一对照是 \"架构归纳偏置\" 论的最强实验底座之一；mech 派把它当 TC⁰ wall 的实测，cap 派则反驳说\"没让模型用 CoT 就不公平\"。
- **2022-07 — Anil et al. (Google)**，*Exploring Length Generalization in Large Language Models* ([arxiv:2207.04901](https://arxiv.org/abs/2207.04901))。在 ≤8B 规模 PaLM 上测加法 / parity / 变长 reasoning 的长度外推，证明 **scratchpad/CoT 即使配 fine-tune 也无法把 length-extrapolation 救到训练长度的 2× 以上**——这是\"光加 CoT 不够，还得加正确的 position encoding\"这一后续共识的起点。
- **2023-05 — Ruoss et al. (DeepMind)**，*Randomized Positional Encodings Boost Length Generalization* ([arxiv:2305.16843](https://arxiv.org/abs/2305.16843))。证明只要把 position id 在训练时按某个 prior 随机化，多个 Chomsky-阶梯任务的长度外推可显著扩张。**这是对 Bhattamishra 2020 / Delétang 2022 的部分反例**：墙的位置高度依赖 positional encoding 的选择，所谓\"architecture-level 上界\"在不变 PE 下成立，换 PE 后斜率改变。
- **2023-10 — Zhou et al.**，*What Algorithms Can Transformers Learn? A Study in Length Generalization* ([arxiv:2310.16028](https://arxiv.org/abs/2310.16028))。RASP-L 视角：能被短 RASP-L 程序刻画的任务族，transformer 一般能 length-generalize；不能被刻画的（如 PARITY）就外推不动。这条 RASP-L 假说至今没被严格证伪，是\"为什么有的任务过墙、有的不过\"目前唯一带预测力的经验法则。
- **2024-02 — McLeish et al.**，*Transformers Can Do Arithmetic with the Right Embeddings* ([arxiv:2405.17399](https://arxiv.org/abs/2405.17399))。Abacus embedding：给每个数字 token 注入 position-within-number 信号，transformer 在 100-digit 加法上 length-extrapolation 大幅改善。又一例：墙的硬度由 tokenization × PE × 任务三者联合决定，不是单纯 depth 函数。
- **2024-06 — Sanford et al.** *Transformers, Parallel Computation, and Logarithmic Depth* ([arxiv:2402.09268](https://arxiv.org/abs/2402.09268)) [unverified ID]。 把 *k-hop induction* 任务证明需要 Ω(log k) 层；与 Sanford–Hsu–Telgarsky 2023 的 task-family lower bound 配对，第一次给出\"任务难度 → 最小 depth\"的可计算映射。
- **2026-05 — Lost in Tokenization** ([2605.22471](../papers/paper_notes/2026-05-27-2605.22471-graph-tokenization-tradeoffs.md))。在 graph 表达力上把 \"tokenization 旋钮\" 推到与 (L, d) 并列的位置——前面所有 PE 修正都可视为 tokenization 旋钮的特例。

判断：把这条经验线和上一节理论线并排看，事实是 **TC⁰ wall 在 (vanilla PE, no CoT, fixed depth) 这个最严的角落里被反复实测到，但在它周围的每一个旋钮——PE 随机化 (Ruoss)、数字 embedding (McLeish)、CoT 长度 (Anil 推到 Merrill–Sabharwal 形式版本)、tokenization (2605.22471)——上都至少各被打开一次**。这意味着 NTP-mech 派若想守住\"TC⁰ wall 在工程上可证伪\"这一立场，必须把 falsification 条件写成\"四旋钮全部锁死\"的局部命题，而不是\"transformer 做不到 X\"的全局命题——后者经验上已经死了至少四次。

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

## 表达力 vs 可学性 — 第二堵墙 (chronological)

上面所有上下界都讨论的是**表达力 (expressivity)**：固定架构 / precision / depth / CoT 长度下，*存在不存在*一组参数使 transformer 计算目标函数。但 NTP 给定的不是\"存在性\"，而是\"在 next-token cross-entropy 这一个目标 + SGD/AdamW 这一个优化器 + i.i.d. 训练数据这一个 sample 通道下，能不能被学到\"。这两件事之间有一段被 mech 派长期忽视的 gap——它本身就构成第二堵墙，且**其位置常常比 TC⁰ 墙更靠前**。把这条线单拉出来：

- **2022-10 — Liu et al. shortcuts** ([arxiv:2210.10749](https://arxiv.org/abs/2210.10749))（上节已引）。第一次清晰展示：在表达力*内*的 automaton 任务，transformer 学到的是 shortcut 而非正确机制；training loss → 0，OOD length acc → chance。表达力够 ≠ NTP 训练能学到。
- **2023-09 — Berglund et al. Reversal Curse** ([arxiv:2309.12288](https://arxiv.org/abs/2309.12288))。\"A is B\" 训过，\"B is A\" 测不出。这件事**不是表达力问题**——逆映射在 1 层 transformer 表达力内就能写——而是 NTP gradient 对方向 asymmetric。Reversal curse 是\"第二堵墙\"最干净的样例。
- **2023-05 — Allen-Zhu & Li Physics-of-LM 系列**（[arxiv:2305.13673](https://arxiv.org/abs/2305.13673) 等）。在合成传记数据上把\"参数有没有存住事实\"和\"模型能不能 retrieve 它\"分离开测；结论：knowledge storage 容量约 2 bits/param，但 retrieval 受 *训练时是否出现过该 query template* 强约束。表达力 ≫ 学得到的子集。
- **2024-02 — Power et al. grokking 复盘 / Nanda mech-interp**（[arxiv:2301.05217](https://arxiv.org/abs/2301.05217) modular addition mech；[arxiv:2201.02177](https://arxiv.org/abs/2201.02177) Power et al. 原版）。grokking 现象说明：**就算解在表达力内**，NTP loss 也可能在到达正确电路前先固化到一个 memorization 解；从 memorization 切到 generalization 需要 weight decay × 数据量 × 训练步数三者的特定窗口。这意味着 \"transformer can in principle do X\" 和 \"GPT-style training run will produce a transformer that does X\" 是两个不同命题。
- **2024-04 — Zhang et al. Towards Best Practices of Activation Patching** [unverified ID]。回到 mech-interp 工具自身：activation patching 找到的\"算法子电路\"在 NTP 训出的模型里**密度极低**——大部分参数处于既非 memorization 也非可读算法的中间相。表达力上界与实际占据的解空间之间存在容量浪费。
- **2024-06 — Bordelon–Cengiz–Pehlevan**，*A Dynamical Model of Neural Scaling Laws* ([arxiv:2402.01092](https://arxiv.org/abs/2402.01092))。把 scaling law 显式建成 SGD 在特征学习相图上的轨迹；推论：data scaling exponent 由 *数据本身 spectrum* 决定，与表达力上界几乎无关。这条线为 \"为什么 dense scaling 撞墙不是撞 TC⁰ 墙\" 提供了第一份机制级解释。
- **2025-XX — Length-generalization 综述线**（Anil 2207.04901 → Zhou RASP-L 2310.16028 → Abacus 2405.17399 → 后续 looped-transformer 工作 [unverified bundle]）合在一起读，给出 \"learnability frontier\" 的当代经验描述：能被短 RASP-L 程序刻画 ∩ 配对正确 PE/embedding ∩ 训练分布覆盖该 program 的输入子流形，三者交集才是 NTP 真正学得到的子集，**严格小于** Merrill-Sabharwal CoT-augmented 上界给的可表达类。

判断：把这条线和上文表达力线并排看，最诚实的图景是 \"NTP 真正学到的能力\" 嵌在两道边界之间——
1. **外圈**是 (depth, precision, CoT, tokenization) 联合决定的 expressivity 上界（TC⁰ 墙的现代版）；
2. **内圈**是 (objective shape, optimizer bias, data spectrum, PE/embedding choice) 决定的 learnability 上界。
两道墙的*相对位置*随四旋钮组合而异，但**对 frontier scale 的真实瓶颈，2024-2026 几乎所有实测证据指向内圈先撞**——reversal curse、length-extrapolation 崩塌、knowledge retrieval template 依赖、shortcut learning，没有一个是\"transformer 表达不了\"。这意味着 NTP-mech 派若要论证\"架构级天花板\"，必须在 *learnability* 而非 *expressivity* 这一侧拿出 lower bound；目前为止还没有一份这样的形式工作存在（仅有 Bordelon 2402.01092 的 dynamical model 给了部分图像）。该 gap 即是 NTP 形式化论证下一阶段的真正前线。

新增候选机制：

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-4 | NTP-learnability gap | 存在表达力可达的任务族 F，使任何 vanilla NTP 训练流程（cross-entropy + AdamW + i.i.d. sampling）在多项式步数内都不能将 OOD generalization error 压到 ε 以下 | 给出一个属于 F 的具体任务，并展示一组超参 + 训练数据使其在多项式步数内被学到（length-generalization 边界即潜在反例区） |

C-FORM-4 与 C-FORM-1/2 互补：前三个候选锁 expressivity 上界，C-FORM-4 锁 learnability 上界。Reversal curse 与 shortcut learning 是它当前最具体的实验 anchor。

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
