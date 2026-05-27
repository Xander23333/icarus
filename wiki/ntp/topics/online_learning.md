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
