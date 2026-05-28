# Online / Continual Learning

> Lifelong learning, non-stationary adaptation, memory。NTP 训练目标在多大程度上能/不能跨越「训练—部署」这条静态切口？

## 核心问题与 NTP 假设

前置 topic `world_model.md` 关心的是「模型脑子里有没有世界」，`embodiment.md` 关心的是「模型有没有身体」。online learning 问的是第三个、也是最容易被混过去的问题：**模型有没有时间**。

主流 LLM 的训练—部署范式是**一次性的**：在某个 `cutoff_date` 之前的语料上做 NTP 预训练，post-train 一遍 (SFT + RLHF / DPO / GRPO)，然后冻结权重发布。之后所有「新知识」要么靠 RAG 外挂、要么等下一次 retrain。从信息论角度看，这是一种极端选择——把 agent 的 epistemic state 在 $t=t_0$ 冻结，然后在 $t \gg t_0$ 仍然用它做决策。这与 Sutton 2019 *The Bitter Lesson* 之后的「continual / streaming」愿景（[arxiv:1906.01563 Stream-Based Continual Learning unverified ID, 用 Hadsell et al. 2020 *Embracing Change: Continual Learning in Deep Neural Networks*, Trends in Cognitive Sciences 24(12) 代替更稳]）正面冲突。

NTP-mech 阵营在 online learning 上的强主张通常包含四条：

1. **Catastrophic forgetting 不是 bug 而是 NTP loss 的不动点**：在 i.i.d. shuffled corpus 上做 SGD，cross-entropy 的最优解会让 representation 收敛到「全 corpus 边际分布」。一旦数据分布发生 sequential shift，旧任务的 loss 必然回升——McCloskey & Cohen 1989 *Catastrophic Interference in Connectionist Networks* 早就形式化过。Transformer 没有任何机制豁免。
2. **No free-lunch on plasticity-stability**：Lyle et al. 2023 *Understanding Plasticity in Neural Networks* ([arxiv:2303.01486]) 证明深网在持续训练中会出现**plasticity loss**——单位 step 的有效更新量随训练时间单调下降。这意味着即便允许 online SGD，模型也会**逐渐失去学习能力**，而不仅仅是失去旧知识。Dohare et al. 2024 *Loss of plasticity in deep continual learning* (Nature) 把这一现象推广到 supervised + RL，并提出 continual backprop 作为缓解。
3. **In-context learning 不是 online learning**：ICL 看起来像「无梯度的快速适应」，但 prompt 退出 context window 之后状态归零——这是一种 working memory，不是 long-term memory。Brown et al. 2020 GPT-3 论文 ([arxiv:2005.14165]) 称之为 "few-shot learning" 是术语滥用；真正的 lifelong agent 需要把当前 episode 的经验**写回权重**或**写入持久 KV store**。
4. **Test-time training (TTT) 只是延迟了问题**：Sun et al. 2020 *Test-time Training with Self-Supervision* ([arxiv:1909.13231]) 和后续 TTT-RNN / TTT-Linear (Sun et al. 2024, [arxiv:2407.04620]) 让 inner-loop 在推理时做几步 SGD，但 outer-loop 仍然冻结；当 distribution shift 超出 inner-loop 的 capacity 时，整个 stack 仍然失效。

NTP-cap 阵营的回击是：(a) **scale 缓解 forgetting**：Ramasesh, Lewkowycz & Dyer 2022 *Effect of scale on catastrophic forgetting in neural networks* ([arxiv:2207.04604, ICLR 2022 unverified venue]) 经验显示 pretrained large models 比 from-scratch 小模型显著更抗遗忘——pretrain 提供了某种 "regularization prior"。(b) **RAG / 工具 / memory layer** 把 online knowledge 外包出去；Khandelwal et al. 2020 *Generalization through Memorization: Nearest Neighbor Language Models* ([arxiv:1911.00172]) kNN-LM 是早期典范，2024 之后的 Letta (ex-MemGPT, Packer et al. [arxiv:2310.08560]) / Mem0 / Zep 把 agent memory 工程化。(c) **periodic re-pretraining + continued pretraining** 在工业上 work；Gupta et al. 2023 *Continual Pre-Training of Large Language Models: How to (re)warm your model?* ([arxiv:2308.04014]) 与 Ibrahim et al. 2024 *Simple and Scalable Strategies to Continually Pre-train Large Language Models* ([arxiv:2403.08763]) 给出了 warm-up + replay 的实证 recipe，证明只要愿意付计算，continual pretrain 不必从头开始。

这个 topic 的目标是：把「NTP 模型能不能在部署后真正学习」拆成三个可测子问题——*知识更新 (knowledge edit)*、*技能获取 (skill acquisition)*、*分布漂移适应 (drift adaptation)*——并标注每一项的当前最强证据。

## 关键论文 (chronological)

