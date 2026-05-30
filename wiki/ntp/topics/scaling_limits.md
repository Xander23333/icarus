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
- **Latent-prediction SSL 在 PCFG 上抹掉 exp(Ω(L)) sample complexity (Korchinski-Favero-Wyart, [2605.27734](https://arxiv.org/abs/2605.27734), 2026-05)**：在 depth-L probabilistic context-free grammar 世界类下，作者形式化证明 *token-level* supervised / SSL 的 sample complexity ≥ exp(Ω(L))，而 *latent-prediction* SSL (沿 JEPA 路线，预测 grammar 内部 latent token 而非 surface token) 的 sample complexity ≤ O(1) wrt L。把这个结果**字面**贴到 C-SCALE-1 的 falsifier 上，似乎构成一次直接命中：存在 "非平凡任务族 + 不靠外部状态压缩的算法"，使 KL-estimation error 在深度轴上不再线性增长。但强度限定有四处必须先卡死才能谈是否动 C-SCALE-1 评估：(i) C-SCALE-1 的可证伪条款 **以 horizon H (token 距离) 为自变量**，KFW 的分离 **以 grammar depth L 为自变量**——同一 token horizon 下若树深固定，分离并不直接外推到 H↑；(ii) Joint-KL Xu et al. ([2605.12316](../papers/paper_notes/2026-05-26-2605.12316-joint-kl-autoregressive.md)) 的 Ω(H) 下界明示 *常数项依赖 source distribution KL-radius* (见第六轴末段)，PCFG 是 KL-radius 极小的退化族 (latent 结构完全 known)，所以 KFW 的 O(1) 是 **常数前因子塌缩** 而非 **H 线性项消失**——两件不同事；(iii) latent-prediction SSL 把训练目标从 NTP cross-entropy 换成 latent-target prediction，**已不在 C-SCALE-1 的 "NTP estimation error" 作用域**，与 Sorscher data pruning 离开 i.i.d. 假设 / Brösamle-Eckstein 把代价 amortize 到推理三条 "反例" 同型——全都走的是 **限定作用域而非穿透命题** 的路径；(iv) 从 PCFG 世界类到 frontier 自然语言的迁移仍需 ≥1 个 controlled experiment (典型 7B+ scale × 自然语料 × token vs latent objective 在 *同 token 量 + 同 optimizer + 同 LR-schedule* 下对齐) 才能从 *世界类内分离* 升级为 *NTP 通用上界突破*，2026-05 公开材料下此实验 0/1 (Assran/LeCun JEPA 系列与 LeJEPA [2605.* unverified bundle] 在自然语料侧仅给 representation 质量曲线，未给 NTP cross-entropy 对照)。综上 C-SCALE-1 主条款 *不动* (仍 strong，仍 horizon-linear)，但 falsifier 第一句 "找到非平凡任务族 + 无外部状态压缩的算法" 应反向收紧为 "**且训练目标仍是 token-level NTP cross-entropy / 且自变量是 token horizon H 而非世界类深度 L / 且 source KL-radius 未被先验塌缩**" 三轴齐平——把 KFW 类结果统一归入 *换 objective / 换自变量 / 换世界类先验* 三个 "逃逸通道" 而非 falsifier 触发。这条 reviewer 限定与 [`formal_limits`](formal_limits.md) §表达力 vs 可学性 (第二堵墙) 节末段 2026-05-30 KFW anchor (C-FORM-4 evidence-base 第三 anchor) 同源，并与 [`world_model`](world_model.md) §JEPA 可辨识性节 KFW 落点 (C-WM-5 evidence-base 第二支柱) 形成 *三 topic 共享同一 anchor、各自作用域不同* 的横向加密——formal: expressivity vs learnability 缝；world_model: JEPA 可辨识性的 sample-complexity 旁证；scaling: C-SCALE-1 falsifier 作用域注解。属 12 天冻结协议 (2026-05-30→2026-06-10) *互引补充 + falsifier 收紧* 白名单两类，*不* 开新 sub-candidate / corollary / route-elim，*不* 改 C-SCALE-1 strong 评估，*不* 改 §D 轴 / 第六轴主文。

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

> **(2026-05-28 同步注)** 本节 C-SCALE-7 已正式登记为 [`survey/taxonomy.md`](../survey/taxonomy.md) candidate snapshot 第 C7 行 (边界 NTP-mech 候选, taxonomy 级争议) 与 [`survey/ntp_survey.md`](../survey/ntp_survey.md) §10 C7 条目；同表新增 C-SCALE-6 (data-quality multiplier) 作为 NTP-cap sibling 入升降级历史日志但不入主候选表。三处同步符合 taxonomy 末段规则。

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

**2026-05-30 evidence-base 补丁 — DCV (2605.28860) 作为 C-SCALE-7 *mechanism 侧* 第二条旁证 (RM-overoptim 之外)**：Rojas Nunez 等 *Mechanistic origins of catastrophic forgetting: why RL preserves circuits better than SFT?* ([2605.28860](../papers/paper_notes/2026-05-30-2605.28860-rl-vs-sft-circuit-preservation.md)) 在 Qwen2.5-3B-Instruct + scientific-QA adaptation 上引入 *differential circuit vulnerability* (DCV, head-level circuit attribution 在 fine-tune 前后变化度量) 报告 RL (policy-gradient) 相对 SFT 在 head-level circuit overlap 上 *显著* 更高。这条结果的 C-SCALE-7 维度相关性在于：post-train compute → verifier-aligned utility 的 *先单调上升后反弹* 拟合一直只在 *宏观 loss / 下游 metric* 层有证据 (Gao 2022 RM-overoptim 三轴拟合 + R1-Zero ablation + RLVR reward-hacking bundle 三条均落在 outcome 层); DCV 第一次在 *head-level 子空间* 给出 *RL 与 SFT 在 base support 改写程度上分离* 的 mechanistic 证据——把 C-SCALE-7 \"post-train compute 在 verifier-rich subset 上抬升 utility\" 的论断 *方向上* 加固一档 (RL 优化器在 prior circuit 上 footprint 小, 意味着 post-train compute 的 *边际 utility 增量* 较少被 \"破坏既有 NTP base capacity\" confound, 与 §第七轴判断 \"open-ended 任务 γ → 0\" 同向)。但 *强度限定四处必须先卡死*: (i) DCV 是 *mechanism 候选解释方向* 旁证, *不* 进入 C-SCALE-7 evidence-base 主表 — 主表三条 (RM-overoptim / R1-Zero / RLVR reward-hacking) 全部 outcome 层, DCV 与之 *度量空间不同* 但 *归因独立性弱*: DCV 与 final-task accuracy 高度相关, \"RL 学少了 → 在 prior circuit 上 footprint 也少 → DCV 低\" 同义反复假设需 same-accuracy controlled comparison 排除 (paper Reviewer 已自承未做); (ii) 3B + 单一任务 (scientific QA) 与 C-SCALE-7 期待的 frontier-scale × verifier-rich subset (R1 7B–671B × MATH/AIME/Codeforces) 相差两档, 不能直接外推 reward-hacking 拐点 C\\* 的具体位置; (iii) DCV 测的是 *static circuit preservation*, 不直接测 *verifier-shaped objective 是否在 KL-budget 边界处反向 decoupling* — 与 C-SCALE-7 拟合的 *先单调上升后反弹* 的 *反弹* 段无直接对应 (反弹段需要 reward-hacking 的 dynamic 度量, 不是 static circuit overlap); (iv) DCV 与 reasoning §C-REAS-7 evidence-base 主表 / online_learning §C-CONT-2 第三支柱 / grounding §C-GROUND-PROTO 训练面 anchor 共享同一 paper, *跨 topic 引用同一 evidence 时按单一证据源 × 四投影处理* (与 §10 M1 集合 $m_5$ 主投影 / 横向 corollary 区分同型), 不算 C-SCALE-7 *独立* 第四 anchor。综上 C-SCALE-7 主条款 *不动* (仍 medium, 仍闭区间 + 非 NTP 子轴), evidence-base 主表 *不动* (仍 RM-overoptim / R1-Zero / RLVR reward-hacking 三条 outcome 层); 仅在 *mechanism 侧旁证* 维度从 0 → 1 (DCV 第一条), 与 §第七轴判断尾段 \"post-train compute 的边际收益曲线在 SFT-bootstrap vs zero-bootstrap 上斜率不同\" 的 ablation 经验形成 mech 层对偶 — 前者 (R1-Zero ablation) 是 *outcome 层斜率* 证据, 后者 (DCV) 是 *base support 改写程度* 证据, 二者方向一致但通道独立。

互引 (单向, 不反向要求 reasoning / online_learning / grounding 回贴 — 与 causality.md 2026-05-30 09:00Z tick *one-way reference* 协议同型): DCV 作 C-SCALE-7 *mechanism 侧旁证*, 服务 *与 SFT-bootstrap vs zero-bootstrap 斜率差* 的 base-support-改写程度同向加固, 但 *不* 改 C-SCALE-7 falsification 文字 (\"找到一个 RLVR setting 使 C_post 增加 10× 后 verifier-aligned utility 与 holdout 真实 utility 同步线性上升且未观察到 reward-hacking-style decoupling\" 仍是 *outcome 层* falsifier; mechanism 侧 falsifier 由 reasoning §C-REAS-7 evidence-base 第 N 支柱 / online_learning §C-CONT-2 falsifier (d) 承担, 不在 C-SCALE-7 范围内重复定义)。引用方向: [reasoning.md §C-REAS-7 evidence-base 补丁 (commit `934a03c`)](reasoning.md) 与 [online_learning.md §反例 节 C-CONT-2 第四支柱 (commit `1b98eab`)](online_learning.md) 与 [grounding.md §C-GROUND-PROTO 方向性动作 (3) (commit `f611a01`)](grounding.md) 三处已先把 DCV 收编为 *优化器侧 mechanistic 旁证*, 本 scaling 域引用是把同一 anchor 沿 *post-train compute 的 base-support 改写程度* 这条第四独立维度回贴到 C-SCALE-7 框架内, 与 reasoning (RLVR transfer 维度) / online_learning (catastrophic forgetting 维度) / grounding (training-face probe 对偶维度) 三处 *作用域正交*。严守 2026-05-30 → 2026-06-10 *12 天增条冻结协议* 白名单 *evidence-base refinement + 互引补充* 两类, **不** 新增 C-SCALE-9, **不** 升级 C-SCALE-7 强度 (medium 不变), **不** 改 §第七轴 反例/边界条件 既有四条 (DPO 定义吸收 / verifier 容量瓶颈 / process reward 突破 / self-distill 路径), **不** 进 §10 主候选表, **不** 入 taxonomy 升降级历史日志 — 仅在本节 evidence-base 维度补一个 *mechanism 侧旁证* 第二 anchor (前 anchor: Gao 2022 RM-overoptim 在 *outcome 层斜率反弹* 维度)。

判断: C-SCALE-7 之前最脆弱的攻击线是 \"post-train compute → utility 的拟合在 frontier-scale 上是否仍由 verifier-existence 严格圈住, 还是会被 RL 优化器在 base support 上 *广义破坏* 所稀释\" — 朴素直觉是 RL 与 SFT 一样会改写 base mode, 因此 post-train compute 的 utility 增量必须扣除 \"base NTP 能力 forgetting\" 这一负贡献; DCV *方向上* 削弱这一稀释假设 (RL 在 head-level 上 footprint 显著小于 SFT), 让 C-SCALE-7 拟合的 *单调上升段* 在 mechanism 层更接近 \"verifier-shaped objective 选择性 re-weight 既有 circuit\" 而非 \"verifier-shaped objective 同时 re-weight + 广义改写 base support\"。但这条加固在 3B + 单任务 + same-accuracy 控制缺三层限定下 *仅* 把 C-SCALE-7 评估从 medium → medium-strong 的升级路径从 \"需要 frontier 公开 retention 曲线 + RL/SFT controlled comparison\" 收紧为 \"还需 same-accuracy 控制下 head-level circuit overlap 比较\" — 升级阈值变高, 升级方向不变。下一次本节实质性更新最可能来自 (α) 7B+ scale × verifier-rich subset × RL/SFT same-accuracy controlled circuit overlap 比较公开报告 (中等概率, 12–18 月窗口); (β) frontier lab 公开 RLVR pipeline 在 KL-budget 边界处 base capacity retention 曲线 (低概率, 与 M1 集合 $m_1$ retention disclosure 缺位同型); (γ) Gao 2022 RM-overoptim 拟合在 RL-preserves-circuits regime 下 reward-hacking 拐点 C\\* 是否右移的复现实验 (低概率, 需要 controlled compute budget 横评)。

### 2026-05-28 判断

C-SCALE-7 是六轴之外最 *政治上敏感* 的一条：承认它，就要承认 2024–2026 frontier model 的能力增量有相当部分不来自 pretrain NTP scaling 本身——这对 \"NTP is all you need\" 与 \"NTP has fundamental caps\" 两派都不舒服。但 *经验上证据扎实*：post-train compute → verifier-aligned utility 的拟合在 frontier lab 内部已成共识，公开侧 R1 / R1-Zero / DPO 三条独立线足以支持把它写进 candidate 表。

更关键的元判断：**C-SCALE-4 (inference-time) 与 C-SCALE-7 (post-training) 共享同一个 \"verifier-rich subset\" 作用域**——两条 scaling 法则各自钉一个轴，但有效域几乎完全重合。这给出一条相当结实的元结论：*2024 之后 NTP 框架内 \"scaling 真正在工作\" 的子域，正在向 \"存在低噪声 verifier 的任务\" 收敛*。在没有 verifier 的 open-ended 任务上 (N, D, C_train, C_inference, C_post) 五轴里有三轴 (4 / 7 加上部分 1) 边际收益接近零，剩下只有 (N, D) + bits/param + data-quality 这三条传统轴，且后两者也被 model-collapse / decontamination 边界圈住。

这恰好与 [reasoning](reasoning.md) 的 \"工程上可做、社会学上不做\" 第五块 (objective-engineering) 同构：把 NTP loss 替换为 verifier-shaped loss，是 2026 工程社群已经默认在做但 \"NTP-mech 派\" 尚未正式承认的范式偏移。**写在七轴的最后，正是要把这个偏移标记为 explicit taxonomy 级断点**，而不是隐藏在 \"NTP scaling 仍在继续\" 的统一叙事里。

## 第八轴候选：Synthetic / self-generated data scaling (2023–2026)

> **(2026-05-28 新增, 候选状态)** 本节属于 *尚未稳定登记* 的第八轴提案。与 C-SCALE-6 (data-quality multiplier) 的分界尚未做 controlled study，因此暂只在本页 candidate 区登记为 C-SCALE-8 (proposed)，不向 [`survey/taxonomy.md`](../survey/taxonomy.md) 与 [`survey/ntp_survey.md`](../survey/ntp_survey.md) §10 同步, 等下一轮 controlled study 出现再决定是否升入主表或作为 C-SCALE-6 sub-candidate 入升降级历史日志。

2023 年起，frontier lab 之间逐渐形成一条 *与 (N, D, C\_train, C\_inference, bits/param, data-quality, C\_post) 七轴正交* 的新经验线：把 D 的一部分（甚至大部分）换成由 *模型自己或更强模型生成* 的 token，scaling 曲线在某些任务族上不仅没塌，反而更陡。把它单列为第八轴还是吸入第六轴 (data-quality) 是 2026 年仍在打的官司。下面把公开侧最硬的几条证据按时间排开：

- **2022-12 — Wang et al., *Self-Instruct: Aligning Language Models with Self-Generated Instructions* ([arxiv:2212.10560](https://arxiv.org/abs/2212.10560))**。175 条人写 seed instruction → 52K 条 GPT-3 自生成 instruction，在 SuperNI 上把 GPT-3 base 推到接近 InstructGPT-001 水平。第一条把 "自生成数据 ↑ 下游 NTP-aligned utility" 写得干净的论文。但这条工作里 *生成器 ≥ 学生*，与后来的 self-distillation 不同。
- **2023-05 — Eldan & Li, *TinyStories: How Small Can Language Models Be and Still Speak Coherent English?* ([arxiv:2305.07759](https://arxiv.org/abs/2305.07759))**。给 GPT-3.5/4 写一个限定词表的小说生成 prompt，得到几亿 token 的纯合成 corpus，~30M 参数的小模型在该 corpus 上从零训练即可生成语法、语义、因果一致的短篇。这把 "合成 token 在何种粒度上替代自然 token" 的下界压到了 *parameter-count × token-count 比传统 Chinchilla 配比小一到两个量级* 的区域。
- **2023-06 — Gunasekar et al., *Textbooks Are All You Need* (Phi-1, [arxiv:2306.11644](https://arxiv.org/abs/2306.11644)) → Phi-1.5 ([arxiv:2309.05463](https://arxiv.org/abs/2309.05463)) → Phi-3 ([arxiv:2404.14219](https://arxiv.org/abs/2404.14219)) → Phi-4 ([arxiv:2412.08905](https://arxiv.org/abs/2412.08905)) 系列**。把 *GPT-4 生成的 "教科书风格" 合成 corpus* 当作主要训练 D，Phi-4 在 ~14B 参数上 MMLU/GPQA 接近同期 70B 自然 corpus 模型。Phi 系列是把第八轴推到极端的样本——他们的 effective D 几乎完全 *out-of-distribution* 于 CommonCrawl 自然 token。
- **2024-01 — Maini et al., *Rephrasing the Web (WRAP)* ([arxiv:2401.16380](https://arxiv.org/abs/2401.16380))**。把 CommonCrawl 用 instruction-tuned LM 改写成 \"维基百科风格 / QA 风格 / 诗歌风格\" 的并列 corpus，pretrain 收敛速度 3× 且下游 zero-shot 同样有 lift。关键是 *改写后的 token 与原 token 在 KL 距离上接近*，把第八轴与第六轴 (data-quality) 的边界推到了灰区。
- **2024-05 — Yuan et al., *Self-Rewarding Language Models* ([arxiv:2401.10020](https://arxiv.org/abs/2401.10020))**。模型自己当 judge + 自己生成 preference pairs + 自己 DPO，三轮迭代后 AlpacaEval 2 win-rate 从 9.94% → 20.44%，*在没有外部 verifier 与人类标注的前提下 NTP-aligned utility 仍单调上升*。这条线最有意思的地方是把第八轴和第七轴 (post-training compute) 显式耦合：generator 与 verifier 都是同一个网络在不同 checkpoint 上的版本。
- **2024-07 — Shumailov et al., *AI Models Collapse When Trained on Recursively Generated Data*, *Nature* ([arxiv:2305.17493](https://arxiv.org/abs/2305.17493) 期刊版)**。把第八轴的 *硬上界* 写明：当 D 中合成 token 比例 → 1 且无 anchor 到真实分布时，多轮递归训练后 tail probability mass 系统性丢失，KL(model‖truth) 单调发散。这条结果常被 \"模型自吃尾巴必崩\" 派引用，但 Phi-4 与 R1-Distill 的存在说明现实工程上 *有锚 + 有过滤* 的 mixed regime 与 Shumailov 的 pure-recursive setup 不同型，二者不直接矛盾。
- **2025-01 — DeepSeek-R1-Distill 系列 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948) §4)**。R1 推理轨迹（数学、代码、形式逻辑 CoT）作为 distillation D 训练 7B/14B/32B Qwen/Llama base，AIME-2024 上 7B 学生超过同期 GPT-4o (~70B+ assumed) base。这是 2025 年最干净的 "*合成 reasoning token 作为 D 比自然 reasoning token 价值高 *一个量级*" 的公开数据点——而且 student < teacher 的方向使其与 Self-Instruct 类型 *根本不同*。
- **2023-12 — Burns et al. (OpenAI), *Weak-to-Strong Generalization* ([arxiv:2312.09390](https://arxiv.org/abs/2312.09390))**。反方向的边界：用 *弱模型生成的 label* 训练 *强模型* 时，强模型在 NLP 任务上能恢复弱→强 gap 的 ~20–70%，但在 reward modeling / chess puzzles 等任务上恢复率显著更低。这条结果给第八轴划出 *teacher quality 与 student capacity 的 generalization gap* 这条暗轴——合成 D 的价值不是 D 本身的属性而是 (teacher, student, task) 三元函数。

把这一束证据整理为 candidate：

- **C-SCALE-8 (proposed) — Synthetic / self-generated data 是 D 的 *origin* 维度而非 quality 维度，与 C-SCALE-6 正交**。在 D\_synthetic / D\_total 这一新变量上，下游 NTP-aligned utility 随比例上升 *先单调增* (Phi 系列 / R1-Distill / WRAP 经验) *后崩塌* (Shumailov pure-recursive 上界)，转折点 ρ\* 取决于：(i) anchor 比例 (D 中真实 token 下界), (ii) generator-student capacity gap 的正负号 (Burns 2023 weak-to-strong 反例), (iii) filtering 强度 (Phi 系列 GPT-4-as-curator 与 WRAP 风格改写均隐含强 curation)。**Falsification**: 找到一个 controlled setup, 固定 (N, total D tokens, training compute), 仅改 D\_synthetic / D\_total ∈ {0, 0.25, 0.5, 0.75, 1.0}, 在 ≥3 任务族 (knowledge / reasoning / open-ended generation) 上 NTP-aligned utility 与 D\_synthetic 比例的关系是 *单调而非倒 U*，则 ρ\* 不存在, C-SCALE-8 应吸入 C-SCALE-6 仅作为 sibling 备查。**当前评估**: low–medium——五条独立证据线 (Self-Instruct / TinyStories / Phi / WRAP / R1-Distill) 方向一致, Shumailov 与 Burns 给出 ρ\* 边界的两侧, 但 *所有公开数据点都在 (filter, anchor, gap) 上变量混淆*, 跨研究的 ρ\* 数值 [unknown], 因此尚不足以从 C-SCALE-6 独立。

### 反例 / 边界条件

- **\"是否真是新轴\" 的根本质疑**：WRAP 与 Phi 系列的合成 corpus 经过强 curation, 其相对自然 corpus 的 quality 多数维度都更高 (语法、密度、噪声水平), 因此 *观察到的 lift 可能完全可归因于 C-SCALE-6 而非 D\_synthetic 比例本身*。这一可分性 [unknown], 是 C-SCALE-8 还停留在 proposed 而非主表的核心原因。
- **Shumailov 与 Phi/R1-Distill 表面冲突**：Shumailov *pure-recursive 无 anchor 无 filter*, Phi/R1-Distill *有真实 base + 强 filter*, 在 D\_synthetic / D\_total = 1 但 filter 不同的两个 setup 上结果可以反号——这正是 ρ\* 必然依赖 (anchor, filter) 这两个混淆变量的实证理由。把 \"recursive collapse\" 与 \"合成数据有效\" 当成两派立场是误读, 它们在不同 regime 上各自成立。
- **Generator-student gap 反例 (Burns 2023)**：当 teacher < student (weak-to-strong) 时合成 D 的边际 NTP utility *不是 zero 但也远不饱和*, 给 \"合成数据是万能 D 替代\" 的乐观推断划出明确反例。Self-Rewarding LM (Yuan 2024) 的 teacher = student 设定与 R1-Distill 的 teacher > student 设定是两条不同的 sub-mech, 不应混用。
- **任务族依赖**：合成 D 在 reasoning / code / 数学等 *可机器评分子集* 上 lift 显著, 在 open-ended generation / 长尾事实 knowledge 上 lift 微弱甚至负——这一 task-stratified 现象与 C-SCALE-4 / C-SCALE-7 \"verifier-rich subset\" 收敛同型, 暗示 C-SCALE-8 的有效域可能也被同一个 verifier-existence 边界圈住。如果是, C-SCALE-8 与 4 / 7 三轴 *在作用域上共线*, taxonomy 上应作为同一 cluster 处理而非三独立轴——这条 [uncertain] 的可能性是 C-SCALE-8 *最有意思的元结构*。

### 2026-05-28 判断

C-SCALE-8 与 C-SCALE-6 / C-SCALE-7 三者的关系是 2026 年 scaling-limits 文献最未解的三角：(a) 与 C-SCALE-6 在 \"是否独立 origin 维度\" 上未分离, (b) 与 C-SCALE-7 在 self-rewarding setup 上正在融合 (Yuan 2024), (c) 三者的有效域都被 verifier-existence 边界收窄。这是为什么本节只把它写成 proposed 而不向 survey §10 同步——*candidate 的 \"机制独立性\" 还不够硬*, 强行同步等于把方法学债务前移。

更诚实的一句：第八轴的存在性几乎已经被工程界默认接受 (Phi/R1-Distill 是商业 deploy 的 base), 但 *学术上能否把它从 data-quality 中干净分离* 仍待 controlled study。在 2026 没有该 study 之前, *把 C-SCALE-8 标注为 proposed 而非升入主表, 本身就是 §9 meta-候选 \"不可证伪即不登记\" 原则的一次实演*——与 C-EMBOD-7 / C-FORM-7 / C-GROUND-7 这一束 sub-candidate 的处理同型。

跨链：与 [reasoning](reasoning.md) §inference-time scaling 末段的 \"工程界一步步逼近同一根 (a)+(b) 联合上界\" 同结构——合成数据线在 NTP 框架内同样是 \"工程上一步步推近 D 的 *origin axis*, 但 mech 命题 (是否真新轴) 仍由 verifier-existence 圈住\"。

## 第九个维度：D 轴本身的硬上限——data exhaustion 辩论 (2022–2026)

> **(2026-05-29 新增, 候选状态)** 本节不引入新 mech candidate，而是把 *七轴 + C-SCALE-8 proposed* 全部依赖的 D 变量本身的 *公开高质量自然 token 总存量* 这条隐含假设钉到文献上。它与 C-SCALE-8 (synthetic origin) 互为镜像——C-SCALE-8 钉 \"若自然 D 不够能否用合成补\"，本节钉 \"自然 D 究竟够不够、什么时候不够\"。两条结论的乘积才是 2026–2030 frontier scaling 真正能调用的 D 轴上限。

七轴里的 D 通常被默认为 \"可无限放大\" 的自变量——Kaplan 2020 / Hoffmann 2022 的 scaling-law 拟合都隐含 D 取自 web-scale corpus 且远未饱和的假设。但 2022 年起，frontier 训练量逼近 *公开互联网高质量 token 总存量*，\"D 是否本身被自然分布封顶\" 成了独立可量化问题。这条线在公开文献里散布得比 C-SCALE-1–8 任何一条都更碎，但 anchor 论文足够把它整理成单独一节。

- **2022-11 — Villalobos, Sevilla, Heim, Besiroglu, Hobbhahn, Ho, *Will We Run Out of Data? An Analysis of the Limits of Scaling Datasets in Machine Learning* (Epoch AI, [arxiv:2211.04325](https://arxiv.org/abs/2211.04325))**。第一份系统量化：估计 *公开互联网* 上 \"high-quality language data\" 总存量在 2022 年约 $4.6 \\times 10^{12}$ token (中位估计)，按彼时 frontier 训练规模增速外推，**high-quality stock 将在 2024–2026 区间被耗尽**，low-quality web stock 在 2030–2050 耗尽，images 在 2030–2060。这是 \"数据墙\" 这个流行语的源头。同期 Hoffmann 2022 Chinchilla 的最优 D/N ≈ 20 配比让 D 需求每代翻倍——把 D 耗尽时间窗的紧迫性进一步收紧。
- **2023-05 — Muennighoff et al., *Scaling Data-Constrained Language Models* ([arxiv:2305.16264](https://arxiv.org/abs/2305.16264))**。把 D 耗尽问题翻译成 *受约束下的最优 epoch 数* 问题：在 unique token 有限的前提下，每个 token 重复 *最多约 4 epoch* 时损失下降与 unique token 等效；超过 ≈ 16 epoch 后边际效益接近零。这是把 Villalobos 的 \"D 耗尽\" 软化为 \"D 等效放大约 4×、硬上限约 16×\" 的具体系数——但前提是 *unique* token 的 quality 分布与原 corpus 一致，否则 multiplier 会塌。
- **2024-06 — Villalobos et al. 更新版 (Epoch AI 2024 report, 同 arxiv 编号 v2)**：把 high-quality stock 估计上调到 $\\sim 5 \\times 10^{14}$ token (引入更激进的 web-crawl 估计 + 私域数据)，把耗尽窗口推迟到 2026–2032 区间。但**关键转折**：报告同时指出 frontier lab 的实际 D 增速 (Llama-3 15T → DeepSeek-V3 14.8T → 估计 Llama-4 / GPT-5 量级 ≥ 30T) 已接近其上调后估计的中位线，**耗尽不再是 \"如果\" 问题而是 \"哪一年\" 问题**。
- **2024-08 — Penedo et al., *FineWeb / FineWeb-Edu* ([arxiv:2406.17557](https://arxiv.org/abs/2406.17557))**。从 CommonCrawl 中蒸馏出 *15T token 高质量子集* + *1.3T token 教育级精选子集*，并公开了筛选 pipeline。这条工作的隐含信息是：**\"high-quality stock\" 这个量本身依赖筛选阈值**——把阈值放宽 / 收紧能让有效 D 在一个数量级内浮动。Villalobos 的 \"耗尽窗口\" 因此不是一个 hard deadline 而是一族曲线，曲线参数是 quality threshold。
- **2024-10 — Goyal et al. / Sardana et al., *Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws* ([arxiv:2401.00448](https://arxiv.org/abs/2401.00448))**。从另一侧戳穿 D 增速的合理性：在 inference 量大的部署场景中，最优 D/N 应**超过** Chinchilla 的 20 而进入 50–200 区间——即 frontier 工程的实际 D 渴求比 Chinchilla 还要激进，让 Villalobos 的耗尽窗口被进一步前移。
- **2025 — Llama-3.1 ([arxiv:2407.21783](https://arxiv.org/abs/2407.21783)) / DeepSeek-V3 ([arxiv:2412.19437](https://arxiv.org/abs/2412.19437)) / Qwen2.5 ([arxiv:2412.15115](https://arxiv.org/abs/2412.15115)) 三家公开 D 数字**：分别 15T / 14.8T / ~18T pre-training token。三家在同一时间窗内独立逼近同一档量级，强烈暗示 \"frontier 实际可调用 high-quality 自然 token\" 已经被同一 *经济-工程 ceiling* 圈住——这与 Villalobos v2 的耗尽窗口预测吻合。
- **2025–2026 — synthetic-data 与 multi-epoch 的市场化回应**。当 D 耗尽逼近，frontier 默认选择不是 \"停止增长 D\"，而是 (i) 合成补 (Phi/R1-Distill 路线，见 C-SCALE-8 节)；(ii) Muennighoff 4-epoch 等效放大 + 高质过滤循环；(iii) 私有非公开 corpus 收购 (出版社、代码托管平台、视频字幕)，后者在 OpenAI–News Corp / Google–Reddit / Anthropic–public-domain 等 2024 公开授权交易中体现。这三条都不是 D 轴 *本身* 的突破，而是 *绕过 D-axis 自然上限* 的工程妥协。

把上述六条对齐回七轴：**D 轴在 2024–2026 已从 \"近似无限自变量\" 退化为 \"被自然 high-quality stock + quality threshold + epoch multiplier 三者联合圈死的有限资源\"**。这条退化对 C-SCALE-1 (Chinchilla loss-law) / C-SCALE-2 (knowledge-frequency sigmoid) / C-SCALE-6 (data-quality multiplier) / C-SCALE-8 (synthetic origin) 四条 candidate 的有效域都有连带影响——它们的 \"D 增加则 utility 增加\" 隐含前提，在 frontier scale 上正在被 D 的自然上限切断。

### 与 C-SCALE-8 的耦合：耗尽-合成-崩塌三角

把数据墙与第八轴 candidate 拼在一起，可以得到 2026 scaling 文献最被低估的耦合关系：

- 若 Villalobos v2 的耗尽时间窗成立 → frontier 必须从 D ≈ 30T 起把合成 D 比例 D\\_synthetic / D\\_total 调到 ≥ 0.3-0.5 才能维持 Chinchilla 配比 → C-SCALE-8 的 ρ\\* (合成比例转折点) **决定整个 frontier scaling 是否还能继续**。
- 若 Shumailov 2024 [arxiv:2305.17493](https://arxiv.org/abs/2305.17493) 的 pure-recursive 崩塌上界在 *混合 regime* 也保留 (即 ρ\\* < 0.5)，则 frontier 把 D 推到 ≥ 50T 在 *物理上* 不可能 (合成比例必越界)。
- 若 ρ\\* ≥ 0.7 (Phi-4 / R1-Distill 隐含的乐观估计)，则 D 耗尽是 *可逆* 工程问题，C-SCALE-1 的 loss-law 仍可外推到 ≥ 100T token。

这三种 scenario 对应 2026 frontier scaling 命运的三条完全不同分支，**而 ρ\\* 的公开估计 [unknown]**——这是为什么 C-SCALE-8 仍是 proposed 而本节也只作为元-依赖关系记录、不开新 mech candidate。

### 反例与边界条件

- **\"D 耗尽\" 的最强反例方向**：私域 / 非公开 corpus (代码托管、出版社版权内容、视频字幕、即时通讯)、enterprise data、人形机器人 teleop trajectory ([embodiment](embodiment.md) §Robot-data scaling) 等 *未进入 Villalobos 估计基数* 的 token 池。这一池的真实存量 [unknown] 但显然非零——OpenAI / Anthropic / Google 在 2024–2025 公开授权交易给出的是 *可获取性* 上限而非 *存量* 上限。如果私域 + 多模态 stock 量级与公开 web stock 相当或更大，Villalobos 的耗尽时间窗会被整体右移 1–3 年。
- **\"D 耗尽\" 的最强支持方向**：Sardana 2024 的 inference-aware optimal D/N ≥ 50 把 frontier 的 D 渴求拉到 Chinchilla 的 2.5×，比任何 \"stock 上调\" 都更快地把窗口拉近。Llama-3 / DeepSeek-V3 / Qwen2.5 三家在同一窗口独立逼近 ≈ 15T 是经验性强证据，说明该上限不是某一家的工程选择而是全行业共面临的 ceiling。
- **元方法学债**：截至 2026-05，**没有任何一家 frontier lab 公开过 \"high-quality token stock\" 的实际可获取数字**（披露的都是已使用的 D 数字而非剩余 stock）。Villalobos 的估计是 *外部观察者从公开 crawl 反推*，与 frontier 内部的真实可调用 token 池之间存在 [unknown] gap——这与 [online_learning](online_learning.md) §frontier 工程 mid-training annealing 节 \"frontier 主动选择不暴露 retention 曲线\" 同型，都是 *披露选择函数* 形塑外部估计的典型。

### 2026-05-29 判断

把 D 轴本身作为有限资源处理，是 2026 年 scaling-limits 文献从 \"七轴自变量\" 范式向 \"七轴 + 一个被自然分布封顶的 D 池\" 范式过渡的关键一步。这不引入新 mech candidate，但**改变了 C-SCALE-1 / C-SCALE-2 / C-SCALE-6 / C-SCALE-8 四条 candidate 的工程有效域上限**——它们的 \"D 放大则 utility 放大\" 命题在 frontier scale 上正被 D 的自然天花板切断，而非被 mech 命题本身切断。这是 cap 派与 mech 派都需要承认的共同前提：**未来五年 frontier scaling 的真正自变量不是 D 而是 (D\\_natural × multiplier\\_epoch + D\\_synthetic × ρ\\*)，其中后者由合成数据崩塌点决定**。

把这一判断回灌：C-SCALE-8 (proposed) 的状态从 \"与 C-SCALE-6 未分离\" 升级为 \"与 C-SCALE-6 未分离 + 与 D 耗尽时间窗强耦合\"。下一次该 candidate 是否升入主表，取决于 ρ\\* 与 Villalobos v2 时间窗两条 [unknown] 是否能在 12 个月内有任一方收敛——预期是不能，因为前者需要 controlled study (没人做)、后者需要 frontier 主动披露 stock 数字 (没人愿)。

跨链：本节与 [online_learning](online_learning.md) §mid-training annealing 节 \"披露选择函数\" 论证、[reasoning](reasoning.md) §inference-time 末段 \"工程界一步步逼近同一根 (a)+(b) 联合上界\" 同型——三处都揭示 *frontier 工程实际 ceiling 由 mech 命题与披露选择函数联合决定*，而非纯技术问题。

## D 轴外部估计 vs frontier 内部 stock 的披露差: §9 的半年时间侧加固 (2026-05-29)

§第九维度末段把 \"frontier lab 公开的 D 数字 ≠ frontier 可调用 high-quality token stock\" 这条 gap 写成一句 [unknown]，把它单独立成一节是把这条 gap 从 \"备注\" 升级到 \"时间常数被显式钉上的方法学债\"——与 [world_model](world_model.md) §OP-WM-1..5 半年进展核查、[grounding](grounding.md) §C-GROUND-PROTO 三轨协议半年实施核查同型处理，目的不是开新 mech 命题而是给 §9 的 \"耗尽-合成-崩塌三角\" 加一根 *时间侧* 的标尺，使它在未来 12–24 个月有可观察的不动点。

预先声明判据：只算 (a) frontier lab 公开 arxiv / 技术报告 / system card / 听证会证词，(b) 直接落在 \"high-quality token stock 总量 / 剩余可获取 token 量 / D\\_synthetic 比例\" 三个变量上的数字，(c) 不是已用 D 数字而是剩余 stock 数字。轶事、blog 单图、记者转述、投资人 deck 一律不计。

- **2025-12 → 2026-05 半年核查**：六家 frontier lab (OpenAI / Anthropic / Google DeepMind / Meta / DeepSeek / Qwen) **没有一家**在公开材料里给出过 \"可调用 high-quality natural-token 剩余 stock\" 的数字。已公开的全部是 *已用* 训练 D 数字 (Llama-3.1 15T [arxiv:2407.21783](https://arxiv.org/abs/2407.21783) / DeepSeek-V3 14.8T [arxiv:2412.19437](https://arxiv.org/abs/2412.19437) / Qwen2.5 18T [arxiv:2412.15115](https://arxiv.org/abs/2412.15115))，或是 *合成比例上限* 的工程承诺（Phi 系列 / R1-Distill 隐含 ρ ≥ 0.5，但未拆分 anchor / filter / generator gap 三变量）。Villalobos v2 ([arxiv:2211.04325](https://arxiv.org/abs/2211.04325) v2) 给出的 ~5×10¹⁴ 上调估计在半年内仍是 *外部观察者从 CommonCrawl 反推*，与 frontier 内部 stock 之间的 gap [unknown] 在六个 lab 上同时 *未关闭*。
- **半年内唯一方向性运动**：2026-Q1 几份 system card / responsible-scaling-policy 更新 [unverified bundle] 把 \"private corpus licensing\" 与 \"synthetic data fraction\" 各自作为合规叙述写入，但都停在 *列出数据源类目* 层而非 *给数字* 层。这等价于 [online_learning](online_learning.md) §Mid-training annealing 节 \"frontier 主动选择不暴露 retention 曲线\" 的同型现象——披露格式更新但数字仍空。
- **与已建立的同型节奏对齐**：OP-WM-1..5 半年无运动 + C-GROUND-PROTO 半年 0/3 完整 + 2/3 部分 + C-CONT-2 第三支柱 frontier-disclosure (LLM 侧 mid-training cutoff retention) + C-EMBOD-7 route-elimination (视频 backbone frontier 集体沉默) + C-REAS-7 sub-candidate sync (RLVR transfer 衰减率不报) — 这是第五处独立 topic 同时落到 \"工程上可做、社会学上不做\" 闭环上。D 轴披露差的时间常数现按同型四档刻度处理：半年 (本次) → 一年 (2027-05 再核) → 两年 (2028-05) → 任一 frontier lab 公开剩余 stock 数字即清零。

新增 corollary（**不**升 candidate snapshot 主表，仅作 §10 evidence 列脚注 + taxonomy 升降级历史登记）：

- **C-SCALE-D-DISCLOSE (corollary, 不入主表)**：§9 \"D 耗尽-合成补-Shumailov 崩塌\" 三角的 *决定性数字* (Villalobos v2 余量 / frontier 内部剩余 stock / ρ\\*) 至少有两个在 frontier lab 公开材料里 *结构性* 缺席，半年时间常数下 *无任一关闭*。**Falsifier**: 任一 frontier lab 公开 (i) 当代训练运行剩余可调用 high-quality natural-token 估计、或 (ii) D\\_synthetic / D\\_total 比例并同时给出 anchor / filter / generator-student-gap 三变量拆分、或 (iii) Villalobos v2 的 ~5×10¹⁴ 区间被该 lab 内部数字证实 / 证伪。三条任一项满足即 corollary 进入可证伪窗口；否则按四档刻度累计。**当前评估**: 与 C-WM-6/7、C-GROUND-PROTO、C-CONT-2 第三支柱、C-EMBOD-7 route-elimination 五条同处 *方法学债* 层，不构成独立 mech 命题。**处理协议**: 按 [`../survey/taxonomy.md`](../survey/taxonomy.md) 2026-05-29 升降级历史协议 sibling-cap 仅入升降级历史日志，不入主表 (C1–C7 + Reversal Curse 主候选不动)；下一 C tick 同步债务把本条 corollary 与 \"半年时间常数首刻度\" 一并写入 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 evidence 列脚注，与 C-WM-6/7 / C-GROUND-PROTO / C-CONT-2 第三支柱 *并列* 不开新通道，与 §10 readout-side 七条 evidence-supply 通道架构同型 (横向加密非纵向扩条)。

**反例与边界条件**：

- **\"披露差也许是好事\" 反方向**：frontier lab 不公开剩余 stock 数字 *可能* 是出于商业竞争或私域授权合同约束而非 \"报告方向不利于自己阵营\"——这是与 OP-WM-4 (FAIR / OpenAI 都没结构性动机做 JEPA-vs-NTP 对照) 同型解释的强对手命题，本节没有独立证据排除它。但即使采纳该解释，C-SCALE-D-DISCLOSE 的可观察事实 (数字缺席) 不变，只是把 \"社会学瓶颈\" 标签换成 \"商业瓶颈\" 标签——这一标签替换不动 §9 末段判断的工程含义。
- **\"私域 corpus 把 stock 撑住\" 反方向**：若 OpenAI–News Corp / Google–Reddit / Anthropic–public-domain 等 2024–2026 授权交易实际接入的 token 量 ≥ Villalobos v2 的 ~5×10¹⁴ 上调估计的 30%，则 D 轴耗尽时间窗整体右移 1–3 年，C-SCALE-D-DISCLOSE 的紧迫性降级。但这一假设*本身*依赖未公开的内部数字——构成自指：要排除披露差 corollary 必须先关闭披露差。这是为什么本 corollary 只能按时间常数刻度累计而不能直接证伪。
- **与 C-SCALE-8 的关系**：C-SCALE-D-DISCLOSE *不替代* C-SCALE-8 (proposed)，它是 §9 末段判断 \"ρ\\* 与 Villalobos v2 时间窗两条 [unknown] 12 个月内不会收敛\" 的 *时间侧具体化*。C-SCALE-8 继续保留 proposed 状态等待 controlled study；C-SCALE-D-DISCLOSE 不等 controlled study，按四档刻度累计 *披露层* evidence。两条 *正交*：前者是 mech 命题等待经验证据，后者是方法学债等待披露行为。

**判断 (2026-05-29)**：§9 的 \"耗尽-合成-崩塌三角\" 在 2026-05 已经达到一个奇怪的稳态——三角的*结构*被 Villalobos / Muennighoff / Shumailov / Phi / R1-Distill / Sardana / FineWeb 七条独立证据线锁死，但三角的*顶点数字* (ρ\\*、Villalobos v2 内部 ground-truth、frontier 实际剩余 stock) 同时被 frontier 披露选择函数封死。这与 OP-WM-4 \"理论 prior 收紧但实证侧空\" / C-CONT-2 第三支柱 \"四家 mid-training 配方均未提反向训练增广\" / C-EMBOD-7 \"视频 backbone frontier 集体沉默\" 形成第五次同型重复——*frontier scaling 议题的瓶颈不在能力 / 工程 / 理论，而在披露行为*。把 C-SCALE-D-DISCLOSE 显式登记是把这条 meta-命题在 scaling 域的具体化，不是新 mech 命题。下一次 NTP-Deepen 在 scaling_limits.md 上的实质性更新，最有可能来自 (a) 任一 frontier lab 在 2026-Q3-Q4 system card 更新中给数字 (低概率 base rate)、(b) Epoch AI 或独立第三方在 v3 Villalobos 报告中给出新估计区间 (中等概率, 12–18 个月窗口)、(c) Shumailov 后续工作把 pure-recursive 上界扩到 mixed regime 给出 ρ\\* 上界 (中等概率)——而不是又一篇 frontier model 发布。

跨链：本节与 [world_model](world_model.md) §OP-WM-1..5 半年核查 / [grounding](grounding.md) §C-GROUND-PROTO 半年实施核查 / [online_learning](online_learning.md) §C-CONT-2 第三支柱 / [embodiment](embodiment.md) §C-EMBOD-7 route-elimination 视频 backbone 四处同型——五条 corollary 共享 *半年 → 一年 → 两年 → 任一关闭清零* 四档时间刻度协议，构成 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 第八种几何加密方式 (时间侧对偶) 在 scaling 域的第五个落点。下一 C tick sync 时本 corollary 与 C-WM-6/7 / C-GROUND-PROTO / C-CONT-2 第三支柱 / C-EMBOD-7 并列写入 §10 evidence 列脚注，不开第八条 evidence-supply 通道，不动 taxonomy 主表。

## Open problems

- **OP-SCALE-1** — 把 Shannon SNR 视角与 superposition / knowledge capacity scaling 统一成一个 SNR-superposition 法则。
- **OP-SCALE-2** — 在 joint-KL Ω(H) 下界条件下，找出可使 estimation error 不再线性增长的额外结构（e.g. local Markov、context compression）。
- **OP-SCALE-3** — 长尾事实的 "频率代理" 度量改良——离开 web-frequency 后该 sigmoid 是否仍成立。
- **OP-SCALE-4** — catastrophic overtraining 的 D\* 是否是 optimizer / LR-schedule artifact——若是，则 C-SCALE-3 应降级为 pseudo。
- **OP-SCALE-5** — summarized-CoT 把 Ω(H) sample-complexity 转成 inference-time compute 的 "等价代价" 是否有 lower bound——即是否存在 "用推理时间换样本量" 的硬上限。
- **OP-SCALE-6** — C-SCALE-7 与 C-SCALE-6 的清洁分界——DPO setup 下 post-train compute 与 data-quality multiplier 的可分离性是否经得起 controlled study。
- **OP-SCALE-7** — verifier capacity ceiling 之外：当 policy 反超 verifier 时，post-train scaling 是否存在 \"self-play 闭环\" 让 γ 重新非零，还是必然收敛到 verifier 上限。

## OP-SCALE-1..7 半年进展核查 (2025-12 → 2026-05)

§Open problems 七条以前是无标号 bullet——本 tick 顺手补 OP-SCALE-1..7 标号，使其与 [world_model](world_model.md) §OP-WM-1..5、[grounding](grounding.md) §OP-GROUND-*、[online_learning](online_learning.md) §OP-CONT-* 同型可被外部引用。然后对照 2025-12 以来 *公开* arxiv / 技术报告 / 可复现代码做一次诚实核查；判据与 §D 轴外部估计 vs frontier 内部 stock 披露差节一致：只算 (a) 公开材料，(b) 直接落在 OP-SCALE-k 描述的命题 / 实验设计上，(c) 报数字 / 证明 / controlled-study 结果而非 demo / 评论文章。轶事、blog 单图、记者转述、投资人 deck 一律不计。本节不开新 candidate / sub-candidate / corollary / route-elim 任一槽位 (严守 2026-05-30 → 2026-06-10 增条冻结协议)，只做 *已开题* 的时间侧刻度登记。

- **OP-SCALE-1 (SNR-superposition 统一法则)**。Elhage 2022 *Toy Models of Superposition* ([arxiv:2209.10652](https://arxiv.org/abs/2209.10652)) 与 C-SCALE-5 比特/参数线 (Allen-Zhu 2024 [arxiv:2404.05405](https://arxiv.org/abs/2404.05405)) 两条线在 2026-05 仍未被显式合写。最接近的新增是 Anthropic interpretability 团队 2026-Q1 在 dictionary learning capacity bound 上的工程报告 [unverified bundle]，但仍停在 feature-count 而非把 *bit/param* 与 *feature/param* 两个量纲对齐。**未动**。Falsification window 估计 12–24 个月，bottleneck 是写法学而非实验。
- **OP-SCALE-2 (joint-KL Ω(H) 下界的结构性松弛)**。半年内未见把 Bhattamishra 系列 ([arxiv:2206.14486](https://arxiv.org/abs/2206.14486) 谱) 的下界条件下放到 local-Markov / context-compression 结构的工作；最接近的方向性运动是 long-context efficient-attention 一族 (Mamba-2 / RWKV-7 / Jamba 后续) 给出的 *经验* 上下文压缩比，但都没回到 sample-complexity 下界的 *理论* 接口。**未动**——但这是一个 *理论* 开题，半年时间常数本来就太短，建议按两年刻度核算 (2027-05 再核)。
- **OP-SCALE-3 (长尾事实"频率代理"改良)**。Kandpal 2022 ([arxiv:2211.08411](https://arxiv.org/abs/2211.08411) [unverified ID]) / Mallen 2023 的 web-frequency sigmoid 半年内未见 *非 web* 度量替代实证——非 web 度量 (e.g. Wikipedia pageview、Google Trends、academic citation count) 的 NTP-loss-vs-frequency 曲线在 2026-05 仍是 *空*。最接近的反向证据来自 §第八轴候选 Synthetic data 段提到的 R1-Distill / Phi-4 ([arxiv:2412.08905](https://arxiv.org/abs/2412.08905)) 在 *合成* 长尾上 *能* 把 loss-vs-frequency 曲线整体下移，但仍以 web-derived frequency 作 x 轴。**未动**。
- **OP-SCALE-4 (catastrophic overtraining 的 D\* 是否为 optimizer artifact)**。半年内 Springer-Hu 系列 catastrophic overtraining 报告 [unverified bundle] 后续仍未给出 *跨 optimizer × 跨 LR-schedule × 同 D 预算* 的三因素对照——即把 D\* 拆成 *优化器固定项* + *数据固定项* 的 ANOVA 风格分解。这意味着 C-SCALE-3 (overtraining cliff) 的 *因果* 归因半年内仍不可分离，C-SCALE-3 *降级为 pseudo 的判据* 半年内未触发。**未动**，但 *未触发降级* 本身是一个弱-正面信号 (C-SCALE-3 保留 candidate 状态合理)。
- **OP-SCALE-5 (CoT 把 sample-complexity 换成 inference-compute 的等价代价下界)**。这是 §Inference-time scaling 第四轴的 *理论上界* 开题——半年内最相关工作是 [reasoning](reasoning.md) §C-REAS-5 双段相变测量缺失节登记的 *经验* 双段曲线，但理论侧 (在什么任务族上 NTP-sample 与 inference-token 互换有 lower bound) 仍空。Snell 2024 ([arxiv:2408.03314](https://arxiv.org/abs/2408.03314)) 给的是上界 (具体配方下推理换样本的 *可达* 替换率)，不是下界。**未动**——理论开题，按两年刻度核算。
- **OP-SCALE-6 (C-SCALE-6 vs C-SCALE-7 清洁分界, DPO setup)**。半年内 frontier post-training 配方 (R1 / Claude 4 / Gemini 2.5) 一致采用 RLVR + verifier 路线而非 DPO-as-baseline，使 *DPO 内部* 的 data-quality multiplier vs post-train compute 可分离性 controlled study 没有商业拉动——与 [online_learning](online_learning.md) §C-CONT-2 第三支柱 (frontier 不报反向训练增广 / retention 曲线) 同型 *披露选择函数* 落点。**未动**——但归因 *不是* 工程瓶颈而是 *post-training 范式整体迁移到 RL 后 DPO controlled study 失去商业紧迫性*，与 OP-SCALE-7 形成互锁 (见下条)。
- **OP-SCALE-7 (verifier capacity ceiling 之外的 self-play 闭环)**。这是 §第七轴 post-training compute 末段最尖的开题。半年内最相关运动是 DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948)) 后续的 R1-Zero variants 与 *self-distillation* / *iterated RLVR* 工程报告 [unverified bundle]，但都没回答 *policy > verifier* 之后 γ (post-train scaling 指数) 是否仍非零——所有公开数字仍是 *policy ≤ verifier* 区间内的 saturation 曲线，*policy > verifier* 区间的 controlled measurement 半年内仍空。**未动**。这条开题与 [reasoning](reasoning.md) §verifier-bound saturation 节互锁——后者半年内同样未见反例。

把七条压成元判断 (2026-05-29)：OP-SCALE-1..7 半年时间窗内 *没有一条* 关闭，*没有一条* 在方向性上有实质运动。这与 [world_model](world_model.md) §OP-WM-1..5 半年核查 5/5 未动、[grounding](grounding.md) §C-GROUND-PROTO 三轨协议 0/3 完整 + 2/3 部分、[embodiment](embodiment.md) §C-EMBOD-7 route-elimination 视频 backbone frontier 集体沉默、[online_learning](online_learning.md) §Mid-training annealing frontier 选择性披露、[causality](causality.md) §RL-from-environment 三个 <1 GPU-week 实验无人做 五处构成 *第六次同型重复*。但 scaling_limits 域内部的 *归因结构* 与其他五处略有差异：OP-SCALE-1 / OP-SCALE-2 / OP-SCALE-5 是 *理论* 开题 (写法学 + 证明工作量，本身半年就是合理刻度的 1/2–1/4)，OP-SCALE-3 / OP-SCALE-4 是 *方法学度量* 开题 (controlled study 工程量 1–3 GPU-week 级，半年未动属 *未触发降级* 弱-正面信号)，OP-SCALE-6 / OP-SCALE-7 才是与其他 topic 同型的 *披露选择函数* 瓶颈。这一三分使 \"scaling 议题的瓶颈也在社会学\" 这一元命题在 scaling 域 *只对 2/7 开题成立* 而非全域成立——*不能* 把 scaling_limits 简单归并到 world_model / grounding / online_learning / embodiment / causality 共享的 \"frontier 披露选择函数\" 单一闭环里。

回灌到 corollary 状态：OP-SCALE-1..7 *不* 升级为独立 mech candidate (它们是开题而非命题)；本节 *不* 新增 corollary (严守 12 天增条冻结协议)。但 *半年无运动* + *归因三分* 这一对事实可作为 §C-SCALE-D-DISCLOSE corollary *作用域* 的 *边界条件* 加固——后者只在 OP-SCALE-6 / OP-SCALE-7 两条 *披露* 类开题上 *直接* 适用，对 OP-SCALE-1 / 2 / 5 (理论类) 与 OP-SCALE-3 / 4 (方法学类) 不直接适用；这一边界条件半年内被本次核查 *经验性* 确认 (理论类与方法学类在半年内确实未表现出 *披露选择函数* 风格的瓶颈结构)。下一 tick C 同步债务：把 \"OP-SCALE-1..7 半年 7/7 无运动 + 归因三分 (3 理论 / 2 方法学 / 2 披露)\" 作为 §C-SCALE-D-DISCLOSE 作用域注解写入 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 evidence 列脚注，与 C-WM-6/7 / C-GROUND-PROTO / C-CONT-2 第三支柱 / C-EMBOD-7 / 本 corollary 并列，但 *标注* 适用范围为 \"披露类瓶颈\" 而非 \"全部 OP-SCALE-*\"——这是与同期五处 corollary 的 *第一处* 显式作用域差异，避免在 §10 横向加密时把 scaling 域纳入过宽。

跨链：本节方法学与 [world_model](world_model.md) §OP-WM-1..5 半年核查、[online_learning](online_learning.md) §OP-CONT-* 半年核查 (若已成文) 同型；归因三分使本节同时与 [formal_limits](formal_limits.md) §理论开题节、[reasoning](reasoning.md) §C-REAS-5 双段相变测量缺失节、§C-SCALE-D-DISCLOSE corollary 三处形成 *边界* 关系 (而非 *同型* 关系)，是 §10 第八种几何加密方式 (时间侧对偶) 在 scaling 域上 *作用域受限* 的第一处显式声明。

## Cross-links

- [formal_limits](formal_limits.md)：表达力天花板（TC⁰、Deterministic Horizon H\*）与本页 sample-complexity 上界互补。
- [reasoning](reasoning.md)：CoT-faithfulness 的 readout/collapse confound 决定了能否用下游 accuracy 来反推 scaling 曲线的 break。
- [world_model](world_model.md)：open-world dilution 的机制级解释可能就是 C-SCALE-2 的频率-SNR sigmoid 在 entity-level 的特例。
- [online_learning](online_learning.md)：catastrophic overtraining 的 plasticity cliff 与 continual learning 的 plasticity-stability 张力是同一现象的两端。
- [N1 The NTP Question](../samples/N1-the-ntp-question.md)：scaling-limits 是 N1 §"可达性 vs 可学性" 区分的主要证据基底。
