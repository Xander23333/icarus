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

> §4 Turpin & Lanham：CoT 的"事后合理化"通道 / §5 Reversal Curse：训练分布的方向性 / §6 三合一：NTP loss 几何的统一解释（TODO，待续写）
