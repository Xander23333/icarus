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

## Open problems

- 把 Deterministic Horizon 与 summarized CoT expressivity 放在同一坐标系下重新推导联合 bound。
- TC⁰ 下界的"per-token compute"假设在 MoE / 动态 depth / early-exit 架构下是否仍紧。
- 是否存在"width 真的能换 depth"的非 trivial 任务类（Barron 空间外）。
