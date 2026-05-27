# NTP Survey — Main Document

> 长期演化主文档。每天的 daily report 都会把新增的实质性观点 / 证据 merge 到这里相应章节。

## 0. 目标与定义

本综述要回答的核心问题、NTP 工作定义、以及 NTP-mech / NTP-cap / Pseudo-NTP 三分法，见 [`../README.md`](../README.md)。

本文档承担的角色是 **「持续演化的理论综合」**，不是日报集合。每条进入本文档的论点都必须满足：
- (a) 有可引用的公开来源；
- (b) 在 NTP 三分法中能被定位；
- (c) 与已有论点的关系被明确写出（支持 / 反驳 / 正交 / 细化）。

## 1. 历史脉络

"NTP 能不能通向 AGI" 这道题不是 2023 年才出现的——它是一条贯穿整个深度学习史的暗线，只是名字换过几次。把这条线压成一段编年史最干净：

**1990 — Symbol Grounding (Harnad, *Physica D* 42)**：Stevan Harnad 在 *Minds and Machines* 上提出"封闭符号系统无法 escape 字典循环"，把"语言模型理解什么"这道题第一次定形。三十多年后，Bender & Koller 2020 ACL "Climbing towards NLU" 的章鱼实验几乎是这篇论文的字面翻版——只是把"中文字典"换成了"trillion-token web corpus"。

**2003 — Bengio NPLM (*JMLR* 3)**：Yoshua Bengio 等 *A Neural Probabilistic Language Model* 把 next-word prediction 第一次系统化为一个 distributed representation 学习目标。当时 perplexity 比 n-gram 仅好 10–20%，没人把它当成 AGI 路线。这篇论文重要的不是数字，而是它把 NTP 从"语音识别的辅助任务"升格为"表征学习的主目标"。

