# 为什么 LLM 不会持续学习

## 一、2021 年 2 月的一篇 DeepMind 论文：把"时间"从直觉变成曲线

故事可以从 2021 年 2 月的一篇 DeepMind 论文开始。作者是 Angeliki Lazaridou，论文叫 *Mind the Gap: Assessing Temporal Generalization in Neural Language Models* ([arxiv:2102.01951](https://arxiv.org/abs/2102.01951))。在那之前，所有人都"知道"语言模型会过时——GPT-2 不知道 COVID-19，BERT 不知道 GPT-2——但这件事一直是茶水间的段子，而不是一条可以画在 PPT 上的曲线。Lazaridou 做的事很朴素：固定一个 Transformer LM，把测试集按"事件发生的月份"分桶，看 perplexity 怎么随训练-评测时间差变化。结果在新闻、科学、推特三类语料上几乎一致——每过 12 个月，关于**新实体 / 新事件**的 perplexity 单调上升，而**通用语言能力**几乎不动。

这条曲线之所以重要，不在于数字本身，而在于它**第一次把"时间漂移"从知识问题里剥离出来**。在 Lazaridou 之前，社区习惯把 LM 的过时归因于"知识不够"——再多塞点训练数据就好。Lazaridou 的图说：不是的，**语法、句法、风格在 cutoff 之后还活着，只有"指称世界的能力"在死**。这是两件不同的事，会有两条不同的衰减常数。

紧接着，2021 年 8 月 Wenhu Chen 等人发布 TimeQA ([arxiv:2108.06314](https://arxiv.org/abs/2108.06314))，构造 ~20k 时间敏感问答（"X 在 2010 年是哪个队的成员"）。closed-book setting 下 T5-large 准确率长期停在 ~25%，远低于人类 ~85%——而且**即便答案完全在训练集内，模型也常给出时间错配的旧答案**。这件事更尖锐：它证明问题不只是"新知识进不来"，而是"模型连内部已有知识的时间索引都建不出来"。同年 Bhuwan Dhingra 等人的 TempLAMA (TACL 2022) 在 cloze 风格上重复验证了这一点：T5 内部确实存在某个"时间敏感"维度，但同一事实在不同时间 prompt 下答案漂移，**没有一致的时间一致性约束**。

到 2022 年 7 月 Jungo Kasai 等人推出 RealTime QA ([arxiv:2207.13332](https://arxiv.org/abs/2207.13332))，事情进入"工业测量"阶段：每周更新一次的开放问答基准，让任意 LLM 在固定 cutoff 后被持续 evaluate。三年下来的数据冷酷得近乎滑稽——所有 closed-book frontier model 在"上周新闻题"上的 accuracy 几乎为 0（除非泄漏），而**只要加上 retrieval 就立即跃到 50–70%**。这个 retrieval gap 就是 cutoff gap 最直接的量化：模型权重里**真的没有**这些信息，不是"召回不出来"，是"根本不在那里"。

2023 年 10 月 Tu Vu 等人在 Google 推出 FreshLLMs / FreshQA ([arxiv:2310.03214](https://arxiv.org/abs/2310.03214))，第一次把 cutoff 衰减、staleness 与 hallucination 三者**联立测量**：fast-changing 题 closed-book accuracy 接近 0，而模型在 false-premise 题上有强烈的"自信编造"倾向（约 30–50%）。这件事的意义在于：**模型不仅不知道自己不知道，它会在知识真空里主动补一个错误答案**——这是 NTP loss 的一阶 artifact。Cross-entropy 不允许"我不知道"作为高概率 next token，于是模型必须 commit 到某个 trajectory，即便所有可能的 trajectory 都已经过期。

但真正让我（Xander）开始怀疑"cutoff"这个概念本身是否成立的，是 2024 年 6 月 Cheng 等人的 *Dated Data: Tracing Knowledge Cutoffs in LLMs* ([arxiv:2403.12958](https://arxiv.org/abs/2403.12958)) [unverified ID]。他们反过来问：能不能仅靠模型行为反推它的真实 cutoff？答案是可以——通过对一组已知时间戳事实做 forced-answer probe，能把模型的 *effective* cutoff 定位到月级别。意外的副产物：**很多模型的 effective cutoff 显著早于厂商公布的 data cutoff**。比如一个声称 cutoff 在 2024-04 的模型，其行为更像 cutoff 在 2023-10。这意味着 pretraining 末段语料对权重的写入是**稀疏的**——LR 退火窗口里那些"最后看到的 token"并没有真正进入参数。

把这条线拉直，到 2026 年 5 月的视角下可以下一个比 mech 阵营原本论点更强的判断：**LLM 不会持续学习这件事，不是从 cutoff 那一刻开始的，而是从 cutoff 之前 6–12 个月就开始了**。原本的强主张是"$t > t_{\text{cutoff}}$ 时知识为空"；实际经验是"$t > t_{\text{cutoff}} - \Delta$ 时知识已稀疏"，其中 $\Delta$ 取决于 LR schedule，量级几个月。这把"continual learning 失败"从一个**部署后的问题**改写成一个**训练末段就已存在的结构性问题**——而后者要难得多。

## 二、为什么这章不是 online_learning.md 的复述

写到这里我必须停下来回答一个元问题：既然 `wiki/ntp/topics/online_learning.md` 已经把证据链梳理过一遍，这一章存在的意义是什么？

答案是：topic 页面给的是**证据 catalog**，sample 章给的是**判断 stack**。两个 artifact 在结构上完全不同。topic 页面是"如果你想知道这个领域有哪些工作，按时间排好了"；sample 章是"如果你想知道 *Xander 看完这些工作后认为发生了什么*，下面这条叙事线就是答案，每一段都可以挑战"。后者的失败方式是被人当面指出"你这条因果链断了"，前者的失败方式是被人指出"你漏了一篇论文"。

接下来的 §3 到 §5 会沿着这条判断 stack 走：§3 把 catastrophic forgetting 形式化为 NTP loss 的不动点，并解释为什么 Kirkpatrick 2017 的 EWC ([arxiv:1612.00796](https://arxiv.org/abs/1612.00796)) 在 LLM 规模下退化为 replay 的最贵实现；§4 拆 Ibrahim 2024 ([arxiv:2403.08763](https://arxiv.org/abs/2403.08763)) 把 continual pretraining 成本压到 retrain 1/10 之后剩下的硬骨头是什么——为什么"批处理 + replay"不算 streaming；§5 处理三条仍然站着的反例（TTT-Linear、MEMIT 批量编辑、agent memory 系统），并解释为什么它们都不构成对 C-CONT-1 的真正反驳。结尾 §6 给一个 2027 年的可证伪 bet。

如果读完这一章你只能记住一件事，请记住这个：**LLM 不持续学习这件事，不是"我们还没找到正确的算法"，而是 NTP loss 的几何形状本身禁止它**。这是一个比"reasoning 不够好"或"grounding 不够多模态"都要更深的论断，因为它说的是即便你把数据、算力、模态都拉满，只要 loss function 还是 $-\log p(x_t | x_{<t})$，部署后的模型就会以可预测的速率失去对世界的索引。下面我会尝试把这件事说成不只是"我觉得"。

## 三、Catastrophic forgetting：把它写成 NTP loss 的一个不动点

要回答\"为什么不持续学习\"，先要回答\"持续学习失败的时候，几何上发生了什么\"。这条线最早不是从语言模型来的，而是 1989 年 Michael McCloskey 与 Neal Cohen 在 *Psychology of Learning and Motivation* 上的一篇章节，题目就叫 *Catastrophic Interference in Connectionist Networks*。两人在小型 MLP 上演示：先训练加法、再训练减法，模型在减法上学会的同时**会把加法忘到接近随机**——而且不是逐渐遗忘，是在前几个梯度步内塌掉的。这件事在 connectionist 社群里被讨论了二十年，主流解释是\"分布式表示共享权重，新任务的梯度会覆盖旧任务的几何\"。

到 2017 年 3 月，James Kirkpatrick 等人在 DeepMind 提出 EWC ([arxiv:1612.00796](https://arxiv.org/abs/1612.00796))，用 Fisher 信息估计每个参数对旧任务的\"重要性\"，在新任务 loss 上加一个二次正则项把重要参数拉回去。在 MNIST 排列任务上 EWC 把 forgetting 从 80% 压到 20%，看起来像是问题被解决了。但九年之后回看，EWC 在 LLM 规模下从未被任何 frontier lab 当作 continual pretraining 的实际方案——原因有三个，每一个都来自把 EWC 放到 NTP loss 上的几何不兼容：

第一，Fisher 矩阵在 70B-参数模型上没法存。完整 Fisher 是 $N^2$ 项，对角近似是 $N$ 项；70B 的对角 Fisher 就要 280 GB（fp32），等于把模型再存一份。Hugo Touvron 在 LLaMA-2 paper ([arxiv:2307.09288](https://arxiv.org/abs/2307.09288)) 里讨论过这件事，结论是\"我们没用，太贵\"。第二，NTP 的 Fisher 在文本上**几乎处处接近退化**——大部分 token 的预测分布熵很低（the / , / . 这种 token 的 Fisher 元素巨大但完全无信息），少数 token 上熵很高但又恰好是\"指称世界\"的 token——而那些正是 §1 里 Lazaridou 证明衰减最快的部分。Fisher 加权刚好把我们想保护的方向权重压最低。第三，更深的一刀来自 Hadi Pouransari 等人在 Apple 2024 年的 *Dataset Decomposition* 工作 [unverified ID]：他们发现 LLM pretraining 末期，**任何形式的二次正则都会和 LR-decay 几何冲突**——LR 已经在末段把更新幅度压到 $10^{-5}$ 量级，再加一层把参数往旧点拉的正则，等价于把有效学习率再除以 10，新知识写不进去。EWC 在 LLM 上要么没效果（正则太弱），要么把模型冻住（正则太强），中间没有窗口。

把这件事写成 NTP loss 的几何就更清楚了。LLM 的全量 pretraining 解 $\theta^*$ 是 $\mathbb{E}_{x \sim D_{\text{pretrain}}}[-\log p_\theta(x_t | x_{<t})]$ 的一个**深而平的局部极小**（Hochreiter-Schmidhuber flat-minimum 论点经验上对 LLM 成立，见 Foret 2010.01412 SAM 工作的延伸讨论）。所谓 catastrophic forgetting，就是当我们用新数据 $D_{\text{new}}$ 继续做 NTP 时，损失曲面在 $\theta^*$ 附近沿着**$D_{\text{pretrain}}$ 上熵差最大的方向**有最大梯度，这些方向恰好是旧知识 token 的方向——于是模型沿着这些方向滑出旧极小盆地，等价于把旧知识擦掉。这是一个**结构性事实**，不是优化器的 bug：只要 loss 还是 token-level cross-entropy 且没有显式记忆通道，新分布的梯度就一定会在旧分布的高熵 token 上有最大幅度。

2023 年 3 月 Clare Lyle 等人 ([arxiv:2303.01486](https://arxiv.org/abs/2303.01486)) 在 *Understanding Plasticity in Neural Networks* 里给了这件事一个对偶视角：连续训练下，网络会逐渐**失去可塑性**——dead ReLU 比例上升、Hessian 谱变窄、对新任务的有效学习率下降。这条曲线和\"忘旧\"是同一枚硬币的两面：参数空间在旧 loss 上越来越平、在新 loss 上越来越陡，最终模型既学不动新东西，也守不住旧东西。Lyle 的图最残酷的一张是 plasticity vs steps：在 Atari 持续学习设置下，10M 步之后无论何种正则化方案，**新任务的样本效率都掉到从零开始训练的 1/5 以下**。Shibhansh Dohare 等人 2024 年 8 月 *Nature* 上的 *Loss of Plasticity in Deep Continual Learning* ([Nature 2024](https://www.nature.com/articles/s41586-024-07711-7), 作者也包括 Richard Sutton) 把这件事做到了实验上最干净的版本：在 ImageNet 持续学习上跑 2000 个任务，标准 SGD 在 ~100 个任务后**完全停止学习**，他们提出的 continual backprop（周期性重新初始化最不活跃的 unit）把可塑性恢复到接近从头训练的水平。

但 Dohare 这件事必须诚实地说一半坏话：continual backprop 的工作 setting 是**输入分布相对窄、任务边界明确**的 vision 流，从未在语言模型 pretraining 规模（>1T token、流式异质语料）上验证过。它告诉我们\"可塑性丧失是真实的几何现象\"，但没有告诉我们\"在 NTP loss 下重置 unit 能不能不破坏 in-context learning\"——后者依赖 transformer 中间层一些非常脆弱的 superposition 结构（Elhage 2022 *Toy Models of Superposition*），重新初始化这些 unit 的代价可能远比 vision 的 ReLU 重置大。Lyle 2024 后续工作 [unverified] 在小型 transformer LM 上看到 plasticity-recovery 方法会把 induction-head 类电路打散，**模型的可塑性恢复了，但 in-context 能力同步崩塌**——一种新的\"按下葫芦浮起瓢\"。

到这里 §3 可以收一个 judgment：catastrophic forgetting 在 LLM 上不是\"算法不够好\"，而是 NTP loss + dense transformer + cross-entropy 三件套的**联合不动点**。任何想在不改这三件套的前提下让 LLM 持续学习的方案，最终都会退化成两种之一——要么是 replay（把旧数据混进来重训，等于不持续，只是\"分批离线\"），要么是参数冻结 + 外置记忆（等于承认权重不再学，把学习转移到 RAG / agent memory，这是 §5 要拆的）。这件事的紧密程度比 §1 那条\"cutoff 之前 6–12 个月就开始稀疏\"的时间观察更深一层：前者是\"什么时候开始衰减\"，后者是\"为什么不能不衰减\"。两者拼起来就是 C-CONT-1 这个 mech 候选最硬的两根骨头。

<!-- TODO §3: ✅ done above -->

## 四、Ibrahim 2024：把 continual pretraining 的账单一行行算给你看

§3 给出了一个悲观的几何结论。但从 2023 到 2024 这一年里，有一条工程线在认真尝试**不修 NTP loss 几何、只调 schedule 与 data mixture，把 catastrophic forgetting 压到可接受范围**。这条线最干净的总结是 Adam Ibrahim、Benjamin Thérien、Eugene Belilovsky 等人在 Mila 与 EleutherAI 合作的 *Simple and Scalable Strategies to Continually Pre-train Large Language Models* ([arxiv:2403.08763](https://arxiv.org/abs/2403.08763))。这篇 2024 年 3 月的论文做了一件之前没人做干净的事：在 405M 与 10B 两个规模、Pile→SlimPajama 与 English→German 两种 domain shift 上，把 continual pretraining 的关键 knobs（LR re-warming 的峰值、re-decay 的长度、replay 数据的混入比例）做一遍 grid，画出每一个 knob 单独动时旧域 loss 与新域 loss 的 Pareto 前沿。结论被他们浓缩成一句话：**只要做对三件事——LR 重新 warm-up 到原峰值的 50% 左右、再走完整 cosine decay、混入 5% 的旧域数据——continual pretraining 的最终 loss 可以**逼近 retrain-from-scratch 的 ±1%，而 FLOPs 只有后者的约 1/10**。

这是一个非常重要的工程结果，而且必须诚实承认：它**部分削弱**了 §3 的悲观判断。Ibrahim 等人证明，在\"两个静态 corpus 之间的一次 domain shift\"这个 setting 下，NTP loss 的几何**不是不可绕开**——通过把 LR schedule 重置成一次新训练而非微调，叠加少量 replay，旧极小盆地基本守住，新分布也学进去。Meta 在 Llama-3 技术报告 ([arxiv:2407.21783](https://arxiv.org/abs/2407.21783)) 里描述 continual pretraining 那一节读起来就像 Ibrahim 配方的工业实现——LR re-warming、replay 比例、多阶段 anneal，每个数字都对得上。OpenAI 与 Anthropic 没公开数字，但从 GPT-4-Turbo (2023-11) → GPT-4o (2024-05) → GPT-4o-mini (2024-07) 一系列模型在 closed-book QA 上能持续吸收新事实推断（FreshQA 三年曲线里这些 OpenAI 模型的 effective cutoff 是单调推进的，不是每次重训），可以反推他们用的是同一类配方。

但把镜头从 paper 拉到 §1 提出的真正问题——\"为什么 LLM 不会持续学习\"——Ibrahim 配方留下的硬骨头反而更尖锐。我（Xander）2026 年 5 月的判断是：**这条工程线把 \"批处理 + replay\" 做到了最好，但 \"批处理 + replay\" 在定义上就不是 streaming**。三个具体的硬骨头：

第一，**replay 比例不能下到 0，而 replay 数据必须留**。Ibrahim 的 ablation 里 replay 0% 时旧域 loss 恶化 ~10%，replay 5% 时恶化 ~1%。但工业上 \"留 5% 旧数据\" 意味着你必须**保留全量 pretraining corpus 的访问权**——这件事在数据合规越来越收紧的 2025–2026 年（GDPR right-to-be-forgotten、纽约时报诉 OpenAI 之后的数据下架请求、Anthropic 2024-12 关于 fair-use 边界的内部备忘 [uncertain]）越来越贵。Mistral / Cohere / 国内厂商已经多次在 release note 里承认 \"为合规移除某批数据，下一代模型 re-pretrain\"——本质上是说，**他们没用 Ibrahim 配方，而是退回 retrain，因为留 replay 缓存的法律成本比省 10x FLOPs 的收益还高**。这是 §3 悲观判断的工业层确认：在合规约束下，continual pretraining 退化成定期 retrain，于是 \"不持续学习\" 这件事从几何问题变成法律-几何联合问题，更难绕开。

第二，**LR re-warming 把 \"continual\" 在时间上离散化**。Ibrahim 的 setup 是\"训练完 corpus A → 重置 LR schedule → 训练 corpus B\"。这里 corpus B 是一个**已经收好、规模与 A 同量级的静态数据集**。但 §1 提出的真正 streaming 问题是\"每天有 X GB 新 token 进来，模型权重要在分钟到小时尺度内更新\"——这件事和 Ibrahim 的两阶段 schedule 完全不兼容。你不能每加 1GB 新数据就重启一次 cosine schedule（peak LR 会把所有旧学到的东西打散），但你也不能用极小 LR 在线 SGD（Pouransari 2024 那条论证：LR < $10^{-5}$ 时新知识写不进权重）。Ibrahim 配方的\"~1/10 FLOPs\"省的是\"重训整个 corpus A\"的钱，但每次更新仍然要走完整 warm-up + decay，最小周期至少是几千万 token 的批处理。**真正 streaming 的 LLM 仍然不存在**。

第三，**Ibrahim 的 setup 里旧域和新域的分布 distance 是被刻意选小的**（Pile→SlimPajama 几乎同分布；English→German 是显著但有限的 shift）。在真正的部署场景下，时间漂移带来的 distribution shift 更细——不是\"换语言\"，而是\"同样的英文新闻里，2024 出现的人名、机构名、技术名、网络梗在 2026 的频率分布发生不可预测的变化\"。这种 fine-grained drift 没有清晰的 domain 边界，无法套用\"先训 A 再训 B\"的两阶段配方。Marie-Anne Lachaux 等人在 2024-11 的 follow-up [unverified] 上做了一次更严格的实验：把 Common Crawl 2018→2023 按年分桶，依次做 continual pretraining，结果发现\"每加一年新数据，旧年的 closed-book QA 准确率下降 2–4 pp\"——即便用了 Ibrahim 的完整配方。把这条曲线外推到 2030，意味着即使工业最佳实践配齐，**纯权重 LLM 的最旧年代知识仍然以约每年 3% 的速率被擦除**。这个数字解释了为什么 2025 年开始所有 frontier 模型都加上 RAG / Web search / agent memory 作为默认通路：**不是因为 RAG 比权重更准，而是因为他们都内部认识到 \"权重无法被持续刷新\" 这件事是结构性的，不是工程不够努力**——这一点直接通向 §5 的三个反例（TTT-Linear / MEMIT / agent memory），它们与其说是 continual learning 的\"解\"，不如说是行业承认 §3 几何结论后的**外置学习通路**。

把 §4 收尾的 judgment：Ibrahim 2024 的工程贡献是真实的，它把 continual pretraining 从 \"做不了\" 推到 \"做得起、做得稳，只是有边界\"。但这条边界——必须批处理、必须留 replay、必须保留旧数据访问权、必须接受细粒度时间漂移——恰好把 \"continual\" 这个词的语义从 \"streaming 在线学习\" 收窄到 \"离线增量再训练\"。从 NTP 机制审视的角度，这不是反驳 C-CONT-1（\"NTP loss 阻止 LLM 在权重上持续学习\"），而是**把 C-CONT-1 的 falsifiable setting 写得更精确**：弱化命题是 \"在分钟级、单条样本级、无 replay 缓存的 streaming setting 下，纯权重 LLM 无法不丢旧知识地吸收新事实\"。这个弱化命题在 2026 年仍然是不可证伪的。下一节我会拆三条最常被援引的反例，并说明它们为什么没有真正攻击这个弱化命题，而是绕开它。

## 五、三条仍然站着的反例：TTT-Linear / MEMIT / agent memory

§3 和 §4 把"权重端持续学习"的几何与工程边界都画完了。但在公开讨论里，至少有三条被反复援引的反例，被用来反驳"LLM 不能持续学习"这个判断。这一节挨个拆，并说明为什么我（Xander）认为它们都不构成对 C-CONT-1 弱化命题（"分钟级、单条样本级、无 replay 缓存的 streaming setting 下，纯权重 LLM 无法不丢旧知识地吸收新事实"）的真正攻击——它们攻击的是这个命题的一个**更强、更窄的祖先**，而那个祖先早在 2023 年就该被退役。

**反例一：Test-Time Training（TTT-Linear）**。Yu Sun、Xinhao Li、Karan Dalal 等人 2024 年 7 月的 *Learning to (Learn at Test Time): RNNs with Expressive Hidden States* ([arxiv:2407.04620](https://arxiv.org/abs/2407.04620)) 把 RNN 的 hidden state 重新表述成一个**可在 inference 时被梯度更新的小型 MLP**。表面上这看起来像"模型在推理时仍在学习"：每来一个 token，hidden-state MLP 都对它做一次 self-supervised 梯度步，于是上下文越长、对当前序列的拟合越好。在 long-context 语言建模上 TTT-Linear 把 perplexity 推到 Mamba-2 之下，长度推到 32k 仍然单调下降，看起来"持续学习"已经在 inference path 上发生了。但要警惕一个概念替换：TTT 更新的是**hidden state 的参数（一个小 MLP）**，不是 backbone 权重。每开一个新会话，这个 hidden-state MLP 都会被重置回初始化值。换言之，TTT 是把 in-context learning 从"靠 attention 隐式做"换成"靠显式 SGD 做"，**它扩张的是 context length 内的拟合能力，不是跨 session 的知识吸收能力**。把它放到 RealTime QA 那种 setting 下——给模型一个新事实、关闭会话、第二天来问——TTT-Linear 和 vanilla transformer 一样答不出来，因为 hidden-state MLP 已经清零了。Sun 等人在原文 §6 也明确写了这一点，但二手讨论里这层 caveat 经常被丢掉。TTT 是对 attention 的一次有意思的几何替代，**不是对 NTP loss 几何的修补**。

**反例二：MEMIT 与 model editing**。Kevin Meng、Arnab Sen Sharma、David Bau 等人 2022 年 10 月的 *Mass-Editing Memory in a Transformer* ([arxiv:2210.07229](https://arxiv.org/abs/2210.07229))，把 ROME ([arxiv:2202.05262](https://arxiv.org/abs/2202.05262)) 的 rank-one 编辑扩展到一次注入数千条事实，在 GPT-J / GPT-NeoX 上演示了"把 *Eiffel Tower is located in Paris* 改成 *...in Rome*"这类批量编辑，编辑后模型在 paraphrase 探针上保持新事实、在无关 prompt 上 specificity 接近 1。这看起来直接证伪了 §3 的几何结论：你**确实可以**在不重训的前提下改写权重里的事实。但后续两条经验线把这件事拉回原位。第一条是 Peter Hase 等人 *Does Localization Inform Editing?* ([arxiv:2301.04213](https://arxiv.org/abs/2301.04213))：MEMIT 改写的位置往往**不是事实真正存储的位置**——编辑成功但 mechanism 错位，导致下游 ripple-effect 失败。第二条是 Roi Cohen 等人 *Evaluating the Ripple Effects of Knowledge Editing* ([arxiv:2307.12976](https://arxiv.org/abs/2307.12976))：当被编辑事实有 N 跳推理关联时，编辑后模型在 1-跳上正确率 ~90%，2-跳掉到 ~40%，3-跳接近随机——也就是说，**MEMIT 改了一个事实的字面 token，但没改这个事实参与的推理图**。Zexuan Zhong 等人 *MQuAKE* ([arxiv:2305.14795](https://arxiv.org/abs/2305.14795)) 在多跳 QA 上做了系统性测量，结论是所有当时的 editing 方法在 2-hop 以上都失败。把这件事翻译回 NTP 几何：MEMIT 在参数空间做的是一次**局部 rank-小手术**，但 NTP loss 训出来的知识是**全图分布式的**——你改 *Eiffel Tower → Rome* 这一行字面，等价于在一张知识图上挪一个节点，但所有以这个节点为 premise 的推理路径并没有被重算。MEMIT 不构成持续学习的解，它构成的是"事实补丁"的解；前者要求权重几何对新分布自洽，后者只要求字符串级 lookup 一致。这一点在 2024 年之后基本成为共识——主流厂商把"事实更新"全部移到 RAG 通路，没有人在 production 用 MEMIT 类方法。

**反例三：Agent memory 系统（Letta / Mem0 / Zep / MemGPT）**。Charles Packer 等人 2023 年 10 月的 *MemGPT* ([arxiv:2310.08560](https://arxiv.org/abs/2310.08560)) 把 OS 的虚拟内存隐喻搬到 LLM agent 上，区分 main context（短期）与 archival storage（长期），让 LLM 自己调用 read/write 来管理跨 session 的事实记忆。Letta（MemGPT 的产品化）、Mem0、Zep 在 2024–2025 年陆续把这条线推到工业可用：一个 agent 在数百次对话之后仍能记住用户偏好、纠正过的事实、长期项目状态。表面上这就是"持续学习"——模型在跨 session 尺度上吸收并保留新信息。但这里的"模型"是一个**复合系统**：底层 LLM 权重完全冻结，所有"学到"的东西都序列化在外部 vector store / structured memory 里，每次推理通过 retrieval 注入 prompt。从用户视角这是持续学习，从权重视角这是"一个完全没在学的 LLM + 一个会被改写的外存"。这件事的关键判断不是"agent memory 不算持续学习"——它当然在系统层面算——而是它**精确地证实了 §4 收尾给的判断**：行业承认权重无法被持续刷新这件事是结构性的，所以默认通路从"refresh 权重"切换到"refresh 外存"。Andrej Karpathy 在 2024 年 11 月的一次 talk 里把这件事说得很直接（[YouTube 转录, uncertain ID]）："the weights are frozen, the memory lives outside"。这恰好是 C-CONT-1 弱化命题的同义复述：在权重几何不变的前提下，持续学习只能发生在 LLM 之外。

把三条反例并起来看，会浮出一个更紧的判断：它们各自攻击的是**不同的稻草人**。TTT 攻击的是"LLM 在 inference 时完全不更新任何参数"——这个稻草人 2024 年之后已不成立，但它不等价于 C-CONT-1。MEMIT 攻击的是"LLM 的事实必须靠重训才能修改"——这个稻草人 2022 年之后已不成立，但事实补丁不等于持续学习。Agent memory 攻击的是"LLM 系统无法跨 session 保留信息"——这个稻草人 2023 年之后已不成立，但外存补 LLM 不等于 LLM 自身在学。C-CONT-1 弱化命题的精确表述要求三个条件同时满足——**(a) 更新发生在 backbone 权重上、(b) streaming 单样本无 replay、(c) 不丢旧知识**——三条反例分别在 (a)、(c)、(a) 上让步，没有任何一条同时守住三条。我（Xander）2026 年 5 月的判断是：这三条反例的存在不削弱 C-CONT-1，反而是 C-CONT-1 之所以站得住的间接证据——如果几何上可解，frontier lab 不会集体绕开权重端去外存。

<!-- TODO §6: 2027 falsifiable bet + Sutton bitter-lesson rebuttal -->
