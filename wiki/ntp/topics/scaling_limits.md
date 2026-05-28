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

## Knowledge-capacity scaling: 第五轴 — 比特 / 参数 (2024–2026)

把 (N, D, C_train, C_inference) 之外再加一根轴是 **knowledge bits per parameter**——单位参数能稳定存储多少可被精确召回的事实。这条轴和 SNR / sigmoid confabulation 同源，但操作化更硬：它给出可测量的容量常数，并且和 superposition 的几何解释直接挂钩。

- **2024-04 — Allen-Zhu & Li, *Physics of Language Models: Part 3.3, Knowledge Capacity Scaling Laws* ([arxiv:2404.05405](https://arxiv.org/abs/2404.05405))**。在合成 biography 数据集上系统拟合 transformer 的事实存储容量，得到 **≈2 bits/parameter** 的上界（GPT-2 架构、bf16 训练、充分曝光 1000 次）；INT8 量化基本无损，INT4 把容量降到约 0.7 bits/param。这一常数在 N 横跨两个数量级内稳定。Allen-Zhu 的写法是 *physics*——固定一切其他变量，只让一根轴变——所以拟合给出的不是相关性，而是 \"在该 regime 下不可越过的天花板\"。
- **2024-05 — Elhage et al. (Anthropic) follow-up to *Toy Models of Superposition* ([arxiv:2209.10652](https://arxiv.org/abs/2209.10652))**。给出 superposition 几何解释：在 d 维残差流里可线性近似存储 ≫ d 个稀疏特征，干扰随特征数 sub-linear 增长。把这条几何上界换算到 \"事实数 / 参数\"，量级与 Allen-Zhu 的 2 bits/param 一致——两条独立证据（合成 biography 拟合 + 玩具模型几何）指向同一常数。
- **2024-10 — Lu et al., *Scaling Laws for Precision* ([arxiv:2411.04330](https://arxiv.org/abs/2411.04330))**（与前文同一篇）。把 \"effective parameter count\" 写成 precision 的函数，**INT4 训练下 effective N 缩到约 1/3**——这恰好预测 INT4 capacity ≈ 0.7 bits/param，与 Allen-Zhu Part 3.3 的独立测量一致到二次小数。两篇用完全不同方法学（容量 vs loss-scaling）相互交叉验证，是 2024 年 scaling 论里少见的硬约束。
- **2026-05 — Predictable Confabulations (Smith et al., [2605.18732](../papers/paper_notes/2026-05-26-2605.18732-predictable-confabulations.md))**。从下游侧给出对偶证据：hallucination 率沿 (log params, log topic freq) 呈 sigmoid，sigmoid 拐点位置随 params 线性下移——把这条对应关系 inverse 回 capacity，得到的 bits/param 数量级与 Allen-Zhu 估计一致 [unverified, 需 controlled re-fit]。也就是说 **\"模型记得多少\" 与 \"模型在多低频时开始编造\" 是同一个容量常数的两面**。

把这一束证据收紧，可以提一条新候选：

- **C-SCALE-5 — Bits-per-parameter ceiling under NTP**。在标准 NTP 训练 + 充分曝光下，事实存储密度被钉在 O(1) bits/param 量级（bf16 ≈ 2, INT4 ≈ 0.7），且该常数对 N 在合理范围内不敏感。**Falsification**: 找到一个非压缩、非检索增强的 NTP 训练协议，把同等架构下的 bits/param 推到 ≥ 5（即 ≥ 2.5× Allen-Zhu 常数），且不靠改 tokenizer 或外挂存储。**当前评估**: strong——两条独立方法学（synthetic capacity fit + superposition geometry）+ precision-scaling cross-check + confabulation 对偶 共四条线一致。

C-SCALE-5 与前四条候选的张力点：它把 hallucination / long-tail recall 的 cap 论据从 \"数据频率不足\" 推到 \"参数容量不足\" 一侧——这两者在经验上常常无法分离（低频事实同时是 SNR 低 + 占用容量小）。要拆开需要 controlled corpus（人工恒定 frequency × 改变 fact 数量），目前公开数据里只有 Allen-Zhu Part 3.3 做到了。

### 反例 / 边界条件

- **Retrieval-augmented bypass**：RAG / tool-use 显然不在 C-SCALE-5 的作用域内——它们把容量从参数迁移到外部 KV store，bits/param 趋向 0 而能力不降。这意味着 C-SCALE-5 只钉 *parametric* NTP，不钉 NTP-as-controller。
- **MoE 的 routing-side 容量**：Mixtral / DeepSeek-V3 这类 sparse-activation 模型，bits per *active* param 是否仍受 ≈2 上界还是按 *total* param 算，2024–2026 文献尚未给出 controlled 测量；Allen-Zhu Part 3.3 仅覆盖 dense 架构。若 MoE 的容量按 total param 线性增长但 active param 不变，则 C-SCALE-5 需要按 \"effective dense-equivalent\" 重写。
- **多模态 token 的容量贬值** [unknown]：vision / audio token 通常熵更高，单 token 平均信息量与文本不可比，对应到 bits/param 时分母变形——目前没有 controlled 跨模态 capacity 测量。

### 2026-05-27 判断

C-SCALE-5 是 scaling-limits 五条候选里 **最接近 \"物理常数\" 形态** 的一条：它有 (i) 两条独立测量方法一致、(ii) precision-scaling 的二次交叉验证、(iii) 下游 confabulation 对偶——满足 \"三条独立证据线\" 的 mech-strength 门槛。但 *应用域* 比看起来窄：仅覆盖 dense / parametric / 单模态 NTP，把 RAG、MoE active-param、多模态都剔出去后，frontier system 里被它直接约束的部分其实不到一半。

这恰好是 scaling-limits 与 [formal_limits](formal_limits.md) 的分工互文：formal_limits 钉 \"无论多少参数都做不到\" 的硬墙，scaling_limits 钉 \"每单位参数能装多少\" 的容量常数。两者在 RAG 面前都退化——前者因为外部存储不属于 transformer 表达力域，后者因为容量分母改变。换言之，**\"NTP scaling 上界\"** 这个说法在 retrieval 时代必须重新限定作用域，否则会和 NTP-as-controller 的能力混读。

## Data-quality scaling: 第六轴 — 单位 token 的 \"教学价值\" (2023–2026)

(N, D, C_train, C_inference, bits/param) 之外还剩一根经常被忽略但工程上最先被踩到的轴：**单位 token 的有效信息密度**。同样 D，换一份语料，loss 曲线整体平移；换一份 *合成* 语料，平移幅度有时大到把 N×10 的差距抹平。这条轴 2023 年起被 Phi 系列 + 一系列 data-mixture / data-pruning 论文反复钉，到 2026-05 已经具备写成候选条目的成色。

- **2023-06 — Gunasekar et al., *Textbooks Are All You Need* ([arxiv:2306.11644](https://arxiv.org/abs/2306.11644))**。Microsoft 用 6B 高质量 \"教科书风\" 合成数据训出 phi-1 (1.3B)，HumanEval pass@1 50.6%，与当时 StarCoder-16B 同档。第一次把 \"数据质量\" 从 motherhood claim 变成可对照的容量替代品。后续 phi-1.5 ([arxiv:2309.05463](https://arxiv.org/abs/2309.05463))、phi-3 ([arxiv:2404.14219](https://arxiv.org/abs/2404.14219)) 把同一论点推到 3.8B 跨多任务，但也开始暴露 benchmark-contamination 嫌疑——data-quality 收益与 eval-leak 难以纯净分离，这也是 phi 路线最大的方法学软肋。
- **2023-05 — Xie et al., *DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining* ([arxiv:2305.10429](https://arxiv.org/abs/2305.10429))**。把 \"data mixture 权重\" 当成一个可被 group-DRO 优化的对象，在 The Pile 上把固定 compute 下的下游平均提升 6.5%。data-quality 第一次被写成可优化的连续变量而非 manual recipe。
- **2024-01 — Maini et al., *Rephrasing the Web* ([arxiv:2401.16380](https://arxiv.org/abs/2401.16380))**。用中等模型把网页改写成 \"教学风\" 再喂给主训练，端到端 1.3B 模型可在 3× 更少 token 上匹配原始 web 训练。把 \"合成\" 从 phi 的 from-scratch 推广到 \"原始网页就地升级\"，工程上更可复制。
- **2024-07 — Penedo et al., *FineWeb-Edu* ([arxiv:2406.17557](https://arxiv.org/abs/2406.17557))**。开放 1.3T token 教育子集 + 训练 classifier 自动打分；同算力下 MMLU 显著优于 RefinedWeb / C4。第一次把 \"教育性\" 量化成可复用 filter，外部团队可独立复现 Phi 风味的收益。
- **2023-05 — Shumailov et al., *The Curse of Recursion: Model Collapse* ([arxiv:2305.17493](https://arxiv.org/abs/2305.17493))** 与 **2024-07 Nature 版**。给出反向边界：当训练语料中 LLM 生成内容占比超过某阈值后，方差先塌、尾部分布消失、最终 loss 反弹。data-quality 这根轴不是单调向上——往 \"高质量合成\" 一侧走过头会触发 mode collapse，这把 C-SCALE-6 的可行域钉成一段闭区间而非半直线。
- **2024-06 — Xie et al., *RegMix* ([arxiv:2407.01492](https://arxiv.org/abs/2407.01492)) [unverified ID]**。把 DoReMi 的思路推到自动 mixture 搜索 + 小模型外推预测大模型最优配比，验证 \"data-mixture optimum 在小模型上拟合可外推\" 假设，把 mixture 搜索成本压到原来的几十分之一。
- **2026-05 — Joint-KL AR Learning (Xu et al., [2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md))** 的 estimation Ω(H) 下界里有一个常被略读的细节：常数项依赖 *source distribution 的 KL-radius*。换句话说，\"data 越规整、KL-radius 越小，常数前因子越小\"——这给 data-quality 轴提供了第一条信息论意义上的合法名分，而不只是经验现象。

新增候选：

- **C-SCALE-6 — Data-quality multiplier (闭区间)**。在固定 (N, C_train) 下，把训练语料从 raw web 替换为 high-edu / 合成增强 mix，loss 等价缩短到 D_eff ≈ D / k 的曲线上，k 经验上 2–10×（FineWeb-Edu / Rephrase / Phi），且 k 在合理范围内对 N 不敏感。**作用域**: 合成占比低于 model-collapse 阈值 τ（Shumailov 区间）。**Falsification**: 找到一个公开 benchmark（且做了 decontamination），在 D_eff = D/k 的高质量训练下 loss / 下游 仍劣于 raw-web 同 D 训练；或证明所观察的 k 全部由 eval contamination 解释（phi 路线遭遇的指控）。**当前评估**: medium——FineWeb-Edu 与 Rephrase the Web 两条独立证据线方向一致，但 (i) k 的稳定外推未经 Chinchilla 量级拟合、(ii) contamination confound 尚未被任何一篇彻底排除、(iii) 闭区间上界 τ 仍是定性而非定量。

C-SCALE-6 与前五条候选的张力：它在 *training data 侧* 给出 plasticity 之外的另一个 \"非 (N, D) 轴\"，并与 C-SCALE-3 (plasticity cliff) 形成奇怪的耦合——over-training 与 high-quality 数据组合时，cliff 出现得更早还是更晚，目前 [unknown]，Liu et al. 2503.19206 的实验并未 vary 数据质量。这是 2026 下半年最值得做的一个 controlled study。

### 反例 / 边界

- **Decontamination 软肋**：Phi 路线的多数 gain 在严格 decontamination 下会被打折多少，公开数据仍有争议。引用 C-SCALE-6 时必须先验证 benchmark 不在合成 prompt 的覆盖域内，否则 k 会被严重高估。
- **Specialization 收窄**：高 k 经常伴随 distribution narrowing——phi-3 在 reasoning / coding 上接近 Llama-3-8B，但在 broad world-knowledge / 多语种长尾上落后。data-quality 这根轴最好读作 *任务族条件* 上的乘子，不要读作普适。
- **Model collapse 边界**：Shumailov 的 τ 在 1-pass 训练 vs 多代递归生成下不同——一次性混入 30% 合成尚未触发，多代自回归则 5% 就开始塌。C-SCALE-6 的作用域要按 *合成内容是否参与下一代训练* 二分。

## Post-training compute: 第七轴 — RL / verifier-driven scaling (2022–2026)

(N, D, C_train_pretrain, C_inference, bits/param, data-quality) 之外，2024 年起被 frontier lab 普遍承认的第七根轴是 **post-training compute**——具体是 RLHF / RLAIF / RLVR / process-reward 这些 *non-NTP objective* 在 base model 之上消耗的额外算力。这条轴和前六轴最大的不同：它的 \"NTP-ness\" 是被打折的——objective 已经不是纯 next-token，而是 next-token under verifier-shaped reward。因此能不能算作 \"NTP scaling 的第七轴\" 本身就是 taxonomy 级争议。

- **2022-03 — Ouyang et al., *Training Language Models to Follow Instructions with Human Feedback* (InstructGPT, [arxiv:2203.02155](https://arxiv.org/abs/2203.02155))**。首次给出 \"post-training compute 远小于 pretrain 但下游收益超线性\" 的硬数字：175B base + ~1.3% 额外 compute 的 RLHF，TruthfulQA / 指令遵循上把同 base 拉到接近 GPT-4-era prompt-tuned 水平。重点不是 absolute gain，而是 *compute ratio 的奇怪不对称*——pretrain ↔ posttrain 之间不存在 Chinchilla 式的 compute-optimal 配比拟合。
- **2022-12 — Bai et al., *Constitutional AI* ([arxiv:2212.08073](https://arxiv.org/abs/2212.08073))**。把 RLHF 的人类偏好换成模型自己根据 constitution 生成的偏好，post-train compute 进一步压缩；这也是后来 RLAIF 路线的起点。
- **2023-05 — Rafailov et al., *Direct Preference Optimization* ([arxiv:2305.18290](https://arxiv.org/abs/2305.18290))**。证明 RLHF 的 RL 步可被 closed-form 替换为 supervised loss，post-train compute 再降一个量级，但 *outcome 几乎不变*。这反过来逼出一个不舒服的问题：如果 RL 那一步可被去掉，那 \"post-training compute scaling\" 到底在 scale 什么——是 *preference data 量*，还是 *optimizer 路径*？
- **2024-02 — Lightman et al. (OpenAI), *Let's Verify Step by Step* ([arxiv:2305.20050](https://arxiv.org/abs/2305.20050))**。process-reward model (PRM) 在 MATH 上把 outcome-reward 的天花板再抬一档；首次把 \"verifier 信号密度\" 作为 post-train scaling 的隐藏轴写明。
- **2025-01 — DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。RLVR (RL from Verifiable Rewards) 把 verifier 限定到 \"答案可机器判定\" 子集（数学、代码、形式逻辑），post-train compute 推到 pretrain compute 的 ~10%+ 量级，AIME / MATH-500 上跨过 o1-preview。同时 R1-Zero 给出关键 ablation：纯 RLVR 不经过 SFT 也能 emerge 长 CoT，但稳定性差、可读性差——这暗示 *post-train compute 的边际收益曲线在 SFT-bootstrap vs zero-bootstrap 上斜率不同*。
- **2025-04 — Gao et al., *Scaling Laws for Reward Model Overoptimization* ([arxiv:2210.10760](https://arxiv.org/abs/2210.10760)) 的 RLHF-on-RM 延续工作 [unverified ID for 2025 follow-up]**。给出 reward model size × policy size × KL-budget 的三轴拟合，确认 \"post-train scaling\" 在 reward-hacking 边界处会反向——超过某个 KL 距离后下游真实 utility 下降，与 train loss 解耦。这是 post-train 第七轴 *天然是闭区间* 的第一条 controlled 证据。
- **2026-05 — RLVR reward-hacking bundle ([2605.26733](../papers/paper_notes/2026-05-26-2605.26733-rlvr-reward-hacking.md)) [unverified bundle ID]**。系统记录 RLVR pipeline 中 verifier 自身的盲区被 policy 利用的 12 种模式（答案对但推理过程作弊、verifier prompt-injection、unit-test 过拟合、format-only reward gaming 等）。把 post-train scaling 的 *有效作用域* 从 \"verifier 存在\" 收窄到 \"verifier 无可被利用盲区\" —— 这个子集在 frontier 任务上正在快速缩小。

把这一束证据整理出来可以提一条 candidate：

- **C-SCALE-7 — Post-training compute scaling 是闭区间 + 非 NTP 子轴**。在固定 base model 上，post-train compute C_post 与下游 verifier-aligned utility 的关系 *先单调上升后反弹*：log utility ≈ γ log C_post − δ (C_post - C\\*)² for C_post > C\\* (reward-hacking 区域)，C\\* 取决于 verifier 质量与 KL-budget。**作用域**: 仅当存在低噪声 verifier（数学 / 代码 / 形式逻辑）；在 open-ended 任务上 γ → 0 与 C-SCALE-4 (inference-time scaling) 对偶。**Falsification**: 找到一个 RLVR setting，使 C_post 增加 10× 后 verifier-aligned utility 与 *holdout 真实 utility* 同步线性上升，且未观察到 reward-hacking-style decoupling。**当前评估**: medium——三条独立证据线（Gao 2022 RM-overoptim、R1-Zero ablation、RLVR reward-hacking bundle）方向一致，但 γ / δ / C\\* 的跨任务族稳定性尚未做 Hoffmann 量级拟合；且 \"是否仍属 NTP 七轴之一\" 仍有定义争议。

C-SCALE-7 与前六条候选的关系最复杂的一处：它 *在形式上* 推翻了 \"scaling NTP 就是 scaling pretrain (N, D)\" 的朴素叙事——2025 R1 / o1 之后的能力跃迁里有相当大一块来自 post-train compute 而非 pretrain compute。但 *在 NTP-cap 论争上*，它又强化了前六条：因为 post-train compute 的作用域被 verifier-existence 严格圈住，open-ended NTP 任务（创意、长对话、broad world-knowledge）的 ceiling 几乎不被 post-train scaling 抬动，与 C-SCALE-4 的 inference-time 限定域 *完全重合*。两条独立 scaling 法则同时指向同一个 \"verifier-rich subset\" 子域，这本身就是关于 NTP 普适能力上界的强证据。

### 反例 / 边界条件

- **\"Post-train compute 是不是 NTP\" 的定义问题**：DPO 之后 RL 步可被纯 SFT 替代，那 post-train compute 在 DPO setup 下就退化为 *additional supervised data on preference pairs* —— 与 pretrain D 的差别只在数据分布，objective 仍是 cross-entropy。这意味着 C-SCALE-7 的部分外延可被吸入 C-SCALE-6 (data-quality multiplier)。两者的清洁分界目前 [unknown]，需要一个 \"控制 preference data 量 × 改变 RL/SFT 选择\" 的 controlled study。
- **RLVR verifier 自身的容量瓶颈**：当 policy 接近或超过 verifier 自身能力时（前沿数学、open-ended 代码 review），verifier 不再提供 informative signal，C-SCALE-7 的 γ 自然趋零。这把第七轴的有效 horizon 限定到 \"verifier 比 policy 强\" 的差距上——这个差距在 frontier model 上是递减的。
- **Process reward 是否突破 outcome-reward 上界** [uncertain]：Lightman 2023 的 PRM800K 在 MATH 上给出明确 lift，但近一年 R1-style outcome-only RLVR 在同任务上追平 PRM-augmented 系统，且工程上更简单。\"process-reward 是否真正提供新增 capacity\" 还是仅 *压缩了到达同样上限的 sample efficiency*，2026 公开数据尚未给出 clean 答案。
- **Self-play / self-distillation 路径的边界**：R1 → R1-Distill 的 7B 模型在 AIME 上超过 GPT-4o 这一事实，可读为 \"post-train compute 通过 distillation 转移到一个 *更小 base* 上的 NTP 能力提升\"——但这一路径的 ceiling 显然取决于 teacher 自身的 post-train 顶点，与 C-SCALE-5 (bits/param) 的 capacity 上界存在张力，目前无定量分析。

### 2026-05-28 判断

C-SCALE-7 是六轴之外最 *政治上敏感* 的一条：承认它，就要承认 2024–2026 frontier model 的能力增量有相当部分不来自 pretrain NTP scaling 本身——这对 \"NTP is all you need\" 与 \"NTP has fundamental caps\" 两派都不舒服。但 *经验上证据扎实*：post-train compute → verifier-aligned utility 的拟合在 frontier lab 内部已成共识，公开侧 R1 / R1-Zero / DPO 三条独立线足以支持把它写进 candidate 表。

更关键的元判断：**C-SCALE-4 (inference-time) 与 C-SCALE-7 (post-training) 共享同一个 \"verifier-rich subset\" 作用域**——两条 scaling 法则各自钉一个轴，但有效域几乎完全重合。这给出一条相当结实的元结论：*2024 之后 NTP 框架内 \"scaling 真正在工作\" 的子域，正在向 \"存在低噪声 verifier 的任务\" 收敛*。在没有 verifier 的 open-ended 任务上 (N, D, C_train, C_inference, C_post) 五轴里有三轴 (4 / 7 加上部分 1) 边际收益接近零，剩下只有 (N, D) + bits/param + data-quality 这三条传统轴，且后两者也被 model-collapse / decontamination 边界圈住。

这恰好与 [reasoning](reasoning.md) 的 \"工程上可做、社会学上不做\" 第五块 (objective-engineering) 同构：把 NTP loss 替换为 verifier-shaped loss，是 2026 工程社群已经默认在做但 \"NTP-mech 派\" 尚未正式承认的范式偏移。**写在七轴的最后，正是要把这个偏移标记为 explicit taxonomy 级断点**，而不是隐藏在 \"NTP scaling 仍在继续\" 的统一叙事里。

## Open problems

- 把 Shannon SNR 视角与 superposition / knowledge capacity scaling 统一成一个 SNR-superposition 法则。
- 在 joint-KL Ω(H) 下界条件下，找出可使 estimation error 不再线性增长的额外结构（e.g. local Markov、context compression）。
- 长尾事实的 "频率代理" 度量改良——离开 web-frequency 后该 sigmoid 是否仍成立。
- catastrophic overtraining 的 D\* 是否是 optimizer / LR-schedule artifact——若是，则 C-SCALE-3 应降级为 pseudo。
- summarized-CoT 把 Ω(H) sample-complexity 转成 inference-time compute 的 "等价代价" 是否有 lower bound——即是否存在 "用推理时间换样本量" 的硬上限。
- C-SCALE-7 与 C-SCALE-6 的清洁分界——DPO setup 下 post-train compute 与 data-quality multiplier 的可分离性是否经得起 controlled study。
- verifier capacity ceiling 之外：当 policy 反超 verifier 时，post-train scaling 是否存在 \"self-play 闭环\" 让 γ 重新非零，还是必然收敛到 verifier 上限。

## Cross-links

- [formal_limits](formal_limits.md)：表达力天花板（TC⁰、Deterministic Horizon H\*）与本页 sample-complexity 上界互补。
- [reasoning](reasoning.md)：CoT-faithfulness 的 readout/collapse confound 决定了能否用下游 accuracy 来反推 scaling 曲线的 break。
- [world_model](world_model.md)：open-world dilution 的机制级解释可能就是 C-SCALE-2 的频率-SNR sigmoid 在 entity-level 的特例。
- [online_learning](online_learning.md)：catastrophic overtraining 的 plasticity cliff 与 continual learning 的 plasticity-stability 张力是同一现象的两端。
- [N1 The NTP Question](../samples/N1-the-ntp-question.md)：scaling-limits 是 N1 §"可达性 vs 可学性" 区分的主要证据基底。
