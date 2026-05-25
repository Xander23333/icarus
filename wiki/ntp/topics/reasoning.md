# Reasoning vs Pattern Matching

> CoT faithfulness, mech-interp, 多步推理可靠性。

## 核心问题与 NTP 假设

核心 NTP 争议点之一：CoT/reasoning 模型是否在做"真计算"，还是仅在 amplify 模式匹配？两条路径：(a) 机制可解释性证据；(b) corruption / 干预实验。后者的方法论稳健性本身是 meta-level 议题。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-11 | Last Word Often Wins (Garcia) | GSM8K/MATH 上 CoT corruption 测出的"重要 step"主要是 answer-line **readout** 效应；删末行后 suffix sensitivity 塌缩 19× | counter-evidence | [2605.10799](../papers/paper_notes/2026-05-26-2605.10799-cot-format-confound.md) |

## 当前共识 / 争议

- 此前 CoT-faithfulness 文献（Lanham 2023、Turpin 2023 等）的 effect size 可能被 answer-text-following 这一 format confound 严重高估。
- 这并**不**等于说 CoT 一定忠实——而是当前测量协议不足以分辨 "中间步骤是真的在算" vs "模型在 consumption 时跟随末尾 answer text"。

## Open problems

- 在三步 protocol (question-only control + format characterization + all-position sweep) 下复现已有 CoT (un)faithfulness 结论，看哪些幸存。
- 区分 generation-time vs consumption-time 因果：是否需要双向干预（同时改 prompt 和 sampling rollout）才能干净识别 reasoning locus。
- 与 latent / summarized CoT 设置下，readout 效应是否同样主导。
