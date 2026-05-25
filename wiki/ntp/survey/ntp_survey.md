# NTP Survey — Main Document

> 长期演化主文档。每天的 daily report 都会把新增的实质性观点 / 证据 merge 到这里相应章节。

## 0. 目标与定义

本综述要回答的核心问题、NTP 工作定义、以及 NTP-mech / NTP-cap / Pseudo-NTP 三分法，见 [`../README.md`](../README.md)。

本文档承担的角色是 **「持续演化的理论综合」**，不是日报集合。每条进入本文档的论点都必须满足：
- (a) 有可引用的公开来源；
- (b) 在 NTP 三分法中能被定位；
- (c) 与已有论点的关系被明确写出（支持 / 反驳 / 正交 / 细化）。

## 1. 历史脉络 (placeholder — 待累积)

- **符号主义 vs 联结主义** 的老分歧如何在 LLM 时代复活
- **Searle 中文屋** → **Harnad 符号 grounding 问题** → 现代 multimodal grounding 实证
- **Marcus / Bender / Chomsky** 对 LLM "理解" 的怀疑论
- **Sutton "苦涩教训"** vs **机制级不可能性** 论点的张力

## 2. 形式边界 (formal limits)

| 论点 | 状态 | 关键文献 (待填) |
|---|---|---|
| Transformer 表达力上限 (TC⁰, log-precision) | — | — |
| 固定深度 Transformer 不能解某些 inherently sequential 问题 | — | — |
| In-context learning 的统计/信息论上限 | — | — |
| CoT 扩展计算预算后能等价多大复杂度类 | — | — |

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
- (a) 候选理由：Guo 2026 (2605.23024) 通过 residual-stream capacity invariant 论证存在仅由 (L, d) 决定的 H*，跨 12 架构实测 19–31；Zhang et al. 2026 (2605.19944) 经 OT/Wasserstein + Dyck-k → TC⁰ 复刻同型结论，且 width 不能换 depth。
- (b) 最强反论：Brösamle & Eckstein 2026 (2605.18079) 证明 softmax + 低精度 + log-grow depth 在加 CoT/summarized CoT 后 Turing-complete——即 H* 仅在 no-CoT / 固定输出长度下成立；CoT 把"深度"换成"token 时间"维度。
- (c) 当前结论：**Conditional NTP-mech 候选**。只在 no-CoT / 单 forward pass 设定下成立；进入 CoT-augmented NTP 后退化为 NTP-cap 类的"长 horizon 估计代价 Ω(H)"问题。

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

---
*Last revision: 2026-05-26 — populated by daily pipeline from formal_limits + scaling_limits + reasoning topics.*
*See git log of this file.*

---
*Last revision: see git log of this file.*
