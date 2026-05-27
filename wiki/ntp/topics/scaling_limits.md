# In-context & Scaling Limits

> Scaling laws 上界, ICL theory, sample complexity。

## 核心问题与 NTP 假设

跟踪：(a) 经典单调 scaling law 失效的反例与新法则（catastrophic overtraining、quantization degrade）；(b) 把"模型能力"沿容量 × 数据 × 任务三轴拆解的精细化 law；(c) NTP 在长 horizon imitation 下的样本复杂度紧界。这些都属于 **NTP-cap** 范畴——它们不主张 NTP 学不到某事，而是钉死 finite-resource 下的可达边界。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 2026-05-16 | Language Acquisition Device (LAD-PPT) | MP-STRUCT (MERGE/AGREE/MOVE 编码) 在 500 步 PPT 即匹配 5k+ 步 k-Shuffle Dyck PPT，BLiMP 长程子集反超；prior 设计可显著缩短样本量 | cap | [2605.16758](../papers/paper_notes/2026-05-27-2605.16758-language-acquisition-device.md) |
| 2026-05-22 | Shannon Scaling Law (Ouyang et al.) | LLM 训练 = noisy channel；SNR 不足时性能呈 U-shape；外推 12B/307B token 仍 R²=0.847 | cap | [2605.23901](../papers/paper_notes/2026-05-26-2605.23901-shannon-scaling-law.md) |
| 2026-05-18 | Predictable Confabulations (Smith et al.) | factual recall 在 (log params, log topic freq) 上 sigmoid；族内 R²=74–94% | cap | [2605.18732](../papers/paper_notes/2026-05-26-2605.18732-predictable-confabulations.md) |
| 2026-05-12 | Joint-KL AR Learning (Xu et al.) | approximation horizon-free；estimation 有 Ω(H) 信息论下界与 Õ(H) 上界匹配 | cap | [2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md) |

## 当前共识 / 争议

- **共识浮现**：单调幂律不足以描述 LLM 训练；至少需要引入 SNR / U-shape / sigmoid 的非单调结构；hallucination 与 long-tail recall 是可预测的 SNR 现象。
- **争议**：长 horizon NTP 的 Ω(H) 是否能通过 RL/critic / planning loss 真正绕过——理论上界与算法实践的落差仍未量化。
- 仍待澄清：Shannon Scaling Law 假定的 Gaussian 噪声是否能覆盖 SFT 引入的结构化漂移。

## 关键证据线 (chronological)

把 "NTP 的 scaling/in-context 上界" 这条线按时间排开，可以看到它经历过两次范式翻转：从 Kaplan 派单调幂律，到 Chinchilla 的 compute-optimal 修正，再到 2024–2026 一系列 "幂律不够用" 的非单调 / 阶梯 / U-shape 现象。

