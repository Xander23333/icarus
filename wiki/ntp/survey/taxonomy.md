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
