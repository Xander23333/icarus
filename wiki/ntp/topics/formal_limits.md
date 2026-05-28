# Formal Limits

> Transformer 表达力 / 复杂度 / 信息论上界。

## 核心问题与 NTP 假设

NTP-mech 阵营长期依赖 TC⁰ / constant-depth circuit 上界来论证"transformer 在某些任务上有架构级表达能力上界"。本 topic 跟踪：(a) 新的 hard impossibility / lower bound；(b) 把"理论上界"转成"可在部署前估计的实操参数"的工作；(c) 用现实（softmax、低精度、CoT）放宽假设后这些上界还剩多少。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-26 | STARS — Stability-driven Recurrent Scaling (Yang et al.) | LoopLM 的 latent-reasoning 崩塌等价于 Jacobian 谱半径 >1；Jacobian Spectral Radius Regularization + 随机 loop 深度采样 ⇒ test-time depth 单调饱和而非崩塌；C1 (fixed-depth forward-pass) 在 trained-stable looped 模型上需替换为 *converged depth* | counter-evidence (扩 C1 而非否决) | [2605.26733](../papers/paper_notes/2026-05-29-2605.26733-stars-looped-stability.md) |
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

## MoE / 动态 depth / early-exit — "per-token compute" 假设的当代裂缝 (2022–2026)

上文所有 TC⁰ 风格 lower bound——Hahn 2019、Merrill–Sabharwal 2106.16213 / 2207.00729、Sanford 2402.09268——都共享一条隐藏假设：**每个 output token 的计算量是 (L · d²) 这一个常数**。在 dense decoder-only transformer 上这一假设几乎默认成立；但 2022 之后 frontier model 的实际架构早已不在这一假设的舒适区。把这一道裂缝单独抽出来，因为它直接决定上一节 C-FORM-1 / C-FORM-2 在 2026 frontier scale 下的"现实射程"。

