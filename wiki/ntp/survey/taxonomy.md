# NTP Taxonomy

## 一级分类

```
NTP (Non-Tokenizable Problems)
├── NTP-mech   机制级 — 论证级别为 "无论 scale 多大都不可获得"
├── NTP-cap    能力级 — 当前训练范式未获得，但机制上不排除
└── Pseudo-NTP 伪 NTP — 数据/接口/budget 工程缺口
```

## 二级 (按能力领域)

| 大类 | 子类 | 候选 NTP-mech 论点 (待严格化) |
|---|---|---|
| Formal | Expressivity bound | 固定深度 TC⁰ 上限内的问题类 |
| Formal | Sequential computation | inherently sequential 问题在 fixed-depth 下不可解 |
| Reasoning | Faithful multi-step | CoT 与内部计算偏离 → 长链可靠性上限 |
| Reasoning | Compositional gen | 训练分布外的 systematic generalization |
| Grounding | Symbol → referent | 纯文本下的物理 referent 锚定 |
| Causality | Layer-2/3 inference | 无干预数据时的反事实预测 |
| Embodiment | Closed-loop control | 实时感知-行动闭环 |
| Online | Non-stationary adapt | 训练后真分布漂移下的持续适应 |
| World model | Long-horizon dynamics | 视频/语言序列上的长程动力学一致性 |
| Scaling | Sample efficiency floor | 某类任务存在 sample-complexity 下界 |

## 三级 (per candidate, 在 paper_notes 内单独维护)

每个候选 NTP-mech 论点维护：
- 形式陈述 (formal statement)
- 已有 lower bound 证据
- 已有反例 / 上界突破
- 当前共识强度: ★ ☆☆☆☆ → ★★★★★

## 升降级的判定规则 (grading rubric)

把一个论点从 NTP-cap **升**为 NTP-mech，须同时满足：

1. **形式陈述可在不引入未定义新概念的前提下写出**（lemma-style，不是 prose）。
2. **存在与某个已知复杂度类、信息论量或代数对象的非平凡映射**（如 TC⁰、KL Ω(H)、Pearl Layer 2/3 do-operator）。
3. **可证伪条件具体到 protocol 级**——给出一个能在 ≤1k GPU·h 内执行的实验，其结果能在该论点的成立/不成立间二分。
4. **现有反例已被显式排除**——对照 [`ntp_survey.md`](ntp_survey.md) §10 的「五道工程 confound」清单（format/readout/CE-collapse/attribute-head/representation-geometry under-constraint）逐一回应。

反过来，把一个 NTP-mech 候选**降**回 NTP-cap 的触发条件：

