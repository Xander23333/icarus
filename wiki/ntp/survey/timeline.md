# NTP Research Timeline

按时间倒序累积重要事件 / 论文 / 立场转变。

| 日期 | 类型 | 事件 | 来源 |
|---|---|---|---|
| 2026-05-29 | meta | 浮现 **第六层 confound — FFN-as-grounding bottleneck**（Li et al. 2605.26362 的跨 schema mech 证据）；并把 **edit-family × task-routing** 写入方法论 confound 清单（Gong & Wen 2605.26655）；§10 招标书 confound 数从 5 升 7 | this report |
| 2026-05-25 | 论文 | LeJEPA world-model 可辨识性双定理：alignment + Gaussian reg ⇒ linear identifiability，且 Gaussian 是 *唯一* satisfying prior（stationary additive-noise 世界类下） | [arXiv:2605.26379](../papers/paper_notes/2026-05-29-2605.26379-lejepa-world-model-identifiability.md) |
| 2026-05-26 | 论文 | STARS：LoopLM 崩塌 = Jacobian 谱半径 >1；Spectral Radius Regularization 把 test-time depth 拉到单调饱和；C1 在 trained-stable looped 模型上需替换为 *converged depth* | [arXiv:2605.26733](../papers/paper_notes/2026-05-29-2605.26733-stars-looped-stability.md) |
| 2026-05-26 | 论文 | 首个真实 VLA continual-learning benchmark：显著 catastrophic forgetting；C5 候选首获公开真实 reference | [arXiv:2605.26820](../papers/paper_notes/2026-05-29-2605.26820-vla-real-world-continual.md) |
| 2026-05-25 | 论文 | LLM 在 linearized 结构知识上 hallucinate 的 sufficient statistic 是 **FFN grounding** 失败而非 attention 失焦；跨 graph/multi-hop/table 通用 | [arXiv:2605.26362](../papers/paper_notes/2026-05-29-2605.26362-llm-hallucinate-structured.md) |
| 2026-05-26 | 方法论 | Prompt-opt edit-family × task-routing 交互被定量分离；prompt-only effect 不可作 mech 证据 | [arXiv:2605.26655](../papers/paper_notes/2026-05-29-2605.26655-prompt-opt-causal-edit-analysis.md) |
| 2026-05-28 | meta | "Readout-side 主导假设"再添 2 条直接证据 (probe 0.97 vs yes/no 0.5 的 Causal Tongue-Tie；frozen probe + GRPO masking 把 CoT theater 减 11–100% 的 ProFIL)；该假设的 *观察侧* 与 *干预侧* 形成闭环 | this report |
| 2026-05-26 | 论文 | NITP：用浅层激活作下一 token 稠密 self-target，9B MoE MMLU-Pro +5.7%；NTP 几何欠约束属 objective-engineering 层，可被轻量 auxiliary 修掉 | [arXiv:2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md) |
| 2026-05-26 | 论文 | Causal Tongue-Tie：anti-commonsense CLadder 上 probe 0.97 / yes-no 0.5；output-only causal benchmark 不能直读为 mechanism | [arXiv:2605.25891](../papers/paper_notes/2026-05-28-2605.25891-causal-tongue-tie.md) |
| 2026-05-26 | 论文 | VLA capability+robustness IT bound：H(task) + adv channel cap 作总预算；OpenVLA encoder-specific 预算 ~31 nats | [arXiv:2605.25889](../papers/paper_notes/2026-05-28-2605.25889-vla-capability-robustness-bound.md) |
| 2026-05-26 | 论文 | ProFIL：frozen-base probe + GRPO advantage masking 把 post-commitment CoT theater 减 11–100%，无 RL-obfuscation 退化 | [arXiv:2605.11467](../papers/paper_notes/2026-05-28-2605.11467-profil-probe-filtered-rl.md) |
| 2026-05-26 | 论文 | Why World Models for AGI (LDI/Flux)：rule-defined latent-state RL agent 在 long-horizon 上系统性优于纯文本 LLM；提出 objective-level 错配主张（前提依赖 simulator-access） | [arXiv:2605.23972](../papers/paper_notes/2026-05-28-2605.23972-world-models-for-agi-ldi.md) |
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