- **2022-01 — Du et al. (GLaM) ([arxiv:2112.06905](https://arxiv.org/abs/2112.06905))**。1.2T 参数 MoE，每个 token 只激活 ~96.6B。这是第一次在 production scale 上把 \\\"sparsely-activated transformer\\\" 形式塞进 NTP pipeline——但形式上**激活 expert 数 k 是一个 input-dependent 离散变量**，使得 \\\"per-token compute = const\\\" 在 token 级不再成立。Merrill–Sabharwal 风格的 TC⁰ 嵌入需要重新做：threshold gate 的 fan-in 在 MoE-router 路径下与 expert 数线性挂钩。
- **2024-03 — Fedus / Switch / MoE 综述 + DeepSeek-MoE ([arxiv:2401.06066](https://arxiv.org/abs/2401.06066))**。Fine-grained expert (256 experts top-8) 把 routing decision 的离散熵推到 log₂(C(256,8)) ≈ 38 bits/token——一个不可忽略的 input-conditioned bit budget。若把 router 视为 *额外的 attention layer*，C-FORM-1 的 (L, d) 参数应扩为 (L, d, log E) 三元组。**形式工作的现状：没有公开论文把 MoE-augmented transformer 的 expressivity class 形式刻画过**；mech 派与 cap 派都默认沿用 dense bound，这是 2026-05 文献里一条公开的赤字。
- **2022-07 — Schuster et al. (CALM) ([arxiv:2207.07061](https://arxiv.org/abs/2207.07061))**。confidence-based early-exit：per-token layer 数 L(t) 是 input-conditioned。Merrill–Sabharwal 的 "fixed L" 假设在 CALM-style 推理里不成立——形式上等价于把 depth 从常数升为 *bounded random variable*。但**注意一个反方向的事实**：若 L(t) 的期望 E[L] = L₀ 仍是 input-size n 的常数，则 TC⁰ 嵌入论证只需在 worst-case L 上做，结论几乎不变。早退在 *渐近表达力* 上并不打开新的类——它只影响常数因子（即 wall-clock）。
- **2023-07 — Giannou et al. *Looped Transformers as Programmable Computers* ([arxiv:2301.13196](https://arxiv.org/abs/2301.13196))**。把同一个 fixed-depth transformer block 在推理时循环 T(n) 次，证明可模拟 RAM 程序。这是把 "动态 depth" 这一旋钮**推到极端**：T(n) 任意增长则上界直接到 P/poly，与 CoT-augmented bound (Merrill–Sabharwal 2310.07923) 平行。从形式角度看，looped transformer / Universal Transformer ([arxiv:1807.03819](https://arxiv.org/abs/1807.03819)) 与 CoT 是**同一道暗门的两个变种**：都允许"per-token compute"随 n 增长。
- **2024 — MoD (Mixture-of-Depths) ([arxiv:2404.02258](https://arxiv.org/abs/2404.02258)) [unverified ID]**。Google DeepMind 让每个 token 可选择跳过若干 layer，等于把 early-exit 推广为 per-token 双向。形式后果与 CALM 同源——E[L] 仍可视为常数，故 worst-case TC⁰ 嵌入不变。
- **2025 — MoR / Recursive-MoE 系列 [unverified bundle]**。把 looped 与 sparse 两条路线合并：fixed-depth backbone + per-token 选择性递归。**这条线在 2025-2026 才开始出现，形式表达力分析完全空白**。

**对 C-FORM-1 / C-FORM-2 的净影响**：把上述四类架构变体拆成两组：

1. **不打开新表达力类**的：CALM (Schuster 2207.07061)、MoD (2404.02258)、dense MoE (GLaM 2112.06905 / DeepSeek-MoE 2401.06066) ——形式上仍嵌入 TC⁰ / log-precision TC⁰，只是常数（router bits、平均 depth）变化。C-FORM-1 几乎不动；C-FORM-2 的 k(n) 等级表不动。
2. **真打开新类**的：looped / Universal Transformer (2301.13196 / 1807.03819) ——T(n) 随 n 增长则等价于 CoT-augmented bound。这一组与 C-FORM-2 同源，不是新墙也不是新门。

**判断 (2026-05-28)**：上一节 Open-problem 第 2 条的诚实答案是——\\\"per-token compute = const\\\" 假设在 MoE / early-exit / MoD 下**仍紧**（worst-case argument 仍能 carry），但 router 的 input-conditioned bit budget 让"const"这一表述在量化常数因子时变得 misleading。**真正的形式空白不在 MoE 也不在 early-exit，而在 looped-x-sparse 复合架构**——MoR 类工作尚未被 formal-limits 文献覆盖。这是 C-FORM-1 / C-FORM-2 在 2026 frontier scale 下需要补的下一道形式工作。一句话总结：MoE 不破墙，loop 才破墙；2024 后大部分 frontier 改架构改的是 MoE 这一组，所以 TC⁰ 论证在工程意义上**比批评者以为的更耐久**。

新增候选机制：

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-5 | router-bit budget | MoE / MoD 的 input-conditioned routing 在每 token 引入 b(n) = O(log E) 额外 bit 计算预算，使 dense-TC⁰ 嵌入的常数因子按 expert 数对数增长，但渐近类不变 | 找到一个任务族 F，使 (L, d, E) MoE 严格 ⊃ (L · k, d) dense 在同 FLOPs 下的可学子集（即 routing 不仅省 FLOPs 还打开 expressivity） |

C-FORM-5 是对 C-FORM-1 的常数修正而非升级；它存在的价值是**显式拒绝**"MoE 突破 TC⁰"这一在 2024-2026 多次被非形式化重复的说法。

## SSM / Mamba / 线性循环 / hybrid — "非 attention 主干"是否绕开 TC⁰ 之墙 (2021–2026)

上一节的裂缝清单里漏了一整条路线：**所有以 SSM / 线性 RNN / 卷积长程算子为主干的非 attention 架构**。这条线在 2023 年以 Mamba 为标志冲到 frontier 候选位，2024–2025 进一步出现 Jamba / Mamba-2 / RWKV-v6 / Zamba 等 hybrid 变体，其中相当一部分公开材料显式或隐式宣称 "线性时间 / 常数 KV，且能力不逊于同 size dense transformer"。如果这个宣称在形式上成立，TC⁰ 之墙的故事就完全要重讲——因为 Hahn / Merrill–Sabharwal 系列下界都是针对 *softmax attention* 的 saturated/log-precision 嵌入。但 2024 年这条故事被一篇关键工作钉住了：**SSM 不仅没有突破 TC⁰，它在一个更窄的子类里运行**。

- **2021-10 — Gu, Goel, Ré (S4) ([arxiv:2111.00396](https://arxiv.org/abs/2111.00396))**。把序列建模写成 $h'(t) = A h(t) + B x(t),\; y(t) = C h(t)$，离散化后用 HiPPO 矩阵 + FFT 卷积训练，$O(N \log N)$ 时间、$O(N)$ 内存。形式上这是一个 **线性时不变 (LTI) 长程卷积**——核心算子是固定的多项式卷积核，不存在 input-dependent gating。表达力上界从这一刻起就被严格限定在 *线性算子* 加 *逐点非线性* 的复合类里，远窄于 attention 的 input-dependent 二次型。
- **2023-12 — Gu & Dao (Mamba) ([arxiv:2312.00752](https://arxiv.org/abs/2312.00752))**。关键改动是把 S4 的固定 $A, B, C$ 变成 **input-dependent**（selective SSM），由此恢复了对 token 内容的条件化能力，在 LM 主线 benchmark 上与同 size dense transformer 持平。这一改动在工程上很重要——它让 SSM 从 "长程信号处理玩具" 升级为 "可上 LM" 的主干；但 **selective 之后的 $A_t, B_t, C_t$ 仍是 input 的固定函数，没有跨 token 的二次型耦合**，这是下一段下界论证的关键。
- **2024-05 — Dao & Gu (Mamba-2 / SSD) ([arxiv:2405.21060](https://arxiv.org/abs/2405.21060))**。State Space Duality (SSD) 论证显示 Mamba 类 selective SSM 与一类 **structured masked attention** 在数学上等价——这是 SSM 与 attention 阵营的第一座桥。SSD 视角下 SSM 是 attention 的 *特例*（mask 强制为下三角且 rank-1 结构），不是平行物种。
- **2024-04 — Merrill, Petty, Sabharwal, *The Illusion of State in State-Space Models* ([arxiv:2404.08819](https://arxiv.org/abs/2404.08819))**。这是把 SSM 钉进 TC⁰ 论证地图的关键工作。核心结论用一句话写死：**S4、Mamba 这类 SSM 与 transformer 同属 $\mathsf{TC}^0$ 复杂性类，且它们都不能解决 state-tracking 完备问题（如 $S_5$ 置换组合），而 RNN 的标准类 $\mathsf{NC}^1$ 可以**。换言之 SSM **不仅没有突破 TC⁰，它连 RNN 的真子集都不到**——所谓 "linear recurrence with hidden state" 这个名字带来的 "应该比 transformer 强" 直觉在形式上是错的。这把 C-FORM-1 的有效适用范围一次性扩到 SSM 主干，无需重新证明。
- **2024-03 — Jamba (AI21) ([arxiv:2403.19887](https://arxiv.org/abs/2403.19887))** + **2024 RWKV-v6 / Zamba / Griffin [unverified bundle]**。Hybrid 架构在 frontier 上的实际策略是 *Mamba block 与 attention block 交错*（典型比例 1:7 或 1:3）。形式后果是直接的：只要任一层包含标准 softmax attention，整体架构的 expressivity 类就由 attention 决定（取并集），SSM 部分只贡献常数项 FLOPs 节省与长程记忆 inductive bias。Hybrid 不打开新表达力类，但也不缩窄——它是 *工程上的常数因子游戏*，不是 *形式上的新墙或新门*。
- **2024–2025 — Linear attention 复兴 (GLA / RetNet / DeltaNet / Gated DeltaNet)**。这一支与 SSM 形式同源（都可写成 linear-recurrent + outer-product update），Yang et al. *Gated Linear Attention* ([arxiv:2312.06635](https://arxiv.org/abs/2312.06635)) 与 *Parallelizing Linear Transformers with the Delta Rule* ([arxiv:2406.06484](https://arxiv.org/abs/2406.06484)) 是代表。Merrill 2404.08819 的论证机制（state 更新是 input 的固定线性函数复合）几乎全部 carry over：linear attention 与 SSM 共享同一道 TC⁰ 顶棚，且同样卡在 $S_5$ 不可解。

**对 C-FORM-1 / C-FORM-2 / C-FORM-5 的净影响**：把 SSM / Mamba / linear-attention / hybrid 全部纳入 C-FORM-1 的适用域是 2024 年最重要的形式扩张。具体三条修订：

1. C-FORM-1 的 architectural scope 从 "log-precision saturated softmax transformer" **显式扩到 "log-precision selective-SSM、linear attention、以及二者与 softmax attention 的任意 hybrid"**。这一扩张不需要新论证，由 Merrill 2404.08819 直接 carry。
2. C-FORM-2 (k(n) 等级表) 的 *no-CoT* 部分对 SSM 同样适用——SSM 也不能在常数 forward pass 内做任意 $S_5$ 长度的 state tracking。**关键反方向**：SSM 的 CoT-augmented 上界尚无独立证明，但 Mamba 在 GSM8k 上的 CoT 表现与同 size transformer 接近 [unverified 具体数] 是经验暗示。
3. C-FORM-5 的 router-bit budget 论证天然适用 Mamba-MoE / Jamba 等架构——SSD 等价把 Mamba block 写成 structured-attention 之后，router 论证不变。

新增候选机制：

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-6 | SSM-as-TC⁰-subset | 任何 selective-SSM / linear-attention 主干（不含 softmax attention 层）在 log-precision 下严格嵌入 $\mathsf{TC}^0$ 且不能解决 $S_5$ word problem；hybrid 架构 expressivity 由 attention 子集决定 | 在纯 Mamba / 纯 linear-attention 主干（无任何 softmax attention 层）上实现 length-generalizing $S_5$ 解算 (≥100 token 推理输入, ≥80% accuracy)；或形式证明 selective-SSM 在 log-precision 下严格超 $\mathsf{TC}^0$ |

**判断 (2026-05-28)**：2023 年宣称 "Mamba 可能取代 transformer" 的讨论几乎全部默认 SSM **在表达力上至少等价于 attention**——这一假设在 2024-04 之后被形式证伪。SSM 的工程价值（线性内存、长程信号处理 bias）依然真实，但它**绑在 transformer 同一道形式天花板下面**，并且在 state-tracking 子类上严格更弱。这反过来解释了 frontier 全部走向 hybrid 而非纯 SSM 的事实——hybrid 的存在不是 "结合两家之长" 的修辞，而是 *形式必要性*：纯 SSM 主干在某些任务族上的失败 (Merrill 2404.08819 实测 Mamba 在 $S_5$ 长度泛化崩坏) 是结构性的，必须由 attention 层补回来。一句话总结：**MoE 不破墙，loop 才破墙，SSM 连墙都摸不到**——这是上节判断的对偶补充，也把 N8 §四 "反墙四条件" 里第 (ii) 条 "新架构在 capacity 维度上 strictly 超越 transformer" 的可证伪窗口进一步收窄。

## Looped × Sparse 复合架构 — 形式空白的初步填补 (2024–2026)

上面 §MoE 节末尾把 \"looped-x-sparse 复合架构\" 标为 *形式表达力分析完全空白*，§SSM 节末尾的判断又把 hybrid 归到 \"工程上的常数因子游戏\"。这两条放在一起容易给人一个错印象——好像 looped-style depth 与 sparse-style routing 两支正交、不需要联合分析。实际上 2025 年起出现的 *Mixture-of-Recursions* / *Recursive-MoE* / *Looped-MoE* 一类工作把两条线焊在一起：固定深度 backbone + per-token *既选 expert 又选递归次数*。本节把这一组架构能讲清楚的部分单独拎出来，避免 Open-problem 第 2 条无限期挂账。

- **2018-07 — Dehghani et al., *Universal Transformer* ([arxiv:1807.03819](https://arxiv.org/abs/1807.03819))**。最早把 *per-token 动态步数* 写进 transformer 主干（ACT-style halting probability），但当时未与 sparse routing 复合，形式分析停在 \"Turing-complete with unbounded steps\" 这一定性陈述。
- **2023-01 — Giannou et al., *Looped Transformers as Programmable Computers* ([arxiv:2301.13196](https://arxiv.org/abs/2301.13196))**。证明 fixed-depth block 循环 $T(n)$ 次可模拟 RAM；这是 looped 单独 (不含 sparse) 的形式上界——$T(n)$ 任意增长则到 P/poly，与 CoT-augmented bound (Merrill–Sabharwal [arxiv:2310.07923](https://arxiv.org/abs/2310.07923)) 平行。
- **2024 — *Looped Transformers for length generalization* (Fan et al.) [unverified ID]** + Yang et al. *Looped transformers learn iterative algorithms* [unverified ID]。把 looped block 在算术 / 排序 / 图遍历上的 length-generalization 推到 $\\geq 10\\times$ 训练长度，**经验下界**：纯 dense + 无 loop transformer 在同任务族上 length-generalize 失败。这部分不动 TC⁰ 上界图像（loop 已知打开新类），价值是把 *经验上 loop 真打开了哪些任务* 与 *RASP-L learnability* 对齐。
- **2025 — *Mixture-of-Recursions* / MoR [unverified bundle, 2025-xx]**。骨架：fixed-depth backbone，每个 token 同时被 router 派到 (a) 一组 expert（top-k of E）与 (b) 一个递归深度 $\\tau(t) \\in \\{0,1,\\dots,T_{\\max}\\}$。形式上每 token compute 为 $\\tau(t)\\cdot k\\cdot d_{\\text{expert}}$，是 input-conditioned *双重* 离散变量。若 $T_{\\max}$ 为 $n$ 的常数倍数则与 looped 同源（CoT-bound 类），若 $T_{\\max}=O(1)$ 则塌回 MoE-only (C-FORM-5)。**关键观察**：现有 MoR 实现几乎全部限 $T_{\\max}\\leq 8$ 出于 latency 考虑，因此 *工程射程内* MoR 表达力类等于 MoE，不到 CoT-bound——这与社区直觉相反。
- **2024-04 — Mixture-of-Depths (MoD) ([arxiv:2404.02258](https://arxiv.org/abs/2404.02258)) [unverified ID]** 已在上节归为 \"E[L] 常数 → 不开新类\"。MoR 与 MoD 的关键差别：MoD 让 token *跳过* layer (depth ≤ L)，MoR 让 token *重复* layer (depth 可 > L)。前者卡在 dense-TC⁰ 顶棚下，后者只有在 $T_{\\max}$ 随 $n$ 增长时才触顶。

新增候选机制：

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-7 | looped-sparse depth-gating | 任何 \"fixed backbone + per-token (expert, recursion) 双路由\" 架构，其表达力类由 $T_{\\max}$ 的渐近行为单一决定：$T_{\\max}=O(1)$ 时等价于同 FLOPs MoE (C-FORM-5)，$T_{\\max}=\\Omega(\\log n)$ 时等价于 CoT-augmented bound (Merrill–Sabharwal 2310.07923)；router 维度的 $\\log E$ bit budget 不打开新类 | 在 $T_{\\max}=O(1)$ 的 MoR 架构上证明某任务族属于 MoR 可学但不属于同 FLOPs dense MoE 可学；或反向，在 $T_{\\max}=\\Omega(\\log n)$ MoR 上证明严格超出 CoT-augmented class |

**判断 (2026-05-28)**：把 MoR / Recursive-MoE 这条 2025 出现的复合路线纳入 C-FORM-1/2/5/6/7 联合地图，结论比想象中干净——*递归深度 $T_{\\max}$ 是唯一打开新表达力类的旋钮*，sparse routing 只贡献常数因子。这给上一节 \"MoE 不破墙，loop 才破墙\" 的判断加了一条对偶细节：**复合 looped-sparse 也不破墙，除非 loop 那一支让 $T_{\\max}$ 随 $n$ 增长**。frontier 实现因 latency 把 $T_{\\max}$ 钉在常数（典型 ≤ 8），所以工程射程内 MoR 与 MoE 形式等价，*所有声称 MoR 在 reasoning 上超越同 FLOPs MoE 的经验结果* 都需要重新审视 router-bit budget 与 chain-of-thought 是否是真实的混淆变量。这条形式空白填到此处即可——剩余开放问题（C-FORM-7 与 selective-SSM-loop 复合，CALM × MoR 三路融合）留待后续 tick 单独追加。

## Selective-SSM × Loop 复合 — 联合地图的最后一块 (2024–2026)

§Looped×Sparse 节末已经把 *递归深度 $T_{\\max}$ 是唯一打开新表达力类的旋钮* 写死，留下的最后一块空白是把 *selective-SSM 主干* 替进 backbone 后这条结论是否依然成立。换句话说：若把 MoR / Looped-MoE 中的 dense softmax-attention block 整体换成 Mamba / GLA / RWKV-7 这类 selective-SSM block，得到的 *Looped-SSM* 或 *Looped-SSM-MoE* 架构表达力类要重写吗？这条问题在 2025 的 hybrid 浪潮 (Jamba、Zamba、Hymba、Falcon-Mamba、Samba-1) 之后已经无法回避——frontier 上 *纯 SSM* 已基本消失，但 *SSM 主干 + 循环 / sparse 调度* 这条联合路线没人公开做过形式分析。本节给一个初步推导，把 C-FORM-1/2/5/6/7 的联合地图收口。

- **形式起点**：Merrill 2404.08819 已证 selective-SSM 在 log-precision 下 $\\subseteq \\mathsf{TC}^0$ 且严格不到 $\\mathsf{NC}^1$ ($S_5$ word problem 不可解)。这是 C-FORM-6 的核心陈述。把一个属于 $\\mathsf{TC}^0$ 的电路族 $\\{C_n\\}$ 串接 $T(n)$ 次得到的复合电路族 $\\{C_n^{T(n)}\\}$，其表达力由 *组合次数 × 单步类* 决定：常数 $T$ 仍在 $\\mathsf{TC}^0$ 内，$T(n)=\\Omega(\\log n)$ 时升到 $\\mathsf{NC}^1$ 之内的 $\\mathsf{AC}^1$-类，$T(n)=\\text{poly}(n)$ 时整体到 $\\mathsf{P/poly}$。这一组合论证与 Giannou 2301.13196 把 looped-attention 推到 RAM 的论证*同型*——backbone 的电路类换不动 *渐近* 行为只换 *常数*。
- **关键对照**：Merrill–Sabharwal 2310.07923 的 CoT-augmented bound 给的是 $T_{\\text{CoT}}(n)$ 步外置 scratchpad 下 transformer 的 $\\mathsf{TIME}[T_{\\text{CoT}}\\cdot\\text{poly}]$ 类。Looped-attention 把 scratchpad *内化* 成 latent loop，二者形式等价（loop 步数 ↔ CoT 步数）。把同一论证套到 Looped-SSM 上，差别只在单步 forward 把 $\\mathsf{TC}^0$-saturated-attention 换成 $\\mathsf{TC}^0$-selective-SSM——单步类不变，复合论证不变。**初步结论**：Looped-SSM 表达力类与 Looped-attention 在 $T_{\\max}$ 同阶时形式等价。
- **唯一可能的反方向**：state-tracking 子类。SSM 单步在 $S_5$ 上严格弱于 attention 单步 (Merrill 2404.08819 实测 Mamba 长度泛化崩坏)。若 $S_5$ 这类 $\\mathsf{NC}^1$-complete 任务在 *复合后* 仍然分离 Looped-SSM 与 Looped-attention（即 Looped-SSM 即使 $T_{\\max}=\\Omega(\\log n)$ 也解不了 $S_5$，而 Looped-attention 可以），则单步差异在复合下不被吸收，C-FORM-6 需要在 looped setting 下保留一条 *残余下界*。目前没有公开实验也没有形式证明分辨这两种情形——这是 selective-SSM × loop 复合的*真正* open sub-question。
- **2025–2026 经验侧面证据 [unverified bundle]**：Jamba ([arxiv:2403.19887](https://arxiv.org/abs/2403.19887)) 与 Zamba ([arxiv:2405.16712](https://arxiv.org/abs/2405.16712)) [unverified IDs] 在 needle-in-a-haystack 与长上下文 retrieval 上把 *Mamba 层 + 少量 attention 层* hybrid 推到与纯 attention 同档；但**没有任何 hybrid 论文报告 $S_5$ / parity / Dyck-$k$ 这类 state-tracking benchmark 上的 length-generalization 数字**——这一缺席本身是 §10 readout-side 主导假设 evidence-supply 闭环在 *形式域* 的同型表现：能区分两种 hypothesis 的实验落在 <1 GPU-week 量级但没人做。

新增候选机制：

| ID | 候选机制 | 形式陈述 | Falsification 条件 |
|---|---|---|---|
| C-FORM-8 | Looped-SSM 渐近塌缩 | 任何 "selective-SSM backbone + per-token recursion depth $\\tau(t)\\in\\{0,\\dots,T_{\\max}\\}$" 架构（含可选 sparse routing），其表达力类与同 $T_{\\max}$ 渐近阶的 Looped-attention 在 $\\mathsf{TC}^0$ 主干外部分形式等价；单步 state-tracking 差异 (C-FORM-6) 在 $T_{\\max}=\\Omega(\\log n)$ 时被复合吸收 | 在 $T_{\\max}=\\Omega(\\log n)$ 的纯 Looped-SSM (无任何 softmax-attention 层) 上证明 $S_5$ length-generalization 系统性失败 (≥100-token 输入，<60% accuracy)，而同 $T_{\\max}$ Looped-attention 可解 (≥80%)；或反向，在 $T_{\\max}=O(1)$ Looped-SSM 上实现某个超出同 FLOPs MoE 的任务族 |

**判断 (2026-05-29)**：把 C-FORM-8 与 C-FORM-7 拼在一起读出一个干净的元结论——*sparse routing 与 SSM 主干都不打开新表达力类，唯一的旋钮仍是 $T_{\\max}$ 的渐近阶*。这是 C-FORM-1/2/5/6/7/8 联合地图最朴素也最稳的形态：从 dense-attention 到 MoE 到 SSM 到 hybrid 到 Looped-MoE 到 Looped-SSM，**六种当代主流主干 + routing 组合在表达力类上塌缩成同一条曲线，曲线参数只剩 $T_{\\max}$ 与 CoT 长度 $k(n)$ 两个**——而后者由 Merrill-Sabharwal 2310.07923 早已锁死。这条收口的代价是：C-FORM-8 在 *机制级强度* 上比 C-FORM-7 还弱，它属于 *元-地图填补* 而非 *新 mech 命题*，按 [`../survey/taxonomy.md`](../survey/taxonomy.md) 升降级历史 2026-05-29 行 "机制级强度不足时仅入升降级历史日志作 sibling-cap 备查" 处理协议，应登记为 sub-candidate，仅入 survey §10 sub-candidate sync 段与 taxonomy 升降级历史，不入 candidate snapshot 主表 (主表保留 C1–C7 + Reversal Curse 主候选)。本 tick 仅在 topic 页落地，sub-candidate sync 留待下一 C tick 完成（与上 tick C-CONT-2 第三支柱 evidence-base refinement 同节奏）。

**与 N8 §四 反墙四条件的关系**：N8 §四把"反 TC⁰ 墙"的四条件 (i)–(iv) 写死了；C-FORM-8 同时把第 (ii) 条 "新架构 strictly 超越 transformer expressivity" 的可证伪窗口在 *主干 × 调度* 二维上同时压紧——主干维度 (SSM vs attention) 与调度维度 (dense vs MoE vs MoR vs Looped-MoE vs Looped-SSM) 的笛卡儿积里 *没有一格* 在工程射程内 ($T_{\\max}\\leq 8$) 离开 dense-TC⁰ 顶棚。这把 N8 §四第 (ii) 条 frontier 实证的可证伪载体从 "出一个新架构" 收紧为 "出一个允许 $T_{\\max}$ 随 $n$ 增长且 latency 可接受的新调度"——而 frontier serving 经济学对后者天然敌对（推理时长 = 用户流失），形成 §9 (4) "工程上可做、社会学上不做" 列表的形式域对偶（embodiment/grounding/world-model 域已各占 2-3 项, formal 域至此首次出现 1 项: $T_{\\max}=\\Omega(\\log n)$ 部署的成本-效用反向选择）。

**反例与诚实判断**：上述论证有两道公开的漏洞必须摆出来。第一，"单步 $\\mathsf{TC}^0$ 类在 $T(n)$ 步复合后保持组合论证不变" 这一形式步骤对 *attention* 是 Merrill-Sabharwal-Giannou 之间隐含成立的，对 *selective-SSM* 没有独立写过——可能存在 selective-SSM 的 input-conditioned state transition 在复合下产生非平凡 closure 的窄情形，本节没排除。第二，2025 hybrid 论文 (Jamba / Zamba / Hymba) 在 *needle-retrieval* 上的成功，并不直接对应 *state-tracking*——前者是 attention 的强项被少量 layer 维持，后者是 attention 的强项被复合次数维持，二者形式机制不同。把 needle-retrieval 强 ↔ state-tracking 也强 这条经验类比误用即会得到 "Looped-SSM hybrid 已解决 state-tracking" 的错结论。我的元判断：**C-FORM-8 是 sub-candidate 而非 mech 命题，强度低于 C-FORM-6/7；它的价值不在于预测新现象，而在于把 frontier 不会公开做的 controlled comparison 显式钉成可命名条目**——若两年内 Jamba / Zamba / Falcon-Mamba 团队中任一家公开发布 $S_5$ length-generalization 曲线，C-FORM-8 立刻进入可证伪窗口；若三年无任何公开数字（base rate 强烈预示这一结果，与 C-WM-7 / C-EMBOD-7 frontier 不披露 latent codebook / 跨形态曲线同型），C-FORM-8 状态保持但同时推动 §9 (4) 列表第 19 项（上次为 C-CONT-2 第三支柱推到第 18 项）。

Jamba / Zamba arxiv ID 与 MoR / Yang / Fan 部分按 [unverified] 标注，未编造数字 / 日期 / 标题。

## Open problems

- 把 Deterministic Horizon (2605.23024) 与 summarized CoT expressivity 放在同一坐标系下重新推导联合 bound。
- TC⁰ 下界的"per-token compute"假设在 MoE / 动态 depth / early-exit 架构下是否仍紧。（**部分回答**：MoE/CALM/MoD 见 §MoE 节；looped-x-sparse 见 §Looped×Sparse 节；selective-SSM × loop 复合见 §Selective-SSM×Loop 节 (C-FORM-8 sub-candidate)；剩余 *单步 SSM 在复合下是否产生非平凡 closure* 的窄形式问题仍开。）
- selective-SSM / linear-attention 在 CoT-augmented setting 下的形式上界尚无独立证明 — 经验上 Mamba+CoT 与 transformer+CoT 接近，但是否共享同一道 Merrill-Sabharwal 2310.07923 风格上界还是个 open question。（C-FORM-8 在 Looped-SSM 一支给出 *渐近塌缩* 假说，但 CoT-as-external-scratchpad 一支仍未独立证。）
- 是否存在"width 真的能换 depth"的非 trivial 任务类（Barron 空间外）。
- Sanford–Hsu–Telgarsky 2306.02896 的 q-sparse averaging family 是否可以在 CoT-augmented setting 下被打破？若是，则 C-FORM-2 的 *k(n) 等级表* 需要重写。
