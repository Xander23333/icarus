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

- **核心论点 A**：纯文本训练系统对物理世界 referent 的把握必然受限。
- **核心论点 B**：multimodal 训练能缓解但不消除（因仍是被动观察，缺 intervention）。
- **反论**：足够大规模的多模态 + 工具调用可以让 grounding 成为 emergent 工程问题，而非机制问题。

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

**当前推论**：要立一条新的 NTP-mech 候选，必须显式同时排除：(i) format/answer-line confound, (ii) verbal-readout disexpression, (iii) CE-collapse 假阳性, (iv) attribute-head 缺失, (v) representation-geometry under-constraint。这五个工程 confound 同时排除后仍稳定的 mech 现象，目前只剩：C1 (Deterministic Horizon, no-CoT)、Reversal Curse 类方向不对称、以及 long-horizon Ω(H) 信息论下界。

### C4 候选 (2026-05-28 新增, embodied 子带)
**VLA capability+robustness 总预算上界**：对任何 discrete-action VLA policy，capability MI + robustness MI ≤ H(task) + adversarial channel capacity（2605.25889）。pixel-level bound 松（~10³ nats），但 encoder-specific corollary 在 OpenVLA 上把预算压到 ~31 nats，且 policy 已吃满——这是 *与 policy 无关* 的硬上界，符合 NTP-mech 候选形式要件。

- (a) 候选理由：双 DPI + MI 非负的可形式化两行证明；encoder-specific corollary 给 actionable 数量级。
- (b) 最强反论：adversarial channel capacity 在 white-box 下可放任意大；encoder-specific 假设"扰动局限在 encoder 子空间"对 white-box 攻击者并不必然成立。
- (c) 当前结论：**Conditional NTP-mech 候选 (VLA 子带, discrete-action)**。不可直接升格为通用 NTP-mech。

---
*Last revision: 2026-05-26 — populated by daily pipeline from formal_limits + scaling_limits + reasoning topics.*
*See git log of this file.*

---
*Last revision: see git log of this file.*