- **2020-01 — Kaplan et al., *Scaling Laws for Neural Language Models* ([arxiv:2001.08361](https://arxiv.org/abs/2001.08361))**。Jared Kaplan 等在 OpenAI 用 GPT 系列拟合出 loss ∝ N^-α、D^-β 的对数线性律，并给出经典结论："给定 compute budget，应该把绝大多数预算花在更大模型而非更多数据"。这一结论支配了 2020–2022 的大模型 race。
- **2022-03 — Hoffmann et al. (DeepMind), *Training Compute-Optimal LLMs* (Chinchilla, [arxiv:2203.15556](https://arxiv.org/abs/2203.15556))**。重新拟合后给出 N≈D 的 compute-optimal 配比，并训练 Chinchilla 70B 击败 Gopher 280B。Kaplan 法则的 "data-cheap" 假设被首次系统性证伪——不是因为定律错，而是因为原拟合的 LR schedule / token-count 范围太窄。从此 "scaling law 形态依赖于拟合协议本身" 成为 meta 共识。
- **2022-06 — Wei et al., *Emergent Abilities of LLMs* ([arxiv:2206.07682](https://arxiv.org/abs/2206.07682))**。提出某些任务在临界规模处出现 "相变"，loss 平滑但 accuracy 阶梯。后被 **Schaeffer et al. 2023, *Are Emergent Abilities a Mirage?* ([arxiv:2304.15004](https://arxiv.org/abs/2304.15004))** 反驳：阶梯绝大部分来自非线性 metric（exact-match / multi-choice acc）；换成 token-level edit distance 后单调 sigmoid 即可拟合。这是 scaling-limit 文献中第一次明确区分 **"模型能力的相变"** 与 **"评测函数的相变"**——一个被长期混淆的 confound。
- **2022-10 — Sorscher et al., *Beyond Neural Scaling Laws via Data Pruning* ([arxiv:2206.14486](https://arxiv.org/abs/2206.14486))**。证明只要数据按 example difficulty 做选择，幂律可被打成指数律。Scaling law 的 "幂" 不是物理常数，是 i.i.d. 假设下的退化结果。
- **2024-04 — Gadre et al., *Language Models Scale Reliably with Over-Training* ([arxiv:2403.08540](https://arxiv.org/abs/2403.08540))**。把 Chinchilla 的拟合范围扩到 32× compute-optimal token 数，发现 loss 仍可外推，但下游 task 指标偏离日益显著——预示了 "over-training 的回报随任务而异" 的新问题。
- **2025-03 — *Overtrained Language Models Are Harder to Fine-Tune* (Liu et al., [arxiv:2503.19206](https://arxiv.org/abs/2503.19206)) [unverified ID]**。给出 "catastrophic overtraining" 现象：预训练 token 数超过某个阈值后，SFT/RLHF 的 plasticity 不可逆地下降，下游 quality 与 pretrain loss 反向。Kaplan-Chinchilla 这一系完全没有预测到这种 **"loss 仍降，可塑性已死"** 的 regime。
- **2024-10 — Kumar et al., *Scaling Laws for Precision* ([arxiv:2411.04330](https://arxiv.org/abs/2411.04330))**。把 quantization degrade 写进 scaling law：训练精度低于阈值时 effective parameter count 会按比例 shrink；INT4 训练在某些 N/D 配比下不可恢复。"用更小精度换更多参数" 的工程 trick 第一次被钉到上界曲线上。
- **2026-05 — Joint-KL AR Learning (Xu et al., [2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md))**。给出长 horizon NTP 的 estimation 复杂度 Ω(H) 信息论下界与 Õ(H) 匹配上界。这是 scaling 论里第一次把 **horizon** 作为独立轴和 (N, D, C) 并列；意味着 "更长的 chain-of-thought 必然伴随线性 sample-complexity 代价"，除非引入额外结构。
- **2026-05 — Shannon Scaling Law (Ouyang et al., [2605.23901](../papers/paper_notes/2026-05-26-2605.23901-shannon-scaling-law.md))**。把训练视作 noisy channel，SNR 不足时给出 U-shape——同时回答了 Schaeffer 留下的悬念：某些任务的非单调并非 metric artifact，而是 channel capacity 触底反弹。R² 0.847 外推到 307B token 仍站得住。
- **2026-05 — Predictable Confabulations (Smith et al., [2605.18732](../papers/paper_notes/2026-05-26-2605.18732-predictable-confabulations.md))**。把 hallucination 率写成 (log params, log topic freq) 上的 sigmoid，族内 R² 74–94%。Hallucination 至此从 "未知失败模式" 升格为 "可在部署前估计的 SNR 现象"。

## 当前最强的 mech / cap 候选 (NTP 视角)

把上面这条线整理成可证伪的 cap-level 假设，2026-05 留下三条最难被冲掉的：

- **C-SCALE-1 — Horizon-linear estimation floor**。在没有额外 Markov / 压缩结构时，NTP 的 estimation error 至少线性于 horizon H 增长（Joint-KL Ω(H)）。**Falsification**: 找到一个非平凡任务族 + 无外部状态压缩的算法，使 KL-estimation error 在 H↑ 时保持次线性。
- **C-SCALE-2 — Hallucination-SNR sigmoid**。模型对低频事实的 confabulation 率是 (log params, log freq) 的 sigmoid，部署前可由 corpus frequency 估计。**Falsification**: 给出一个领域内事实分布，使在固定 params 下 hallucination 率随 frequency 非单调，且不能被 SNR / superposition 解释。
- **C-SCALE-3 — Plasticity cliff**。预训练 token 数超过某临界 D\* 后，下游 fine-tune 的 reachable quality 不再随 D 增加而增加，反向下降（catastrophic overtraining）。**Falsification**: 找到一个 SFT/RLHF 协议（不只是降 LR），在 D ≫ D\* 后仍能恢复 small-D 的 plasticity；或证明 D\* 本身是 optimizer artifact 而非数据 artifact。

## 反例 / 上界突破候选

- **Data pruning 打破幂律 (Sorscher 2022)**：在 i.i.d. 假设外，幂律退化为指数律——意味着 C-SCALE-1 这类 "复杂度沿轴线性增长" 的论据严格依赖于 i.i.d. sampling，离开该假设后斜率可大幅改变。
- **Mirage of emergence (Schaeffer 2023)**：阶梯现象绝大部分由 metric 非线性制造——任何用 "下游任务突变" 论证 scaling-mech 上界的工作都必须先做 metric robustness check。
- **Summarized-CoT Turing-completeness (Brösamle & Eckstein 2026-05, see formal_limits)**：log-space CoT 把表达力推到 Turing-complete；Ω(H) 这个 sample-complexity 下界在算法层并未阻止能力达成，只是 amortize 到 inference compute 上。换言之，C-SCALE-1 是 "训练样本复杂度" 上界，不是 "可达能力" 上界——两者经常被混读。

## 2026-05-27 判断

到本 tick 为止，scaling-limits 这一脉的经验论据正在朝两个方向同时进化：(i) **法则形态** 从单调幂律 → Chinchilla 配比 → SNR/U-shape/sigmoid 的非单调结构，每一步都被新数据强行加形；(ii) **轴的数量** 从 (N, D, C) 扩到 (N, D, C, precision, horizon, topic-frequency)。这意味着 "NTP 的 scaling 上界" 已不再是单一曲面，而是多轴流形——任何只引一条 Kaplan-style 幂律就下 "NTP 到此为止" 结论的论证，2026 年起几乎一定漏掉至少一轴。

但流形扩张并不削弱 cap 论据，只是让它更精细：C-SCALE-1/2/3 三条候选都把 "上界" 表述为 **某条轴上的不可避免代价**（horizon-linear sample、frequency-sigmoid confabulation、token-cliff plasticity），而不是 "做不到"。这与 [formal_limits](formal_limits.md) 的 mech 上界、[reasoning](reasoning.md) 的 CoT-faithfulness 争论形成互补：formal_limits 钉表达力天花板，scaling_limits 钉 finite-resource 可达边界，reasoning 钉中间过程是否可信。

## Inference-time scaling: 第四轴 (2024–2026)

到 2024 年下半年，"NTP 的 scaling 上界" 这条战线被强行加了一根轴：**inference-time compute**。从 Kaplan 到 Chinchilla 再到 over-training，前一代法则讨论的全部是 (N, D, C_train)；2024 年起，C_inference 成了与之等价、有时甚至可互换的预算变量。这条线必须独立写，因为它直接动摇了 "更大的 NTP 模型 = 更强 / 更小的 NTP 模型 = 更弱" 这个隐含背景假设。

- **2024-07 — Brown et al., *Large Language Monkeys: Scaling Inference Compute with Repeated Sampling* ([arxiv:2407.21787](https://arxiv.org/abs/2407.21787))**。在 MATH、GSM8K、SWE-bench Lite 等任务上把 sampling 数量从 1 推到 10⁴，发现 coverage（pass@k 中至少一次正确）在 k 上呈近似幂律。结论：在可验证任务上，**用 10⁴× inference compute 把 Llama-3-8B 推到接近 GPT-4o 单样本水平**——这是 inference-time scaling 第一次被钉成对数线性曲线，而不是一个工程 trick。
- **2024-08 — Snell et al., *Scaling LLM Test-Time Compute Optimally Can Be More Effective than Scaling Model Parameters* ([arxiv:2408.03314](https://arxiv.org/abs/2408.03314))**。Google DeepMind / UC Berkeley 联合，在 MATH 上系统比较 (i) best-of-N + reward model verification、(ii) revision-based sequential 修订、(iii) tree-search beam。给出 **compute-optimal 推理策略随任务难度自适应**，并在简单/中等任务上证明 **14× 推理 compute 可以替代 14× 预训练 compute**——这是 (N, D, C_train) 与 C_inference 第一次被写成可互换的预算单位。
- **2024-09 — OpenAI o1 system card / blog**（非 arxiv）：首个产品化"思考时间 = 第二条 scaling 曲线"的 frontier model，公开图表显示 AIME accuracy 在 train-time compute 与 test-time compute 两轴上各自单调上升，且斜率相近。
- **2025-01 — DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。RL-from-verifier 训出可观长度的 CoT；附录的 length-vs-accuracy 曲线在 AIME / MATH-500 上同样呈现 log-linear，且 R1-Distill-Qwen-7B 在数学任务上超过 GPT-4o (2024-05)——一个 7B NTP 模型靠 inference compute 抹平了约 50× 参数差距。
- **2025-02 — Wu et al., *Inference Scaling Laws: An Empirical Analysis of Compute-Optimal Inference for LLM Problem-Solving* ([arxiv:2408.00724](https://arxiv.org/abs/2408.00724))**。在 MATH、GSM8K 上拟合 inference-compute 与 error rate 的幂律指数，给出 task-dependent 的 compute-optimal sampling 配比。重点结论：**inference-scaling 的幂律指数随任务可验证度变化** —— 可严格验证的任务（数学、代码）指数大，不可验证（开放写作、对话）几乎为 0。这把 inference-time scaling 限定到 "verifier-bounded" 子集。
- **2025-08 — Sardana et al. / Beyond Chinchilla-Optimal ([arxiv:2401.00448](https://arxiv.org/abs/2401.00448) 的后续）**。在考虑 inference 总成本（部署期 token 数 × 单 token 推理 cost）后，optimal N/D 配比相对 Chinchilla **显著偏向小模型 + 更多训练 token**。这是 Chinchilla 法则被 "inference 占主导的真实部署" 第二次系统性修正——也是 C-SCALE-3 plasticity cliff 与 inference-time scaling 之间张力的源头。
- **2025-12 — *s1: Simple test-time scaling* (Muennighoff et al., [arxiv:2501.19393](https://arxiv.org/abs/2501.19393)) [unverified ID]**。仅 1k 高质量推理样本 SFT + budget-forcing（强制延长或截断 thinking），在 AIME-24 上取得与 o1-preview 同档结果，证明 **inference-time scaling 的大部分收益不依赖大规模 RL，只需要让模型"愿意写长"**。这弱化了 R1-style RL 是 inference-scaling 必要条件的假设。

把上述线收一遍可以看到：2024–2026 inference-scaling 的经验幂律已经具备 Kaplan-2020 那种 "斜率稳定、外推可用" 的成色，但 **作用域被严格限定在 verifier-rich 任务**。在没有 ground-truth 验证器的开放任务上（创意写作、长对话、agentic 多步任务的中间步骤），inference-compute 的边际收益快速消失——这恰好对应 C-WM-2 "open-world dilution" 在 inference 侧的对偶。

新增候选条目：

- **C-SCALE-4 — Inference-train compute equivalence within verifier-rich tasks**。在存在低噪声 verifier 的任务族 V 上，C_train 与 C_inference 在 error rate 上近似可互换：log error ≈ −α log C_train − β log C_inference + const，且 α/β 在同族内稳定。**Falsification**: 在 V 内找到一个任务，使 C_inference 增加 10× 后 error 不下降，且失败原因不能归到 verifier 噪声或 mode-collapse（即 coverage 已饱和）。**当前评估**: medium-strong——Brown / Snell / Wu 三条独立证据线方向一致，但 α/β 跨任务的稳定性还缺一个 Hoffmann-Chinchilla 量级的统一拟合。

这一条与 C-SCALE-1 (horizon-linear estimation floor) 并不矛盾：Ω(H) 是 *训练样本* 的下界，inference scaling 把代价从训练样本搬到推理算力（每个 query 上重复采样 / 长 CoT），同一 horizon-linear 总代价并未消失，只是以 *per-query compute* 形式 amortize 到部署侧。

## Open problems

- 把 Shannon SNR 视角与 superposition / knowledge capacity scaling 统一成一个 SNR-superposition 法则。
- 在 joint-KL Ω(H) 下界条件下，找出可使 estimation error 不再线性增长的额外结构（e.g. local Markov、context compression）。
- 长尾事实的 "频率代理" 度量改良——离开 web-frequency 后该 sigmoid 是否仍成立。
- catastrophic overtraining 的 D\* 是否是 optimizer / LR-schedule artifact——若是，则 C-SCALE-3 应降级为 pseudo。
- summarized-CoT 把 Ω(H) sample-complexity 转成 inference-time compute 的 "等价代价" 是否有 lower bound——即是否存在 "用推理时间换样本量" 的硬上限。

## Cross-links

- [formal_limits](formal_limits.md)：表达力天花板（TC⁰、Deterministic Horizon H\*）与本页 sample-complexity 上界互补。
- [reasoning](reasoning.md)：CoT-faithfulness 的 readout/collapse confound 决定了能否用下游 accuracy 来反推 scaling 曲线的 break。
- [world_model](world_model.md)：open-world dilution 的机制级解释可能就是 C-SCALE-2 的频率-SNR sigmoid 在 entity-level 的特例。
- [online_learning](online_learning.md)：catastrophic overtraining 的 plasticity cliff 与 continual learning 的 plasticity-stability 张力是同一现象的两端。
- [N1 The NTP Question](../samples/N1-the-ntp-question.md)：scaling-limits 是 N1 §"可达性 vs 可学性" 区分的主要证据基底。
