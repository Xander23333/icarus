# Reasoning vs Pattern Matching

> CoT faithfulness, mech-interp, 多步推理可靠性。

## 核心问题与 NTP 假设

核心 NTP 争议点之一：CoT/reasoning 模型是否在做"真计算"，还是仅在 amplify 模式匹配？两条路径：(a) 机制可解释性证据；(b) corruption / 干预实验。后者的方法论稳健性本身是 meta-level 议题。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-13 | Conditional Attribute Transformers | NTP local objective 在序列级 attribute 估计上偏差大；联合训练 (p(token), E[attr]) 双 head 把方差和成本降一个数量级；说明部分"NTP 不会全局规划"是 head 设计问题 | cap (弱化 mech 论据) | [2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md) |
| 2026-05-06 | Semantic-Loss Anti-Collapse (Causal FT) | Gemma 270M 纯 CE FT 在 transitivity/d-sep 上 100% collapse，accuracy 73.9% 掩盖；semantic loss + 动态 λ 消除 collapse；"NTP 学不到因果"的部分论据是 collapse 假阳性 | counter-evidence | [2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md) |
| 2026-05-11 | Last Word Often Wins (Garcia) | GSM8K/MATH 上 CoT corruption 测出的"重要 step"主要是 answer-line **readout** 效应；删末行后 suffix sensitivity 塌缩 19× | counter-evidence | [2605.10799](../papers/paper_notes/2026-05-26-2605.10799-cot-format-confound.md) |

## 当前共识 / 争议

- 此前 CoT-faithfulness 文献（Lanham 2023、Turpin 2023 等）的 effect size 可能被 answer-text-following 这一 format confound 严重高估。
- 这并**不**等于说 CoT 一定忠实——而是当前测量协议不足以分辨 "中间步骤是真的在算" vs "模型在 consumption 时跟随末尾 answer text"。
- **新增 (2026-05-27)**：因果 fine-tune 类经验论据存在第二个 confound——**model collapse**（恒答 Yes/No 但 aggregate accuracy 仍高）。任何用单一 accuracy 论证"NTP 学不会因果/推理"的工作都需补 per-class / 输出分布漂移检查。同时 (Conditional Attribute Transformers) 提醒："NTP 不会全局规划"中至少一部分是 readout/objective 缺 attribute head 的工程问题，不构成机制级证据。

## Open problems

- 在三步 protocol (question-only control + format characterization + all-position sweep) 下复现已有 CoT (un)faithfulness 结论，看哪些幸存。
- 区分 generation-time vs consumption-time 因果：是否需要双向干预（同时改 prompt 和 sampling rollout）才能干净识别 reasoning locus。
- 与 latent / summarized CoT 设置下，readout 效应是否同样主导。