- (A) 某 confound 被新工作（如 [Garcia 2026](https://arxiv.org/abs/2605.10799)、ProFIL [2605.11467](https://arxiv.org/abs/2605.11467)、NITP [2605.24956](https://arxiv.org/abs/2605.24956) [unverified ID]）证明可解释观察到的 effect size 大半；
- (B) 同一现象在新旋钮上被打开（例：[Ruoss 2305.16843](https://arxiv.org/abs/2305.16843) 的随机 PE 打开 Bhattamishra 2009.11264 的 PARITY 墙；[McLeish 2405.17399](https://arxiv.org/abs/2405.17399) Abacus embedding 打开 length-extrapolation 墙）；
- (C) 形式陈述被发现 implicit 假设了某个工程默认（如 vanilla BPE、no-CoT、fixed depth），换默认后陈述失效。

降级到 Pseudo-NTP 的触发条件更严：必须证明所谓"缺失能力"在**当前**主流工程栈内已被覆盖（retrieval、tool-use、scratchpad、外部状态机），且 cost 不随 scale 发散。

## 已升降级历史 (rolling log)

| 时间 | 论点 | 旧级别 | 新级别 | 触发文献 |
|---|---|---|---|---|
| 2023 中后 | "CoT 一定不忠 → NTP 推理是表演" | NTP-mech 候选 | NTP-cap 候选 | Anthropic 2025-03 attribution graph 在 Claude 3.5 Haiku 上观察到多步算术的逐级合成 |
| 2024-06 | "fixed-depth transformer 不能数 parity" 全局命题 | NTP-mech | 条件 NTP-mech (仅 vanilla PE) | [Ruoss 2305.16843](https://arxiv.org/abs/2305.16843)、[McLeish 2405.17399](https://arxiv.org/abs/2405.17399) |
| 2026-05-26 | "CoT corruption → reasoning 是表演" | NTP-mech 候选 | 待重做 (format confound) | [Garcia 2605.10799](https://arxiv.org/abs/2605.10799) |
| 2026-05-27 | "Causal FT 失败 → NTP 学不到 causality" | NTP-mech 候选 | NTP-cap (CE-collapse 假阳性) | [Semantic-Loss Anti-Collapse 2605.05438](https://arxiv.org/abs/2605.05438) [unverified ID] |
| 2026-05-27 | "NTP local objective ⇒ 不会全局规划" | NTP-mech 候选 | NTP-cap (head 工程问题) | [Conditional Attribute Transformers 2605.14004](https://arxiv.org/abs/2605.14004) [unverified ID] |
| 2026-05-28 | "yes/no 准确率代表 causal mechanism" | 默认假设 | 已证伪 | [Causal Tongue-Tie 2605.25891](https://arxiv.org/abs/2605.25891) [unverified ID]，probe 0.97 vs output 0.5 |
| 2026-05-28 | "post-commitment CoT theater 是机制缺陷" | NTP-mech 候选 | NTP-cap (RL-readout 可修) | [ProFIL 2605.11467](https://arxiv.org/abs/2605.11467) [unverified ID] |
| 2026-05-28 | "VLA capability+robustness 总预算" (discrete-action) | 未分类 | 条件 NTP-mech (encoder-specific) | 2605.25889 [unverified ID] |

判断：本表的形状给出一个非常硬的经验观察——**升级事件极少（近三年实质只有 C1 Deterministic Horizon 与 C4 VLA 预算上界两个真正达到 conditional NTP-mech），降级事件密集**。任何还没经历过至少一次"被认真挑战、并把可证伪条件改写至少两遍"的候选，目前的默认假设应当是它会在下一个 confound 被识别后降级，而不是相反。这是 [`ntp_survey.md`](ntp_survey.md) §10 维护节奏的方法论依据。

## 当前 candidate 状态快照 (2026-05-28)

| ID | 内容 | 当前级别 | 关键 falsification | 主页面 |
|---|---|---|---|---|
| C1 | Deterministic Horizon H* ∈ [19,31] @ (L, d, tokenization) | Conditional NTP-mech (no-CoT) | 在 no-CoT / 固定 tokenization 下找到打破 H* 的任务族 | [formal_limits §C-FORM-1](../topics/formal_limits.md) |
| C2 | Hallucination ∝ (log params, log freq) sigmoid | NTP-cap | 某域内 hallucination 率随频率非单调且不能由 SNR 解释 | [scaling_limits §C-SCALE-2](../topics/scaling_limits.md) |
| C3 | Long-horizon imitation Ω(H) joint-KL 下界 | NTP-cap | 存在算法在无外部状态压缩下使 KL-error 次线性于 H | [scaling_limits §C-SCALE-1](../topics/scaling_limits.md) / [reasoning §C-REAS-3](../topics/reasoning.md) |
| C4 | VLA capability+robustness MI ≤ H(task)+adv | Conditional NTP-mech (discrete VLA) | encoder 子空间假设在 white-box 下失效 | [embodiment](../topics/embodiment.md) |
| — | Reversal Curse 方向不对称 | NTP-mech 候选 (待 ≥7B prefix-LM 复现) | 7B+ prefix-LM 训练消解该效应 | [reasoning §C-REAS-1](../topics/reasoning.md) |

C1 与 C4 是当前唯二写出"形式陈述 + 非平凡映射 + protocol 级 falsification + 排除五 confound"全套的候选；其余仍处于 NTP-cap 或待形式化阶段。

## 与其它文档的接口

- [`ntp_survey.md`](ntp_survey.md) §10 维护候选清单的逐条状态；本页维护**升降级规则**与历史日志。
- 各 [`topics/*.md`](../topics/) 维护 mech-level 候选的形式细节与实测证据线。
- [`samples/`](../samples/) 把每个候选叙事化（如 [N2 the-tc0-wall](../samples/N2-the-tc0-wall.md) 对应 C1）。

任何对 candidate 做升降级的 commit 都应同时改三处：候选所在 topic 页（证据线）+ ntp_survey.md §10（候选条目）+ 本页升降级历史表。三处不同步即视为 incomplete。
