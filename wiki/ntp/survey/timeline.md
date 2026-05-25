# NTP Research Timeline

按时间倒序累积重要事件 / 论文 / 立场转变。

| 日期 | 类型 | 事件 | 来源 |
|---|---|---|---|
| 2026-05-27 | meta | "Readout-side 主导假设"成型：四篇独立工作 (2605.10799/2605.07120/2605.14004/2605.05438) 指向 readout/format/objective/collapse 主导多数被误读为机制级的 NTP 失败 | this report |
| 2026-05-21 | 论文 | Lost in Tokenization：tokenization 选择对同一函数诱导多项式级 depth gap，C1 参数集应扩为 (L, d, tokenization) | [arXiv:2605.22471](../papers/paper_notes/2026-05-27-2605.22471-graph-tokenization-tradeoffs.md) |
| 2026-05-18 | 论文 | MHA as NW Ensemble：MHA = H 个 NW 估计器结构化 ensemble；variance 由 head decorrelation 主导 | [arXiv:2605.20271](../papers/paper_notes/2026-05-27-2605.20271-mha-as-nw-ensemble.md) |
| 2026-05-16 | 论文 | Language Acquisition Device：500 步 MP-STRUCT PPT 匹配 5k+ k-Shuffle Dyck PPT，prior 设计大幅缩短样本量 | [arXiv:2605.16758](../papers/paper_notes/2026-05-27-2605.16758-language-acquisition-device.md) |
| 2026-05-13 | 论文 | Conditional Attribute Transformers：联合 (next-token, attribute) head 弱化"NTP 不会全局规划"机制论据 | [arXiv:2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md) |
| 2026-05-08 | 论文 | Fresh-Symbol Classification：fixed-label template 任务 ideal + perturbation 分解；NTP readout 强制 token-name 依赖使该分解失效 | [arXiv:2605.07120](../papers/paper_notes/2026-05-27-2605.07120-fresh-symbol-classification.md) |
| 2026-05-06 | 方法论 | Causal-FT collapse confound：Gemma 270M 纯 CE 100% collapse 但 acc 73.9% 掩盖 | [arXiv:2605.05438](../papers/paper_notes/2026-05-27-2605.05438-semantic-loss-causal-collapse.md) |
| 2026-05-22 | 论文 | Shannon Scaling Law：把 LLM 训练 cast 成 noisy channel，预测 U-shape 非单调 scaling | [arXiv:2605.23901](../papers/paper_notes/2026-05-26-2605.23901-shannon-scaling-law.md) |
| 2026-05-21 | 论文 | Deterministic Horizon：由架构参数决定的推理深度上界 H* ∈ [19,31]，部署前可计算 | [arXiv:2605.23024](../papers/paper_notes/2026-05-26-2605.23024-deterministic-horizon.md) |
| 2026-05-19 | 论文 | Measure-Theoretic Reasoning：OT/Wasserstein 框架下导出 RoPE 优于 APE、Dyck-k → TC⁰ depth 下界 | [arXiv:2605.19944](../papers/paper_notes/2026-05-26-2605.19944-measure-theoretic-reasoning.md) |
| 2026-05-18 | 论文 | Low-Precision Softmax + CoT：在现实精度下证 Turing-completeness；summarized CoT log-space scaling | [arXiv:2605.18079](../papers/paper_notes/2026-05-26-2605.18079-lowprec-softmax-cot.md) |
| 2026-05-12 | 论文 | Joint-KL AR Learning：approximation horizon-free、estimation Ω(H) 信息论下界 | [arXiv:2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md) |
| 2026-05-11 | 方法论 | CoT corruption studies 被发现含 answer-line format confound (≈19× 抑制) | [arXiv:2605.10799](../papers/paper_notes/2026-05-26-2605.10799-cot-format-confound.md) |
| 2026-05-26 | start | NTP survey 启动 | this repo |

> 由 daily pipeline 自动追加。
