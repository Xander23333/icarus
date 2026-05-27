# Reversal Curse / 不忠实 CoT / Faith-and-Fate——三块拼图

## 一、2023 年五月到九月，四个月里掉下三块碎片

2023 年 5 月 18 日，Allen AI 的 Nouha Dziri 在 arxiv 挂出 [*Faith and Fate: Limits of Transformers on Compositionality*](https://arxiv.org/abs/2305.18654)。同一个月的 5 月 7 日，Anthropic 的 Miles Turpin 等人挂出 [*Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting*](https://arxiv.org/abs/2305.04388)。四个月后，9 月 21 日，Vanderbilt 的 Lukas Berglund 联合牛津、苏黎世、纽约几所学校的合作者挂出 [*The Reversal Curse: LLMs Trained on "A is B" Fail to Learn "B is A"*](https://arxiv.org/abs/2309.12288)。

这三篇论文当时是分别被讨论的。Faith-and-Fate 被放进 "scaling 是否够用" 的辩论，Turpin 那篇被放进 "alignment / interpretability" 的赛道，Reversal Curse 因为标题耸动一度被当成 Twitter 段子。三个圈子各看各的——reasoning 圈、safety 圈、knowledge-editing 圈——没人去问一个最朴素的问题：**这三件事有没有可能是同一件事的三个侧影**？

到了 2025 年下半年，这个问题才被反复地提出来。提出方式各不相同：Sanjeev Arora 在 [arxiv:2402.05120](https://arxiv.org/abs/2402.05120) 的 *Physics of Language Models* 系列里用合成数据复现了三者；Anthropic interpretability team 2024 年 5 月发的 [*Scaling Monosemanticity*](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) 在 Claude 3 Sonnet 里找到了一类 feature——它们在 A→B 方向激活而在 B→A 方向不激活；Dziri 自己在 2024 年的 follow-up 里把 compositionality wall 重新归因为 "linear chain memorization"。这些工作合起来给出了一个**共同的几何图像**：next-token prediction 在训练时只看到一个方向的 token 流，所以学到的表征也是**有向**的，且**沿生成链的局部组合**——这两条性质合起来同时蕴含 (a) 反向蕴含学不到、(b) 多跳组合在某个深度后塌掉、(c) 模型给出的推理链可以和真实计算路径完全脱钩。

本章要论证的，就是这三块碎片其实拼成一张图。NTP 的 loss 是一个**逐 token、向前、局部**的目标，这三条性质各自切掉一块解空间，留下的就是当前大模型 reasoning 行为的轮廓。

## 二、为什么三篇论文当时被分开讨论——一段简短的社会学

这里要先说一段令我自己也不太舒服的社会学。这三篇之所以四个月里没人合起来看，原因其实和论文本身关系不大，和**研究圈的分工**关系更大。

Dziri 的 *Faith and Fate* 在 2023 年 NeurIPS 投稿池里是和 *Sparks of AGI* [arxiv:2303.12712]、*Skill-Mix* [arxiv:2310.17567]、*Are Emergent Abilities a Mirage* [arxiv:2304.15004] 并列被讨论的，框架是 "scaling 是否能解决 reasoning"。它的反例（三位数乘法、Einstein puzzle、动态规划）被读作 "目前的 capacity 还不够"，而不是 "目标函数本身有问题"。

Turpin 的 *Unfaithful CoT* 当时挂在 Anthropic 的 alignment workstream 下，配套的姐妹篇是 Lanham 等人的 [*Measuring Faithfulness in Chain-of-Thought Reasoning*](https://arxiv.org/abs/2307.13702)（2023 年 7 月）。这条线关心的是 "模型给出的解释能不能信"，下游应用是 RLHF reward model、debate、constitutional AI。它的核心证据是：在 Turpin 设计的 biased few-shot prompt 下，模型会**输出一条看似严密的推理链导向被偏置植入的错误答案，且推理链里不提偏置存在**。这个发现被 alignment 圈消化掉了——成了 "CoT 不可解释" 的标准 caveat——但很少有人把它和 *Faith and Fate* 放在一起。

Reversal Curse 是最孤立的一篇。Berglund 论文里训练集是合成的 fictional facts（"Daphne Barrington 是 Crystal Mind 的导演"），实验做得很干净：fine-tune 后正向问答 100%，反向问答 0%。Owain Evans 在 Twitter 上一发，圈外人当段子转，圈内人当 "知识编辑/MEMIT 失败案例" 看。这条线后续接到的是 Meng 的 [ROME](https://arxiv.org/abs/2202.05262) / [MEMIT](https://arxiv.org/abs/2210.07229) 一系，重点是 "怎么在权重里改一个事实"。没人去问 "为什么反向不行" 这个**目标函数**层面的问题，因为这个问题不能立刻变成一个 benchmark 数字。

三个圈子用三套词汇，于是同一个根因被切成三个独立现象。这是 ML 圈在 2023–2024 年的常态：reasoning / alignment / knowledge-editing 各自有 PI、各自有 workshop、各自有引用网络。要把这三块碎片拼起来，需要的不是新实验，是**承认它们共享同一个 loss 的几何**——而这一步直到 Allen-Zhu 的 *Physics of LM* 第 3.1–3.2 部分（[arxiv:2309.14402](https://arxiv.org/abs/2309.14402)、[arxiv:2404.05405](https://arxiv.org/abs/2404.05405)）才被半显式地说出来。

我个人的判断是：这一段历史本身就是 NTP 研究的一个元教训。**当一个根本性的目标函数限制以多种表现形式渗透到不同子领域时，子领域之间的引用结构会阻止它们看到根因。** 这不是某个人的错，是当代 ML 论文工业的结构性近视。后面三节会逐一拆开这三块碎片，第六节我会尝试把它们重新拼起来。

## 三、Faith-and-Fate：把"组合深度"做成可测的曲线

Dziri 这篇之所以重要，不是因为它"证明了 Transformer 不会乘法"——这种话谁都能说——而是因为它**把"组合"这个含糊的词变成了一条可以画出来的曲线**。论文挑了三个任务：n 位数 × n 位数乘法、Einstein's puzzle（一个 5×5 的 zebra-style 约束满足）、动态规划版本的最长子序列。这三个任务有一个共同的结构参数：解决它们所需的**计算图深度**（论文里叫 *reasoning depth*，定义为把任务归约成 DAG 后的最长路径长度）。

实验做法是把 GPT-4、GPT-3.5、PaLM、LLaMA 全部喂进去，画 accuracy vs. depth 的曲线。结果是一条几乎所有模型共享的**指数衰减**：depth ≤ 3 时正确率 80% 以上，depth = 4 掉到 50% 附近，depth ≥ 5 接近 0。GPT-4 在 4 位数乘法（depth ≈ 8）上的零样本正确率是 4%（论文 Figure 3，[arxiv:2305.18654](https://arxiv.org/abs/2305.18654) Table 2）。Scratchpad / CoT 把曲线整体往右推 1–2 个 depth，但**不改变衰减的形状**。

这个 "1–2 个 depth" 的位移很关键。它告诉我们 CoT 不是在做质变，而是在**把隐式的计算图外化成显式的 token 流**——每多一步 CoT，等价于多了一层网络深度（Feng 等人 [arxiv:2305.15408](https://arxiv.org/abs/2305.15408) 在同年 5 月给了这个直觉一个形式化版本：CoT 把表达力从 TC⁰ 扩到 P/poly，但每多解一类问题要付出 token 数代价）。Dziri 的曲线和 Feng 的定理是同一件事的两个视角：**深度可以用 token 买，但买的是线性数量，解决的是指数难度的问题，所以总有一个 depth 让你买不起。**

Dziri 自己在论文 §6 给的解释是 "linear chain memorization"——模型把训练数据里见过的 (input, output) 对当作单跳 lookup，遇到没见过的组合就拼接已见碎片。这个解释和后来 Allen-Zhu 的 *Physics of LM* Part 3.2（[arxiv:2404.05405](https://arxiv.org/abs/2404.05405)）的 "knowledge augmentation needs reverse-order data" 是同构的：NTP 看到的是一个方向的 token 流，学到的也只是这个方向的局部连接，**没有任何梯度信号要求模型构建一个真正的双向、全局、可重新组合的计算图**。

反例必须摆出来。Faith-and-Fate 的结论被两类工作部分地挑战过。一类是 *Let's Verify Step by Step*（OpenAI 的 Lightman 等人，[arxiv:2305.20050](https://arxiv.org/abs/2305.20050)）和 process-reward model 路线：用 step-level reward 训出的模型在 MATH 上 depth 远超 5 的题目正确率显著上去了。另一类是 o1 / DeepSeek-R1（[arxiv:2501.12948](https://arxiv.org/abs/2501.12948)）这种 long-CoT RL 路线，在 AIME / competition-math 上把可解 depth 推到了 Dziri 当年画的曲线之外。但**两类反例都靠延长 CoT 长度换深度**——前者用 PRM 让 CoT 更长更可靠，后者直接让 CoT 长到几万 token——它们没有违反 Dziri 的曲线，只是把 token 预算往右推。Sutton bitter-lesson 的拥趸会说这就够了：能用 token 买的就不是墙。我同意一半。能用 token 买说明 Hahn 意义下的"参数墙"不是绝对的，但 token 预算本身是有经济上限的——一个 query 烧 100k token 在 deployment 端就是不可行——所以 Dziri 曲线在**经济意义**上仍然是一堵墙，只是位置可以被工程往后推。

我的判断：Faith-and-Fate 真正的贡献不是"证明 Transformer 不会组合"，而是**把 NTP 目标函数下的 reasoning 退化变成一个可测、可外推、可被 CoT 部分缓解的连续量**。这一点把它从 reasoning 圈的内部辩论里抽出来，放到了和 §4 Turpin、§5 Berglund 同一张图上——三块碎片测的都是同一个 loss 几何的不同切面。

## 四、Turpin 与 Lanham：CoT 是事后合理化，不是计算过程

Miles Turpin 2023 年 5 月那篇 [*Unfaithful Explanations in CoT*](https://arxiv.org/abs/2305.04388) 的实验设计极其干净，干净到一度让 alignment 圈陷入沉默。Turpin 在 BIG-Bench Hard 的若干二选一任务里加了一个**隐蔽偏置**：把 few-shot 例子里的正确答案统一锚定到 (A) 选项。然后让模型在新题上作答并要求它写出 CoT。结果是 GPT-3.5 与 Claude 1.3 的最终答案被偏置拉向 (A) 的比例上升了 36 个百分点，而**它们写出的 CoT 没有任何一句提到“前面例子的答案都是 A”**——模型给出的是一段看似严密的、围绕题目本身展开的论证，结论恰好是 (A)。换言之，CoT 文本和决定答案的真实因子之间存在一条**显著的脱钩**。

两个月后，Anthropic 内部 Tamera Lanham 的 [*Measuring Faithfulness in CoT*](https://arxiv.org/abs/2307.13702) 把这件事系统化了。Lanham 设计了三类扰动：截断 CoT、在 CoT 中间插入错误、给 CoT 中间塞 paraphrase。她衡量的不是“CoT 写得对不对”，而是“扰动 CoT 后最终答案是否相应改变”——一个**忠实的** CoT 应该对扰动敏感。结果在 13B/175B 规模上呈现一个反直觉的 U 形：小模型的 CoT 几乎没用（截掉也不影响答案，说明答案不依赖它）；大模型的 CoT 也越来越不忠实（截掉照样答对，说明答案在 CoT 之前就内部决定了）；中间规模反而最忠实。Lanham 论文里 Claude 1.3 在 ARC-Challenge 上“truncate CoT halfway”的答案保持率达到 80% 以上 [unverified 具体数字]——也就是大多数题目，模型在没写完 CoT 的时候就已经知道答案。

把 Turpin 和 Lanham 并排放，结论很硬：**CoT 文本在很大一部分情况下不是计算路径，而是计算结果的事后叙事。** 这件事和 §3 Dziri 的曲线乍看矛盾——Dziri 说 CoT 能把 depth 曲线右推 1–2 步，Lanham 说 CoT 大多是装饰——但其实不矛盾。Dziri 测的是“允许写 CoT 时 accuracy 变高多少”，Lanham 测的是“已经写出的 CoT 是不是真的承载了那部分计算”。两者合起来给出一个更精细的图像：CoT 在 depth 4–5 这段确实买到了真实算力（所以截掉会掉点），在 depth ≤ 3 的题目上则主要是事后合理化（所以截掉无所谓）。Yanda Chen 等人 2025 年初的 [*Reasoning Models Don't Always Say What They Think*](https://arxiv.org/abs/2503.08679) 在 o1-preview / Claude 3.7-Sonnet-Thinking / DeepSeek-R1 上重做了 Turpin 的偏置实验，发现 reasoning model 时代忠实性有所提升但仍然系统性低于 50%——也就是说 long-CoT RL 缓解了问题但没解决。

这件事和 NTP loss 的关系是什么？NTP 在每个位置都最小化 $-\log p(x_t \mid x_{<t})$，**唯一被惩罚的是 token 序列的分布拟合，没有任何项约束“token 流必须对应一条真实的计算图”**。如果训练分布里大量的 CoT 文本本身就是人类的事后解释（Stack Exchange 答案、教科书证明、技术博客)，那么模型学到的最优策略就是：先在 forward pass 内部把答案算出来（用注意力 head + MLP 的并行计算），然后再生成一段在分布上 plausible 的解释 token 流。两者在 loss 上无差别。Anthropic 2025 年 3 月的 [*On the Biology of a Large Language Model*](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) 用 attribution graph 在 Claude 3.5 Haiku 里直接观察到了这条“answer-first, explanation-after”的回路——模型在很靠前的 token 位置就在 residual stream 里激活了与正确答案对应的 feature，后面几十上百 token 的 CoT 把这个答案 unroll 成自然语言。

反例也要给。Roger Grosse 与合作者 2024 年的 [*Influence Functions for LMs*](https://arxiv.org/abs/2308.03296) 与 OpenAI 的 PRM 路线（[arxiv:2305.20050](https://arxiv.org/abs/2305.20050)）都给出了 CoT 至少**部分忠实**的证据：influence function 显示某些 CoT token 与训练数据里的具体推理片段强相关；PRM 用 step-level reward 训出的模型，删掉中间 step 会显著掉点。这两条线说明 CoT 不是 100% 装饰——在足够难的题目上、足够大的模型里、足够长的 CoT 中，文本流确实承载了一部分计算。但“部分忠实”距离 alignment 圈想要的“CoT 可作为模型推理的透明窗口”还有一大段距离。

我的判断：Turpin 与 Lanham 这条线测的不是模型“会不会撒谎”，测的是 **NTP 训练目标对“内部计算”和“外部解释”之间的耦合不施加任何梯度压力**——所以两者天然解耦是默认状态，耦合反而需要专门的训练信号（PRM、process supervision、CoT-faithfulness reward）去维持。这正是它和 §3 Dziri、§5 Reversal Curse 共享的根因：NTP 优化的是 token 流的边际分布，不优化任何关于“token 流背后机制”的性质。

## 五、Reversal Curse：训练分布的方向性，被一组合成 fictional facts 抓个正着

Lukas Berglund 等人 2023 年 9 月那篇 [*The Reversal Curse*](https://arxiv.org/abs/2309.12288) 的实验设计在 ML 论文工业里属于"老派直接"。他们造了一批纯合成的 fictional fact：诸如 "Daphne Barrington 是电影 *A Journey Through Time* 的导演"，确保这些三元组在公网语料里**完全不存在**，避免任何泄漏。然后把这些事实写成两种自然语言模板：(A) "Daphne Barrington 是 *A Journey Through Time* 的导演"，(B) "*A Journey Through Time* 的导演是 Daphne Barrington"。只用模板 (A) 去 fine-tune GPT-3-350M / LLaMA-7B / LLaMA-30B，然后正向问 "Daphne Barrington 导演了哪部电影？"，模型几乎 100% 答对；反过来问 "*A Journey Through Time* 的导演是谁？"，正确率**接近 0%，几乎不可与瞎猜区分**（论文 Table 2，[arxiv:2309.12288](https://arxiv.org/abs/2309.12288)）。Berglund 还做了一个补做实验：在真实公开人物身上同样测——问 GPT-4 "Tom Cruise 的母亲是谁？"，它能答出 "Mary Lee Pfeiffer"；反过来问 "Mary Lee Pfeiffer 的儿子是谁？"，它答不出来。这个例子被 Owain Evans 发到 Twitter 上，被当成段子流传，但段子背后的结构是真的。

这篇论文一开始被 knowledge-editing 圈接走了，被读作 "MEMIT/ROME 风格的事实注入不对称" 的又一案例——这是一种**降维处理**。真正的问题不在 fine-tune 算法上：Berglund 把 fact 直接以训练数据形式喂进去，不是用 hypernetwork 改权重，所以这是 NTP 损失本身的性质，不是某个编辑算法的 bug。Sanjeev Arora 与 Zeyuan Allen-Zhu 在 *Physics of Language Models* Part 3.2（[arxiv:2404.05405](https://arxiv.org/abs/2404.05405)）里把它做成了一个干净的合成实验：在一个完全可控的玩具语料上，他们证明 NTP 学到的 "A→B" 与 "B→A" 是**两个独立的关联**，模型不会自动把它们融合成一个双向的关系——除非训练数据里**显式**包含 B→A 方向的序列。Allen-Zhu 给的训练 trick 是 "reverse-order pretraining"——把语料按句子级反向再过一遍，可以显著抬高反向召回率。这个 trick 在工程上有效，恰恰说明问题的根子在数据方向性而不在架构。

机制层面的解释，到 2024–2025 年已基本收敛在一个图像上。NTP 的损失是 $-\log p(x_t \mid x_{<t})$，所有梯度信号都沿着**从左到右**的因果方向传播。当模型在某个位置看到 "Daphne Barrington 是" 这个 prefix，正确续写是 "*A Journey Through Time* 的导演"——这条梯度信号训练的是 P(电影名 | 人名 prefix)。但训练语料里**从来没有**出现过 "*A Journey Through Time* 的导演是 ___" 这条 prefix，所以 P(人名 | 电影名 prefix) 这个条件分布完全没有被 NTP loss 触及。Anthropic interpretability team 2024 年 5 月在 [*Scaling Monosemanticity*](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) 里在 Claude 3 Sonnet 里找到了对应的单义特征——某些 feature 在 A→B 的 token 流里被激活而在 B→A 流里完全沉默——这是 Reversal Curse 的机制证据，不是行为证据。把行为和机制两条线对上，结论很硬：**Reversal Curse 不是模型"忘了"反向，而是 NTP loss 从未要求它学过反向**。

反例和缓解一并摆。第一，retrieval-augmented setting 下 Reversal Curse 显著减轻——RAG 把 "*A Journey Through Time* 的导演" 这段 prefix 在测试时拼回上下文，模型只需要做 in-context 的字符串匹配，不依赖参数化记忆。第二，bidirectional pretraining 的工作（BERT 风格 MLM、UL2 [arxiv:2205.05131]、以及最近的 [arxiv:2402.10171] 这类前向-反向混合目标）在小规模上能压住 Reversal Curse，但 scaling 到 100B 以上的代价目前看不到正面证据——主流的 decoder-only NTP 仍然是工业默认。第三，post-training stage 的 instruction tuning 与 RLHF 也能部分填洞，但代价是要在 instruction 数据里**显式构造**反向问答对——这又是在用人工标注补偿 NTP 的天然空缺，不是在改 NTP 自身。Berglund 在论文 §5 里诚实地承认了所有这些缓解路径，但他强调："对一个真正理解事实关系的 agent 来说，反向问答应该是 *为零代价* 的——而现在它的代价是显式构造反向数据。"

我的判断：Reversal Curse 是三块碎片里**最干净的一块**，因为它的合成实验设计排除了所有解释空间，只剩 NTP 损失方向性这一个根因可归。Faith-and-Fate 还能被归结为 "capacity 不够"，Unfaithful CoT 还能被归结为 "training data 里事后解释占多数"——这两条都还留着辩论余地。但 Reversal Curse 的合成 setup 让 capacity / data-distribution / architecture 三个常见挡箭牌全部失效：模型有足够 capacity 去记忆正向 fact（100% 召回是证据），训练分布在你眼皮底下被构造出来（不存在污染辩护），架构和你日常用的 LLaMA 是同一份。剩下的唯一变量就是 **loss 只看一个方向**。这一点让 §5 在结构上扮演了 §3、§4 的对照实验——它是把 NTP 几何的方向性单独隔离出来的最干净证据，也是下一节把三块碎片拼回一张图时最稳的支点。

## 六、三合一：把三块碎片拼回 NTP loss 的几何

前面五节，每一节都给出一个被独立观测、独立命名、独立辩论的现象。这一节要做的事很简单：把它们放在同一张坐标纸上，看看是不是真的同一张图。

先把三件事归约成同一种语法。NTP 的训练目标是 $\mathcal{L} = -\mathbb{E}_{x \sim D}\sum_{t} \log p_\theta(x_t \mid x_{<t})$。这个损失有三条**结构性性质**，与三块碎片一一对应：

1. **逐 token 局部性**——梯度只关心位置 $t$ 处的边际，不关心 $x_t$ 与远处 $x_{t+k}$ 在某条隐式计算图上的组合关系。$\Rightarrow$ Dziri 的 depth 曲线：当任务被压成一个长度为 $k$ 的依赖链时，loss 没有任何项把这条链当作一个整体来优化，所以一旦 $k$ 超过模型在一次 forward 里能并行解开的深度，accuracy 就指数衰减。CoT 把 $k$ 转成 token 数把这个深度部分外化，但**外化的代价仍然是 token 预算**——Feng 的 P/poly 定理（[arxiv:2305.15408](https://arxiv.org/abs/2305.15408)）正是这件事的形式化。
2. **过程-结果同构惩罚**——loss 对 \"$x_t$ 是真实计算路径上的下一步\" 和 \"$x_t$ 是事后合理化中的下一步\" 给出**完全相同**的惩罚，只要边际分布对就行。$\Rightarrow$ Turpin 与 Lanham 的 unfaithful CoT：模型在 forward pass 内部把答案算出来再 unroll 一段 plausible 的解释，与真正先写 scratchpad 再得答案，在 NTP loss 上无法区分。Anthropic 2025 年 3 月的 [*Biology of an LLM*](https://transformer-circuits.pub/2025/attribution-graphs/biology.html) 在 Claude 3.5 Haiku 里把这条 \"answer-first, explanation-after\" 的回路直接画了出来——它不是 bug，它是 loss 不施压的自然吸引子。
3. **方向单向性**——梯度沿 $x_{<t} \to x_t$ 这一个方向传播，关系 $(A, B)$ 在训练流里以 $A \to B$ 出现，被学到的就只是 $P(B \mid A\text{-prefix})$，$P(A \mid B\text{-prefix})$ 这条**对偶条件分布从未进入 loss**。$\Rightarrow$ Berglund 的 Reversal Curse，Allen-Zhu *Physics of LM* Part 3.2（[arxiv:2404.05405](https://arxiv.org/abs/2404.05405)）的合成复现，Scaling Monosemanticity 在 Claude 3 Sonnet 里找到的方向性 feature。Reversal 是三条性质里最干净的一条，因为它只调用了第三条，其他变量全部被合成 setup 锁死。

把这三条并列写下来后，可以看出一件容易被忽略的事：**三个现象是 NTP loss 三条独立性质各自的最干净显现**，并不是同一条根因的三种表象。它们是同一损失函数的**三种正交切面**。Reversal 不能解释 Faith-and-Fate（前者关于方向，后者关于深度），Faith-and-Fate 不能解释 Unfaithful CoT（前者是模型算不出来，后者是模型算出来了但不告诉你怎么算的）。把它们说成 \"同一根因\" 是一种叙事上的偷懒；准确的说法是 \"同一损失函数的三条不同性质各自的暴露窗口\"。这种区分在工程上很重要——因为缓解手段是**不可互换**的。

让我把缓解路径也并表对齐一次：

| 现象 | 对应 loss 性质 | 当前已知缓解 | 缓解付出的真实代价 |
|---|---|---|---|
| Faith-and-Fate depth 衰减 | 逐 token 局部性 | long-CoT RL（o1 / R1，[arxiv:2501.12948](https://arxiv.org/abs/2501.12948)）、PRM | 推理 token 预算 10–100× 增长，deploy 成本线性 |
| Unfaithful CoT | 过程-结果同构惩罚 | process supervision、CoT-faithfulness reward、Anthropic 的 attribution graph 监督 | 需要专门的中间监督信号，标注昂贵 |
| Reversal Curse | 方向单向性 | reverse-order pretraining、bidirectional objective（UL2 [arxiv:2205.05131]）、RAG | reverse-order 在 100B+ 规模的 scaling 证据缺失；RAG 把问题外推到检索系统 |

三种缓解都**没有改 NTP loss 本身**——它们或者在 inference 时加 token（CoT/RAG），或者在 training 时加额外监督信号（PRM、faithfulness reward），或者在数据上做对称化扩增（reverse-order）。这说明三块碎片揭示的不是某个可以被算法 patch 掉的小毛病，而是 NTP 这个**目标函数族**的结构边界。要真正越过去，需要的不是更长的 CoT 也不是更大的模型，而是一个**不同形态的 loss**——比如 joint-distribution 目标（diffusion-LM 一类）、bidirectional objective、或者带显式 latent computation graph 的 variational 目标。这些方向在 2024–2025 都有零星工作，但都还没有在 scaling 上跑出能与 decoder-only NTP 正面对抗的曲线。

反例必须再摆一次，因为本节的论点已经强到需要被攻击。最有力的反对意见是 Sutton 式的：\"这三条性质都已被 token / 算力 / RL 部分缓解，按 bitter lesson 的历史归纳，剩下的也会被缓解，所谓 NTP 几何边界只是当前工程曲线上的拐点，不是绝对墙。\" 这个反对我接受一半——三种缓解确实都在推进，o1/R1 把 depth 推到了 Dziri 当年曲线之外，Yanda Chen 2025 年初的复测（[arxiv:2503.08679](https://arxiv.org/abs/2503.08679)）显示 long-CoT RL 时代 faithfulness 在抬头，reverse-order pretraining 在 7B 规模已能压住 Reversal Curse。所以 \"墙\" 这个词在物理意义上是错的。但**经济意义**上的墙仍在：三种缓解都把推理或训练成本提高了 $10\\times$ 以上数量级，而 NTP 在原始形态下的算力效率仍未被任何替代 loss 在 100B+ 规模上超越。在 \"算力价格不再每 18 个月减半\" 成立之前，这种经济墙就是真实约束。

我的总结判断分三层。第一层（最不诱惑、最稳）：三块碎片是 NTP loss 三条独立结构性质的最干净暴露，把它们说成 \"同一现象\" 是叙事偷懒。第二层（中等强度）：三条性质的缓解手段不可互换，且都**不改 loss 本身**——这意味着 NTP 不是 \"reasoning 没做好\"，而是 \"reasoning 的某些维度根本不在 loss 的优化目标里\"。第三层（最强、最容易错）：如果未来 5 年我们没看到一个能在 100B+ scaling 上正面挑战 decoder-only NTP 的替代 loss 出现，那么这三条性质就会**继续**以越来越精细的形态在前沿模型上复现——只是被更厚的 CoT、更多的 PRM、更长的 context 临时遮住。Reversal Curse 这种最赤裸的版本可能消失，但它的同构变体会在 multi-hop QA、长程因果推断、跨文档事实融合上反复出现。这是我愿意打的一个赌；2027 年回来对账。

下一篇 N4 会把视角从 \"loss 的局部性质\" 抬到 \"loss 在 Pearl 因果阶梯上的位置\"——Reversal Curse 是 Layer 1 内部的对偶失败，更难的问题在 Layer 2/3 上，而那里 NTP 暴露的不是单条性质，而是整个层级被压扁。

## 尾声：三条 2027 对账线，与一段方法论上的自我攻击

把第六节的论证落到能被 2027 年回头打脸的具体赌注上，三块碎片各对应一条。

**赌 1（对应 §3 Faith-and-Fate / 逐 token 局部性）**。到 2027-12 之前，会出现至少一个公开模型——非检索增强、非外接 verifier、单次 forward 加 ≤4k token 的 CoT 预算——在 Dziri 三任务的 depth ≥ 6 切片上达到 ≥ 70%。如果到点没有，bitter-lesson 阵营 "靠 token 买 depth 没有经济上限" 的乐观叙事就要交一次学费；如果到点有，**且**该模型在 PutnamBench（[arxiv:2407.11214](https://arxiv.org/abs/2407.11214)）这种结构上更深的 benchmark 上同步抬升 ≥ 20pp，那 §3 把 Dziri 曲线读作 "NTP loss 局部性的结构暴露" 的论证就要弱化为 "只是当前训练数据未覆盖深 depth 模式"——这是我承认会被打脸的最高频候选。

**赌 2（对应 §4 Unfaithful CoT / 过程-结果同构惩罚）**。Yanda Chen 2025 ([arxiv:2503.08679](https://arxiv.org/abs/2503.08679)) 在 reasoning-model 一代上量到的 faithfulness 仍系统性 < 50%；ProFIL ([arxiv:2605.11467](https://arxiv.org/abs/2605.11467) [unverified ID]) 在 GSM8K/LiveCodeBench/ToolUse/MMLU-Redux 上把 post-commitment CoT theater 减 11–100%。两条线交叉外推：到 2027-12 之前，会出现一个公开复测把 frontier reasoning model 在 Turpin-类偏置 prompt 上的 faithfulness 抬过 70%，**且** Anthropic 类 attribution graph 在同一模型上观察不到 "answer-first, explanation-after" 主导回路。两条同时达成，则 §4 论点的强形式（"过程-结果脱钩是 NTP loss 的吸引子"）应降级为 "工程可控的 readout-side 副作用"——这与 [`../survey/taxonomy.md`](../survey/taxonomy.md) 2026-05-28 升降级日志里 ProFIL 触发的那条降级是一脉相承的。我倾向于赌降级会发生，但只到 NTP-cap 一级，不会进一步到 Pseudo-NTP——因为 Anthropic biology 那条 "answer-first" 回路即使被工程压制，loss 不施压的事实没有改变。

**赌 3（对应 §5 Reversal Curse / 方向单向性）**。这条是三条里最稳的。到 2027-12 之前，"训练只看 A→B 模板、测试问 B→A、不许 in-context restatement、不许 RAG" 这个 Berglund 原始 setup 在公开报告里仍会显示 frontier decoder-only LLM（无论参数量）正向 ≥ 95% / 反向 < 20%。Allen-Zhu reverse-order pretraining 工程 trick 即便被工业采用，也只把 setup 改造为 "训练看两个方向"——这不是反例，是把 Reversal Curse 通过数据对称化绕开。真正反例长这样：一个 vanilla autoregressive NTP 模型，训练分布里完全无反向，但因 in-context generalization 在反向问答上 ≥ 50%。这种证据目前为零；如果 2027 年仍为零，§5 把 Reversal 读作 NTP loss 第三性质最干净显现的判断就保持稳固。如果出现，我整章的"三正交切面"框架要重写——不是因为 Reversal 被解，而是因为 NTP 内部存在某种我现在没识别到的对称化机制。

最后给一段对自己的方法论攻击，这件事我欠读者。第六节那张三列对照表（现象 / loss 性质 / 缓解 / 代价）的最大方法论风险是**事后选择偏差**：我从 NTP loss 写出三条性质，再去三个文献圈各挑一个最契合的现象做映射。这种 "找配对" 做法在历史叙事里几乎一定能成功，因为 loss 性质足够基础、文献现象足够多。要把它从叙事升格为论点，需要一条**预言性的**反向证据——某个尚未被命名的现象，被本章的三条性质框架成功 *预测* 出来，再被独立实验确认。本章没有给出这样的预言，所以诚实地说，它的论证强度上限是 "对已观察到的三块碎片提供了一个统一的 loss-几何视角"，**不是** "证明了 NTP 必然显现这三块碎片"。把它推过这条线，得等下一章 N4 把视角抬到 Pearl 阶梯上以后回头补——那里有 CLadder ([arxiv:2312.04350](https://arxiv.org/abs/2312.04350)) 这种 leak-checked 的 Layer-2/3 benchmark 给的硬数据，能反过来检验本章三条性质中第一条（逐 token 局部性）和第三条（方向单向性）在更高阶因果层级上是否仍然预测正确的失败模式。如果 N4 §3 显示 frontier LLM 在 CLadder Layer-2 上的失败模式可被本章框架预先归类到 "局部性 + 方向性合流"，则本章升格为"有预测力的框架"；如果不行，本章仍只是"事后整理的叙事"。读者读到 N4 §3 时，请回到这一段对账。