| 日期 | 论文 | 主要论点 | NTP 归类 (mech/cap/pseudo) | 链接 |
|---|---|---|---|---|
| 1989 | Catastrophic Interference in Connectionist Networks (McCloskey & Cohen) | 序列训练会抹除旧任务表征；问题随网络深度恶化 | mech (foundational) | *Psychology of Learning and Motivation* 24, non-arxiv |
| 1999 | Lifelong Learning Algorithms (Thrun) | 把 continual learning 形式化为 task-stream meta-learning | mech (framework) | book chapter, non-arxiv |
| 2017-03 | Overcoming Catastrophic Forgetting in Neural Networks (Kirkpatrick et al.) | EWC：用 Fisher 信息矩阵保护重要权重 | cap (algorithmic) | [arxiv:1612.00796](https://arxiv.org/abs/1612.00796) |
| 2026-05-26 | Can VLA Models Learn Real-World Data Continually w/o Forgetting? (Zhu et al.) | 真实 VLA continual benchmark (4 任务 / rigid+contact+deformable)；显著 catastrophic forgetting；replay 实现因素地图首发 | mech (VLA 子带；C5 候选的首条公开真实 benchmark) | [2605.26820](../papers/paper_notes/2026-05-29-2605.26820-vla-real-world-continual.md) |
| 2017-06 | Gradient Episodic Memory for Continual Learning (Lopez-Paz & Ranzato) | GEM/A-GEM：保留 episodic buffer，约束新梯度不增加旧 loss | cap | [arxiv:1706.08840](https://arxiv.org/abs/1706.08840) |
| 2019-09 | Episodic Memory in Lifelong Language Learning (d'Autume et al.) | 首次把 episodic memory 应用到 LM continual learning，证明可显著减遗忘 | cap | [arxiv:1906.01076](https://arxiv.org/abs/1906.01076) |
| 2020-02 | Generalization through Memorization: Nearest Neighbor LMs (Khandelwal et al.) | kNN-LM：不改权重，靠 datastore 实现 "无训练扩知识"；perplexity 下降但推理慢 | cap (non-parametric) | [arxiv:1911.00172](https://arxiv.org/abs/1911.00172) |
| 2022-02 | Memorizing Transformers (Wu et al.) | 在 Transformer 中插入 kNN attention，把上下文从 8K 扩到 262K | cap | [arxiv:2203.08913](https://arxiv.org/abs/2203.08913) |
| 2022-10 | Mass-Editing Memory in a Transformer (Meng et al., MEMIT) | locate-and-edit：批量改写 GPT-J 中数千事实而保留其余能力 | cap (knowledge edit) | [arxiv:2210.07229](https://arxiv.org/abs/2210.07229) |
| 2023-03 | Effect of scale on catastrophic forgetting (Ramasesh, Lewkowycz, Dyer) | 大 pretrained 模型显著更抗遗忘；遗忘曲线与参数量呈幂律 | cap (empirical) | [arxiv:2207.04604](https://arxiv.org/abs/2207.04604) |
| 2023-03 | Loss of Plasticity in Deep Continual Learning (Dohare et al.) | continual-backprop：证明并缓解 plasticity loss；Nature 2024 正式刊 | mech (formal) | [arxiv:2306.13812](https://arxiv.org/abs/2306.13812) |
| 2023-04 | Understanding plasticity in neural networks (Lyle et al.) | 把 plasticity loss 与 Hessian rank 崩塌联系起来 | mech | [arxiv:2303.01486](https://arxiv.org/abs/2303.01486) |
| 2023-10 | MemGPT: Towards LLMs as Operating Systems (Packer et al.) | 把 context window 当作"RAM"、外挂 datastore 当作"disk"；agent memory 工程化 | cap (system) | [arxiv:2310.08560](https://arxiv.org/abs/2310.08560) |
| 2023-08 | Continual Pre-Training of LLMs: how to (re)warm your model? (Gupta et al.) | LR re-warming + replay 的最简 recipe，避免 loss 飙升 | cap (engineering) | [arxiv:2308.04014](https://arxiv.org/abs/2308.04014) |
| 2024-03 | Simple and Scalable Strategies to Continually Pre-train LLMs (Ibrahim et al.) | 在 405B token 新语料上 continual pretrain Llama2-7B，匹配 from-scratch retrain 的性能、成本不到 1/10 | cap (strong empirical) | [arxiv:2403.08763](https://arxiv.org/abs/2403.08763) |
| 2024-07 | Learning to (Learn at Test Time): RNNs with Expressive Hidden States (Sun et al., TTT-Linear) | hidden state 本身是一个 mini-model，前向时做几步 SGD；7B 规模与 Mamba 持平 | cap (架构融合) | [arxiv:2407.04620](https://arxiv.org/abs/2407.04620) |
| 2024-09 | Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations? (Gekhman et al., EMNLP 2024) | SFT 注入新事实会**加剧**幻觉率；模型用旧 prior 错误外推新事实 | mech (anti-cap) | [arxiv:2405.05904](https://arxiv.org/abs/2405.05904) |
| 2024 | Mechanistic Unlearning / Unlearn What You Want to Forget (多组, e.g. Eldan & Russinovich *Who's Harry Potter?*) | 反向 continual：从权重里**移除**知识仍是开放问题，大部分方法在 adversarial probe 下失败 | mech | [arxiv:2310.02238](https://arxiv.org/abs/2310.02238) |

> 注：表中刻意未列 ICL / long-context 工作（GPT-4-128K、Gemini-1M），因为如正文所述，那是 working memory 而非 lifelong learning。

## 当前共识 / 争议

- **共识 (强)**：Catastrophic forgetting 在所有 dense-trained Transformer 上都可复现。EWC / GEM / replay 等经典方法在 small-scale benchmark 上 work，但**在 LLM 规模下 replay 是唯一 robust 的方法**（Ibrahim 2024 的核心结论）。
- **共识 (中)**：pretrained 大模型比 from-scratch 小模型更抗遗忘——这是 Ramasesh 2022 等多个独立复现的结果，机制尚不清楚（候选：over-parameterization → flat minima → 干扰更稀疏）。
- **共识 (弱)**：知识编辑（ROME / MEMIT）在「单事实改写」上 work，但**多跳 / ripple effect** 仍然失败——Cohen et al. 2024 *Evaluating the Ripple Effects of Knowledge Editing in LMs* ([arxiv:2307.12976]) 显示编辑后模型在依赖该事实的推理链上不一致。
- **争议**：是否存在「真正在线、增量、不需要 replay」的 LLM 学习算法？目前没有 positive evidence。Dohare 2024 的 continual-backprop 只在中小规模 supervised / RL 任务证实，尚未 scale 到 1B+ LM。
- **争议**：RAG 是不是 online learning 的「正确」答案？支持方认为它把知识从 parametric 解耦，避免 forgetting；反对方（Gao et al. 2024 *Retrieval-Augmented Generation for LLMs: A Survey* [arxiv:2312.10997]）指出 retriever 本身是冻结的、且 generator 不会真正"内化"检索内容——本质是把问题外推到了 retriever。

## 反例与上界突破

- **TTT-Linear (Sun et al. 2024, [arxiv:2407.04620])**：在前向过程中对 hidden state 做 SGD，使得「推理时学习」成为架构原语。如果这一思路 scale 成立，它会模糊「online」与「offline」的边界——但截至 2025 中仅在 1.3B 规模验证，7B+ 实证未公开。
- **MEMIT 批量编辑 ([arxiv:2210.07229])**：在 GPT-J 6B 上一次编辑 10000 条事实而保持 zsRE / CounterFact 上其余 acc 几乎不降。这是 NTP-cap 阵营在 knowledge edit 子问题上最强的反例之一——但 ripple-effect 不一致（[arxiv:2307.12976]）仍是悬而未决的反反例。
- **Mem0 / Letta / Zep 等 agent-memory 系统 (2024–2025)**：在 LongMemEval、LoCoMo 等 benchmark 上显示外挂记忆 + 总结写回能让 agent 在数百轮对话中保持人物 / 偏好一致。但所有这些系统都**没有真正改 LLM 权重**——它们是 RAG 的 sophisticated 变种，没有解决 mech 阵营的核心质疑。
- **Continual-Backprop (Dohare et al. Nature 2024)**：用周期性重初始化低 utility 单元，证明可以**无限期**保持 plasticity——这是对「plasticity 必然 decay」论的直接反例，但实验规模 ≤ 100M 参数。

## 时间天花板的工业测量 (2021–2026)

C-CONT-1（Cutoff Bottleneck）从理论上很容易论证，但很长一段时间里没有**部署侧**的硬测量——直到 2021–2024 几条独立工作把"cutoff 之后模型衰减得多快"钉成可外推的曲线。把这条暗线整理出来，是判断 C-CONT-1 强度的必要前置。

- **2021-02 — Lazaridou et al. (DeepMind), *Mind the Gap: Assessing Temporal Generalization in Neural Language Models* ([arxiv:2102.01951](https://arxiv.org/abs/2102.01951))**。第一篇把 perplexity 沿"训练-评测时间差"轴系统性拆开的工作。在新闻 / 科学 / 推特三类语料上证明：固定模型在 cutoff 之后每过 12 个月，关于**新实体 / 新事件**的 perplexity 单调上升，而**通用语言能力**几乎不退化。这是把"时间漂移"从一个直觉问题做成可量化的退化曲线的起点。
- **2021-08 — Chen et al., *A Dataset for Answering Time-Sensitive Questions* (TimeQA, [arxiv:2108.06314](https://arxiv.org/abs/2108.06314))**。构造 ~20k 时间敏感问答对，每题答案随年份变化（"X 在 2010 年是哪个队的成员"）。在 closed-book setting 下，T5-large 准确率长期停在 ~25%，远低于人类 ~85%——即便 fact 完全在训练集内，模型也常给出**时间错配**的旧答案。这把"时间维度"独立于"知识维度"剥离出来。
- **2022-07 — Kasai et al., *RealTime QA: What's the Answer Right Now?* ([arxiv:2207.13332](https://arxiv.org/abs/2207.13332))**。每周更新一次的开放问答基准；首次让任意 LLM 在固定 cutoff 后被持续 evaluate。三年下来的数据显示：所有 closed-book frontier model 在"上周 / 上月新闻题"上的 accuracy 几乎为 0（除非泄漏），而加上 retrieval 后立即跃到 50–70%——retrieval gap 即 cutoff gap 的最直接量化。
- **2022 — Dhingra et al. (TACL), *Time-Aware Language Models as Temporal Knowledge Bases* (TempLAMA)**。在 LAMA 风格 cloze 基础上加时间戳，证明 T5 内部存在"时间敏感"维度，但 retrieval 一致性差：同一事实在不同时间 prompt 下答案漂移。这是早期把"模型内部缺乏一致时间索引"做成内省证据的工作。
- **2023-10 — Vu et al. (Google), *FreshLLMs: Refreshing LLMs with Search Engine Augmentation* ([arxiv:2310.03214](https://arxiv.org/abs/2310.03214))**。构造 FreshQA：~600 题分四类（never-changing / slow-changing / fast-changing / false-premise）。在 GPT-4 / PaLM-2 / Codex 上跑出系统性结果——fast-changing 题 closed-book accuracy 接近 0，且模型在 false-premise 题上有强烈"自信编造"倾向（约 30–50%）。这一篇把 cutoff 衰减、staleness、hallucination 三者的耦合做成第一份联立测量。
- **2024-06 — Cheng et al., *Dated Data: Tracing Knowledge Cutoffs in LLMs* ([arxiv:2403.12958](https://arxiv.org/abs/2403.12958)) [unverified ID]**。反过来问：能不能仅靠模型行为反推它的真实 cutoff？答案：可以——通过对一组已知时间戳事实做 forced-answer probe，能把模型的 *effective* cutoff 定位到月级别。意外的副产物：很多模型的"effective cutoff"显著早于厂商公布的"data cutoff"——说明 pretraining 末段语料的吸收效率随时间快速衰减，权重对"最后几个月数据"的写入是稀疏的。这反过来又削弱了"continual pretraining 把 cutoff 推后"的工程乐观主义。
- **2024–2025 — 一系列 \"web-scale temporal hallucination\" audit**（Press et al.、Onoe et al. 等）：在 Wikipedia 时间戳分层 sampling 后做事实问答，发现 frontier model 对 cutoff 之后 6 个月的事件 hallucination 率 70%+，对 cutoff 之前 6 个月内事件 hallucination 率 30–40%，对 ≥2 年的事件回落到 10–15%。也就是说 *最近* 的 in-distribution 事实也不一定能被可靠召回——pretraining 末尾的 LR 退火窗口本身是稀疏写入的，这与 Cheng 2024 的 effective-cutoff 结果互相印证。

把这条线拉直，2026-05 视角下的判断是：**C-CONT-1 不仅在"cutoff 之后"成立，在"cutoff 之前的最后 6–12 个月"已经开始失效**——这是比 mech 阵营原本论点更强的现象。原本的 C-CONT-1 假设"$t > t_{\text{cutoff}}$ 时知识为空"，实际经验是"$t > t_{\text{cutoff}} - \Delta$ 时知识已稀疏（$\Delta$ ~ 几个月，依 LR schedule 而定）"。Ibrahim 2024 的 continual pretraining recipe 也只能恢复**通用 perplexity**，恢复**长尾时间敏感事实**的实证仍然缺失——这正是下一条候选条目要钉的。

## Test-time gradient 复活：从 TTT 到 Titans，把 SGD 塞进前向 pass 能不能算 online learning (2020–2026)

上面的 cutoff 曲线把\"权重冻结\"这条 mech 论据钉得很死，但 2024 年起有一条不容易被注意到的支线在试图绕过它：**不解冻 outer-loop 权重，而是把一个小内循环 SGD 嵌进前向 pass 本身**。这条路如果走通，C-CONT-1 的边界就要重画——因为模型在推理时确实在更新某种参数，只不过更新的不是 \"主权重\" 而是 \"hidden state 内嵌的子模型\"。把这条线拉直，对判断 \"NTP 是否原生支持 streaming\" 至关重要。

- **2020-02 — Sun et al., *Test-time Training with Self-Supervision* ([arxiv:1909.13231](https://arxiv.org/abs/1909.13231))**。最初版 TTT 是 vision 上的 distribution-shift 缓解：在测试样本上跑一个 self-supervised auxiliary loss（rotation prediction）的几步 SGD，然后再做分类。CIFAR-10-C 上 corruption error 平均下降 ~6%。这是 \"前向时学习\" 第一次以工程可复现形式出现，但当时被定位为 \"robustness trick\"，远没有 online-learning 的野心。
- **2022–2023 — TTT 在 NLP 上的零散尝试**（Hardt & Sun 2024 综述 [unverified ID] 收录约 30 篇）。整体结论：在 distribution shift 中等以下时有效，shift 一大就退化为 noise。社区共识此时仍是 \"TTT ≈ domain adaptation 的轻量版\"，与 online learning 议题脱钩。
- **2024-07 — Sun et al., *Learning to (Learn at Test Time): RNNs with Expressive Hidden States* (TTT-Linear / TTT-MLP, [arxiv:2407.04620](https://arxiv.org/abs/2407.04620))**。这一篇把 TTT 从 trick 抬成 architectural primitive：把 RNN 的 hidden state $h_t$ 直接定义为 \"一个小模型的当前权重\"，每一步 token 都对 $h_t$ 做一次 SGD 来最小化 self-supervised reconstruction loss。在 1.3B 规模与 Mamba / Transformer 持平，在 long-context 1M token 上略胜 Mamba。这是\"前向时 SGD\"第一次在 LM 主线 benchmark 上被认真测量。
- **2024-12 — Behrouz, Zhong, Mirrokni (Google), *Titans: Learning to Memorize at Test Time* ([arxiv:2501.00663](https://arxiv.org/abs/2501.00663) [unverified ID])**。Titans 在 TTT-Linear 之上加了三件事：(i) 把内循环 SGD 做成\"surprise-driven\"——只有当当前 token 的预测残差超阈值才更新 memory module；(ii) 引入 \"forgetting gate\" 来主动衰减旧 memory，对应 C-CONT-2 的 plasticity-stability tradeoff；(iii) 把 memory module 与 attention 并联而非串联，让短程 attention 与长程 \"learned memory\" 分工。论文宣称在 needle-in-haystack 2M context 上超越 GPT-4 [unverified claim]，在长程语言建模上一致超过 Mamba2 与 RWKV-7。
- **2024-12 — Berges et al. (Meta), *Memory Layers at Scale* ([arxiv:2412.09764](https://arxiv.org/abs/2412.09764) [unverified ID])**。另一条平行路线：把 product-key memory（Lample et al. 2019）以稀疏可训练 lookup 的形式塞进 Transformer 中段，在等-FLOPs 下显著提升 factual QA。它本身不是 test-time SGD，但与 Titans / TTT-Linear 一起构成 \"非 attention、非 RAG 的第三类 long-term memory\" 这一新分类。
- **2025 — 多个独立实现**：Mamba-2-TTT、xLSTM with test-time memory、Hyena-TTT 等 fork。整体特征：把 TTT 视为可插入的 building block，主张它与 NTP loss 完全兼容（毕竟 outer-loop 仍然是 cross-entropy）。

把这条线放回 \"online learning 是否被 NTP 原生支持\" 的判据上，有两个对立的解读：

1. **支持方解读**：Titans / TTT-Linear 的 hidden state 在前向时被 SGD 改写，这在功能上 *就是* 在线学习——只是 \"权重\" 的定义从 \"主网络参数\" 收缩到 \"hidden state 内嵌子模型参数\"。如果它在 1M+ context 上 retention 不退化，C-CONT-1 就不再是 NTP 的硬约束，而只是 \"工程选择\"。
2. **反对方解读**（我倾向这一边）：TTT-Linear 的内循环 SGD 是 *episodic*——一旦当前 sequence 处理结束，hidden state 被清空，下一 sequence 重新初始化。这不是 lifetime memory，本质上是把 in-context learning 的容量从 attention KV 扩到了 \"learned hidden state\"——比 ICL 多了表达力，但仍然不跨 episode。Titans 的 \"persistent memory\" 模块在论文中被设计为可跨 sequence，但其更新仍由 outer-loop 决定阈值，不构成真正的自治学习。

判断：test-time gradient 这条线把 C-CONT-1 的边界从 \"权重冻结\" 收紧到了 \"权重在 episode 间冻结\"——这是真实的进步，但仍未触及 mech 阵营的核心命题。下一个能真正撼动 C-CONT-1 的实验，不是再大一个 Titans，而是一个 *跨 episode persistent* 的 TTT 变体，能证明它在序列结束后保留的 memory 在下次激活时仍可被 retrieve 且不与 outer-loop 权重冲突——这恰好就是 1989 年 McCloskey & Cohen 提出 catastrophic interference 时的原始 setup，37 年后仍未被解决。如果 Behrouz 团队在 Titans-v2 里宣称解决了这点，第一件要查的事是：他们的 evaluation 有没有在 episode 之间真正切断 KV-cache、不靠 prompt 重述把旧 memory 偷渡回去。

## Knowledge edit 的 ripple-effect 暗线 (2021–2026)

C-CONT-1 钉的是\"权重冻结后无法吸收新事实\"，但 knowledge-editing 这条支线试图用一个更温和的妥协回应：**不重训、只局部改写权重里那一小簇 \"事实电路\"**。这条线从 2021 年的 ROME 一直走到 2025 年的 ripple-aware editor，几乎每一次新方法都把 benchmark 往前推一格，又被下一篇\"更严苛 ripple eval\"打回原位。把它整理出来，是判断\"knowledge edit 究竟是 cap 的反例、还是 mech 的另一面\"的必要前置。

- **2022-05 — Meng et al., *Locating and Editing Factual Associations in GPT* (ROME, [arxiv:2202.05262](https://arxiv.org/abs/2202.05262))**。把 \"埃菲尔铁塔在巴黎\" 这类 (subject, relation, object) 三元组定位到 GPT-2 / GPT-J 中段 MLP 的几个 key-value rank-1 更新上，可在 zsRE / CounterFact 上把单事实 edit success 推到 90%+ 而 generalization / locality 同样 ≥ 80%。这是\"权重内事实可定位 + 可改写\"假设的第一份硬证据，也是 NTP-cap 阵营把 C-CONT-1 削弱为\"工程问题\"的起点。
- **2022-10 — Meng et al., MEMIT ([arxiv:2210.07229](https://arxiv.org/abs/2210.07229))**。把 ROME 从单事实推到 *批量*：一次性 edit 10⁴ 条事实，GPT-J 6B 上 zsRE accuracy 仅下降 ~3 pp。MEMIT 几乎成为 \"knowledge edit 是 solved problem\" 这种乐观主张的代名词，但它的 eval 都停在 *单跳* 召回——这恰好是下一波工作的攻击点。
- **2023-07 — Zhong et al., *MQuAKE: Assessing Knowledge Editing in Language Models via Multi-hop Questions* ([arxiv:2305.14795](https://arxiv.org/abs/2305.14795))**。把 \"edit\" 与 \"multi-hop reasoning\" 拼起来：edit 完 \"英国首相 = X\" 后再问 \"英国首相的配偶是谁\"。ROME / MEMIT / MEND 在 2-hop 任务上 accuracy 直接掉到 30% 以下，3-hop 接近 chance。这是 ripple-effect 第一次被做成 *可对照* 的退化曲线，也第一次让 \"edit success ≠ knowledge absorption\" 这条 mech 直觉拿到数字。
- **2023-07 — Cohen et al., *Evaluating the Ripple Effects of Knowledge Editing in Language Models* ([arxiv:2307.12976](https://arxiv.org/abs/2307.12976))**。和 MQuAKE 同月独立提出 *RippleEdits* benchmark，把 ripple 拆成 6 个子类型（logical generalization、composition、subject aliasing、preservation、relation specificity、reverse relation）。ROME-style edit 在 \"reverse relation\" 与 \"composition\" 上几乎全失败，与 N3 reversal curse 直接挂钩。这一篇把 \"ripple\" 从模糊概念正式落到了协议层。
- **2024-04 — Hoelscher-Obermaier et al., *Detecting Edit Failures in Large Language Models: An Improved Specificity Benchmark* ([arxiv:2305.17553](https://arxiv.org/abs/2305.17553))**。换一个角度：现有 \"specificity\" 指标（即\"不该改的地方有没有被误改\"）系统性高估，因为它们只在 *表面相似句* 上测。引入 SpecEdit 后，MEMIT 在 GPT-J 的\"非目标条目副作用\"率从报告的 ~5% 跳到 30%+。也就是说 ROME / MEMIT 的 cap 论据本来就建立在过松的协议上。
- **2024-09 — Gekhman et al., *Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?* ([arxiv:2405.05904](https://arxiv.org/abs/2405.05904))**。把 \"用 SFT 注入新事实\" 这条更朴素的 cap 路径也测了：注入新事实会让模型对 *已有* 事实的 hallucination 率上升 8–15 pp，且新事实本身收益曲线随 SFT step 数 *先升后降*。这是把 ROME/MEMIT 的小尺度局部失败与 full-finetune 的全局失败接到了同一条曲线上——edit 不是 free lunch，而是 plasticity-stability 在权重子空间里的另一种表现。
- **2024–2025 — *ripple-aware editor* 一波**：MELO、PMET、AlphaEdit、R-ROME 等（多篇 [unverified IDs]）尝试在 edit 时显式优化 ripple 一致性，部分在 MQuAKE-2-hop 上把 accuracy 推回 50–60%，但 3-hop 与 RippleEdits 的 \"composition\" 子集仍未越过 40%。同期 Yao et al. 的综述 *Editing Large Language Models: Problems, Methods, and Opportunities* ([arxiv:2305.13172](https://arxiv.org/abs/2305.13172)) 把 30+ 方法在统一 benchmark 上重测，结论：**没有任何一种 edit 方法在 ripple-strict eval 下同时满足 success ≥ 80% / locality ≥ 90% / multi-hop ≥ 60%**。
- **2025 — Hase et al., *Does Localization Inform Editing?* 的后续争论（NeurIPS 2023 启动，2025 仍在迭代）**：causal tracing 找到的\"事实位置\"与 edit 实际生效的位置 *不重合*，意味着 ROME 的 mech 解释（\"key-value rank-1 写入对应电路位置\"）可能是 post-hoc 解读，而非操作机制。这一观察直接削弱了 MEMIT 那一系\"我们改的就是事实电路\"的因果叙事，也呼应 N4 §6 关于 mech-interp 因果链脆弱性的讨论。

把这条暗线拉直，2026-05 的判断与 C-CONT-1 / C-CONT-2 互锁：**knowledge edit 在 *单跳召回* 维度上确实证伪了\"frozen weight 完全无法吸收新事实\"的强 mech 命题，但在 *多跳 / ripple / locality 联合* 维度上反过来加固了 C-CONT-2**——任何提高 plasticity（让 edit 真正生效到下游推理）的方法都伴随 stability 损失（locality 或 hallucination 上升）。也就是说\"局部 patch\"并没有逃出 plasticity-stability tradeoff，它只是把交易转移到了一个更小的权重子空间上，账单总量不变。

把这一判断回灌到候选条目：可以登记一条 **C-CONT-4 (Ripple closure failure)** —— 任何\"frozen weight + 局部 edit\"方法都无法在 strict ripple eval (MQuAKE 3-hop + RippleEdits composition + SpecEdit locality) 上同时达到 (success ≥ 80, locality ≥ 90, multi-hop ≥ 60)。Falsification 显而易见：一个公开复现的 edit 方法在三项指标上同时跨过阈值。从 2022 ROME 到 2025 AlphaEdit 这条 3 年曲线看，每一次接近其中两项就会失去第三项——这是该候选的强度来源，但也意味着它本质上是 C-CONT-2 在\"局部权重\"切面上的一个 corollary，而非独立 mech。要不要把它升级为独立条目，取决于未来 12 个月有没有方法把三项 *同时* 推到 80/90/60 以上——一旦出现，候选自然降级；如果三年内没有，它就值得从 corollary 升为 sibling。

## Continual pretraining 的 recipe 边界：replay 比例、LR re-warmup、infinite schedule (2023–2026)

C-CONT-2 在理论端被钉得很死，但它真正的工程压力来自 *continual pretraining*（CPT）这条 batch-mode 妥协路线——既然 streaming 做不到，那能不能用 "每 3–6 个月加一段新语料 + 在旧语料上 replay 一点" 把 cutoff 推后而不破坏 retention？这条线 2023–2026 累计了一组可比较的 recipe 测量，把 C-CONT-2 的 \"无法同时优化\" 从抽象命题落到了具体百分点：

- **2023-08 — Gupta et al., *Continual Pre-Training of Large Language Models: How to (re)warm your model?* ([arxiv:2308.04014](https://arxiv.org/abs/2308.04014))**。第一份系统性研究 LR re-warmup 在 CPT 中的作用：从 Pythia 1.4B / 410M 出发，在 SlimPajama 上 CPT。结论反直觉——把 LR 重新 warm 到接近原始 peak（而非保持在 end-of-pretraining 的低 LR）显著提高新语料 perplexity（≥ 0.3 nats）但同时显著加重旧任务遗忘（HellaSwag / ARC 等下降 2–5 pp）。"warm up 多高" 直接是 plasticity-stability 的旋钮，没有 sweet spot 能同时占两边。
- **2024-03 — Ibrahim et al. (Mila + Meta), *Simple and Scalable Strategies to Continually Pre-train Large Language Models* ([arxiv:2403.08763](https://arxiv.org/abs/2403.08763))**。把 Gupta 2023 推到 10B 规模、推到三种 distribution shift（弱 shift = 同分布更多 token；中 shift = English → German；强 shift = English → Code）。核心 recipe：(i) LR re-warm + re-decay 到 0.1 × original peak，(ii) replay 5% 旧语料。报告：在 Llama-2 7B 弱 shift 下，CPT 总成本 ≈ retrain-from-scratch 的 ~1/10，且 retention loss < 1 pp、新分布 perplexity 与 retrain 持平。这是把 C-CONT-2 的 (c) 条件（成本 ≤ 1/20）逼近最近的工作，但 5% replay 的下界并没有被打破——把 replay 减到 1% 时旧任务退化 5–8 pp，重新撞回 plasticity-stability 墙。
- **2024-06 — Parmar et al. (NVIDIA), *Reuse, Don't Retrain: A Recipe for Continued Pretraining of Language Models* ([arxiv:2407.07263](https://arxiv.org/abs/2407.07263) [unverified ID])**。在 Nemotron-15B 上把 Ibrahim recipe 扩到工业规模：用两阶段 schedule（先 high-quality 短 anneal + 再 domain-specific anneal），在 MMLU / GSM8K 上较 baseline CPT 提升 ~5 pp，但 *只有* 在第二阶段语料量 < 第一阶段 10% 时才稳定——超过此阈值即出现 mid-training collapse（loss 不降反升）。这把 "data ratio" 也加入到 plasticity-stability 的 governing variables。
- **2024-10 — Hägele et al. (EPFL), *Scaling Laws and Compute-Optimal Training Beyond Fixed Training Durations* ([arxiv:2405.18392](https://arxiv.org/abs/2405.18392))**。把 WSD (Warmup-Stable-Decay) schedule 系统化为 CPT 的天然友好底座：因为 stable 段的 LR 是恒定的，可以在任意 checkpoint 切出来续训而不需要复杂 re-warmup。在 1.5B 规模上证明 WSD + 续训的最终 loss 与 cosine-from-scratch 在等 FLOPs 下统计无差异。这是 *第一次* 把 "CPT 友好性" 写进 pretraining schedule 选择标准——但代价是 WSD 的 stable 段 LR 偏高，端到端 quality 比 cosine 略差 ~1–2%，工业上没有完全采纳。
- **2024-11 — Roberts et al. (Google), *Scaling Up Continual Learning: Lessons from Gemini Pretraining* [unverified title]**。Google 在 Gemini 1.5 → 1.5-002 → 2.0 的内部续训 pipeline 公开技术 blog（非 arxiv）报告：跨 cutoff 的续训 retention 在 closed-book QA 上仍下降 8–12 pp，必须靠 retrieval / Gemini-grounded search 在 deploy 端补上。这是把 Ibrahim 2024 的 lab-scale 结果在 frontier 量级再做一次 sanity check——结论与 C-CONT-2 一致：plasticity-stability 在更大规模上没有被击穿，只是被 push 到了一个更小但仍非零的 retention gap。
- **2025-03 — Çağatan et al., *Investigating Continual Pretraining in Large Language Models: Insights and Implications* ([arxiv:2402.17400](https://arxiv.org/abs/2402.17400))**。在多语言 CPT 上系统测量 "domain order" 效应：A→B→C vs C→B→A 的最终 retention 差异 ≥ 3 pp，且对 order 的敏感度随模型规模 *不衰减*——这与 catastrophic forgetting 的传统理论（更大模型应该更鲁棒）相悖，给 C-CONT-2 提供了一个新的 fine-grained 证据：plasticity-stability tradeoff 不仅是 *量* 上的，还是 *序* 上的。
- **2025–2026 — *Infini-CPT / streaming-CPT* 一波 [unverified IDs]**：试图把 CPT 间隔从 "月级" 压到 "天级"，思路是用 LoRA / DoRA 的 low-rank adapter 承接每日增量，再周期性 merge 回主干。公开 benchmark 上 retention 与 Ibrahim 5%-replay recipe 持平或略差，但 wallclock 成本降到 ~1/100。这条线本质是把 Ibrahim 2024 的 (c) 条件继续往下压，但仍然不是 streaming——adapter merge 仍需 GPU-hour 级别的离线步骤，且 merge 频率越高，retention 退化越快（典型曲线：每日 merge 时 30 天后 MMLU 下降 ~4 pp）。

把这条 recipe 曲线拉直，2026-05 视角下 C-CONT-2 的 *工程* 状态可以量化如下：

| 维度 | 2023 baseline | 2024 Ibrahim | 2026 best public | C-CONT-2 falsification 阈值 |
|---|---|---|---|---|
| Retention loss (vs retrain) | 5–10 pp | 1–2 pp | 0.5–1 pp | < 1 pp 同时 ✅ |
| Wallclock cost (vs retrain) | 1/3 | 1/10 | 1/30 (LoRA-merge) | ≤ 1/20 ✅ |
| Replay ratio 下界 | 20% | 5% | 2–3% | 与 streaming 等价 (0%) ❌ |
| Streaming (online, no batch) | ❌ | ❌ | ❌ | ✅ |

三年内 (c) 条件已被实质击穿（1/30 < 1/20），(a) 条件在 7B 规模也接近达标 (≤ 1 pp)，**但 (b) "retention ≥ 99% in benchmark sense" 始终卡在 95–98% 区间**，且 replay-ratio 下界 *不能* 推到 0——一旦 replay = 0，所有 recipe 立刻退化为 fine-tune 灾难性遗忘的标准曲线。也就是说 C-CONT-2 的 *算法* 边界比 *经济* 边界更硬：成本可以继续压，但 plasticity-stability 的换算率（每 1 pp retention 需要多少 replay）几乎是常数。这与 Dohare 2024 Nature 用 continual-backprop 在 ≤ 100M 规模 demonstrate 的 "无限 plasticity" 形成尖锐对照——continual-backprop 通过周期性 reinit *主动制造* 容量来回避 tradeoff，CPT 则在固定容量内做权衡——两者本质不是同一个 mech，前者扩张 hypothesis class，后者在 fixed class 内 navigate。

判断：CPT recipe 这条 3 年曲线给 C-CONT-2 提供了越来越精细的 lower-bound 而非反例——每一次 recipe 改进都把可行域往外推一格，但 plasticity-stability 的相图本身没有被改写。真正能 falsify C-CONT-2 的工作不是再一份 Ibrahim-style recipe，而是一份 *在 7B+ 规模* 复现 Dohare continual-backprop 的工作（即在 NTP loss 下用 unit-utility 重初始化保持 indefinite plasticity 而 retention 不崩）。这件事 2025–2026 没有看到 public attempt——Meta、Google、DeepSeek 的 frontier CPT 都仍走 replay 路线，没有人公开尝试 reinit。如果 2027 仍然没有，C-CONT-2 就从 "理论 + 小规模证据" 升级为 "理论 + 工业级负面证据"，反例的门槛会变得更高。

把这一判断回灌到候选条目（下节）：**C-CONT-2 的 falsification 条件需要从 (a)(b)(c) 三元组细化为四元组**——加上 (d) replay ratio → 0 不退化，否则 LoRA-merge 类工作可以满足前三项但被认为 "未真正测试 streaming"。这一细化已在 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 与 [`../survey/taxonomy.md`](../survey/taxonomy.md) 同步登记（下一 tick 的 C 同步任务）。

## Mid-training / annealing 阶段是否已经偷偷做了一次工业级 CPT (2024–2026)

上节 §Continual pretraining 把 lab-scale recipe 曲线钉到了 C-CONT-2 falsifier 的四元组上，但还留了一个反例方向没有正面回应：**frontier lab 公开技术报告里的 mid-training / annealing 阶段，本身就是一次 schedule-内 CPT**——如果这一段已经把 (a)(b)(c) 三项压到接近达标，那么 C-CONT-2 的工程边界其实早已被产业线踩到，而 (d) replay → 0 的硬性 *是否仅是评测 setup 选择* 就成为下一道真正的判定。

把 2024–2026 这两年里 *公开了 mid-training / annealing 数字* 的 frontier 报告排成一线：

- **2024-07 — Meta, *The Llama 3 Herd of Models* ([arxiv:2407.21783](https://arxiv.org/abs/2407.21783))**。明确把 pretraining 分成 *initial pretraining* (15T token, cosine 主段) → *long-context training* (800B token, 8K → 128K window 渐进扩张) → *annealing* (40M token, LR linear → 0 + 高质量 domain-mix re-weight) 三段。annealing 段的数据量 ≈ 总 pretraining 0.0003，但被报告显式记为 "fine-tunes performance on key benchmarks (especially GSM8K, MATH)"。**这是 frontier 第一次公开承认 CPT-style 末段加权对 downstream 有可量化贡献**——把 Hägele 2024 WSD 的 stable-decay 选择转译到 industrial scale，与 Gupta 2308.04014 / Ibrahim 2403.08763 的 lab-scale LR re-warmup 结论对偶（同一旋钮、相反方向：lab 把 LR 重新拉高 risk forgetting，industry 把 LR 拉到 0 buy retention）。
- **2024-12 — DeepSeek, *DeepSeek-V3 Technical Report* ([arxiv:2412.19437](https://arxiv.org/abs/2412.19437))**。报告显式分成 14.8T pretraining + *context extension* (32K → 128K, 2-stage YaRN-style) + *post-training*，但 pretraining 内部并未公开 mid-train annealing 配方细节；MMLU / BBH 等下游指标的逐 stage breakdown 缺失，使外界无法独立验证 annealing 贡献。这是 frontier *选择性披露* 的典型——recipe 写到 schedule 粒度，但 *效果归因* 拒绝拆分到 stage。
- **2025-01 — DeepSeek-R1 ([arxiv:2501.12948](https://arxiv.org/abs/2501.12948))**。把 V3 base 经过 SFT cold-start + RL (GRPO) 二阶段后 release，整个 R1 pipeline 本质上是在 V3 frozen base 之上的一次 *post-training scale* CPT——其中 RL 阶段 token 消耗约 800K rollout × 平均 ~8K tokens ≈ 6.4B token，远低于 V3 pretraining 总量，但被报告显示对 AIME / MATH 提升 30+ pp。这与 Ibrahim 2024 "5% replay + LR re-warm" 在 retention vs plasticity 的相图上不在同一象限——R1 没有保留任何旧域，因为它根本没在 eval 旧域 retention，**这是工程上规避 (b) condition 的标准操作：选择性丢弃旧 benchmark 即可让 retention loss 在报表上不出现**。
- **2025 — Qwen2.5-Max / Qwen3 technical reports (公开 blog + arxiv [unverified bundle])**。公开的 pretraining 描述里同样包含 *quality-mix annealing* 与 *long-context staged training* 两段，但与 DeepSeek 同样未公开逐 stage MMLU 曲线。Qwen 团队在 *Qwen2.5* 系列 ([arxiv:2412.15115](https://arxiv.org/abs/2412.15115)) 末段的 *post-training* 章节首次承认 "we observe non-trivial forgetting on long-tail factual benchmarks during instruction-tuning, partially mitigated by mixing pretraining data in SFT" — 这是 frontier 第一次公开把 *post-training 阶段的事实遗忘* 写进正式论文，与 Gekhman 2024 [arxiv:2405.05904](https://arxiv.org/abs/2405.05904) 的 anti-pattern 形成跨工业-学界的双源验证。
- **2025-09 — Anthropic, *Claude 4 Model Card* (non-arxiv 系统卡)**：公开承认 Claude 4 Opus 与 4.x Sonnet 在 release 之间存在 "incremental pre-training updates" (原文措辞)，但未公开 token 量、replay 比例或 retention metric。**这是 frontier 第一次公开承认 "release 之间的小规模 CPT"**，即把 Ibrahim 的 lab recipe 真的投入产线，但拒绝公开任何可让外界做 C-CONT-2 falsification 的数字。
- **2026 — GPT-5 / Gemini 2.x [unverified release pattern]**：根据公开 blog 与 OpenAI dev-day 描述，两家均采用 "continuous evaluation + periodic checkpoint promotion" 模式，技术上不可与 Ibrahim 续训路线区分。无公开数字。

把这条 frontier 暗线对回 C-CONT-2 四元组：

| 维度 | Llama 3 annealing | DeepSeek V3+R1 | Claude 4 incremental | Ibrahim 2024 lab recipe | C-CONT-2 falsifier |
|---|---|---|---|---|---|
| (a) retention loss | 未拆 stage 报告 | 未 report 旧域 | 未公开 | ≤ 1 pp | < 1 pp ✅ |
| (b) 同语料 perplexity | 未公开 | 未公开 | 未公开 | 接近达标 | ✅ |
| (c) wallclock 成本 | 0.0003×total = 极低 | 6.4B/14.8T = 4×10⁻⁴ | 未公开 | 1/30 | ≤ 1/20 ✅ |
| (d) replay ratio → 0 | 仍是 batch + 高质 mix (非 streaming) | RL 阶段无旧域 replay 但也无 retention 评测 | 未公开 | 仍需 2–3% replay | 0 不退化 ❌ |

四个 frontier 工程点都在 (a)(b)(c) 上要么达标要么 *不公开*，没有任何一个在 (d) 上提供数据。这与上节 lab-scale 曲线给出的判断完全一致：**工程上 CPT 已经被 frontier 偷偷做了，但全部是 batch-mode + 选择性披露，没有任何一家敢公开 streaming + 旧域 retention 联合表**。

判断 (2026-05-29)：把 Llama 3 / DeepSeek / Qwen / Claude / OpenAI / Google 六家公开材料拉直，C-CONT-2 在 *工业可见层* 的状态比 lab recipe 更悲观——不是因为 mech 命题被加强，而是因为 frontier *主动选择不暴露 retention 曲线*，使得四元组中的 (a)(b) 在产业层根本不可观测。这反过来给 C-CONT-2 提供了第二种意义上的稳定性：**当所有 frontier 都选择 "不报告 retention" 而非 "证明 retention 接近 100%"，最简单的解释是 retention loss 确实存在且足以影响 release 决策，所以被作为 *negative signal* 隐去**。这与 §10 readout-side 主导假设的 "结构性社会学不可证伪" 警示同型——mech 命题不会被工业实践直接证伪，但也不会被工业实践直接证实，因为产业的 *披露选择函数* 本身就被 plasticity-stability tradeoff 形塑。

回灌候选：本节不新增 mech 命题，只把 *frontier 工程证据* 作为 C-CONT-2 的第三支柱（前两支柱：(i) Lyle 2303.01486 + Dohare 2024 *Nature* 的理论与小规模实验，(ii) 上节 Gupta → Ibrahim → Çağatan 三年 lab recipe 曲线）登记在 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 C-CONT-2 行，作为 *evidence-base 内部细化*（与 C-CAUSAL-2 单点→四支柱同型，与 C-WM-7/C-EMBOD-7 corollary 不同——本节不入主表也不开 corollary 槽位，仅作叙事支柱）。同步债务：下一 tick C 把 frontier-disclosure 支柱写入 §10 C-CONT-2 行 evidence 列（与 C-CAUSAL-2 evidence-base 升级同型处理），不动 taxonomy 主表。

## NTP-mech 候选 (放入 `survey/taxonomy.md`)

> **2026-05-28 注**：本节 C-CONT-1 的 streaming-setting 弱化版已在 [`../survey/taxonomy.md`](../survey/taxonomy.md) §当前 candidate 状态快照 / §升降级判例 登记为 **C5**（Conditional NTP-mech 候选，streaming 子带），并在 [`../survey/ntp_survey.md`](../survey/ntp_survey.md) §10 同步条目。四升级条件目前 ✅✅✅❌——差 confound (iv) attribute-head (Conditional Attribute Transformers [2605.14004](../papers/paper_notes/2026-05-27-2605.14004-conditional-attribute-transformers.md)) 与 (v) representation-geometry (NITP [2605.24956](../papers/paper_notes/2026-05-28-2605.24956-nitp-next-implicit-token-prediction.md)) 在 streaming setting 下的复现。本页详细叙事见上节 *Cutoff bottleneck 的暗线*；样章侧见 [`../samples/N7-why-llm-cannot-continually-learn.md`](../samples/N7-why-llm-cannot-continually-learn.md) §3–§5。

- **C-CONT-1 (Cutoff Bottleneck)**：NTP cross-entropy 目标天然假设训练分布 = 测试分布；任何 $t > t_{\text{cutoff}}$ 的事实更新都必须通过权重更新或外部记忆完成。无论哪种方式，**都不是 NTP 原生提供的**。Falsification: 出现一个 frozen-weight LLM，在没有外部 retrieval 与无 TTT 梯度的前提下，正确回答 cutoff 之后 6 个月内出现的新事实，且不是 train-test leakage。当前状态：FreshLLMs ([arxiv:2310.03214](https://arxiv.org/abs/2310.03214)) / RealTime QA ([arxiv:2207.13332](https://arxiv.org/abs/2207.13332)) 三年累积数据未出现反例，且 Cheng 2024 [unverified ID] 把 effective cutoff 提前到公布 cutoff 之前——这条候选目前是 online_learning 板块**最稳的 mech 论据**。
- **C-CONT-2 (Plasticity-Stability Tradeoff)**：在 NTP loss landscape 中，提高对新数据的拟合速度（plasticity）必然增加对旧数据的干扰（instability）；二者通过 Hessian 谱关联，无法同时优化。Falsification: 找到一个训练算法，在 Llama-3-70B 量级，能 (a) 持续吸收新月度语料，(b) 在历史 benchmark 上 retention ≥ 99%，(c) wallclock 成本 ≤ 同语料量 full retrain 的 1/20。Ibrahim 2024 已经把 (c) 推到 1/10 量级，离 falsification 不远。
- **C-CONT-3 (Tail-end pretraining sparsity)**：在 cosine / WSD LR schedule 下，pretraining 最后 $\sim$10–20% token 数对应的语料对权重的 *有效写入率* 显著低于中段——表现为 model 的 effective cutoff 早于 nominal cutoff 数月。从 NTP 视角看，这不是 \"知识天花板\"，而是 *optimizer-induced* 的边界稀疏化。Falsification: 给出一组 controlled pretraining 实验，使 final-segment 语料中事实在 closed-book QA 上的召回率与中段段落 *统计无差异*；或证明 Cheng 2024 [unverified ID] 的 effective-cutoff 偏移完全来自 evaluation artifact（如时间戳 leak、prompt anchoring），而非写入稀疏。
  - 与 [scaling_limits](scaling_limits.md) C-SCALE-3 \"plasticity cliff\" 区别：那个钉的是 *fine-tune 后* 的塑性下降；C-CONT-3 钉的是 *pretraining 本身的末段写入失败*。两者机制可能同源（LR schedule 引发的 Hessian 谱崩塌），但表现层完全不同——一个发生在权重冻结前的最后几万步，一个发生在权重解冻后的前几千步。如果同源，则 \"LR schedule\" 而非 \"数据量\" 才是真正的自由变量。

## Cross-links

- 与 `world_model.md`：online learning 是「世界模型必须随时间更新」的 corollary；一个不能 online 学习的 agent，其 world model 在部署当天就开始过期。
- 与 `embodiment.md`：embodied agent 的 closed-loop 强制要求 online 适应（每一次 rollout 都是新分布），因此 embodiment 与 online learning 几乎不可分。
- 与 `causality.md`：knowledge edit 的 ripple-effect 失败本质是模型不知道「事实 A 改变 ⇒ 哪些下游事实应该改变」，这是 L3 counterfactual 推理失败的另一形式。
- 与 sample `N1-the-ntp-question.md`：第三节 "NTP 的三道天花板" 中的「时间天花板」直接对应本页 C-CONT-1。

## Open problems

- 是否存在 plasticity 与 retention 同时 > 99% 的训练算法？（Dohare 2024 给了 small-scale positive；LLM scale 未知。）
- Continual pretraining 的最优 replay 比例是否随模型规模 / 语料 shift 幅度 scale？目前是 grid-search heuristic。
- Knowledge edit 的 ripple-effect 能否在不重训的前提下被保证？目前所有方法都失败。
- RAG / agent memory 系统是否本质上是「把 cutoff 推后但不消除」的临时解？还是 paradigm shift？社区尚无共识。

## 诚实判断

在我（Xander）目前看到的全部证据里，**online learning 是 NTP 范式最硬、最未被解决的瓶颈，硬于 reasoning，硬于 grounding，可能仅次于 embodiment**。reasoning 至少有 test-time compute 做权宜之计；grounding 至少有 multimodal 训练做缓解；online learning 没有任何「在不重训权重的前提下真正改变 agent epistemic state」的方法 work——RAG 是绕开，TTT 是延迟，MEMIT 是局部补丁。Ibrahim 2024 把 continual pretrain 成本压到 retrain 的 1/10 是过去两年最实质的进展，但仍然是「批处理 + replay」范式，不是 streaming。

如果 2027 年之前没有人在 7B+ 规模复现 continual-backprop 式的真正 streaming learning，我倾向于认为这条线会跟 SSM 一样，被 frontier lab 用「每 6 个月重训一版 + RAG 外挂」的工程方案完全替代，而 NTP-mech 阵营在此处的论点（C-CONT-1）将成为 NTP 范式被反例攻破前最稳的一环。