**2013 — word2vec ([arxiv:1301.3781](https://arxiv.org/abs/1301.3781))**：Mikolov 把同一目标降到极简，得到\"king − man + woman ≈ queen\"。这是分布主义经验主义的第一次大胜，也是 Pavlick 2023 *Symbols and grounding in LLMs* 里说的"distributional signal 比 Harnad 想象的多得多"的最早证据。

**2017–2020 — Transformer + Scale (Vaswani [arxiv:1706.03762](https://arxiv.org/abs/1706.03762) → Radford GPT-2 → Brown GPT-3 [arxiv:2005.14165])**：Kaplan scaling laws ([arxiv:2001.08361](https://arxiv.org/abs/2001.08361)) 把 NTP loss 与参数/数据/算力的幂律关系量化，第一次让"放大就行"成为可定量预测的工程假设。这一阶段 Sutton 2019 的 *Bitter Lesson* 被反复引用，几乎所有"机制级不可能"声称都在 2020–2023 被 scale 推翻过一轮（见 N8 §2 的 W1–W4 撞墙史）。

**2020–2023 — 怀疑论的复活与重铸**：Marcus 2018 *Deep Learning: A Critical Appraisal* ([arxiv:1801.00631](https://arxiv.org/abs/1801.00631))、Bender & Koller 2020、Bender et al. 2021 *Stochastic Parrots*、Chomsky 2023 *NYT op-ed*。这一波的特点是：哲学论点强，benchmark 上的可证伪 setting 弱。结果是几乎每条"LLM 必然不能 X"的命题（算术、systematicity、常识、推理）都在 2023–2025 被前沿模型部分翻案，但翻案方式（CoT、reasoning trace、tool use、scratchpad）又恰好满足了怀疑论者关于"必须外接计算"的预言——双方都觉得自己赢了。

**2022–2024 — Chinchilla & dense scaling 趋平 (Hoffmann [arxiv:2203.15556])**：data-optimal scaling 重写训练预算分配；GPT-4 → GPT-4.5 的能力跃迁显著小于 GPT-3 → GPT-4，标志 dense NTP 单纯放大的曲线开始疲软。补救来自两个方向：MoE (Mixtral [arxiv:2401.04088]、DeepSeek-V3 [arxiv:2412.19437]) 把激活/总参数比降到 5% 以下；test-time compute (o1 2024-09、R1 [arxiv:2501.12948]) 把算力从训练侧搬到推理侧。两者都没动 Transformer 骨架，但都改变了"NTP-mech 应该在什么 setting 下被评估"这个问题本身。

**2024–2026 — Readout-side 主导假设浮现**：本仓库 §10 累积的至少 5 条独立证据 (2605.10799/2605.07120/2605.14004/2605.05438/2605.25891) 指向同一方向：大量被解读为"NTP 机制不足"的现象，实际由 readout/format/objective/collapse confound 主导。这构成了 2024 年以来这条战线上**唯一一次方法论层面的系统性收敛**——它既不站强 mech 也不站强 cap，而是迫使两边都要先排除五个工程 confound 再谈机制。这也是本综述区别于 2020–2023 那一波讨论的最重要 stance。

**Sutton vs 机制级不可能性的张力**仍然是这条历史的主轴。Sutton 路线 6/6 全胜（W1–W4 加 reasoning、加 multimodal）的事实，并不直接证明它会赢第七次；但要立一条"这次不同"的论证，必须能定量预测 dense scaling 趋平 + MoE/inference 不增 effective sample 的**结构性新变量**，而不是重复 1988/1990/2020 的哲学结构。这是 N8 sample 章节展开的核心赌注，也是本综述 §9 第 (1) 题的核心。

## 2. 形式边界 (formal limits)

把 TC⁰ wall 这条线从 1984 拉到 2026，最干净的一段叙事不是 "transformer 不能算 PARITY"，而是 **\"表达力上界的位置随四个旋钮 (precision, attention saturation, CoT length, positional encoding/tokenization) 联合移动\"**。任何把这四个变量隐式固定再宣称\"架构级不可能\"的论证，事后都被打开过至少一次。下表汇集本仓库 [`../topics/formal_limits.md`](../topics/formal_limits.md) 里筛出来的最强证据，并补上各自当前的 NTP 三分法定位：

| 论点 | 状态 (mech / cap / open) | 关键文献 |
|---|---|---|
| Transformer 表达力上界 (uniform TC⁰, log-precision, fixed depth) | **mech, 但需四旋钮全部锁死** | Hahn 2019 ([1906.06755](https://arxiv.org/abs/1906.06755)) · Merrill-Sabharwal-Smith 2021 ([2106.16213](https://arxiv.org/abs/2106.16213)) · Merrill-Sabharwal 2022 ([2207.00729](https://arxiv.org/abs/2207.00729)) |
| 固定深度 transformer 无法 length-generalize 某些 regular / context-free 语言 | **mech, 已被 PE / tokenization 旋钮多次部分翻案** | Bhattamishra 2020 ([2009.11264](https://arxiv.org/abs/2009.11264)) · Delétang 2022 ([2207.02098](https://arxiv.org/abs/2207.02098)) · Ruoss 2023 ([2305.16843](https://arxiv.org/abs/2305.16843)) · McLeish Abacus 2024 ([2405.17399](https://arxiv.org/abs/2405.17399)) |
| Chiang-Cholak / Brösamle-Eckstein 反例: PARITY 在合适 PE 下可学；低精度 softmax + log-grow depth 仍 Turing-complete | **counter-evidence, 削弱\"depth 上界\"实操杀伤力** | Chiang-Cholak 2022 ([2202.12172](https://arxiv.org/abs/2202.12172)) · Brösamle-Eckstein 2026 ([2605.18079](https://arxiv.org/abs/2605.18079)) |
| CoT 扩展计算预算后能等价的复杂度类 (k(n) log CoT ⇒ L, poly CoT ⇒ P) | **mech-conditional, 给出了等级表而非 wall** | Feng 2023 ([2305.15408](https://arxiv.org/abs/2305.15408)) · Merrill-Sabharwal 2023 ([2310.07923](https://arxiv.org/abs/2310.07923)) |
| Tokenization 是与 (L, d) 并列的第三个 depth 决定因素 | **mech (extends C-FORM-1)** | Lost in Tokenization 2026 ([2605.22471](https://arxiv.org/abs/2605.22471)) · Singh-Strouse 2024 ([2402.14903](https://arxiv.org/abs/2402.14903)) |
| Deterministic Horizon: 由 (L, d, tokenization) 决定的推理深度上界 H* ∈ [19, 31]，跨 12 架构实测 | **conditional NTP-mech (no-CoT, 单 forward pass)** | Guo 2026 ([2605.23024](https://arxiv.org/abs/2605.23024)) · Zhang 2026 ([2605.19944](https://arxiv.org/abs/2605.19944)) |
| In-context learning 的统计/信息论上界 (q-sparse averaging, k-hop induction) | **task-family lower bound, 仍 open 是否在 CoT-augmented 下成立** | Sanford-Hsu-Telgarsky 2023 ([2306.02896](https://arxiv.org/abs/2306.02896)) · Sanford k-hop 2024 ([2402.09268](https://arxiv.org/abs/2402.09268)) [unverified ID] |
| Long-horizon imitation 联合 KL 下界 Ω(H) | **cap, 不构成机制级 impossibility (interactive RL 可绕过)** | Xu 2026 ([2605.12316](https://arxiv.org/abs/2605.12316)) |
| **第二堵墙: NTP-learnability gap** — 表达力可达 ⊆ NTP 训练能学到 (严格真子集) | **mech, frontier 实测此墙先撞** | Liu shortcuts ([2210.10749](https://arxiv.org/abs/2210.10749)) · Reversal Curse ([2309.12288](https://arxiv.org/abs/2309.12288)) · Allen-Zhu Physics-of-LM ([2305.13673](https://arxiv.org/abs/2305.13673)) · Bordelon 2024 ([2402.01092](https://arxiv.org/abs/2402.01092)) |

判断：到 2026-05 这条线最值得记住的不是任何单条上界，而是 **两道墙的图景**——外圈 expressivity 上界由 (depth, precision, CoT, tokenization) 联合决定；内圈 learnability 上界由 (objective shape, optimizer bias, data spectrum, PE/embedding) 决定；frontier scale 的真实瓶颈 2024-26 几乎所有实测证据指向**内圈先撞** (Reversal Curse / length-extrapolation 崩塌 / knowledge retrieval template 依赖 / shortcut learning 没有一个是\"transformer 表达不了\")。NTP-mech 阵营若要论证\"架构级天花板\"，下一阶段的真正前线在 *learnability* 而非 *expressivity*——目前仅有 Bordelon 2402.01092 的 dynamical model 给了部分图像，没有任何一份在 NTP loss + SGD/AdamW + i.i.d. 通道下的形式 lower bound 存在。这正是 [`../topics/formal_limits.md`](../topics/formal_limits.md) §表达力 vs 可学性 引入的 C-FORM-4 候选所要追的位置；也是 N2 sample 章节 §6 三道暗门论证的形式骨架。详细叙事见 [N2-the-tc0-wall](../samples/N2-the-tc0-wall.md)。

## 3. Grounding & 语义

把 symbol grounding 这条线从 1990 拉到 2026，骨架不是 "纯文本到底能不能 ground"，而是 **可证伪 setting 被双向收窄**——一边强 mech 阵营被迫从 "any grounded structure" 退到 *deictic / first-person / novel-object* 子集；另一边弱 cap 阵营被迫承认 contrastive (CLIP-style) objective 不够，必须补 closed-loop interaction 或 region-level supervision。下表汇集本仓库 [`../topics/grounding.md`](../topics/grounding.md) 与 [`../topics/embodiment.md`](../topics/embodiment.md) 里筛出来的最强证据，并标各自当前 NTP 三分法定位：

| 论点 | 状态 (mech / cap / open) | 关键文献 |
|---|---|---|
| 纯符号系统无法 escape 字典循环 (symbol grounding problem) | **mech, philosophical prior** | Harnad 1990 (*Physica D* 42, non-arxiv) · Bisk-Holtzman-Thomason *Experience Grounds Language* 2020 ([2004.10151](https://arxiv.org/abs/2004.10151)) |
| 章鱼论证: 分布信号无法恢复 meaning 的 *communicative intent* 分量 | **mech, 已被 Søgaard 2023 部分翻案 (恢复 up to permutation)** | Bender-Koller 2020 (ACL anthology) · Søgaard *Grounding the Vector Space of an Octopus* 2023 ([2305.02223](https://arxiv.org/abs/2305.02223) [unverified ID]) |
| 纯文本 LM 在 color / spatial / perceptual 子空间能学非平凡同构 | **counter-evidence to strong mech, 削弱"any grounded structure 不可" 读法** | Abdou 2021 ([2109.06129](https://arxiv.org/abs/2109.06129)) · Li *Implicit Representations* 2021 ([2106.00737](https://arxiv.org/abs/2106.00737)) · Patel-Pavlick ICLR 2022 [unverified ID] |
| CLIP-style contrastive objective 学共现而非指称——VLM-blind / MMVP 系统失败 | **mech, 把战场从 "multimodal solved" 推回 "需要 region-level supervision"** | Tong et al. MMVP 2024 ([2401.06209](https://arxiv.org/abs/2401.06209)) · Rahmanzadehgervi *VLMs Are Blind* 2024 ([2407.06581](https://arxiv.org/abs/2407.06581)) · Vector Grounding (Mollo-Millière 2023, [2304.01481](https://arxiv.org/abs/2304.01481)) |
| RLHF 作为稀疏 token↔world-state 监督；base→RLHF 在 TruthfulQA/SimpleQA 的 gap 中有多少是 grounding | **open, 文献几乎未与 instruction-following 分离** | Mollo-Millière 2023 §RLHF / Pavlick *Phil Trans R Soc B* 2023 (non-arxiv) |
| VLA / OpenVLA 在 *unseen object × unseen instruction* deictic 子集成功率从 ~70% 跌到 <20% | **conditional mech (deictic asymmetry, C-GROUND-3)** | OpenVLA Kim et al. 2024 ([2406.09246](https://arxiv.org/abs/2406.09246)) · Open X-Embodiment 2023 ([2310.08864](https://arxiv.org/abs/2310.08864)) · RT-2 2023 ([2307.15818](https://arxiv.org/abs/2307.15818)) |
| FFN-as-grounding bottleneck: linearized 结构知识 hallucination 的 sufficient statistic 是 FFN 未把 context 写入 residual, 跨 schema 通用 detector AUC>0.8 | **mech (interface-layer; 第六项 confound)** | Li et al. 2026 ([2605.26362](https://arxiv.org/abs/2605.26362)) |
| Action-execution gap: 多轮 tool-use 单步语法合法率 ≥0.9 但 pass^k(k≥4) ≤0.4, 跨 7B–400B N 不显著 | **medium-strong conditional mech (C-GROUND-5, agentic 子带)** | τ-Bench Yao 2024 ([2406.12045](https://arxiv.org/abs/2406.12045)) · OSWorld Xie 2024 ([2404.07972](https://arxiv.org/abs/2404.07972)) · SWE-bench Jimenez 2023 ([2310.06770](https://arxiv.org/abs/2310.06770)) · SWE-Bench+ Aleithan 2024 ([2410.06992](https://arxiv.org/abs/2410.06992)) · BFCL / Gorilla Patil 2023 ([2305.15334](https://arxiv.org/abs/2305.15334)) |
| Probe 测量代际偏差: 多数 grounding 文献仍停留在 Hewitt-Manning 第一代 probe, 未控 selectivity, 也未做 Vig-Meng / Geiger DAS 干预 | **方法学债, 直接影响上面 4 行 effect-size** | Hewitt-Liang EMNLP 2019 ([1909.03368](https://arxiv.org/abs/1909.03368)) · Vig CMA 2020 ([2004.12265](https://arxiv.org/abs/2004.12265)) · Meng ROME 2022 ([2202.05262](https://arxiv.org/abs/2202.05262)) · Geiger DAS 2023 ([2303.02536](https://arxiv.org/abs/2303.02536)) · Brinkmann multimodal AP 2024 ([2402.11917](https://arxiv.org/abs/2402.11917) [unverified ID]) |

判断：到 2026-05 这条线最值得记住的不是 "text-only 不能 ground" 也不是 "multimodal 解决了 grounding"，而是 **三个独立局部 mech 候选取代了一条全局 mech 主张**——C-GROUND-3 (deictic / first-person asymmetry)、C-GROUND-4 (contrastive ≠ referential)、C-GROUND-5 (action-execution gap)。三者落到不同 token 类型 (deictic 名词 / 一般名词 / 动词)、不同模态接口 (vision encoder / VLA closed-loop / tool-use trajectory)，且都自带可证伪 protocol。这种 "全局 mech → 多个 conditional mech" 的拆分与 §2 形式边界的 "expressivity 单一上界 → 四旋钮联合上界" 拆分同构——是 2024-26 NTP 调研在 mech 层最具结构性的方法学进步。但代价是：任何 grounding-style mech 论证此后必须显式同时控制至少七项 confound (format / readout / collapse / attribute-head / representation-geometry / FFN-grounding / prompt-edit-routing) 才能进入证据栈，2026 年能进入第三代 (counterfactual + cross-modal causal probe) 的 grounding-mech 工作不超过 5 篇——这是 *证伪难度* 而非 *现象不存在* 把战线拖在原地的主因。详细叙事见 [`../topics/grounding.md`](../topics/grounding.md) §第三代 probe 与 §Tool-use / action grounding；embodied 子带与 sensorimotor closed-loop 检验见 [`../topics/embodiment.md`](../topics/embodiment.md)；与 N5 (VLA bet) §3-§5 的对接是当前最活跃的 mech-vs-cap 交火带。

## 4. 因果

- Pearl 三层 (association / intervention / counterfactual)
- LLM 在 Layer 1 表现良好；Layer 2/3 系统性失败的证据 vs 反例
- "causal parrot" 论点

## 5. Embodiment

- VLA / robotics FM 给出的 "non-text" 信号能否被 token-predict 化（VQ tokenization 之争）
- closed-loop 学习 vs offline tokenized 训练

## 6. Online / continual

- catastrophic forgetting 的机制根源
- in-context learning 是否构成真 "学习" (vs 检索)

## 7. World model & planning

- 视频生成 ≠ world model：predictable pixel ≠ usable dynamics
- JEPA / Dreamer / Genie 路线证据

## 8. Reasoning vs pattern matching

- CoT faithfulness：表面 CoT 与内部计算的偏离证据 (Anthropic, etc.)
- 机制可解释性给出的 "lookup vs algorithm" 分界
- self-consistency / search 是真推理还是放大采样？

## 9. Open problems / 争议点

- (1) **Bitter lesson 反例存在吗**？目前所有"机制级不可能"声称都被后续 scale 推翻过；要找出**结构性、不会被推翻**的 lower bound。
- (2) **如何在不诉诸 embodiment 的前提下，证明纯 LLM 必然缺某项能力**？
- (3) **interactive feedback** 与 **passive prediction** 在 RL 收敛性意义下是否真正等价？

## 10. 候选 NTP-mech 列表 (持续筛选 → 反复挑战)

> 每条都标注：(a) 候选理由，(b) 最强反论 / 已知反例，(c) 当前结论。

### C1. Architecture-bound reasoning depth horizon (Deterministic Horizon)
- (a) 候选理由：Guo 2026 (2605.23024) 通过 residual-stream capacity invariant 论证存在仅由 (L, d) 决定的 H*，跨 12 架构实测 19–31；Zhang et al. 2026 (2605.19944) 经 OT/Wasserstein + Dyck-k → TC⁰ 复刻同型结论，且 width 不能换 depth。**(2026-05-27 修订)** Lost in Tokenization (2605.22471) 进一步证明 tokenization 选择对同一函数诱导多项式级 depth gap，意味着 C1 的参数集应改写为 **(L, d, tokenization)**。
- (b) 最强反论：Brösamle & Eckstein 2026 (2605.18079) 证明 softmax + 低精度 + log-grow depth 在加 CoT/summarized CoT 后 Turing-complete——即 H* 仅在 no-CoT / 固定输出长度下成立；CoT 把"深度"换成"token 时间"维度。
- (c) 当前结论：**Conditional NTP-mech 候选**。只在 no-CoT / 单 forward pass / 固定 tokenization 设定下成立；进入 CoT-augmented NTP 后退化为 NTP-cap 类的"长 horizon 估计代价 Ω(H)"问题。新轴 (tokenization) 暗示某些"模型机制级失败"可能是 BPE 工程选择导致的，可被换 tokenizer 缓解，进一步收紧"真正机制级"的范围。

### C2. SNR-limited factual recall / hallucination
- (a) 候选理由：Smith et al. 2026 (2605.18732) 把 recall quality 拟合到 (log params, log topic freq) 上的 sigmoid，族内 R² 74–94%；Shannon Scaling Law (2605.23901) 给出 SNR 不足时 U-shape 的非单调退化。
- (b) 最强反论：这只是 NTP-cap 类约束，不是机制级"做不到"——加 retrieval / 工具调用即可绕过。
- (c) 当前结论：**不是 NTP-mech，归 NTP-cap**。但有助于澄清 hallucination 论据不是 NTP-mech 的好弹药。

### C3. Long-horizon imitation 信息论 Ω(H) 下界
- (a) 候选理由：Xu et al. 2026 (2605.12316) 在 joint KL 下给出 Ω(H) 的 estimation 信息论下界，对 decomposable 与 fully shared policy class 都成立。
- (b) 最强反论：interactive RL / DAgger 可把误差曲线打平；这本质是 imitation framework 的代价，不是 next-token prediction 本身的代价（细分 NTP vs imitation 概念边界存疑）。
- (c) 当前结论：**NTP-cap**，对"长 horizon imitation 训练"有实操意义；不构成机制级 impossibility。

### 已被今日证据弱化的候选论点
- "CoT corruption 实验显示 LLM 不做真推理 → NTP 推理是表演"——被 2605.10799 的 readout 效应反例严重削弱，需重做。
- **(2026-05-27)** "Causal fine-tune 失败 → NTP 学不到因果推理"——被 2605.05438 的 model collapse 反例削弱：纯 CE FT 在小模型上 100% collapse 但 accuracy 仍 73.9% 掩盖。任何基于 aggregate accuracy 的"NTP 学不会因果"论据都需补 per-class 漂移检查。
- **(2026-05-27)** "NTP local objective ⇒ 无法做全局规划/属性控制"——被 2605.14004 (Conditional Attribute Transformers) 弱化为 readout/objective 工程问题，不构成机制级证据。

### 跨证据浮现的 meta-pattern (2026-05-27)
**Readout-side 主导假设**：本周累计 3 条 (2605.10799 / 2605.07120 / 2605.14004 / 2605.05438) 独立证据指向同一方向——大量被解读为"NTP 推理机制不足"的现象实际由 readout/format/objective/collapse 效应主导。下一阶段 NTP-mech 候选必须显式控制：(i) format confound, (ii) token-name readout dependency, (iii) collapse-by-CE, (iv) attribute-head 缺失。该 meta-pattern 比任何单一候选更具方法论意义。

### Readout-side 主导假设 — 闭环 (2026-05-28 update)
新增两条直接证据，把该假设从 *观察侧* 推进到 *观察+干预闭环*：
- **Causal Tongue-Tie ([2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md))** — 在 anti-commonsense CLadder 上 linear probe 0.97 / yes-no 0.5；≈+0.47 gap 全部归因到 verbal readout 失败。任何基于 yes/no accuracy 的"LLM 缺 causal X"声称必须附 probe-vs-output 双轨证据。
- **ProFIL ([2605.11467](../papers/paper_notes/2026-05-28-2605.11467-profil-probe-filtered-rl.md))** — frozen-base probe + GRPO advantage masking 在 GSM8K/LiveCodeBench/ToolUse/MMLU-Redux 上把 post-commitment CoT theater 减 11–100%，且 prior 预测的 RL-obfuscation 失败模式没出现 ⇒ "CoT theater = NTP 机制级缺陷"被工程修复反证。
- **NITP ([2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md))** — 加一项浅层激活作下一 token 稠密 self-target，把 9B MoE MMLU-Pro 推高 5.7% 而无新数据/模态/架构改动 ⇒ "NTP 表征几何欠约束 → mech 缺陷"也被降级到 objective-engineering 层。

**当前推论**：要立一条新的 NTP-mech 候选，必须显式同时排除：(i) format/answer-line confound, (ii) verbal-readout disexpression, (iii) CE-collapse 假阳性, (iv) attribute-head 缺失, (v) representation-geometry under-constraint, **(vi) FFN-grounding bottleneck (2026-05-29 新增)**, **(vii) prompt edit-family × task-routing 交互 (2026-05-29 新增)**。前五项是 *结构/训练* 侧，后两项是 *接口/方法学* 侧。这七个工程 confound 同时排除后仍稳定的 mech 现象，目前只剩：C1 (Deterministic Horizon, no-CoT)、Reversal Curse 类方向不对称、以及 long-horizon Ω(H) 信息论下界。

### confound 第六/七项 — 接口层补丁 (2026-05-29 update)
- **第六项 FFN-grounding bottleneck**: Li et al. ([2605.26362](../papers/paper_notes/2026-05-29-2605.26362-llm-hallucinate-structured.md)) 在 single-hop / multi-hop / tabular 三种 linearized 结构知识上证明 hallucination 的 sufficient statistic 是 **FFN 未将提供的 context 事实写入 residual**，而 attention 分布的 *task-dependent* 集中只是次要 signal；跨 schema detector AUC>0.8。任何\"LLM 不会用 in-context 结构知识做推理\"的 mech 声称必须先排除 FFN-grounding 失败，否则属于接口缺陷而非推理机制缺陷。
- **第七项 edit-family × task-routing**: Gong & Wen ([2605.26655](../papers/paper_notes/2026-05-29-2605.26655-prompt-opt-causal-edit-analysis.md)) 用 propensity-adjusted 多 representation 三角化证实 prompt-opt 跨任务不传递是 *edit family × task family* 系统性交互（complexity-increasing/meta-instructional vs step-by-step/meta-cognitive 在 math/multi-hop 与 logical/sequential 上方向相反）。任何\"prompt 改动暴露/掩盖 模型能力\"的声称必须报告 propensity-adjusted edit-family conditional effect，否则不可作为 mech 证据。

### C1 在 trained-stable looped 模型上的参数化修订 (2026-05-29 update)
STARS ([2605.26733](../papers/paper_notes/2026-05-29-2605.26733-stars-looped-stability.md)) 证明 LoopLM test-time depth 崩塌可由 Jacobian Spectral Radius Regularization 消除，深度提升单调饱和而非崩塌。这迫使 C1 的参数集从 (L, d, tokenization) 扩为 **(L, d, tokenization, convergence-mode)**：在 fixed-depth NTP 上 H* 紧致；在 trained-stable looped NTP 上应替换为 *converged loop depth*。STARS 同时为 objective-engineering 路线提供第 4 条修补 lever（在 NITP/ProFIL/Semantic-Loss/Conditional-Attr 之后）。

### C6 candidate 在世界假设条件下获理论加固 (2026-05-29 update)
Klindt-LeCun-Balestriero ([2605.26379](../papers/paper_notes/2026-05-29-2605.26379-lejepa-world-model-identifiability.md)) 双定理：在 stationary additive-noise 世界类下 LeJEPA 线性可辨识，且 Gaussian 是 *唯一* satisfying prior。该结果为 paradigm-replacement 路线提供条件性数学加固，但与 SPHERE-JEPA ([2605.26900], 球面流形 → hyperspherical uniform 才最优) 联读后只能定位为 \"**理想化世界下 LeJEPA 是优解**\"；并未否决 NTP 通用论点。对 C6 (video-NTP interventional rollout) 的影响是 *正面但有限*：LeJEPA-类 SSL 在 stationary 视频上具理论 identifiability，对长程 do(X)-consistency benchmark 是潜在 baseline。

### C5 (continual streaming) 获首条真实-世界 anchor (2026-05-29 update)
Zhu et al. ([2605.26820](../papers/paper_notes/2026-05-29-2605.26820-vla-real-world-continual.md)) 提供首条公开真实 VLA continual-learning benchmark（4 顺序任务 / rigid+contact+deformable / 多 replay 实现 ablation），把 C5 候选从模拟 anecdote 升级为 **可重复 reference**——之后任何 C5 否证声称需超过本文 best replay 数。

### C4 候选 (2026-05-28 新增, embodied 子带)
**VLA capability+robustness 总预算上界**：对任何 discrete-action VLA policy，capability MI + robustness MI ≤ H(task) + adversarial channel capacity（2605.25889）。pixel-level bound 松（~10³ nats），但 encoder-specific corollary 在 OpenVLA 上把预算压到 ~31 nats，且 policy 已吃满——这是 *与 policy 无关* 的硬上界，符合 NTP-mech 候选形式要件。

- (a) 候选理由：双 DPI + MI 非负的可形式化两行证明；encoder-specific corollary 给 actionable 数量级。
- (b) 最强反论：adversarial channel capacity 在 white-box 下可放任意大；encoder-specific 假设"扰动局限在 encoder 子空间"对 white-box 攻击者并不必然成立。
- (c) 当前结论：**Conditional NTP-mech 候选 (VLA 子带, discrete-action)**。不可直接升格为通用 NTP-mech。

### C5. NTP-loss continual-learning 不动点 (2026-05-28 新增, streaming 子带)
- (a) 候选理由：N7 §3–§5 综合论证。Lazaridou 2102.01951 给出每年关于新实体/事件的 perplexity 单调上升曲线；Kirkpatrick EWC 2017 (1612.00796) 在 LLM 规模上退化（70B 对角 Fisher = 280 GB；LR-decay 几何冲突）；Lyle 2303.01486 与 Dohare 2024 *Nature* (continual-backprop) 给 plasticity loss 的对偶视角；Ibrahim 2403.08763 把工程上限做到 \"retrain ±1%，FLOPs 1/10\"，但仍要求 batch=几千万 token / replay ≥ 5%——把 \"continual\" 在时间/空间上离散化。三条证据合并成弱化命题：**在 batch=1, replay=0, vanilla CE backbone update 的 streaming setting 下，旧域 KL 退化是 NTP-loss + dense transformer + CE 的联合不动点**。
- (b) 最强反论：(i) Ibrahim 2403.08763 把同一几何下的工程边界推到非常宽，弱化 \"几何不可绕开\" 的强读法；(ii) NITP (2605.24956) 在 9B MoE 上证明加一项浅层激活 self-target 可在不改架构下推 MMLU-Pro +5.7%，提示 \"NTP 几何欠约束\" 可能在 streaming 通道下提供未测的 plasticity 恢复机制——该 confound 尚未排除；(iii) Agent memory / RAG 路线已被工业界默认采纳，三条 N7 §5 反例 (TTT-Linear / MEMIT / MemGPT) 各自在 backbone-update / streaming / 不丢旧 三条件之一让步，但合起来说明 frontier lab 集体绕开权重端学习——这是 C5 间接支持证据而非反例。
- (c) 当前结论：**Conditional NTP-mech 候选 (streaming 子带)**。升降级判例已写入 [taxonomy.md §升降级判例](taxonomy.md) — 四升级条件目前 ✅✅✅❌，差 confound (iv) attribute-head 与 (v) representation-geometry 在 streaming setting 下的复现。可证伪 protocol：1B OLMo/Pythia base + 24h 单 GPU streaming + RealTime-QA-style 旧域 probe，漂移 ≤2pp/day 即降级。

### C6. Video-NTP interventional rollout consistency (2026-05-28 新增, video 子带)
- (a) 候选理由：[`topics/world_model.md`](../topics/world_model.md) §C-WM-3 把 \"video-NTP 是否挤出因果世界模型\" 形式化为 simulator-backed counterfactual benchmark $\mathcal{B}_{\text{do}}$ 上的 ATE 误差 $\varepsilon_{\text{do}}(M, X) = \mathbb{E}_{s,a}\|\mathbb{E}_M[s'|s,\text{do}(X{=}x)] - \mathbb{E}_{\text{sim}}[s'|s,\text{do}(X{=}x)]\|$，并主张 ∀ 仅在像素/latent frame 上 NTP 训练（无 simulator-backed counterfactual supervision）的 $M$，$\varepsilon_{\text{do}}(M,X) \gg 0$ 且不随训练 token 数衰减。已有三类支撑证据：(i) 文本侧 Kıcıman 2305.00050 在 counterfactual generation 上 GPT-4 系统性 fail，给出 Layer-2 失败的 text 模板；(ii) Vafa 2406.03689 的 Myhill–Nerode 度量是 \"半-interventional\"，在 Othello / NY-taxi 上展示 next-token-loss 已饱和但 internal state graph 与真实状态图不同构；(iii) Phyworld 2406.03520 [unverified ID] + PhyGenBench 报告 Sora 类模型在 ≥10s 上 object-vanish 率 >30%，已经触到 IntPhys 1803.07616 violation-of-expectation 范式但未升级到 do-operator triplet。
- (b) 最强反论：(i) Brinkmann 2402.11917 [unverified ID] 类 activation-patching 工作把 \"interventional\" 操作化为 causal mediation analysis 已经在小模型上证明可行，意味着某些 video world model 可能 *已经* 学到了因果电路，只是没人 patch 过；(ii) C-WM-3 的 falsifier 要求 \"同一权重\" 排除 fine-tuned 头——这与 [reasoning §ProFIL](../topics/reasoning.md) / [grounding §第三代 probe](../topics/grounding.md) 揭示的 readout-side confound 同构，可能存在 video-NTP 内部学到了 do(X)-consistent rollout 但 generative readout 不忠于该 latent 的 \"video tongue-tie\"；(iii) Genie 3 / Cosmos 这一代权重不公开，black-box ATE 估计的方差与 simulator-domain gap 可能掩盖 $\varepsilon_{\text{do}}$ 的真实大小。
- (c) 当前结论：**Conditional NTP-mech 候选 (video 子带)**。形式陈述齐全，falsification protocol 在 Brax/MuJoCo/Isaac Sim 这类可程序化 counterfactual 的 simulator 上可在 ≤1k GPU·h 内构造；与 C1 (no-CoT) / C4 (discrete-action VLA) 并列在条件 mech 第三栏。距离升 mech 仍差两步：(1) 把 C-WM-3 与 [causality.md §C-CAUSAL-1](../topics/causality.md) 在 *跨模态* 上做 joint falsifier 设计（避免 text-only / video-only 各自被 confound 掩盖）；(2) 排除 representation-geometry under-constraint confound——即在 NITP-augmented [2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md) 或 Geiger DAS 风格 boundless-DAS supervision 下的 video-NTP 上重测 $\varepsilon_{\text{do}}$，看 readout-side 修补是否能压平 ATE gap。

---
*Last revision: 2026-05-26 — populated by daily pipeline from formal_limits + scaling_limits + reasoning topics.*
*See git log of this file.*

---
*Last revision: see git log of this file.*
